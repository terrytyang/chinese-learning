"""Import a text from the page (/texts/import): the form, its live preview of the file, and the import itself, which
writes data/texts/<id>-<title>.md, inserts the text as build does, and runs intake. Matches docs/mockups/import-text.dc.html."""

from fastapi import Depends, Form, Request
from fastapi.responses import HTMLResponse

from .. import db, drift, texts
from ..annotations import AnnotationError
from ..intake import intake
from ..texts import TextFileError

FIELDS = ("title", "author", "period", "tags", "body")
EMPTY = {"title": "", "author": "", "period": "", "tags": "诗词", "body": ""}


def preview(conn, fields) -> str:
    """The exact file content, or the parse error it would raise."""
    content, name = compose(conn, fields)
    try:
        texts.parse_text(content, name)
    except TextFileError as e:
        return str(e)
    return content


def compose(conn, fields) -> tuple[str, str]:
    """(content, data/texts/<file name>) for the next id."""
    text_id = db.next_text_id(conn)
    return texts.compose(text_id, fields["title"], fields["tags"], fields["body"], fields["author"], fields["period"]), f"data/texts/{texts.file_name(text_id, fields['title'])}"


def routes(r, admin, connection):
    templates = admin.templates

    def form_context(conn, fields, **state) -> dict:
        return {"fields": fields, "preview": preview(conn, fields), "error": None, "missing": None, "done": None, **state}

    def form(request, conn, fields, status=200, **state):
        return HTMLResponse(templates.get_template("admin/import_form.html").render({"request": request, **form_context(conn, fields, **state)}).strip(), status_code=status)

    @r.get("/texts/import", response_class=HTMLResponse)
    def page(request: Request, conn=Depends(connection)):
        return templates.TemplateResponse(request, "admin/import.html", {**form_context(conn, dict(EMPTY)), "drift": admin.drift(conn)})

    @r.post("/texts/import/preview", response_class=HTMLResponse)
    def preview_fragment(request: Request, title: str = Form(""), author: str = Form(""), period: str = Form(""), tags: str = Form(""), body: str = Form(""), conn=Depends(connection)):
        text = preview(conn, {"title": title, "author": author, "period": period, "tags": tags, "body": body})
        return HTMLResponse(templates.get_template("admin/import_preview.html").render({"preview": text}).strip())

    @r.post("/texts/import", response_class=HTMLResponse)
    def import_(request: Request, title: str = Form(""), author: str = Form(""), period: str = Form(""), tags: str = Form(""), body: str = Form(""), conn=Depends(connection)):
        """Validate everything, then write the file, insert the text like build does, run intake and commit; the form
        comes back with a confirmation card above it, or the message at the form (422)."""
        fields = {"title": title, "author": author, "period": period, "tags": tags, "body": body}
        content, name = compose(conn, fields)
        try:
            text = texts.parse_text(content, name)
        except TextFileError as e:
            return form(request, conn, fields, 422, error=str(e))
        if "/" in text.title:
            return form(request, conn, fields, 422, error="the title must not contain /")
        missing = [c["char"] for c in db.lookup_characters(conn, db.unique_characters(text.body)) if not c["found"]]
        if missing:
            return form(request, conn, fields, 422, missing=missing)
        path = admin.data_dir / "texts" / texts.file_name(text.id, text.title)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        try:
            drift.touch(conn, admin.data_dir, path)
            db.insert_text(conn, text)
            counts = intake(conn, text.id, admin.data_dir)  # commits, and writes the annotation and lesson files
        except (AnnotationError, TextFileError) as e:
            conn.rollback()
            return form(request, conn, fields, 422, error=f"{name} was written, but intake failed: {e}. The file is the source; build and intake will pick it up")
        conn.commit()
        done = {"file": name, "id": text.id, "title": text.title, "characters": len(db.unique_characters(text.body)), "words": counts["words"]}
        return form(request, conn, dict(EMPTY), done=done, oob_preview=True)
