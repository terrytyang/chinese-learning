"""Annotations: admin curation of a text, persisted write-through to data/annotations/<id>.json.

The JSON file is the source of truth; it stores surfaces, never word ids.
`build` re-imports every file through the same add_* functions the admin page uses.
"""

import json
from pathlib import Path

from .texts import HAN

KINDS = ("characters", "words", "expansions", "notes")


class AnnotationError(ValueError):
    """Invalid annotation; the message is Chinese, for the admin page."""


# --- validation helpers ---------------------------------------------------


def _clean(value):
    value = (value or "").strip()
    return value or None


def _body(conn, text_id):
    row = conn.execute("SELECT body FROM text WHERE id = ?", (text_id,)).fetchone()
    if row is None:
        raise AnnotationError("没有这篇课文")
    return row[0]


def _char_in(body, char):
    char = _clean(char) or ""
    if len(char) != 1 or not HAN.fullmatch(char) or char not in body:
        raise AnnotationError(f"「{char}」不是正文里的单个汉字")
    return char


def _resolve(conn, surface, gloss):
    """word_id of a master word; a surface absent from the master must be glossed."""
    row = conn.execute("SELECT id FROM word WHERE simplified = ?", (surface,)).fetchone()
    if row is None and gloss is None:
        raise AnnotationError(f"字库里没有「{surface}」，请填写释义")
    return row[0] if row else None


# --- add / remove (duplicates are no-ops) ---------------------------------


def add_character(conn, text_id, char, gloss=None):
    char = _char_in(_body(conn, text_id), char)
    conn.execute("INSERT OR IGNORE INTO text_character (text_id, char, gloss) VALUES (?, ?, ?)", (text_id, char, _clean(gloss)))


def add_word(conn, text_id, surface, gloss=None):
    body, surface, gloss = _body(conn, text_id), _clean(surface), _clean(gloss)
    if not surface or surface not in body:
        raise AnnotationError(f"「{surface or ''}」没有出现在正文里")
    word_id = _resolve(conn, surface, gloss)
    conn.execute("INSERT OR IGNORE INTO text_word (text_id, surface, word_id, gloss) VALUES (?, ?, ?, ?)", (text_id, surface, word_id, gloss))


def add_expansion(conn, text_id, char, surface, gloss=None):
    char, surface, gloss = _char_in(_body(conn, text_id), char), _clean(surface), _clean(gloss)
    if not surface:
        raise AnnotationError("请填写扩展词")
    word_id = _resolve(conn, surface, gloss)
    conn.execute(
        "INSERT OR IGNORE INTO text_expansion (text_id, char, surface, word_id, gloss) VALUES (?, ?, ?, ?, ?)",
        (text_id, char, surface, word_id, gloss),
    )


def add_note(conn, text_id, note, anchor=None):
    body, note, anchor = _body(conn, text_id), _clean(note), _clean(anchor)
    if not note:
        raise AnnotationError("请填写注")
    if anchor and anchor not in body:
        raise AnnotationError(f"「{anchor}」没有出现在正文里")
    if not conn.execute("SELECT 1 FROM text_note WHERE text_id = ? AND anchor IS ? AND note = ?", (text_id, anchor, note)).fetchone():
        conn.execute("INSERT INTO text_note (text_id, anchor, note) VALUES (?, ?, ?)", (text_id, anchor, note))


def remove_character(conn, text_id, char):
    conn.execute("DELETE FROM text_character WHERE text_id = ? AND char = ?", (text_id, char))


def remove_word(conn, text_id, surface):
    conn.execute("DELETE FROM text_word WHERE text_id = ? AND surface = ?", (text_id, surface))


def remove_expansion(conn, text_id, char, surface):
    conn.execute("DELETE FROM text_expansion WHERE text_id = ? AND char = ? AND surface = ?", (text_id, char, surface))


def remove_note(conn, text_id, note_id):
    conn.execute("DELETE FROM text_note WHERE text_id = ? AND id = ?", (text_id, note_id))


# --- read ------------------------------------------------------------------

MASTER = "w.pinyin, w.hsk_level, w.hsk_edition, w.meanings"


def load(conn, text_id) -> dict:
    """Annotations for the page, joined to the master, in body order."""
    body = _body(conn, text_id)
    position = lambda s: body.find(s) if s else len(body)  # noqa: E731
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (text_id,))]  # noqa: E731
    words = rows(f"SELECT t.surface, t.word_id, t.gloss, {MASTER} FROM text_word t LEFT JOIN word w ON w.id = t.word_id WHERE t.text_id = ?")
    expansions = rows(f"SELECT t.char, t.surface, t.word_id, t.gloss, {MASTER} FROM text_expansion t LEFT JOIN word w ON w.id = t.word_id WHERE t.text_id = ?")
    for r in words + expansions:
        r["meanings"] = json.loads(r["meanings"]) if r["meanings"] else []
    return {
        "characters": sorted(rows("SELECT char, gloss FROM text_character WHERE text_id = ?"), key=lambda r: position(r["char"])),
        "words": sorted(words, key=lambda r: position(r["surface"])),
        "expansions": sorted(expansions, key=lambda r: (position(r["char"]), r["surface"])),
        "notes": sorted(rows("SELECT id, anchor, note FROM text_note WHERE text_id = ?"), key=lambda r: (position(r["anchor"]), r["note"])),
    }


def export(conn, text_id) -> dict:
    """File content: keys in documented order, lists sorted by natural key, surfaces only."""
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (text_id,))]  # noqa: E731
    return {
        "text_id": text_id,
        "characters": rows("SELECT char, gloss FROM text_character WHERE text_id = ? ORDER BY char"),
        "words": rows("SELECT surface, gloss FROM text_word WHERE text_id = ? ORDER BY surface"),
        "expansions": rows("SELECT char, surface, gloss FROM text_expansion WHERE text_id = ? ORDER BY char, surface"),
        "notes": rows("SELECT anchor, note FROM text_note WHERE text_id = ? ORDER BY coalesce(anchor, ''), note"),
    }


# --- files -----------------------------------------------------------------


def file_path(data_dir, text_id) -> Path:
    return Path(data_dir) / "annotations" / f"{text_id}.json"


def write_file(conn, text_id, data_dir):
    """Rewrite data/annotations/<id>.json from the database; no annotations, no file."""
    path, data = file_path(data_dir, text_id), export(conn, text_id)
    if not any(data[kind] for kind in KINDS):
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_all(conn, data_dir):
    """Import every data/annotations/*.json; any problem is an AnnotationError naming the file."""
    for path in sorted(Path(data_dir, "annotations").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        text_id = data.get("text_id")
        try:
            if path.stem != str(text_id) or not conn.execute("SELECT 1 FROM text WHERE id = ?", (text_id,)).fetchone():
                raise AnnotationError(f"没有 id 为 {text_id} 的课文")
            for c in data.get("characters", []):
                add_character(conn, text_id, c["char"], c.get("gloss"))
            for w in data.get("words", []):
                add_word(conn, text_id, w["surface"], w.get("gloss"))
            for e in data.get("expansions", []):
                add_expansion(conn, text_id, e["char"], e["surface"], e.get("gloss"))
            for n in data.get("notes", []):
                add_note(conn, text_id, n["note"], n.get("anchor"))
        except AnnotationError as e:
            raise AnnotationError(f"{path}: {e}") from None
