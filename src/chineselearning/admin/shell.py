"""The admin shell: the texts index, the page for a text and lesson, the lesson controls, the tags."""

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse

from .. import db, lessons, texts
from ..annotations import AnnotationError, clean
from . import text_block


def lesson_context(request, conn, text_id, lesson) -> dict:
    return {"lessons": lessons.for_text(conn, text_id)}


def routes(r, admin, connection):
    def switch(request, conn, text_id, lesson, region):
        """The tab card, the lesson controls and the text block for `lesson`, with its Characters tab as the URL."""
        ctx = {**lesson_context(request, conn, text_id, lesson), **text_block.context(request, conn, text_id, lesson),
               **admin.tab_context(request, conn, text_id, lesson, "characters")}
        push = f"/texts/{text_id}/lessons/{lesson['id']}/characters" if lesson else None
        return admin.respond(request, conn, text_id, lesson, region, ctx, push=push)

    def controls(request, conn, text_id, lesson, form=None, message=None, **fields):
        """The lesson controls, with a validation message at `form`."""
        state = {"error": {"form": form, "message": message}, "submitted": {"form": form, **fields}} if message else {}
        ctx = {**lesson_context(request, conn, text_id, lesson), **state}
        return admin.respond(request, conn, text_id, lesson, "lesson", ctx, 422 if message else 200)

    @r.get("/texts", response_class=HTMLResponse)
    def index(request: Request, tag: str = "", author: str = "", period: str = "", conn=Depends(connection)):
        rows = [dict(t, lessons=lessons.for_text(conn, t["id"])) for t in db.list_texts(conn, tag=tag, author=author, period=period)]
        context = {"texts": rows, "options": db.filter_options(conn), "selected": {"tag": tag, "author": author, "period": period}}
        return admin.templates.TemplateResponse(request, "texts.html", context)

    @r.get("/api/characters")
    def api_characters(chars: str = "", conn=Depends(connection)):
        return {"characters": db.lookup_characters(conn, db.unique_characters(chars))}

    @r.get("/texts/{text_id}", response_class=HTMLResponse)
    def page(request: Request, text_id: int, conn=Depends(connection)):
        """The shell for `?lesson=`; for htmx (the lesson select) the tab card, with the lesson controls and text block out of band."""
        admin.text(conn, text_id)
        return switch(request, conn, text_id, admin.current_lesson(request, conn, text_id), "switch")

    @r.post("/texts/{text_id}/lessons")
    def lesson_create(request: Request, text_id: int, name: str = Form(""), conn=Depends(connection)):
        """A new lesson becomes the current one: the lesson controls, with its (empty) tab card out of band."""
        admin.text(conn, text_id)
        new, message = admin.mutate(conn, text_id, lambda: lessons.create(conn, text_id, name))
        if message is not None:
            return controls(request, conn, text_id, admin.current_lesson(request, conn, text_id), "lesson-new", message, name=name)
        return switch(request, conn, text_id, lessons.get(conn, new), "lesson_created")

    @r.post("/texts/{text_id}/lessons/{lesson_id}/rename")
    def lesson_rename(request: Request, text_id: int, lesson_id: int, name: str = Form(""), conn=Depends(connection)):
        admin.lesson(conn, text_id, lesson_id)
        _, message = admin.mutate(conn, text_id, lambda: lessons.rename(conn, lesson_id, name))
        return controls(request, conn, text_id, lessons.get(conn, lesson_id), "rename", message, name=name)

    @r.post("/texts/{text_id}/tags/{action}")
    def tags(request: Request, text_id: int, action: str, tag: str = Form(""), conn=Depends(connection)):
        """Add or remove one tag: the only header edit from the app, rewriting the `tags:` line."""
        if action not in ("add", "remove"):
            raise HTTPException(status_code=404)
        current = admin.text(conn, text_id)["tags"]

        def change():
            wanted = clean(tag)
            if not wanted:
                raise AnnotationError("a tag is required")
            new = (current if wanted in current else [*current, wanted]) if action == "add" else [t for t in current if t != wanted]
            if not new:
                raise AnnotationError("a text needs at least one tag")
            parsed = texts.write_header(texts.path_for(admin.data_dir / "texts", text_id), tags=", ".join(new))
            db.update_text_tags(conn, text_id, parsed.tags)

        _, message = admin.mutate(conn, text_id, change, write=False)
        state = {"error": {"form": "tag", "message": message}, "submitted": {"form": "tag", "tag": tag}} if message else {}
        return admin.respond(request, conn, text_id, admin.current_lesson(request, conn, text_id), "tags", state, 422 if message else 200)

