"""Text facts: readings per position, character facts, words (design.md, layer 3). Validation, add, edit, remove, page query.

`annotation_files` persists them write-through to data/annotations/<id>.json and
re-imports them on build through the same functions the admin page uses.
"""

import json

from . import pinyin as pinyin_, readings
from .texts import HAN

ORIGINS = ("auto", "suggested", "manual")
TABLES = {"characters": ("text_character", "char = ?"), "words": ("text_word", "surface = ?")}
SINGLE_CHARACTER = "a single character is a character; add it in Characters"


class AnnotationError(ValueError):
    """Invalid annotation; the message names the offending value, for the admin page."""


# --- validation helpers (shared with lessons.py) ---------------------------

def clean(value):
    value = (value or "").strip()
    return value or None


def body_of(conn, text_id):
    row = conn.execute("SELECT body FROM text WHERE id = ?", (text_id,)).fetchone()
    if row is None:
        raise AnnotationError("no such text")
    return row[0]


def char_in(body, char):
    char = clean(char) or ""
    if len(char) != 1 or not HAN.fullmatch(char) or char not in body:
        raise AnnotationError(f"“{char}” is not a single character of the text")
    return char


def word_surface(surface):
    """A word is at least two characters; a single character is a character everywhere."""
    surface = clean(surface)
    if not surface:
        raise AnnotationError("a word is required")
    if len(surface) == 1:
        raise AnnotationError(SINGLE_CHARACTER)
    return surface


def origin_of(value):
    if value not in ORIGINS:
        raise AnnotationError(f"origin must be auto, suggested or manual, not “{value}”")
    return value


def level_of(value):
    """HSK level for a local word, unlinked extra word or character fact: blank means none, else 1–7."""
    if value in (None, ""):
        return None
    if not (isinstance(value, int) or str(value).isdigit()) or not 1 <= int(value) <= 7:
        raise AnnotationError("level must be 1 to 7")
    return int(value)


def resolve_word(conn, surface, gloss):
    """word_id of a master word; a surface absent from the master must be glossed."""
    row = conn.execute("SELECT id FROM word WHERE simplified = ?", (surface,)).fetchone()
    if row is None and gloss is None:
        raise AnnotationError(f"“{surface}” is not in the master; a gloss is required")
    return row[0] if row else None


def _local_pinyin(conn, text_id, surface, pinyin):
    """A local word always stores its reading: the given one, else prefilled from its characters."""
    pinyin = pinyin or readings.default_pinyin(conn, text_id, surface)
    if pinyin is None:
        raise AnnotationError(f"“{surface}” contains a character the master lacks; a pinyin is required")
    return pinyin


# --- readings: one row per Han position; setting replaces -----------------

def set_reading(conn, text_id, position, char, pinyin, origin="manual"):
    body, pinyin = body_of(conn, text_id), pinyin_.to_marks(clean(pinyin))
    if not isinstance(position, int) or not 0 <= position < len(body) or not HAN.fullmatch(body[position]):
        raise AnnotationError(f"position {position} is not a Han character")
    if body[position] != char:
        raise AnnotationError(f"position {position} is “{body[position]}”, not “{char}”; re-run intake")
    row = conn.execute("SELECT readings FROM character WHERE char = ?", (char,)).fetchone()
    allowed = json.loads(row[0]) if row else None
    if allowed and pinyin not in allowed:
        raise AnnotationError(f"the reading of “{char}” must be one of {', '.join(allowed)}")
    if not pinyin:
        raise AnnotationError(f"a reading for “{char}” is required")
    sql = "INSERT OR REPLACE INTO text_reading (text_id, position, char, pinyin, origin) VALUES (?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, position, char, pinyin, origin_of(origin)))


# --- character facts and words (duplicates are no-ops) --------------------

def add_character(conn, text_id, char, gloss=None, hsk_level=None, origin="manual"):
    char = char_in(body_of(conn, text_id), char)
    sql = "INSERT OR IGNORE INTO text_character (text_id, char, hsk_level, gloss, origin) VALUES (?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, char, level_of(hsk_level), clean(gloss), origin_of(origin)))


def add_word(conn, text_id, surface, gloss=None, pinyin=None, origin="manual", hsk_level=None):
    body, surface, gloss, pinyin = body_of(conn, text_id), word_surface(surface), clean(gloss), pinyin_.to_marks(clean(pinyin))
    if surface not in body:
        raise AnnotationError(f"“{surface}” does not occur in the text")
    word_id, level = resolve_word(conn, surface, gloss), level_of(hsk_level)
    if word_id is None:
        pinyin = _local_pinyin(conn, text_id, surface, pinyin)
    sql = "INSERT OR IGNORE INTO text_word (text_id, surface, word_id, pinyin, hsk_level, gloss, origin) VALUES (?, ?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, surface, word_id, pinyin, level if word_id is None else None, gloss, origin_of(origin)))


def remove(conn, text_id, kind, *key):
    table, where = TABLES[kind]
    conn.execute(f"DELETE FROM {table} WHERE text_id = ? AND {where}", (text_id, *key))
    if kind == "words":  # a deleted fact leaves no dangling lesson selection
        conn.execute("DELETE FROM lesson_word WHERE surface = ? AND lesson_id IN (SELECT id FROM lesson WHERE text_id = ?)", (key[0], text_id))


def confirm(conn, text_id, kind, *key):
    """The admin vouches for an auto or suggested row: origin becomes manual."""
    table, where = TABLES[kind]
    conn.execute(f"UPDATE {table} SET origin = 'manual' WHERE text_id = ? AND {where}", (text_id, *key))


def update(conn, text_id, kind, key, fields):
    """Edit one fact in place (validation as for add); origin becomes manual.

    A character's gloss and level are upserted: the fact row appears when something is set and goes when both are blank.
    """
    gloss = clean(fields.get("gloss"))
    if kind == "characters":
        char, level = char_in(body_of(conn, text_id), key[0]), level_of(fields.get("hsk_level"))
        conn.execute("DELETE FROM text_character WHERE text_id = ? AND char = ?", (text_id, char))
        if gloss is not None or level is not None:
            add_character(conn, text_id, char, gloss, level)
        return
    row = conn.execute("SELECT word_id FROM text_word WHERE text_id = ? AND surface = ?", (text_id, *key)).fetchone()
    if row is None:
        raise AnnotationError("no such word")
    pinyin, level = pinyin_.to_marks(clean(fields.get("pinyin"))), None
    if row["word_id"] is None:
        if gloss is None:
            raise AnnotationError(f"“{key[0]}” is not in the master; a gloss is required")
        conn.execute("UPDATE text_word SET pinyin = NULL WHERE text_id = ? AND surface = ?", (text_id, *key))  # so a prefill ignores the old reading
        pinyin, level = _local_pinyin(conn, text_id, key[0], pinyin), level_of(fields.get("hsk_level"))
    sql = "UPDATE text_word SET pinyin = ?, hsk_level = ?, gloss = ?, origin = 'manual' WHERE text_id = ? AND surface = ?"
    conn.execute(sql, (pinyin, level, gloss, text_id, *key))


# --- read ------------------------------------------------------------------
MASTER = "coalesce(w.hsk_level, t.hsk_level) AS hsk_level, w.hsk_edition, w.meanings, w.alt_readings"


def decode_master(row: dict) -> dict:
    """Parse the master's JSON columns on a joined row; an unlinked row gets empty lists."""
    for column in ("meanings", "alt_readings"):
        row[column] = json.loads(row[column]) if row.get(column) else []
    return row


def load(conn, text_id) -> dict:
    """Facts for the page: readings by position, character facts and words in body order, words joined to the master."""
    body = body_of(conn, text_id)
    position = lambda s: body.find(s) if s else len(body)  # noqa: E731
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (text_id,))]  # noqa: E731
    words = rows(f"SELECT t.surface, t.word_id, coalesce(t.pinyin, w.pinyin) AS pinyin, t.gloss, t.origin, {MASTER} FROM text_word t LEFT JOIN word w ON w.id = t.word_id WHERE t.text_id = ?")
    return {
        "readings": rows("SELECT position, char, pinyin, origin FROM text_reading WHERE text_id = ? ORDER BY position"),
        "characters": sorted(rows("SELECT char, hsk_level, gloss, origin FROM text_character WHERE text_id = ?"), key=lambda r: position(r["char"])),
        "words": sorted((decode_master(r) for r in words), key=lambda r: position(r["surface"])),
    }
