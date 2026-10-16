"""Content database (build/content.sqlite): open, build from data/, query."""

import json
import sqlite3
from pathlib import Path

from . import annotation_files
from . import texts as text_files
from .texts import HAN, HAN_RUN

PACKAGE_DIR = Path(__file__).parent
SCHEMA_PATH = PACKAGE_DIR / "schema.sql"
PROGRESS_SCHEMA_PATH = PACKAGE_DIR / "progress.sql"
CONTENT_TABLES = ("character", "word", "text", "tag", "text_character", "text_word", "text_expansion", "text_reading", "text_note")


def connect(path, readonly=False, progress_path=None) -> sqlite3.Connection:
    """Open the content database; with `progress_path`, attach the learner database as `progress` (created if missing)."""
    mode = "ro" if readonly else "rwc"
    conn = sqlite3.connect(f"file:{Path(path).resolve()}?mode={mode}", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if progress_path is not None:
        Path(progress_path).parent.mkdir(parents=True, exist_ok=True)
        conn.execute("ATTACH DATABASE ? AS progress", (str(Path(progress_path).resolve()),))
        conn.executescript(PROGRESS_SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO progress.learner (id, name) SELECT 1, '学生' WHERE NOT EXISTS (SELECT 1 FROM progress.learner)")
        conn.commit()
    return conn


class GlossFileError(ValueError):
    """data/character-gloss.tsv violates its format; the message names the line."""


def load_character_glosses(conn, path) -> int:
    """Apply the curated overlay `char<TAB>gloss` (rules: docs/prompts/character-gloss.md). Returns how many were set."""
    seen = {}
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        columns = line.split("\t")
        if len(columns) != 2:
            raise GlossFileError(f"{path}:{number}: expected two tab-separated columns, got {len(columns)}")
        char, gloss = columns[0].strip(), columns[1].strip()
        if not gloss:
            raise GlossFileError(f"{path}:{number}: blank gloss for {char!r}")
        if len(gloss) > 120:
            raise GlossFileError(f"{path}:{number}: gloss for {char!r} is {len(gloss)} characters, over 120")
        if char in seen:
            raise GlossFileError(f"{path}:{number}: duplicate character {char!r} (also on line {seen[char]})")
        if conn.execute("UPDATE character SET gloss = ? WHERE char = ?", (gloss, char)).rowcount == 0:
            raise GlossFileError(f"{path}:{number}: character {char!r} is not in the master")
        seen[char] = number
    return len(seen)


def build(db_path, data_dir) -> dict[str, int]:
    """Delete and recreate the content database from data/. Returns row counts."""
    db_path, data_dir = Path(db_path), Path(data_dir)
    texts = text_files.load_texts(data_dir / "texts")
    for suffix in ("", "-journal", "-wal", "-shm"):
        Path(str(db_path) + suffix).unlink(missing_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    with conn:
        conn.executescript((data_dir / "hsk.sql").read_text(encoding="utf-8"))
        load_character_glosses(conn, data_dir / "character-gloss.tsv")
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        for t in texts:
            conn.execute(
                "INSERT INTO text (id, title, author, period, body, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (t.id, t.title, t.author, t.period, t.body, t.notes),
            )
            for tag in t.tags:
                conn.execute("INSERT OR IGNORE INTO tag (name) VALUES (?)", (tag,))
                conn.execute("INSERT INTO text_tag (text_id, tag_name) VALUES (?, ?)", (t.id, tag))
        annotation_files.import_all(conn, data_dir)
    counts = {table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in CONTENT_TABLES}
    counts["character_gloss"] = conn.execute("SELECT count(*) FROM character WHERE gloss IS NOT NULL").fetchone()[0]
    conn.close()
    return counts


# --- texts ---------------------------------------------------------------


def filter_options(conn) -> dict[str, list[str]]:
    return {
        "tags": [r[0] for r in conn.execute("SELECT name FROM tag ORDER BY rowid")],
        "authors": [r[0] for r in conn.execute("SELECT DISTINCT author FROM text WHERE author IS NOT NULL ORDER BY author")],
        "periods": [r[0] for r in conn.execute("SELECT DISTINCT period FROM text WHERE period IS NOT NULL ORDER BY period")],
    }


def list_texts(conn, tag=None, author=None, period=None) -> list[dict]:
    where, params = [], []
    if tag:
        where.append("id IN (SELECT text_id FROM text_tag WHERE tag_name = ?)")
        params.append(tag)
    if author:
        where.append("author = ?")
        params.append(author)
    if period:
        where.append("period = ?")
        params.append(period)
    sql = "SELECT id, title, author, period FROM text"
    if where:
        sql += " WHERE " + " AND ".join(where)
    rows = conn.execute(sql + " ORDER BY id", params).fetchall()
    return [dict(r, tags=text_tags(conn, r["id"])) for r in rows]


def text_tags(conn, text_id) -> list[str]:
    return [r[0] for r in conn.execute("SELECT tag_name FROM text_tag WHERE text_id = ? ORDER BY rowid", (text_id,))]


def get_text(conn, text_id) -> dict | None:
    row = conn.execute("SELECT * FROM text WHERE id = ?", (text_id,)).fetchone()
    return dict(row, tags=text_tags(conn, text_id)) if row else None


# --- characters and words ------------------------------------------------


def unique_characters(body: str) -> list[str]:
    """Every Han character in `body`, once each, in order of first appearance."""
    return list(dict.fromkeys(HAN.findall(body)))


def lookup_characters(conn, chars) -> list[dict]:
    """One entry per character, in the given order; `found` is False when absent from the master."""
    chars = list(dict.fromkeys(chars))
    found = {}
    for chunk in _chunks(chars):
        marks = ",".join("?" * len(chunk))
        for r in conn.execute(f"SELECT * FROM character WHERE char IN ({marks})", chunk):
            found[r["char"]] = dict(r, readings=json.loads(r["readings"]), found=True)
    return [found.get(c, {"char": c, "found": False}) for c in chars]


def find_words(conn, body: str) -> list[dict]:
    """Every 2–4 character window inside a run of Han characters that is a master word, once each, in order of first appearance."""
    runs = [m.group() for m in HAN_RUN.finditer(body)]
    candidates = list(dict.fromkeys(run[i : i + n] for run in runs for i in range(len(run)) for n in (2, 3, 4) if i + n <= len(run)))
    found = {}
    for chunk in _chunks(candidates):
        marks = ",".join("?" * len(chunk))
        for r in conn.execute(f"SELECT * FROM word WHERE simplified IN ({marks})", chunk):
            found[r["simplified"]] = dict(r, meanings=json.loads(r["meanings"]), readings=json.loads(r["readings"]))
    return [found[c] for c in candidates if c in found]


def _chunks(items, size=500):
    for i in range(0, len(items), size):
        yield items[i : i + size]
