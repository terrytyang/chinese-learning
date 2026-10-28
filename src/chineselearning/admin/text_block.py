"""The text block: the body with ruby readings and its summary line, the pinyin edit form, and the save that stores only changed positions."""

from fastapi import Depends, Request

from .. import annotations
from .. import pinyin as pinyin_
from ..annotations import AnnotationError
from . import rows


def context(request, conn, text_id, lesson, editing=False) -> dict:
    body = annotations.body_of(conn, text_id)
    return {"lines": rows.text_lines(conn, text_id, body), "summary": rows.summary(rows.character_rows(conn, text_id, body)), "text_editing": editing}


def routes(r, admin, connection):
    async def raw_form(request: Request) -> dict:
        """Raw form fields: the edit form's field names are body positions."""
        return dict(await request.form())

    def block(request, conn, text_id, editing=False, status=200, **state):
        admin.text(conn, text_id)
        lesson = admin.current_lesson(request, conn, text_id)
        return admin.respond(request, conn, text_id, lesson, "text_block", {**context(request, conn, text_id, lesson, editing), **state}, status)

    @r.get("/texts/{text_id}/text")
    def show(request: Request, text_id: int, conn=Depends(connection)):
        return block(request, conn, text_id)

    @r.get("/texts/{text_id}/text/edit")
    def edit(request: Request, text_id: int, conn=Depends(connection)):
        """Polyphones get a select of the dictionary's readings, characters the dictionary lacks a text input, the rest is fixed."""
        return block(request, conn, text_id, editing=True)

    @r.post("/texts/{text_id}/text")
    def save(request: Request, text_id: int, fields=Depends(raw_form), conn=Depends(connection)):
        """Store a `manual` reading for every submitted position whose value differs from the stored one."""
        body = admin.text(conn, text_id)["body"]
        values = {int(k[1:]): pinyin_.to_marks(v.strip()) for k, v in fields.items() if k[:1] == "p" and k[1:].isdigit()}

        def change():
            stored = {x["position"]: x["pinyin"] for x in annotations.load(conn, text_id)["readings"]}
            for position, value in sorted(values.items()):
                char = body[position] if position < len(body) else ""
                if not value:
                    raise AnnotationError(f"a reading for position {position} “{char}” is required")
                if value != stored.get(position):
                    annotations.set_reading(conn, text_id, position, char, value)

        _, message = admin.mutate(conn, text_id, change)
        if message is None:
            return block(request, conn, text_id)
        return block(request, conn, text_id, True, 422, error={"form": "pinyin", "message": message}, submitted={"form": "pinyin", **fields})
