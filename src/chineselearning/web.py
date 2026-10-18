"""FastAPI app factory: templates, the per-request connection, /health. Routes: admin.py (/texts…), learn.py (/learn…)."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import admin, db, learn, progress

DEFAULT_DB = "build/content.sqlite"
DEFAULT_DATA = "data"
DEFAULT_PROGRESS = "build/progress.sqlite"
PACKAGE_DIR = Path(__file__).parent
SOURCE_LABELS = {"manual": "指定", "auto": "默认", "suggested": "建议", "none": "无"}


def hsk_label(level) -> str:
    """Level 7 is the combined 7–9 band."""
    return "7–9" if level == 7 else str(level)


def source_label(source) -> str:
    """Where a stored reading came from (its origin), for the 字表."""
    return f"由「{source[5:]}」确定" if source.startswith("word:") else SOURCE_LABELS[source]


def create_app(db_path=None, data_dir=DEFAULT_DATA, progress_path=None) -> FastAPI:
    """`data_dir` is where annotation files are written; the database paths fall back to $CHINESELEARNING_DB / _PROGRESS."""
    db_path = Path(db_path or os.environ.get("CHINESELEARNING_DB", DEFAULT_DB))
    progress_path = Path(progress_path or os.environ.get("CHINESELEARNING_PROGRESS", DEFAULT_PROGRESS))
    app = FastAPI(title="chineselearning")
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    templates = Jinja2Templates(directory=PACKAGE_DIR / "templates")
    templates.env.filters["hsk"] = hsk_label
    templates.env.filters["source"] = source_label
    templates.env.filters["state"] = progress.LABELS.get

    def connection():
        conn = db.connect(db_path, progress_path=progress_path)
        try:
            yield conn
        finally:
            conn.close()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(admin.router(templates, connection, Path(data_dir)))
    app.include_router(learn.router(templates, connection))
    return app


app = create_app()
