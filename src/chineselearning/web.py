"""FastAPI app: admin plain views of the texts plus a JSON character lookup."""

import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import db

DEFAULT_DB = "build/content.sqlite"
PACKAGE_DIR = Path(__file__).parent


def hsk_label(level) -> str:
    """Level 7 is the combined 7–9 band."""
    return "7–9" if level == 7 else str(level)


def create_app(db_path=None) -> FastAPI:
    db_path = Path(db_path or os.environ.get("CHINESELEARNING_DB", DEFAULT_DB))
    app = FastAPI(title="chineselearning")
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")
    templates.env.filters["hsk"] = hsk_label

    def connection():
        conn = db.connect(db_path, readonly=True)
        try:
            yield conn
        finally:
            conn.close()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/texts", response_class=HTMLResponse)
    def texts(request: Request, tag: str = "", author: str = "", period: str = "", conn=Depends(connection)):
        rows = db.list_texts(conn, tag=tag, author=author, period=period)
        context = {
            "texts": rows,
            "options": db.filter_options(conn),
            "selected": {"tag": tag, "author": author, "period": period},
        }
        return templates.TemplateResponse(request, "texts.html", context)

    @app.get("/texts/{text_id}", response_class=HTMLResponse)
    def text(request: Request, text_id: int, conn=Depends(connection)):
        row = db.get_text(conn, text_id)
        if row is None:
            raise HTTPException(status_code=404, detail="没有这篇课文")
        characters = db.lookup_characters(conn, db.unique_characters(row["body"]))
        words = db.find_words(conn, row["body"])
        context = {
            "text": row,
            "characters": characters,
            "missing": sum(1 for c in characters if not c["found"]),
            "words": words,
        }
        return templates.TemplateResponse(request, "text.html", context)

    @app.get("/api/characters")
    def api_characters(chars: str = "", conn=Depends(connection)):
        return {"characters": db.lookup_characters(conn, db.unique_characters(chars))}

    return app


app = create_app()
