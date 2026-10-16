"""FastAPI app: the admin text page (reader plus annotation forms) and a JSON character lookup."""

import os
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import annotations, db, readings
from .annotations import AnnotationError

DEFAULT_DB = "build/content.sqlite"
DEFAULT_DATA = "data"
PACKAGE_DIR = Path(__file__).parent
SOURCE_LABELS = {"override": "指定", "primary": "默认", "none": "无"}


def hsk_label(level) -> str:
    """Level 7 is the combined 7–9 band."""
    return "7–9" if level == 7 else str(level)


def source_label(source) -> str:
    """How a reading was resolved, for the 字表."""
    return f"由「{source[5:]}」确定" if source.startswith("word:") else SOURCE_LABELS[source]


def create_app(db_path=None, data_dir=DEFAULT_DATA) -> FastAPI:
    """`data_dir` is where annotation files are written; `db_path` falls back to $CHINESELEARNING_DB."""
    db_path = Path(db_path or os.environ.get("CHINESELEARNING_DB", DEFAULT_DB))
    data_dir = Path(data_dir)
    app = FastAPI(title="chineselearning")
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")
    templates.env.filters["hsk"] = hsk_label
    templates.env.filters["source"] = source_label

    def connection():
        conn = db.connect(db_path)
        try:
            yield conn
        finally:
            conn.close()

    def require_text(conn, text_id) -> dict:
        row = db.get_text(conn, text_id)
        if row is None:
            raise HTTPException(status_code=404, detail="没有这篇课文")
        return row

    def text_page(request, conn, text_id, status=200, error=None, submitted=None):
        row = require_text(conn, text_id)
        current = annotations.load(conn, text_id)
        overrides = {r["char"]: r["pinyin"] for r in current["readings"] if r["position"] is None}
        resolved = readings.by_character(readings.readings_for(conn, text_id))
        characters = db.lookup_characters(conn, db.unique_characters(row["body"]))
        for c in characters:
            c.update(resolved=resolved.get(c["char"], []), override=overrides.get(c["char"]))
            c["current"] = c["override"] or c.get("pinyin")
        context = {
            "text": row,
            "characters": characters,
            "missing": sum(1 for c in characters if not c["found"]),
            "annotations": current,
            "error": error,
            "submitted": submitted or {},
        }
        return templates.TemplateResponse(request, "text.html", context, status_code=status)

    def save(request, conn, text_id, change, submitted=None):
        """POST → redirect → GET. On a validation error, 422 with the page, message and submitted values."""
        require_text(conn, text_id)
        try:
            change()
        except AnnotationError as e:
            conn.rollback()
            return text_page(request, conn, text_id, 422, str(e), submitted)
        conn.commit()
        annotations.write_file(conn, text_id, data_dir)
        return RedirectResponse(f"/texts/{text_id}", status_code=303)

    def act(request, conn, text_id, kind, action, *key):
        """`delete` or `confirm` one annotation row identified by its natural key."""
        if action not in ("delete", "confirm"):
            raise HTTPException(status_code=404)
        change = annotations.remove if action == "delete" else annotations.confirm
        return save(request, conn, text_id, lambda: change(conn, text_id, kind, *key))

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/texts", response_class=HTMLResponse)
    def texts(request: Request, tag: str = "", author: str = "", period: str = "", conn=Depends(connection)):
        context = {
            "texts": db.list_texts(conn, tag=tag, author=author, period=period),
            "options": db.filter_options(conn),
            "selected": {"tag": tag, "author": author, "period": period},
        }
        return templates.TemplateResponse(request, "texts.html", context)

    @app.get("/texts/{text_id}", response_class=HTMLResponse)
    def text(request: Request, text_id: int, conn=Depends(connection)):
        return text_page(request, conn, text_id)

    @app.get("/api/characters")
    def api_characters(chars: str = "", conn=Depends(connection)):
        return {"characters": db.lookup_characters(conn, db.unique_characters(chars))}

    # --- annotation forms; field names match the template inputs ---

    @app.post("/texts/{text_id}/characters")
    def add_character(request: Request, text_id: int, char: str = Form(""), gloss: str = Form(""), conn=Depends(connection)):
        change = lambda: annotations.add_character(conn, text_id, char, gloss)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "character", "char": char, "gloss": gloss})

    @app.post("/texts/{text_id}/words")
    def add_word(
        request: Request, text_id: int, surface: str = Form(""), gloss: str = Form(""), pinyin: str = Form(""), conn=Depends(connection)
    ):
        change = lambda: annotations.add_word(conn, text_id, surface, gloss, pinyin)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "word", "surface": surface, "gloss": gloss, "pinyin": pinyin})

    @app.post("/texts/{text_id}/expansions")
    def add_expansion(
        request: Request, text_id: int, char: str = Form(""), surface: str = Form(""), gloss: str = Form(""), conn=Depends(connection)
    ):
        change = lambda: annotations.add_expansion(conn, text_id, char, surface, gloss)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "expansion", "char": char, "surface": surface, "gloss": gloss})

    @app.post("/texts/{text_id}/readings")
    def add_reading(request: Request, text_id: int, char: str = Form(""), pinyin: str = Form(""), conn=Depends(connection)):
        change = lambda: annotations.add_reading(conn, text_id, char, pinyin)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "reading", "char": char, "pinyin": pinyin})

    @app.post("/texts/{text_id}/notes")
    def add_note(request: Request, text_id: int, anchor: str = Form(""), note: str = Form(""), conn=Depends(connection)):
        change = lambda: annotations.add_note(conn, text_id, note, anchor)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "note", "anchor": anchor, "note": note})

    # --- delete / confirm, by natural key ---

    @app.post("/texts/{text_id}/characters/{char}/{action}")
    def character_action(request: Request, text_id: int, char: str, action: str, conn=Depends(connection)):
        return act(request, conn, text_id, "characters", action, char)

    @app.post("/texts/{text_id}/words/{surface}/{action}")
    def word_action(request: Request, text_id: int, surface: str, action: str, conn=Depends(connection)):
        return act(request, conn, text_id, "words", action, surface)

    @app.post("/texts/{text_id}/expansions/{char}/{surface}/{action}")
    def expansion_action(request: Request, text_id: int, char: str, surface: str, action: str, conn=Depends(connection)):
        return act(request, conn, text_id, "expansions", action, char, surface)

    @app.post("/texts/{text_id}/readings/{char}/{action}")
    def reading_action(request: Request, text_id: int, char: str, action: str, conn=Depends(connection)):
        return act(request, conn, text_id, "readings", action, char)

    @app.post("/texts/{text_id}/notes/{note_id}/{action}")
    def note_action(request: Request, text_id: int, note_id: int, action: str, conn=Depends(connection)):
        return act(request, conn, text_id, "notes", action, note_id)

    return app


app = create_app()
