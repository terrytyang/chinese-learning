"""Annotations: admin curation of a text, persisted write-through to data/annotations/<id>.json.

The JSON file is the source of truth; it stores surfaces, never word ids.
`build` re-imports every file through the same add_* functions the admin page uses.
"""

import json
from pathlib import Path

from . import readings
from .texts import HAN

KINDS = ("characters", "words", "expansions", "readings", "notes")
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


def add_word(conn, text_id, surface, gloss=None, pinyin=None, origin="manual"):
    body, surface, gloss, pinyin = _body(conn, text_id), _clean(surface), _clean(gloss), _clean(pinyin)
    if not surface or surface not in body:
        raise AnnotationError(f"「{surface or ''}」没有出现在正文里")
    word_id = _resolve(conn, surface, gloss)
    if word_id is None and pinyin is None:  # a local word always stores its reading
        pinyin = readings.default_pinyin(conn, text_id, surface)
        if pinyin is None:
            raise AnnotationError(f"「{surface}」里有字库没有的字，请填写拼音")
    sql = "INSERT OR IGNORE INTO text_word (text_id, surface, word_id, pinyin, gloss, origin) VALUES (?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, surface, word_id, pinyin, gloss, _origin(origin)))


def add_expansion(conn, text_id, char, surface, gloss=None, origin="manual"):
    char, surface, gloss = _char_in(_body(conn, text_id), char), _clean(surface), _clean(gloss)
    if not surface:
        raise AnnotationError("请填写扩展词")
    word_id = _resolve(conn, surface, gloss)
    sql = "INSERT OR IGNORE INTO text_expansion (text_id, char, surface, word_id, gloss, origin) VALUES (?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (text_id, char, surface, word_id, gloss, _origin(origin)))


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


# --- read ------------------------------------------------------------------
MASTER = "w.hsk_level, w.hsk_edition, w.meanings"


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


def export(conn, text_id) -> dict:
    """File content: keys in documented order, lists sorted by natural key, surfaces only."""
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (text_id,))]  # noqa: E731
    return {
        "text_id": text_id,
        "characters": rows("SELECT char, gloss, origin FROM text_character WHERE text_id = ? ORDER BY char"),
        "words": rows("SELECT surface, pinyin, gloss, origin FROM text_word WHERE text_id = ? ORDER BY surface"),
        "expansions": rows("SELECT char, surface, gloss, origin FROM text_expansion WHERE text_id = ? ORDER BY char, surface"),
        "readings": rows("SELECT char, pinyin, position, origin FROM text_reading WHERE text_id = ? ORDER BY char, position"),
        "notes": rows("SELECT anchor, note, origin FROM text_note WHERE text_id = ? ORDER BY coalesce(anchor, ''), note"),
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
                add_character(conn, text_id, c["char"], c.get("gloss"), c.get("origin", "manual"))
            for r in data.get("readings", []):  # before words, so a local word's prefilled reading sees overrides
                add_reading(conn, text_id, r["char"], r["pinyin"], r.get("position"), r.get("origin", "manual"))
            for w in data.get("words", []):
                add_word(conn, text_id, w["surface"], w.get("gloss"), w.get("pinyin"), w.get("origin", "manual"))
            for e in data.get("expansions", []):
                add_expansion(conn, text_id, e["char"], e["surface"], e.get("gloss"), e.get("origin", "manual"))
            for n in data.get("notes", []):
                add_note(conn, text_id, n["note"], n.get("anchor"), n.get("origin", "manual"))
        except AnnotationError as e:
            raise AnnotationError(f"{path}: {e}") from None
        except KeyError as e:
            raise AnnotationError(f"{path}: 缺少字段 {e}") from None
