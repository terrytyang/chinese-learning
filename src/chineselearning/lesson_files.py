"""Lesson files data/lessons/<text id>-<lesson id>.json: export, write-through, and import on build."""

import json
import re
from pathlib import Path

from . import lessons
from .annotation_files import unlinked_level, write_json
from .annotations import AnnotationError

NAME = re.compile(r"(\d+)-(\d+)\.json")


def export(conn, lesson_id) -> dict:
    """File content: selections as sorted lists, expansions by (char, surface), notes by (anchor, note)."""
    lesson = lessons.get(conn, lesson_id)
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (lesson_id,))]  # noqa: E731
    return {
        "lesson_id": lesson_id,
        "text_id": lesson["text_id"],
        "name": lesson["name"],
        "characters": [r[0] for r in conn.execute("SELECT char FROM lesson_character WHERE lesson_id = ? ORDER BY char", (lesson_id,))],
        "words": [r[0] for r in conn.execute("SELECT surface FROM lesson_word WHERE lesson_id = ? ORDER BY surface", (lesson_id,))],
        "expansions": [unlinked_level(r) for r in rows("SELECT char, surface, hsk_level, gloss, origin, word_id FROM lesson_expansion WHERE lesson_id = ? ORDER BY char, surface")],
        "notes": rows("SELECT anchor, note, origin FROM lesson_note WHERE lesson_id = ? ORDER BY coalesce(anchor, ''), note"),
    }


def file_path(data_dir, text_id, lesson_id) -> Path:
    return Path(data_dir) / "lessons" / f"{text_id}-{lesson_id}.json"


def write_files(conn, text_id, data_dir):
    """Rewrite every lesson file of the text and drop files of lessons that no longer exist."""
    current = {lesson["id"] for lesson in lessons.for_text(conn, text_id)}
    for lesson_id in current:
        write_json(file_path(data_dir, text_id, lesson_id), export(conn, lesson_id))
    for path in Path(data_dir, "lessons").glob(f"{text_id}-*.json"):
        match = NAME.fullmatch(path.name)
        if match and int(match.group(2)) not in current:
            path.unlink()


def import_all(conn, data_dir):
    """Import every data/lessons/*.json after the text facts; any problem is an AnnotationError naming the file."""
    for path in sorted(Path(data_dir, "lessons").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        try:
            match = NAME.fullmatch(path.name)
            text_id, lesson_id = data.get("text_id"), data.get("lesson_id")
            if not match or (int(match.group(1)), int(match.group(2))) != (text_id, lesson_id):
                raise AnnotationError(f"文件名应为 {text_id}-{lesson_id}.json")
            if not conn.execute("SELECT 1 FROM text WHERE id = ?", (text_id,)).fetchone():
                raise AnnotationError(f"没有 id 为 {text_id} 的课文")
            lessons.create(conn, text_id, data["name"], lesson_id)
            for char in data.get("characters", []):
                lessons.add_character(conn, lesson_id, char)
            for surface in data.get("words", []):
                lessons.add_word(conn, lesson_id, surface)
            for e in data.get("expansions", []):
                lessons.add_expansion(conn, lesson_id, e["char"], e["surface"], e.get("gloss"), e.get("origin", "manual"), e.get("hsk_level"))
            for n in data.get("notes", []):
                lessons.add_note(conn, lesson_id, n["note"], n.get("anchor"), n.get("origin", "manual"))
        except AnnotationError as e:
            raise AnnotationError(f"{path}: {e}") from None
        except KeyError as e:
            raise AnnotationError(f"{path}: 缺少字段 {e}") from None
