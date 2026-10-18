"""Lessons: a named selection of a text's characters and words plus expansions and notes (design.md, layer 3).

`lesson_files` persists each lesson write-through to data/lessons/<text id>-<lesson id>.json.
"""

import json

from .annotations import MASTER, AnnotationError, body_of, char_in, clean, level_of, origin_of, resolve_word

TABLES = {
    "characters": ("lesson_character", "char = ?"),
    "words": ("lesson_word", "surface = ?"),
    "expansions": ("lesson_expansion", "char = ? AND surface = ?"),
    "notes": ("lesson_note", "id = ?"),
}
CONTENT_TABLES = ("lesson_character", "lesson_word", "lesson_expansion", "lesson_note")


def get(conn, lesson_id) -> dict | None:
    row = conn.execute("SELECT id, text_id, name FROM lesson WHERE id = ?", (lesson_id,)).fetchone()
    return dict(row) if row else None


def for_text(conn, text_id) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT id, text_id, name FROM lesson WHERE text_id = ? ORDER BY id", (text_id,))]


def _require(conn, lesson_id) -> dict:
    lesson = get(conn, lesson_id)
    if lesson is None:
        raise AnnotationError("没有这个课程")
    return lesson


def _check_name(conn, text_id, name, lesson_id=None):
    name = clean(name)
    if not name:
        raise AnnotationError("请填写课程名")
    if conn.execute("SELECT 1 FROM lesson WHERE text_id = ? AND name = ? AND id IS NOT ?", (text_id, name, lesson_id)).fetchone():
        raise AnnotationError(f"已有名为「{name}」的课程")
    return name


def create(conn, text_id, name, lesson_id=None) -> int:
    """A new lesson; the id is assigned here (or given, on import) and then fixed by the file."""
    body_of(conn, text_id)
    name = _check_name(conn, text_id, name)
    if lesson_id is not None and get(conn, lesson_id):
        raise AnnotationError(f"课程 id {lesson_id} 已被占用")
    cursor = conn.execute("INSERT INTO lesson (id, text_id, name) VALUES (?, ?, ?)", (lesson_id, text_id, name))
    return cursor.lastrowid


def rename(conn, lesson_id, name):
    lesson = _require(conn, lesson_id)
    conn.execute("UPDATE lesson SET name = ? WHERE id = ?", (_check_name(conn, lesson["text_id"], name, lesson_id), lesson_id))


def is_empty(conn, lesson_id) -> bool:
    return not any(conn.execute(f"SELECT 1 FROM {t} WHERE lesson_id = ?", (lesson_id,)).fetchone() for t in CONTENT_TABLES)


def delete(conn, lesson_id):
    """Only an empty lesson can go; the admin empties it first."""
    _require(conn, lesson_id)
    if not is_empty(conn, lesson_id):
        raise AnnotationError("课程不是空的；先删除里面的学习字、词、扩展和注")
    conn.execute("DELETE FROM lesson WHERE id = ?", (lesson_id,))


# --- selections and additions (duplicates are no-ops) ----------------------

def add_character(conn, lesson_id, char):
    char = char_in(body_of(conn, _require(conn, lesson_id)["text_id"]), char)
    conn.execute("INSERT OR IGNORE INTO lesson_character (lesson_id, char) VALUES (?, ?)", (lesson_id, char))


def add_word(conn, lesson_id, surface):
    """Only a word the text already has as a fact can be selected."""
    text_id, surface = _require(conn, lesson_id)["text_id"], clean(surface)
    if not conn.execute("SELECT 1 FROM text_word WHERE text_id = ? AND surface = ?", (text_id, surface)).fetchone():
        raise AnnotationError(f"「{surface or ''}」还不是课文的词，请先添加")
    conn.execute("INSERT OR IGNORE INTO lesson_word (lesson_id, surface) VALUES (?, ?)", (lesson_id, surface))


def add_expansion(conn, lesson_id, char, surface, gloss=None, origin="manual", hsk_level=None, replace=False):
    char = char_in(body_of(conn, _require(conn, lesson_id)["text_id"]), char)
    surface, gloss = clean(surface), clean(gloss)
    if not surface:
        raise AnnotationError("请填写扩展词")
    word_id, level = resolve_word(conn, surface, gloss), level_of(hsk_level)
    sql = f"INSERT OR {'REPLACE' if replace else 'IGNORE'} INTO lesson_expansion (lesson_id, char, surface, word_id, hsk_level, gloss, origin) VALUES (?, ?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (lesson_id, char, surface, word_id, level if word_id is None else None, gloss, origin_of(origin)))


def add_note(conn, lesson_id, note, anchor=None, origin="manual"):
    body, note, anchor = body_of(conn, _require(conn, lesson_id)["text_id"]), clean(note), clean(anchor)
    if not note:
        raise AnnotationError("请填写注")
    if anchor and anchor not in body:
        raise AnnotationError(f"「{anchor}」没有出现在正文里")
    if not conn.execute("SELECT 1 FROM lesson_note WHERE lesson_id = ? AND anchor IS ? AND note = ?", (lesson_id, anchor, note)).fetchone():
        conn.execute("INSERT INTO lesson_note (lesson_id, anchor, note, origin) VALUES (?, ?, ?, ?)", (lesson_id, anchor, note, origin_of(origin)))


def remove(conn, lesson_id, kind, *key):
    table, where = TABLES[kind]
    conn.execute(f"DELETE FROM {table} WHERE lesson_id = ? AND {where}", (lesson_id, *key))


def confirm(conn, lesson_id, kind, *key):
    table, where = TABLES[kind]
    conn.execute(f"UPDATE {table} SET origin = 'manual' WHERE lesson_id = ? AND {where}", (lesson_id, *key))


def update(conn, lesson_id, kind, key, fields):
    """Edit an expansion or note in place (validation as for add); origin becomes manual."""
    table, where = TABLES[kind]
    if not conn.execute(f"SELECT 1 FROM {table} WHERE lesson_id = ? AND {where}", (lesson_id, *key)).fetchone():
        raise AnnotationError("没有这条标注")
    if kind == "expansions":  # the surface is part of the key: delete and re-add in this transaction
        remove(conn, lesson_id, kind, *key)
        add_expansion(conn, lesson_id, key[0], fields.get("surface"), fields.get("gloss"), "manual", fields.get("hsk_level"), replace=True)
    else:
        body = body_of(conn, _require(conn, lesson_id)["text_id"])
        note, anchor = clean(fields.get("note")), clean(fields.get("anchor"))
        if not note:
            raise AnnotationError("请填写注")
        if anchor and anchor not in body:
            raise AnnotationError(f"「{anchor}」没有出现在正文里")
        conn.execute("UPDATE lesson_note SET anchor = ?, note = ?, origin = 'manual' WHERE lesson_id = ? AND id = ?", (anchor, note, lesson_id, *key))


# --- read ------------------------------------------------------------------

def load(conn, lesson_id) -> dict:
    """The lesson's content for pages, in body order; characters carry the text fact and master gloss/level."""
    lesson = _require(conn, lesson_id)
    body = body_of(conn, lesson["text_id"])
    position = lambda s: body.find(s) if s else len(body)  # noqa: E731
    rows = lambda sql, *args: [dict(r) for r in conn.execute(sql, args)]  # noqa: E731
    characters = rows(
        "SELECT l.char, coalesce(f.gloss, c.gloss) AS gloss, coalesce(f.hsk_level, c.hsk_level) AS hsk_level FROM lesson_character l"
        " LEFT JOIN text_character f ON f.text_id = ? AND f.char = l.char LEFT JOIN character c ON c.char = l.char WHERE l.lesson_id = ?",
        lesson["text_id"], lesson_id)
    expansions = rows(f"SELECT t.char, t.surface, t.word_id, w.pinyin, t.gloss, t.origin, {MASTER} FROM lesson_expansion t LEFT JOIN word w ON w.id = t.word_id WHERE t.lesson_id = ?", lesson_id)
    for r in expansions:
        r["meanings"] = json.loads(r["meanings"]) if r["meanings"] else []
    return {
        **lesson,
        "characters": sorted(characters, key=lambda r: position(r["char"])),
        "words": {r[0] for r in conn.execute("SELECT surface FROM lesson_word WHERE lesson_id = ?", (lesson_id,))},
        "expansions": sorted(expansions, key=lambda r: (position(r["char"]), r["surface"])),
        "notes": sorted(rows("SELECT id, anchor, note, origin FROM lesson_note WHERE lesson_id = ?", lesson_id), key=lambda r: (position(r["anchor"]), r["note"])),
    }
