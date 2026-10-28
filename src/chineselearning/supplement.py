"""data/supplement.tsv: curated non-HSK vocabulary, loaded into `character` and `word` with source 'supplement' (design.md, layer 2).

`load` runs at build after hsk.sql. `add` and `update` are the only writers of the file; each mirrors its line to the row.
A line is `item  pinyin  gloss  level` (tabs); `#` starts a comment. A character's level defaults to 7, a word's to the
highest level among its characters, its pinyin to their primary readings joined; a word id is 10,000,000 + its line index.
"""

import json
from pathlib import Path

from opencc import OpenCC

from . import drift
from . import pinyin as pinyin_

WORD_ID_BASE = 10_000_000
FILE = "supplement.tsv"
_S2T = OpenCC("s2t")


class SupplementError(ValueError):
    """An invalid entry; at load the message starts with the file and line."""


def file_path(data_dir) -> Path:
    return Path(data_dir) / FILE


def entry(item, pinyin=None, gloss=None, level=None) -> dict:
    """A validated entry: stripped strings (pinyin with tone marks), level as int or None (derived)."""
    item, pinyin, gloss, level = (str(x or "").strip() for x in (item, pinyin, gloss, level))
    if not item:
        raise SupplementError("blank item")
    if level and (not level.isdigit() or not 1 <= int(level) <= 7):
        raise SupplementError(f"level must be 1 to 7, not “{level}”")
    return {"item": item, "pinyin": pinyin_.to_marks(pinyin), "gloss": gloss, "level": int(level) if level else None}


def parse_line(line) -> dict | None:
    """The entry on a line, or None for a comment or blank line."""
    if not line.strip() or line.lstrip().startswith("#"):
        return None
    return entry(*(line.split("\t") + ["", "", ""])[:4])


def format_line(e) -> str:
    return f"{e['item']}\t{e['pinyin']}\t{e['gloss']}\t{e['level'] or ''}\n"


def source_of(conn, item) -> str | None:
    """'hsk' or 'supplement' when the dictionary has the item, else None."""
    table, column = ("character", "char") if len(item) == 1 else ("word", "simplified")
    row = conn.execute(f"SELECT source FROM {table} WHERE {column} = ?", (item,)).fetchone()
    return row[0] if row else None


def check_new(conn, e):
    source = source_of(conn, e["item"])
    if source == "hsk":
        raise SupplementError(f"“{e['item']}” is in the HSK master")
    if source == "supplement":
        raise SupplementError(f"duplicate item “{e['item']}”")


# --- rows ------------------------------------------------------------------

def character_values(e) -> dict:
    """pinyin, readings (the file's first, then pypinyin's), gloss, hsk_level (default 7)."""
    readings = pinyin_.readings_of(e["item"])
    if e["pinyin"]:
        readings = [e["pinyin"]] + [r for r in readings if r.lower() != e["pinyin"].lower()]
    if not readings:
        raise SupplementError(f"“{e['item']}” has no known reading; give its pinyin")
    return {"pinyin": readings[0], "readings": json.dumps(readings, ensure_ascii=False), "gloss": e["gloss"] or None, "hsk_level": e["level"] or 7}


def word_values(conn, e) -> dict:
    """pinyin (the file's, else the characters' primary readings), meanings ([gloss] or []), hsk_level (the file's, else the
    characters' highest); every character must be in the dictionary."""
    chars = list(dict.fromkeys(e["item"]))
    found = {r["char"]: r for r in conn.execute(f"SELECT char, pinyin, hsk_level FROM character WHERE char IN ({','.join('?' * len(chars))})", chars)}
    missing = [ch for ch in chars if ch not in found]
    if missing:
        raise SupplementError(f"“{e['item']}” has characters not in the dictionary: {', '.join(missing)}; add them to data/{FILE}")
    return {
        "pinyin": e["pinyin"] or " ".join(found[ch]["pinyin"] for ch in e["item"]),
        "meanings": json.dumps([e["gloss"]] if e["gloss"] else [], ensure_ascii=False),
        "hsk_level": e["level"] or max(found[ch]["hsk_level"] for ch in e["item"]),
    }


def insert(conn, e, line_index) -> int:
    """The row for an entry; returns its id (a character's code point, a word's 10,000,000 + line index)."""
    if len(e["item"]) == 1:
        v = character_values(e)
        conn.execute("INSERT INTO character (id, char, pinyin, readings, gloss, hsk_level, hsk_edition, source) VALUES (?, ?, ?, ?, ?, ?, 'none', 'supplement')",
                     (ord(e["item"]), e["item"], v["pinyin"], v["readings"], v["gloss"], v["hsk_level"]))
        return ord(e["item"])
    v, word_id = word_values(conn, e), WORD_ID_BASE + line_index
    conn.execute("INSERT INTO word (id, simplified, traditional, pinyin, meanings, hsk_level, hsk_edition, source) VALUES (?, ?, ?, ?, ?, ?, 'none', 'supplement')",
                 (word_id, e["item"], _S2T.convert(e["item"]), v["pinyin"], v["meanings"], v["hsk_level"]))
    return word_id


# --- load, add, update -----------------------------------------------------

def load(conn, data_dir) -> tuple[int, int]:
    """Insert every entry of data/supplement.tsv; characters first, so a word may precede its characters in the file.

    Returns (entries, entries without a gloss). Any problem is a SupplementError naming the file and line.
    """
    path = file_path(data_dir)
    if not path.is_file():
        return 0, 0
    seen, words, count, unglossed = set(), [], 0, 0
    for index, line in enumerate(path.read_text(encoding="utf-8").split("\n")):
        try:
            e = parse_line(line)
            if e is None:
                continue
            if e["item"] in seen:
                raise SupplementError(f"duplicate item “{e['item']}”")
            check_new(conn, e)
            seen.add(e["item"])
            if len(e["item"]) == 1:
                insert(conn, e, index)
            else:
                words.append((index, e))
        except SupplementError as err:
            raise SupplementError(f"{path}:{index + 1}: {err}") from None
        count, unglossed = count + 1, unglossed + (not e["gloss"])
    for index, e in words:
        try:
            insert(conn, e, index)
        except SupplementError as err:
            raise SupplementError(f"{path}:{index + 1}: {err}") from None
    return count, unglossed


def check_drift(conn, data_dir):
    """The file must be the one the database was built from; a hand edit since then needs `build` first."""
    files = drift.changed(conn, data_dir)
    if FILE in files:
        raise SupplementError(drift.message(files))


def add(conn, data_dir, item, pinyin=None, gloss=None, level=None) -> int:
    """Append a line and insert its row; returns the row's id. The item must be absent from the dictionary."""
    e = entry(item, pinyin, gloss, level)
    check_new(conn, e)
    check_drift(conn, data_dir)
    path = file_path(data_dir)
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    row_id = insert(conn, e, text.count("\n"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + format_line(e), encoding="utf-8")
    drift.touch(conn, data_dir, path)
    return row_id


def update(conn, data_dir, item, pinyin=None, gloss=None, level=None):
    """Rewrite an existing supplement entry's line and the derived columns of its row."""
    e = entry(item, pinyin, gloss, level)
    if source_of(conn, e["item"]) != "supplement":
        raise SupplementError(f"“{e['item']}” is not a supplement entry")
    check_drift(conn, data_dir)
    path = file_path(data_dir)
    lines = path.read_text(encoding="utf-8").split("\n") if path.is_file() else []
    at = next((i for i, line in enumerate(lines) if (parse_line(line) or {}).get("item") == e["item"]), None)
    if at is None:
        raise SupplementError(f"“{e['item']}” is not in data/{FILE}")
    if len(e["item"]) == 1:
        v = character_values(e)
        conn.execute("UPDATE character SET pinyin = ?, readings = ?, gloss = ?, hsk_level = ? WHERE char = ?", (v["pinyin"], v["readings"], v["gloss"], v["hsk_level"], e["item"]))
    else:
        v = word_values(conn, e)
        conn.execute("UPDATE word SET pinyin = ?, meanings = ?, hsk_level = ? WHERE simplified = ?", (v["pinyin"], v["meanings"], v["hsk_level"], e["item"]))
    lines[at] = format_line(e).removesuffix("\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    drift.touch(conn, data_dir, path)
