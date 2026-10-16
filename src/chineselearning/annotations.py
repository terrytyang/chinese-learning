"""Annotations: admin curation of a text (validation, add, edit, remove, confirm, page query).

`annotation_files` persists them write-through to data/annotations/<id>.json and
re-imports them on build through the same add_* functions the admin page uses.
"""

import json

from . import readings
from .texts import HAN

ORIGINS = ("auto", "suggested", "manual")
# Table and key clause per kind, for remove() and confirm(); readings only in the every-occurrence form.
TABLES = {
    "characters": ("text_character", "char = ?"),
    "words": ("text_word", "surface = ?"),
    "expansions": ("text_expansion", "char = ? AND surface = ?"),
    "readings": ("text_reading", "char = ? AND position IS NULL"),
    "notes": ("text_note", "id = ?"),
}


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


def _origin(value):
    if value not in ORIGINS:
        raise AnnotationError(f"origin 必须是 auto、suggested 或 manual，不是「{value}」")
    return value


def _level(value):
    """HSK level for a local word or unlinked expansion: blank means none, else 1–7."""
    if value in (None, ""):
        return None
    if not (isinstance(value, int) or str(value).isdigit()) or not 1 <= int(value) <= 7:
        raise AnnotationError("级只能是 1 到 7")
    return int(value)


def _local_pinyin(conn, text_id, surface, pinyin):
    """A local word always stores its reading: the given one, else prefilled from its characters."""
    pinyin = pinyin or readings.default_pinyin(conn, text_id, surface)
    if pinyin is None:
        raise AnnotationError(f"「{surface}」里有字库没有的字，请填写拼音")
    return pinyin


def _resolve(conn, surface, gloss):
    """word_id of a master word; a surface absent from the master must be glossed."""
    row = conn.execute("SELECT id FROM word WHERE simplified = ?", (surface,)).fetchone()
    if row is None and gloss is None:
        raise AnnotationError(f"字库里没有「{surface}」，请填写释义")
    return row[0] if row else None


# --- add (duplicates are no-ops; a reading replaces the previous one) -----

def add_character(conn, text_id, char, gloss=None, origin="manual"):
    char = _char_in(_body(conn, text_id), char)
    conn.execute("INSERT OR IGNORE INTO text_character (text_id, char, gloss, origin) VALUES (?, ?, ?, ?)", (text_id, char, _clean(gloss), _origin(origin)))


def add_word(conn, text_id, surface, gloss=None, pinyin=None, origin="manual", hsk_level=None):
    body, surface, gloss, pinyin = _body(conn, text_id), _clean(surface), _clean(gloss), _clean(pinyin)
    if not surface or surface not in body:
        raise AnnotationError(f"「{surface or ''}」没有出现在正文里")
    word_id, level = _resolve(conn, surface, gloss), _level(hsk_level)
    if word_id is None:
        pinyin = _local_pinyin(conn, text_id, surface, pinyin)
    sql = "INSERT OR IGNORE INTO text_word (text_id, surface, word_id, pinyin, hsk_level, gloss, origin) VALUES (?, ?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, surface, word_id, pinyin, level if word_id is None else None, gloss, _origin(origin)))


def add_expansion(conn, text_id, char, surface, gloss=None, origin="manual", hsk_level=None, replace=False):
    char, surface, gloss = _char_in(_body(conn, text_id), char), _clean(surface), _clean(gloss)
    if not surface:
        raise AnnotationError("请填写扩展词")
    word_id, level = _resolve(conn, surface, gloss), _level(hsk_level)
    sql = f"INSERT OR {'REPLACE' if replace else 'IGNORE'} INTO text_expansion (text_id, char, surface, word_id, hsk_level, gloss, origin) VALUES (?, ?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, char, surface, word_id, level if word_id is None else None, gloss, _origin(origin)))


def add_reading(conn, text_id, char, pinyin, position=None, origin="manual"):
    body, pinyin = _body(conn, text_id), _clean(pinyin)
    char = _char_in(body, char)
    row = conn.execute("SELECT readings FROM character WHERE char = ?", (char,)).fetchone()
    allowed = json.loads(row[0]) if row else None
    if allowed and pinyin not in allowed:
        raise AnnotationError(f"「{char}」的读音只能是 {'、'.join(allowed)}")
    if not pinyin:
        raise AnnotationError(f"请填写「{char}」的读音")
    if position is not None and not (isinstance(position, int) and 0 <= position < len(body) and body[position] == char):
        raise AnnotationError(f"位置 {position} 不是「{char}」")
    sql = "INSERT OR REPLACE INTO text_reading (text_id, char, pinyin, position, origin) VALUES (?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, char, pinyin, position, _origin(origin)))


def add_note(conn, text_id, note, anchor=None, origin="manual"):
    body, note, anchor = _body(conn, text_id), _clean(note), _clean(anchor)
    if not note:
        raise AnnotationError("请填写注")
    if anchor and anchor not in body:
        raise AnnotationError(f"「{anchor}」没有出现在正文里")
    if not conn.execute("SELECT 1 FROM text_note WHERE text_id = ? AND anchor IS ? AND note = ?", (text_id, anchor, note)).fetchone():
        conn.execute("INSERT INTO text_note (text_id, anchor, note, origin) VALUES (?, ?, ?, ?)", (text_id, anchor, note, _origin(origin)))


def remove(conn, text_id, kind, *key):
    table, where = TABLES[kind]
    conn.execute(f"DELETE FROM {table} WHERE text_id = ? AND {where}", (text_id, *key))


def confirm(conn, text_id, kind, *key):
    """The admin vouches for an auto or suggested row: origin becomes manual."""
    table, where = TABLES[kind]
    conn.execute(f"UPDATE {table} SET origin = 'manual' WHERE text_id = ? AND {where}", (text_id, *key))


def update(conn, text_id, kind, key, fields):
    """Edit one row in place (validation as for add); origin becomes manual. `key` is the row's natural key tuple."""
    table, where = TABLES[kind]
    row = conn.execute(f"SELECT * FROM {table} WHERE text_id = ? AND {where}", (text_id, *key)).fetchone()
    if row is None:
        raise AnnotationError("没有这条标注")
    gloss = _clean(fields.get("gloss"))
    if kind == "characters":
        conn.execute("UPDATE text_character SET gloss = ?, origin = 'manual' WHERE text_id = ? AND char = ?", (gloss, text_id, *key))
    elif kind == "words":
        pinyin, level = _clean(fields.get("pinyin")), None
        if row["word_id"] is None:
            if gloss is None:
                raise AnnotationError(f"字库里没有「{key[0]}」，请填写释义")
            conn.execute("UPDATE text_word SET pinyin = NULL WHERE text_id = ? AND surface = ?", (text_id, *key))  # so a prefill ignores the old reading
            pinyin, level = _local_pinyin(conn, text_id, key[0], pinyin), _level(fields.get("hsk_level"))
        sql = "UPDATE text_word SET pinyin = ?, hsk_level = ?, gloss = ?, origin = 'manual' WHERE text_id = ? AND surface = ?"
        conn.execute(sql, (pinyin, level, gloss, text_id, *key))
    elif kind == "expansions":  # the surface is part of the key: delete and re-add in this transaction
        remove(conn, text_id, kind, *key)
        add_expansion(conn, text_id, key[0], fields.get("surface"), gloss, "manual", fields.get("hsk_level"), replace=True)
    elif kind == "notes":
        body, note, anchor = _body(conn, text_id), _clean(fields.get("note")), _clean(fields.get("anchor"))
        if not note:
            raise AnnotationError("请填写注")
        if anchor and anchor not in body:
            raise AnnotationError(f"「{anchor}」没有出现在正文里")
        conn.execute("UPDATE text_note SET anchor = ?, note = ?, origin = 'manual' WHERE text_id = ? AND id = ?", (anchor, note, text_id, *key))


# --- read ------------------------------------------------------------------
MASTER = "coalesce(w.hsk_level, t.hsk_level) AS hsk_level, w.hsk_edition, w.meanings"


def load(conn, text_id) -> dict:
    """Annotations for the page, joined to the master, in body order."""
    body = _body(conn, text_id)
    position = lambda s: body.find(s) if s else len(body)  # noqa: E731
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (text_id,))]  # noqa: E731
    words = rows(f"SELECT t.surface, t.word_id, coalesce(t.pinyin, w.pinyin) AS pinyin, t.gloss, t.origin, {MASTER} FROM text_word t LEFT JOIN word w ON w.id = t.word_id WHERE t.text_id = ?")
    expansions = rows(f"SELECT t.char, t.surface, t.word_id, w.pinyin, t.gloss, t.origin, {MASTER} FROM text_expansion t LEFT JOIN word w ON w.id = t.word_id WHERE t.text_id = ?")
    for r in words + expansions:
        r["meanings"] = json.loads(r["meanings"]) if r["meanings"] else []
    return {
        "characters": sorted(rows("SELECT char, gloss, origin FROM text_character WHERE text_id = ?"), key=lambda r: position(r["char"])),
        "words": sorted(words, key=lambda r: position(r["surface"])),
        "expansions": sorted(expansions, key=lambda r: (position(r["char"]), r["surface"])),
        "readings": rows("SELECT char, pinyin, position, origin FROM text_reading WHERE text_id = ? ORDER BY char, position"),
        "notes": sorted(rows("SELECT id, anchor, note, origin FROM text_note WHERE text_id = ?"), key=lambda r: (position(r["anchor"]), r["note"])),
    }

