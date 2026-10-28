"""Lessons: a named selection of a text's characters and words plus extra words and notes, or a vocabulary lesson with no
text whose members are any dictionary items (design.md, layer 3).

`lesson_files` persists each lesson write-through to data/lessons/<text id>-<lesson id>.json, or <lesson id>.json.
"""

from datetime import date

from . import pinyin as pinyin_
from .annotations import MASTER, AnnotationError, body_of, char_in, clean, decode_master, origin_of, resolve_word, word_surface
from .texts import HAN

NO_EXTRA = "a vocabulary lesson's words are members; add it as a word"
NO_ANCHOR = "a vocabulary lesson's notes have no anchor"

TABLES = {
    "characters": ("lesson_character", "char = ?"),
    "words": ("lesson_word", "surface = ?"),
    "extra_words": ("lesson_extra_word", "surface = ? AND coalesce(anchor, '') = ?"),
    "notes": ("lesson_note", "id = ?"),
}
CONTENT_TABLES = ("lesson_character", "lesson_word", "lesson_extra_word", "lesson_note")


def get(conn, lesson_id) -> dict | None:
    row = conn.execute("SELECT id, text_id, name FROM lesson WHERE id = ?", (lesson_id,)).fetchone()
    return dict(row) if row else None


def for_text(conn, text_id) -> list[dict]:
    return [dict(r) for r in conn.execute("SELECT id, text_id, name FROM lesson WHERE text_id = ? ORDER BY id", (text_id,))]


def vocabulary(conn) -> list[dict]:
    """The lessons with no text, newest first."""
    return [dict(r) for r in conn.execute("SELECT id, text_id, name FROM lesson WHERE text_id IS NULL ORDER BY id DESC")]


def default_name(conn) -> str:
    """`Vocabulary <today>`, then `Vocabulary <today> (2)`, `(3)`… — the first not yet taken by a vocabulary lesson."""
    base = f"Vocabulary {date.today().isoformat()}"  # the local date: the name is for the owner, not for changed_at
    taken = {r[0] for r in conn.execute("SELECT name FROM lesson WHERE text_id IS NULL")}
    name, n = base, 2
    while name in taken:
        name, n = f"{base} ({n})", n + 1
    return name


def _require(conn, lesson_id) -> dict:
    lesson = get(conn, lesson_id)
    if lesson is None:
        raise AnnotationError("no such lesson")
    return lesson


def _check_name(conn, text_id, name, lesson_id=None):
    name = clean(name)
    if not name:
        raise AnnotationError("a lesson name is required")
    if conn.execute("SELECT 1 FROM lesson WHERE text_id IS ? AND name = ? AND id IS NOT ?", (text_id, name, lesson_id)).fetchone():
        raise AnnotationError(f"a lesson named “{name}” already exists")
    return name


def create(conn, text_id, name, lesson_id=None) -> int:
    """A new lesson (a vocabulary lesson when `text_id` is None); the id is assigned here (or given, on import) and then fixed by the file."""
    if text_id is not None:
        body_of(conn, text_id)
    name = _check_name(conn, text_id, name)
    if lesson_id is not None and get(conn, lesson_id):
        raise AnnotationError(f"lesson id {lesson_id} is already taken")
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
        raise AnnotationError("the lesson is not empty; remove its characters, words, extra words and notes first")
    conn.execute("DELETE FROM lesson WHERE id = ?", (lesson_id,))


# --- selections and additions (duplicates are no-ops) ----------------------

def add_character(conn, lesson_id, char):
    """A character of the text; in a vocabulary lesson, any character the dictionary has."""
    text_id = _require(conn, lesson_id)["text_id"]
    if text_id is not None:
        char = char_in(body_of(conn, text_id), char)
    else:
        char = clean(char) or ""
        if len(char) != 1 or not HAN.fullmatch(char):
            raise AnnotationError(f"“{char}” is not a single character")
        if not conn.execute("SELECT 1 FROM character WHERE char = ?", (char,)).fetchone():
            raise AnnotationError(f"“{char}” is not in the dictionary")
    conn.execute("INSERT OR IGNORE INTO lesson_character (lesson_id, char) VALUES (?, ?)", (lesson_id, char))


def add_word(conn, lesson_id, surface):
    """Only a word the text already has as a fact can be selected; in a vocabulary lesson, any dictionary word (HSK or supplement)."""
    text_id, surface = _require(conn, lesson_id)["text_id"], word_surface(surface)
    if text_id is None:
        if not conn.execute("SELECT 1 FROM word WHERE simplified = ?", (surface,)).fetchone():
            raise AnnotationError(f"“{surface}” is not a dictionary word")
    elif not conn.execute("SELECT 1 FROM text_word WHERE text_id = ? AND surface = ?", (text_id, surface)).fetchone():
        raise AnnotationError(f"“{surface}” is not yet a word of the text; add it first")
    conn.execute("INSERT OR IGNORE INTO lesson_word (lesson_id, surface) VALUES (?, ?)", (lesson_id, surface))


def held(conn, kind, key) -> bool:
    """Whether any lesson, text or vocabulary, has the character or word (as a member or an extra word)."""
    if kind == "character":
        return bool(conn.execute("SELECT 1 FROM lesson_character WHERE char = ?", (key,)).fetchone())
    return bool(conn.execute("SELECT 1 FROM lesson_word WHERE surface = ? UNION SELECT 1 FROM lesson_extra_word WHERE surface = ?", (key, key)).fetchone())


def kind_of(anchor) -> str:
    """An extra word anchored on one character is an expansion of it (月 → 月亮); anything else is a related word."""
    return "expansion" if anchor and len(anchor) == 1 else "related"


def extra_key(anchor, surface) -> str:
    """The page's row id and edit key of an extra word: `anchor-surface`, or the surface alone when unanchored."""
    return f"{anchor}-{surface}" if anchor else surface


def characters_pinyin(conn, surface) -> str:
    """A word's reading from its characters' primary readings; every character must be in the dictionary."""
    primary = dict(conn.execute(f"SELECT char, pinyin FROM character WHERE char IN ({','.join('?' * len(surface))})", list(surface)).fetchall())
    if any(ch not in primary for ch in surface):
        raise AnnotationError(f"“{surface}” contains a character the dictionary lacks; a pinyin is required")
    return " ".join(primary[ch] for ch in surface)


def add_extra_word(conn, lesson_id, surface, anchor=None, gloss=None, pinyin=None, origin="manual", replace=False):
    """A word the lesson teaches beyond the text, linked to its dictionary row. `anchor`, when given, is a passage of the
    text; a one-character anchor makes it an expansion, which must contain that character. Pinyin is prefilled from the
    dictionary; `gloss` is contextual. A vocabulary lesson has none: its words are members."""
    text_id = _require(conn, lesson_id)["text_id"]
    if text_id is None:
        raise AnnotationError(NO_EXTRA)
    body = body_of(conn, text_id)
    surface, anchor, gloss, pinyin = word_surface(surface), clean(anchor), clean(gloss), pinyin_.to_marks(clean(pinyin))
    if anchor and anchor not in body:
        raise AnnotationError(f"“{anchor}” does not occur in the text")
    if kind_of(anchor) == "expansion" and anchor not in surface:
        raise AnnotationError(f"an expansion of “{anchor}” must contain it; “{surface}” does not")
    word_id = resolve_word(conn, surface)
    pinyin = pinyin or conn.execute("SELECT pinyin FROM word WHERE id = ?", (word_id,)).fetchone()[0]
    sql = f"INSERT OR {'REPLACE' if replace else 'IGNORE'} INTO lesson_extra_word (lesson_id, surface, anchor, word_id, pinyin, gloss, origin) VALUES (?, ?, ?, ?, ?, ?, ?)"
    conn.execute(sql, (lesson_id, surface, anchor, word_id, pinyin, gloss, origin_of(origin)))


def add_note(conn, lesson_id, note, anchor=None, origin="manual") -> int:
    """Returns the note's id (the existing one for a duplicate). A vocabulary lesson's notes have no anchor."""
    note, anchor = clean(note), clean(anchor)
    if not note:
        raise AnnotationError("a note is required")
    _check_anchor(conn, lesson_id, anchor)
    row = conn.execute("SELECT id FROM lesson_note WHERE lesson_id = ? AND anchor IS ? AND note = ?", (lesson_id, anchor, note)).fetchone()
    if row:
        return row[0]
    return conn.execute("INSERT INTO lesson_note (lesson_id, anchor, note, origin) VALUES (?, ?, ?, ?)", (lesson_id, anchor, note, origin_of(origin))).lastrowid


def _check_anchor(conn, lesson_id, anchor):
    text_id = _require(conn, lesson_id)["text_id"]
    if anchor and text_id is None:
        raise AnnotationError(NO_ANCHOR)
    if anchor and anchor not in body_of(conn, text_id):
        raise AnnotationError(f"“{anchor}” does not occur in the text")


def remove(conn, lesson_id, kind, *key):
    """`key` is the char, the surface, (surface, anchor or ''), or the note id."""
    table, where = TABLES[kind]
    conn.execute(f"DELETE FROM {table} WHERE lesson_id = ? AND {where}", (lesson_id, *key))


def confirm(conn, lesson_id, kind, *key):
    table, where = TABLES[kind]
    conn.execute(f"UPDATE {table} SET origin = 'manual' WHERE lesson_id = ? AND {where}", (lesson_id, *key))


def update(conn, lesson_id, kind, key, fields):
    """Edit an extra word or note in place (validation as for add); origin becomes manual. An extra word keeps its anchor."""
    table, where = TABLES[kind]
    if not conn.execute(f"SELECT 1 FROM {table} WHERE lesson_id = ? AND {where}", (lesson_id, *key)).fetchone():
        raise AnnotationError("no such entry")
    if kind == "extra_words":  # the surface is part of the key: delete and re-add in this transaction
        remove(conn, lesson_id, kind, *key)
        add_extra_word(conn, lesson_id, fields.get("surface"), key[1] or None, fields.get("gloss"), fields.get("pinyin"), "manual", replace=True)
    else:
        note, anchor = clean(fields.get("note")), clean(fields.get("anchor"))
        if not note:
            raise AnnotationError("a note is required")
        _check_anchor(conn, lesson_id, anchor)
        conn.execute("UPDATE lesson_note SET anchor = ?, note = ?, origin = 'manual' WHERE lesson_id = ? AND id = ?", (anchor, note, lesson_id, *key))


# --- read ------------------------------------------------------------------

def load(conn, lesson_id) -> dict:
    """The lesson's content for pages, in body order; characters carry the text's or the dictionary's gloss and the level, extra words their kind."""
    lesson = _require(conn, lesson_id)
    body = body_of(conn, lesson["text_id"]) if lesson["text_id"] is not None else ""  # a vocabulary lesson: no positions, members sorted by the page
    position = lambda s: body.find(s) if s else len(body)  # noqa: E731
    rows = lambda sql, *args: [dict(r) for r in conn.execute(sql, args)]  # noqa: E731
    characters = rows(
        "SELECT l.char, coalesce(f.gloss, c.gloss) AS gloss, c.hsk_level FROM lesson_character l"
        " LEFT JOIN text_character f ON f.text_id = ? AND f.char = l.char LEFT JOIN character c ON c.char = l.char WHERE l.lesson_id = ?",
        lesson["text_id"], lesson_id)
    extra = rows(f"SELECT t.surface, t.anchor, t.word_id, coalesce(t.pinyin, w.pinyin) AS pinyin, t.gloss, t.origin, {MASTER} FROM lesson_extra_word t JOIN word w ON w.id = t.word_id WHERE t.lesson_id = ?", lesson_id)
    for r in extra:
        decode_master(r)
        r["kind"] = kind_of(r["anchor"])
    return {
        **lesson,
        "characters": sorted(characters, key=lambda r: position(r["char"])),
        "words": {r[0] for r in conn.execute("SELECT surface FROM lesson_word WHERE lesson_id = ?", (lesson_id,))},
        "extra_words": sorted(extra, key=lambda r: (position(r["anchor"]), r["surface"])),
        "notes": sorted(rows("SELECT id, anchor, note, origin FROM lesson_note WHERE lesson_id = ?", lesson_id), key=lambda r: (position(r["anchor"]), r["note"])),
    }
