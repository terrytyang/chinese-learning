"""Content database (build/content.sqlite): open, build from data/, query."""

import json
import sqlite3
from pathlib import Path

from . import annotation_files, lesson_files, supplement
from . import texts as text_files
from .texts import HAN, HAN_RUN

PACKAGE_DIR = Path(__file__).parent
SCHEMA_PATH = PACKAGE_DIR / "schema.sql"
PROGRESS_SCHEMA_PATH = PACKAGE_DIR / "progress.sql"
CONTENT_TABLES = ("character", "word", "text", "tag", "text_reading", "text_character", "text_word", "lesson", "lesson_character", "lesson_word", "lesson_extra_word", "lesson_note")
JSON_COLUMNS = ("readings", "meanings", "alt_readings")


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
        conn.execute("INSERT INTO progress.learner (id, name) SELECT 1, 'Student' WHERE NOT EXISTS (SELECT 1 FROM progress.learner)")
        conn.commit()
    return conn


def build(db_path, data_dir) -> dict[str, int]:
    """Delete and recreate the content database from data/. Returns row counts, plus the supplement's entries and how many lack a gloss."""
    db_path, data_dir = Path(db_path), Path(data_dir)
    texts = text_files.load_texts(data_dir / "texts")
    for suffix in ("", "-journal", "-wal", "-shm"):
        Path(str(db_path) + suffix).unlink(missing_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(db_path)
    with conn:
        conn.executescript((data_dir / "hsk.sql").read_text(encoding="utf-8"))
        entries, unglossed = supplement.load(conn, data_dir)
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
        lesson_files.import_all(conn, data_dir)
    counts = {table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] for table in CONTENT_TABLES}
    conn.close()
    return {**counts, "supplement": entries, "supplement_unglossed": unglossed}


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


def update_text_tags(conn, text_id, tags):
    """Mirror a rewritten header: the tag set (new tag names are created)."""
    conn.execute("DELETE FROM text_tag WHERE text_id = ?", (text_id,))
    for tag in tags:
        conn.execute("INSERT OR IGNORE INTO tag (name) VALUES (?)", (tag,))
        conn.execute("INSERT INTO text_tag (text_id, tag_name) VALUES (?, ?)", (text_id, tag))


def text_tags(conn, text_id) -> list[str]:
    return [r[0] for r in conn.execute("SELECT tag_name FROM text_tag WHERE text_id = ? ORDER BY rowid", (text_id,))]


def get_text(conn, text_id) -> dict | None:
    row = conn.execute("SELECT * FROM text WHERE id = ?", (text_id,)).fetchone()
    return dict(row, tags=text_tags(conn, text_id)) if row else None


# --- characters and words ------------------------------------------------


def unique_characters(body: str) -> list[str]:
    """Every Han character in `body`, once each, in order of first appearance."""
    return list(dict.fromkeys(HAN.findall(body)))


def _decoded(row) -> dict:
    """A master row with its JSON columns parsed; a null list column becomes []."""
    out = dict(row)
    for column in JSON_COLUMNS:
        if column in out:
            out[column] = json.loads(out[column]) if out[column] else []
    return out


def lookup_character(conn, char) -> dict | None:
    """The `character` row, HSK or supplement, with its JSON columns parsed; None when the dictionary lacks it."""
    row = conn.execute("SELECT * FROM character WHERE char = ?", (char,)).fetchone()
    return _decoded(row) if row else None


def lookup_word(conn, surface) -> dict | None:
    """The `word` row, HSK or supplement, with its JSON columns parsed; None when the dictionary lacks it."""
    row = conn.execute("SELECT * FROM word WHERE simplified = ?", (surface,)).fetchone()
    return _decoded(row) if row else None


def lookup_characters(conn, chars) -> list[dict]:
    """One entry per character, in the given order; `found` is False when the dictionary lacks it.

    A found entry carries every `character` column: the readings list, and the item data
    (`meanings`, `alt_readings`, `pos`, `frequency_rank`, `word_level`) when the syllabus lists it alone.
    """
    chars = list(dict.fromkeys(chars))
    found = {}
    for chunk in _chunks(chars):
        marks = ",".join("?" * len(chunk))
        for r in conn.execute(f"SELECT * FROM character WHERE char IN ({marks})", chunk):
            found[r["char"]] = dict(_decoded(r), found=True)
    return [found.get(c, {"char": c, "found": False}) for c in chars]


def find_words(conn, body: str) -> list[dict]:
    """Every 2–4 character window inside a run of Han characters that is a dictionary word, once each, in order of first appearance.

    Each entry is the `word` row with `meanings` and `alt_readings` parsed; the full list of forms is the primary columns plus `alt_readings`.
    """
    runs = [m.group() for m in HAN_RUN.finditer(body)]
    candidates = list(dict.fromkeys(run[i : i + n] for run in runs for i in range(len(run)) for n in (2, 3, 4) if i + n <= len(run)))
    found = {}
    for chunk in _chunks(candidates):
        marks = ",".join("?" * len(chunk))
        for r in conn.execute(f"SELECT * FROM word WHERE simplified IN ({marks})", chunk):
            found[r["simplified"]] = _decoded(r)
    return [found[c] for c in candidates if c in found]


def _chunks(items, size=500):
    for i in range(0, len(items), size):
        yield items[i : i + size]
