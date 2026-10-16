"""The annotation file data/annotations/<id>.json: export, write-through, and import on build.

The file is the source of truth; it stores surfaces, never word ids, and `hsk_level`
only for rows that are not linked to the master.
"""

import json
from pathlib import Path

from . import annotations
from .annotations import AnnotationError

KINDS = ("characters", "words", "expansions", "readings", "notes")


def _unlinked_level(row) -> dict:
    """Drop word_id; keep hsk_level only when the row is not linked."""
    row = dict(row)
    if row.pop("word_id") is not None:
        del row["hsk_level"]
    return row


def export(conn, text_id) -> dict:
    """File content: keys in documented order, lists sorted by natural key."""
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (text_id,))]  # noqa: E731
    return {
        "text_id": text_id,
        "characters": rows("SELECT char, gloss, origin FROM text_character WHERE text_id = ? ORDER BY char"),
        "words": [_unlinked_level(r) for r in rows("SELECT surface, pinyin, hsk_level, gloss, origin, word_id FROM text_word WHERE text_id = ? ORDER BY surface")],
        "expansions": [_unlinked_level(r) for r in rows("SELECT char, surface, hsk_level, gloss, origin, word_id FROM text_expansion WHERE text_id = ? ORDER BY char, surface")],
        "readings": rows("SELECT char, pinyin, position, origin FROM text_reading WHERE text_id = ? ORDER BY char, position"),
        "notes": rows("SELECT anchor, note, origin FROM text_note WHERE text_id = ? ORDER BY coalesce(anchor, ''), note"),
    }


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
                annotations.add_character(conn, text_id, c["char"], c.get("gloss"), c.get("origin", "manual"))
            for r in data.get("readings", []):  # before words, so a local word's prefilled reading sees overrides
                annotations.add_reading(conn, text_id, r["char"], r["pinyin"], r.get("position"), r.get("origin", "manual"))
            for w in data.get("words", []):
                annotations.add_word(conn, text_id, w["surface"], w.get("gloss"), w.get("pinyin"), w.get("origin", "manual"), w.get("hsk_level"))
            for e in data.get("expansions", []):
                annotations.add_expansion(conn, text_id, e["char"], e["surface"], e.get("gloss"), e.get("origin", "manual"), e.get("hsk_level"))
            for n in data.get("notes", []):
                annotations.add_note(conn, text_id, n["note"], n.get("anchor"), n.get("origin", "manual"))
        except AnnotationError as e:
            raise AnnotationError(f"{path}: {e}") from None
        except KeyError as e:
            raise AnnotationError(f"{path}: 缺少字段 {e}") from None
