"""Admin routes under /texts: the shell, the text block and one module per tab, every region an htmx fragment (design.md, Modes).

Fragment URLs: `/texts/{text}/text` (and `/edit`), `/texts/{text}/lessons/{lesson}/<tab>`; tags and lesson controls under
`/texts/{text}`. A mutation returns the fragment it changed; a validation failure returns it with the message at its form, 422.
"""

from fastapi import APIRouter, Depends, Form, HTTPException, Request

from .. import progress
from . import characters, extra_words, notes, shell, text_block, words
from .common import TABS, Admin


def router(templates, connection, data_dir) -> APIRouter:
    """`connection` is the app's per-request dependency; `data_dir` holds the text, annotation and lesson files."""
    r = APIRouter()
    templates.env.globals["TABS"] = TABS
    admin = Admin(templates, data_dir)
    admin.tabs = {"characters": characters.context, "words": words.context, "expansions": extra_words.expansions_context,
                  "related": extra_words.related_context, "notes": notes.context}
    admin.regions = {"lessons": shell.lesson_context, "lines": text_block.context,
                     "tab": lambda request, conn, text_id, lesson: admin.tab_context(request, conn, text_id, lesson, "characters")}
    for module in (shell, text_block, characters, words, extra_words, notes):
        module.routes(r, admin, connection)

    @r.get("/texts/{text_id}/lessons/{lesson_id}/{tab}")
    def tab(request: Request, text_id: int, lesson_id: int, tab: str, edit: str = "", conn=Depends(connection)):
        """The tab card; `?edit=<key>` opens a row's inline edit, the other query parameters are the tab's filters."""
        if tab not in TABS:
            raise HTTPException(status_code=404)
        return admin.tab(request, conn, text_id, admin.lesson(conn, text_id, lesson_id), tab, editing=edit or None)

    @r.post("/texts/{text_id}/lessons/{lesson_id}/{tab}/progress")
    def set_progress(request: Request, text_id: int, lesson_id: int, tab: str, kind: str = Form(""), key: str = Form(""), state: str = Form(""), conn=Depends(connection)):
        """The four state buttons on any row; the response is the tab the row is on."""
        if tab not in TABS:
            raise HTTPException(status_code=404)
        lesson = admin.lesson(conn, text_id, lesson_id)
        change = lambda: progress.set_state(conn, kind, key, state)  # noqa: E731
        return admin.tab_mutate(request, conn, text_id, lesson, tab, change, f"state:{kind}:{key}", write=False, editing=request.query_params.get("edit") or None)

    return r
