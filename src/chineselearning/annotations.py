"""Text facts: readings per position, character facts, words (design.md, layer 3). Validation, add, edit, remove, page query.

`annotation_files` persists them write-through to data/annotations/<id>.json and
re-imports them on build through the same functions the admin page uses.
"""

import json

from . import readings
from .texts import HAN

ORIGINS = ("auto", "suggested", "manual")
TABLES = {"characters": ("text_character", "char = ?"), "words": ("text_word", "surface = ?")}


class AnnotationError(ValueError):
    """Invalid annotation; the message is Chinese, for the admin page."""


# --- validation helpers (shared with lessons.py) ---------------------------

def clean(value):
    value = (value or "").strip()
    return value or None


def body_of(conn, text_id):
    row = conn.execute("SELECT body FROM text WHERE id = ?", (text_id,)).fetchone()
    if row is None:
        raise AnnotationError("没有这篇课文")
    return row[0]


def char_in(body, char):
    char = clean(char) or ""
    if len(char) != 1 or not HAN.fullmatch(char) or char not in body:
        raise AnnotationError(f"「{char}」不是正文里的单个汉字")
    return char


def origin_of(value):
    if value not in ORIGINS:
        raise AnnotationError(f"origin 必须是 auto、suggested 或 manual，不是「{value}」")
    return value


def level_of(value):
    """HSK level for a local word, unlinked expansion or character fact: blank means none, else 1–7."""
    if value in (None, ""):
        return None
    if not (isinstance(value, int) or str(value).isdigit()) or not 1 <= int(value) <= 7:
        raise AnnotationError("级只能是 1 到 7")
    return int(value)


def resolve_word(conn, surface, gloss):
    """word_id of a master word; a surface absent from the master must be glossed."""
    row = conn.execute("SELECT id FROM word WHERE simplified = ?", (surface,)).fetchone()
    if row is None and gloss is None:
        raise AnnotationError(f"字库里没有「{surface}」，请填写释义")
    return row[0] if row else None


def _local_pinyin(conn, text_id, surface, pinyin):
    """A local word always stores its reading: the given one, else prefilled from its characters."""
    pinyin = pinyin or readings.default_pinyin(conn, text_id, surface)
    if pinyin is None:
        raise AnnotationError(f"「{surface}」里有字库没有的字，请填写拼音")
    return pinyin


# --- readings: one row per Han position; setting replaces -----------------

def set_reading(conn, text_id, position, char, pinyin, origin="manual"):
    body, pinyin = body_of(conn, text_id), clean(pinyin)
    if not isinstance(position, int) or not 0 <= position < len(body) or not HAN.fullmatch(body[position]):
        raise AnnotationError(f"位置 {position} 不是汉字")
    if body[position] != char:
        raise AnnotationError(f"位置 {position} 的字是「{body[position]}」，不是「{char}」；请重新 intake")
    row = conn.execute("SELECT readings FROM character WHERE char = ?", (char,)).fetchone()
    allowed = json.loads(row[0]) if row else None
    if allowed and pinyin not in allowed:
        raise AnnotationError(f"「{char}」的读音只能是 {'、'.join(allowed)}")
    if not pinyin:
        raise AnnotationError(f"请填写「{char}」的读音")
    sql = "INSERT OR REPLACE INTO text_reading (text_id, position, char, pinyin, origin) VALUES (?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, position, char, pinyin, origin_of(origin)))


def set_reading_everywhere(conn, text_id, char, pinyin, origin="manual"):
    """The 字表 form: one reading for every position of `char`."""
    body = body_of(conn, text_id)
    char = char_in(body, char)
    for position, ch in enumerate(body):
        if ch == char:
            set_reading(conn, text_id, position, char, pinyin, origin)


def reset_reading(conn, text_id, char):
    """Back to the default resolution for every position of `char` (origin auto); none at all when nothing resolves."""
    char = char_in(body_of(conn, text_id), char)
    for r in readings.resolve(conn, text_id, ignore_stored={char}):
        if r["char"] == char:
            conn.execute("DELETE FROM text_reading WHERE text_id = ? AND position = ?", (text_id, r["position"]))
            if r["pinyin"]:
                set_reading(conn, text_id, r["position"], char, r["pinyin"], "auto")


# --- character facts and words (duplicates are no-ops) --------------------

def add_character(conn, text_id, char, gloss=None, pinyin=None, hsk_level=None, origin="manual"):
    char = char_in(body_of(conn, text_id), char)
    sql = "INSERT OR IGNORE INTO text_character (text_id, char, pinyin, hsk_level, gloss, origin) VALUES (?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, char, clean(pinyin), level_of(hsk_level), clean(gloss), origin_of(origin)))


def add_word(conn, text_id, surface, gloss=None, pinyin=None, origin="manual", hsk_level=None):
    body, surface, gloss, pinyin = body_of(conn, text_id), clean(surface), clean(gloss), clean(pinyin)
    if not surface or surface not in body:
        raise AnnotationError(f"「{surface or ''}」没有出现在正文里")
    word_id, level = resolve_word(conn, surface, gloss), level_of(hsk_level)
    if word_id is None:
        pinyin = _local_pinyin(conn, text_id, surface, pinyin)
    sql = "INSERT OR IGNORE INTO text_word (text_id, surface, word_id, pinyin, hsk_level, gloss, origin) VALUES (?, ?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, surface, word_id, pinyin, level if word_id is None else None, gloss, origin_of(origin)))


def remove(conn, text_id, kind, *key):
    table, where = TABLES[kind]
    conn.execute(f"DELETE FROM {table} WHERE text_id = ? AND {where}", (text_id, *key))


def confirm(conn, text_id, kind, *key):
    """The admin vouches for an auto or suggested row: origin becomes manual."""
    table, where = TABLES[kind]
    conn.execute(f"UPDATE {table} SET origin = 'manual' WHERE text_id = ? AND {where}", (text_id, *key))


def update(conn, text_id, kind, key, fields):
    """Edit one fact in place (validation as for add); origin becomes manual. A character gloss edit creates the fact if missing."""
    gloss = clean(fields.get("gloss"))
    if kind == "characters":
        char = char_in(body_of(conn, text_id), key[0])
        add_character(conn, text_id, char, gloss)
        conn.execute("UPDATE text_character SET gloss = ?, origin = 'manual' WHERE text_id = ? AND char = ?", (gloss, text_id, char))
        return
    row = conn.execute("SELECT word_id FROM text_word WHERE text_id = ? AND surface = ?", (text_id, *key)).fetchone()
    if row is None:
        raise AnnotationError("没有这条标注")
    pinyin, level = clean(fields.get("pinyin")), None
    if row["word_id"] is None:
        if gloss is None:
            raise AnnotationError(f"字库里没有「{key[0]}」，请填写释义")
        conn.execute("UPDATE text_word SET pinyin = NULL WHERE text_id = ? AND surface = ?", (text_id, *key))  # so a prefill ignores the old reading
        pinyin, level = _local_pinyin(conn, text_id, key[0], pinyin), level_of(fields.get("hsk_level"))
    sql = "UPDATE text_word SET pinyin = ?, hsk_level = ?, gloss = ?, origin = 'manual' WHERE text_id = ? AND surface = ?"
    conn.execute(sql, (pinyin, level, gloss, text_id, *key))


# --- read ------------------------------------------------------------------
MASTER = "coalesce(w.hsk_level, t.hsk_level) AS hsk_level, w.hsk_edition, w.meanings"


def load(conn, text_id) -> dict:
    """Facts for the page: readings by position, character facts and words in body order, words joined to the master."""
    body = body_of(conn, text_id)
    position = lambda s: body.find(s) if s else len(body)  # noqa: E731
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (text_id,))]  # noqa: E731
    words = rows(f"SELECT t.surface, t.word_id, coalesce(t.pinyin, w.pinyin) AS pinyin, t.gloss, t.origin, {MASTER} FROM text_word t LEFT JOIN word w ON w.id = t.word_id WHERE t.text_id = ?")
    for r in words:
        r["meanings"] = json.loads(r["meanings"]) if r["meanings"] else []
    return {
        "readings": rows("SELECT position, char, pinyin, origin FROM text_reading WHERE text_id = ? ORDER BY position"),
        "characters": sorted(rows("SELECT char, pinyin, hsk_level, gloss, origin FROM text_character WHERE text_id = ?"), key=lambda r: position(r["char"])),
        "words": sorted(words, key=lambda r: position(r["surface"])),
    }
