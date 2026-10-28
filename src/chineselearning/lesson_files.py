"""Lesson files data/lessons/<text id>-<lesson id>.json (a vocabulary lesson: <lesson id>.json): export, write-through, and import on build."""

import json
import re
from pathlib import Path

from . import lessons
from .annotation_files import write_json
from .annotations import AnnotationError

NAME = re.compile(r"(?:(\d+)-)?(\d+)\.json")


def export(conn, lesson_id) -> dict:
    """File content: selections as sorted lists, extra words by (anchor or '', surface), notes by (anchor, note)."""
    lesson = lessons.get(conn, lesson_id)
    rows = lambda sql: [dict(r) for r in conn.execute(sql, (lesson_id,))]  # noqa: E731
    return {
        "lesson_id": lesson_id,
        "text_id": lesson["text_id"],
        "name": lesson["name"],
        "characters": [r[0] for r in conn.execute("SELECT char FROM lesson_character WHERE lesson_id = ? ORDER BY char", (lesson_id,))],
        "words": [r[0] for r in conn.execute("SELECT surface FROM lesson_word WHERE lesson_id = ? ORDER BY surface", (lesson_id,))],
        "extra_words": rows("SELECT anchor, surface, pinyin, gloss, origin FROM lesson_extra_word WHERE lesson_id = ? ORDER BY coalesce(anchor, ''), surface"),
        "notes": rows("SELECT anchor, note, origin FROM lesson_note WHERE lesson_id = ? ORDER BY coalesce(anchor, ''), note"),
    }


def file_path(data_dir, text_id, lesson_id) -> Path:
    return Path(data_dir) / "lessons" / (f"{text_id}-{lesson_id}.json" if text_id is not None else f"{lesson_id}.json")


def write_file(conn, lesson_id, data_dir):
    """Rewrite one vocabulary lesson's file; a lesson that no longer exists loses its file."""
    lesson = lessons.get(conn, lesson_id)
    if lesson:
        write_json(file_path(data_dir, lesson["text_id"], lesson_id), export(conn, lesson_id))
    else:
        file_path(data_dir, None, lesson_id).unlink(missing_ok=True)


def write_files(conn, text_id, data_dir):
    """Rewrite every lesson file of the text and drop files of lessons that no longer exist."""
    current = {lesson["id"] for lesson in lessons.for_text(conn, text_id)}
    for lesson_id in current:
        write_json(file_path(data_dir, text_id, lesson_id), export(conn, lesson_id))
    for path in Path(data_dir, "lessons").glob(f"{text_id}-*.json"):
        match = NAME.fullmatch(path.name)
        if match and match.group(1) and int(match.group(2)) not in current:
            path.unlink()


def import_all(conn, data_dir):
    """Import every data/lessons/*.json after the text facts; any problem is an AnnotationError naming the file."""
    for path in sorted(Path(data_dir, "lessons").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        try:
            text_id, lesson_id = data.get("text_id"), data.get("lesson_id")
            expected = file_path(data_dir, text_id, lesson_id).name  # a text lesson is <text>-<lesson>.json, a vocabulary lesson <lesson>.json
            if path.name != expected:
                raise AnnotationError(f"the file name should be {expected}")
            if text_id is not None and not conn.execute("SELECT 1 FROM text WHERE id = ?", (text_id,)).fetchone():
                raise AnnotationError(f"no text with id {text_id}")
            lessons.create(conn, text_id, data["name"], lesson_id)
            for char in data.get("characters", []):
                lessons.add_character(conn, lesson_id, char)
            for surface in data.get("words", []):
                lessons.add_word(conn, lesson_id, surface)
            for e in data.get("extra_words", []):
                lessons.add_extra_word(conn, lesson_id, e["surface"], e.get("anchor"), e.get("gloss"), e.get("pinyin"), e.get("origin", "manual"))
            for n in data.get("notes", []):
                lessons.add_note(conn, lesson_id, n["note"], n.get("anchor"), n.get("origin", "manual"))
        except AnnotationError as e:
            raise AnnotationError(f"{path}: {e}") from None
        except KeyError as e:
            raise AnnotationError(f"{path}: missing field {e}") from None
