"""The Notes tab: a lesson's notes, each anchored on a passage or on the whole text; add and delete."""

from fastapi import Depends, Form, Request

from .. import lessons

PATH = "/texts/{text_id}/lessons/{lesson_id}/notes"


def context(request, conn, text_id, lesson) -> dict:
    return {"notes": lessons.load(conn, lesson["id"])["notes"]}


def routes(r, admin, connection):
    @r.post(PATH + "/add")
    def add(request: Request, text_id: int, lesson_id: int, anchor: str = Form(""), note: str = Form(""), conn=Depends(connection)):
        lesson = admin.lesson(conn, text_id, lesson_id)
        change = lambda: lessons.add_note(conn, lesson_id, note, anchor)  # noqa: E731
        return admin.tab_mutate(request, conn, text_id, lesson, "notes", change, "note", {"anchor": anchor, "note": note})

    @r.post(PATH + "/{note_id}/delete")
    def delete(request: Request, text_id: int, lesson_id: int, note_id: int, conn=Depends(connection)):
        lesson = admin.lesson(conn, text_id, lesson_id)
        return admin.tab_mutate(request, conn, text_id, lesson, "notes", lambda: lessons.remove(conn, lesson_id, "notes", note_id), "note")
