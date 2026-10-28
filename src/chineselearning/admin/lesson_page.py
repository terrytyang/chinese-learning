"""The vocabulary lesson page (/lessons/{id}): the name, the members in the dictionary page's row style with Remove,
"Mark all as", and notes; and the vocabulary section of /texts with its New lesson button. A text lesson's id renders one
line pointing at its text page. Every region is an htmx fragment."""

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse

from .. import db, lesson_files, lessons, progress
from ..progress_import import RANK
from .common import ERRORS, deselect
from .dictionary import COLUMNS, ENTRIES

MARK_OPTIONS = progress.STATES[1:]
MEMBERS = f"""SELECT {COLUMNS} {ENTRIES}
              WHERE (d.kind, d.item) IN (SELECT 'character', char FROM lesson_character WHERE lesson_id = ? UNION SELECT 'word', surface FROM lesson_word WHERE lesson_id = ?)
              ORDER BY d.level, d.item"""


def members(conn, lesson_id, learner_id=progress.LEARNER) -> list[dict]:
    """The lesson's characters and words as dictionary rows with the learner's state, by level then item."""
    return [dict(r) for r in conn.execute(MEMBERS, (learner_id, lesson_id, lesson_id))]


def mark(conn, lesson_id, state) -> dict:
    """Raise every member below `state` to it (origin manual, now); higher states are kept. Returns the counts."""
    if state not in MARK_OPTIONS:
        raise progress.ProgressError("state must be exposed, recognized or mastered")
    raised = 0
    for m in members(conn, lesson_id):
        if RANK[m["state"]] < RANK[state]:
            progress.set_state(conn, m["kind"], m["item"], state, "manual")
            raised += 1
    return {"state": state, "raised": raised, "kept": len(members(conn, lesson_id)) - raised}


def routes(r, admin, connection):
    templates = admin.templates

    def vocabulary_lesson(conn, lesson_id) -> dict:
        lesson = lessons.get(conn, lesson_id)
        if lesson is None or lesson["text_id"] is not None:
            raise HTTPException(status_code=404, detail="no such vocabulary lesson")
        return lesson

    def fragment(name, ctx, status=200):
        return HTMLResponse(templates.get_template(f"admin/lesson_{name}.html").render(ctx).strip(), status_code=status)

    def base(request, conn, lesson) -> dict:
        return {"request": request, "lesson": lesson, "lesson_base": f"/lessons/{lesson['id']}", "STATES": progress.STATES, "error": None, "submitted": {}}

    def header(request, conn, lesson, status=200, error=None, name=None):
        rows = members(conn, lesson["id"])
        counts = {"characters": sum(m["kind"] == "character" for m in rows), "words": sum(m["kind"] == "word" for m in rows)}
        state = {"error": {"form": "name", "message": error}, "submitted": {"form": "name", "name": name}} if error else {}
        return fragment("header", {**base(request, conn, lesson), "counts": counts, **state}, status)

    def members_fragment(request, conn, lesson, status=200, **state):
        return fragment("members", {**base(request, conn, lesson), "members": members(conn, lesson["id"]), "mark_options": MARK_OPTIONS, "marked": None, **state}, status)

    def notes(request, conn, lesson, status=200, **state):
        return fragment("notes", {**base(request, conn, lesson), "notes": lessons.load(conn, lesson["id"])["notes"], **state}, status)

    def section(request, conn, status=200, error=None):
        return fragment("section", {"request": request, "vocabulary": lessons.vocabulary(conn), "error": error}, status)

    @r.get("/lessons/{lesson_id}", response_class=HTMLResponse)
    def page(request: Request, lesson_id: int, conn=Depends(connection)):
        lesson = lessons.get(conn, lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="no such lesson")
        rows = members(conn, lesson_id) if lesson["text_id"] is None else []
        ctx = {**base(request, conn, lesson), "text": db.get_text(conn, lesson["text_id"]) if lesson["text_id"] is not None else None,
               "members": rows, "mark_options": MARK_OPTIONS, "marked": None, "notes": lessons.load(conn, lesson_id)["notes"],
               "counts": {"characters": sum(m["kind"] == "character" for m in rows), "words": sum(m["kind"] == "word" for m in rows)}, "drift": admin.drift(conn)}
        return templates.TemplateResponse(request, "admin/lesson_page.html", ctx)

    @r.post("/lessons", response_class=HTMLResponse)
    def create(request: Request, conn=Depends(connection)):
        """A new vocabulary lesson with the default name; the response is the vocabulary section of /texts."""
        lesson_id = lessons.create(conn, None, lessons.default_name(conn))
        conn.commit()
        lesson_files.write_file(conn, lesson_id, admin.data_dir)
        return section(request, conn)

    @r.post("/lessons/{lesson_id}/name", response_class=HTMLResponse)
    def rename(request: Request, lesson_id: int, name: str = Form(""), conn=Depends(connection)):
        lesson = vocabulary_lesson(conn, lesson_id)
        try:
            lessons.rename(conn, lesson_id, name)
        except ERRORS as e:
            conn.rollback()
            return header(request, conn, lesson, 422, error=str(e), name=name)
        conn.commit()
        lesson_files.write_file(conn, lesson_id, admin.data_dir)
        return header(request, conn, lessons.get(conn, lesson_id))

    @r.post("/lessons/{lesson_id}/remove", response_class=HTMLResponse)
    def remove(request: Request, lesson_id: int, item: str = Form(""), conn=Depends(connection)):
        lesson = vocabulary_lesson(conn, lesson_id)
        item = item.strip()
        deselect(conn, lesson_id, "characters" if len(item) == 1 else "words", item)
        conn.commit()
        lesson_files.write_file(conn, lesson_id, admin.data_dir)
        return members_fragment(request, conn, lesson)

    @r.post("/lessons/{lesson_id}/mark", response_class=HTMLResponse)
    def mark_all(request: Request, lesson_id: int, state: str = Form(""), conn=Depends(connection)):
        lesson = vocabulary_lesson(conn, lesson_id)
        try:
            marked = mark(conn, lesson_id, state)
        except ERRORS as e:
            conn.rollback()
            return members_fragment(request, conn, lesson, 422, error={"form": "mark", "message": str(e)})
        conn.commit()
        return members_fragment(request, conn, lesson, marked=marked)

    @r.post("/lessons/{lesson_id}/notes/add", response_class=HTMLResponse)
    def note_add(request: Request, lesson_id: int, note: str = Form(""), conn=Depends(connection)):
        lesson = vocabulary_lesson(conn, lesson_id)
        try:
            lessons.add_note(conn, lesson_id, note)
        except ERRORS as e:
            conn.rollback()
            return notes(request, conn, lesson, 422, error={"form": "note", "message": str(e)}, submitted={"form": "note", "note": note, "anchor": ""})
        conn.commit()
        lesson_files.write_file(conn, lesson_id, admin.data_dir)
        return notes(request, conn, lesson)

    @r.post("/lessons/{lesson_id}/notes/{note_id}/delete", response_class=HTMLResponse)
    def note_delete(request: Request, lesson_id: int, note_id: int, conn=Depends(connection)):
        lesson = vocabulary_lesson(conn, lesson_id)
        lessons.remove(conn, lesson_id, "notes", note_id)
        conn.commit()
        lesson_files.write_file(conn, lesson_id, admin.data_dir)
        return notes(request, conn, lesson)
