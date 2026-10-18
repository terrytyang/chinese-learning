"""The text facts file data/annotations/<text id>.json: export, write-through, and import on build.

The file is the source of truth; it stores surfaces, never word ids, and `hsk_level`
on words only for rows that are not linked to the master.
"""

import json
from pathlib import Path

from . import annotations
from .annotations import AnnotationError

KINDS = ("readings", "characters", "words")


def unlinked_level(row) -> dict:
    """Drop word_id; keep hsk_level only when the row is not linked."""
    row = dict(row)
    if row.pop("word_id") is not None:
        del row["hsk_level"]
    return row


def export(conn, text_id) -> dict:
    """File content: keys in documented order, readings by position, characters by char, words by surface."""
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (text_id,))]  # noqa: E731
    return {
        "text_id": text_id,
        "readings": rows("SELECT position, char, pinyin, origin FROM text_reading WHERE text_id = ? ORDER BY position"),
        "characters": rows("SELECT char, pinyin, hsk_level, gloss, origin FROM text_character WHERE text_id = ? ORDER BY char"),
        "words": [unlinked_level(r) for r in rows("SELECT surface, pinyin, hsk_level, gloss, origin, word_id FROM text_word WHERE text_id = ? ORDER BY surface")],
    }


def file_path(data_dir, text_id) -> Path:
    return Path(data_dir) / "annotations" / f"{text_id}.json"


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_file(conn, text_id, data_dir):
    """Rewrite data/annotations/<id>.json from the database; no facts, no file."""
    path, data = file_path(data_dir, text_id), export(conn, text_id)
    if any(data[kind] for kind in KINDS):
        write_json(path, data)
    else:
        path.unlink(missing_ok=True)


def import_all(conn, data_dir):
    """Import every data/annotations/*.json; any problem is an AnnotationError naming the file (and position, for a reading)."""
    for path in sorted(Path(data_dir, "annotations").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        text_id = data.get("text_id")
        try:
            if path.stem != str(text_id) or not conn.execute("SELECT 1 FROM text WHERE id = ?", (text_id,)).fetchone():
                raise AnnotationError(f"没有 id 为 {text_id} 的课文")
            for r in data.get("readings", []):
                annotations.set_reading(conn, text_id, r["position"], r["char"], r["pinyin"], r.get("origin", "manual"))
            for c in data.get("characters", []):
                annotations.add_character(conn, text_id, c["char"], c.get("gloss"), c.get("pinyin"), c.get("hsk_level"), c.get("origin", "manual"))
            for w in data.get("words", []):
                annotations.add_word(conn, text_id, w["surface"], w.get("gloss"), w.get("pinyin"), w.get("origin", "manual"), w.get("hsk_level"))
        except AnnotationError as e:
            raise AnnotationError(f"{path}: {e}") from None
        except KeyError as e:
            raise AnnotationError(f"{path}: 缺少字段 {e}") from None
