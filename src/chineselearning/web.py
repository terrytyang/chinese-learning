"""FastAPI application factory. Startup only opens an existing application DB."""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from chineselearning.inventory_query import (
    InvalidInventoryQuery, list_characters, open_inventory_database,
)


class CharacterItem(BaseModel):
    id: int
    simplified: str
    traditional: str | None
    english_gloss: str | None
    usage_note: str | None
    hsk_level: int
    hsk_level_label: str
    recognition_status: str | None
    production_status: str | None


class SelectedScheme(BaseModel):
    code: str
    label: str


class CharacterPage(BaseModel):
    items: list[CharacterItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    hsk_scheme: SelectedScheme


def create_app(database_path=None):
    path = database_path if database_path is not None else os.environ.get(
        "CHINESELEARNING_DATABASE", "build/inventory.sqlite"
    )
    engine = open_inventory_database(path)

    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="Chineselearning character inventory", lifespan=lifespan)
    package = Path(__file__).resolve().parent
    templates = Jinja2Templates(directory=package / "templates")
    app.mount("/static", StaticFiles(directory=package / "static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    def inventory_page(request: Request):
        return templates.TemplateResponse(request=request, name="inventory.html")

    @app.get("/api/characters", response_model=CharacterPage)
    def characters(
        hsk_scheme: Literal["old", "new", "newest"] = "newest",
        hsk_level: Annotated[int | None, Query(ge=1, le=7)] = None,
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: int = 20,
        sort: Literal["simplified", "hsk_level"] = "simplified",
        order: Literal["asc", "desc"] = "asc",
    ):
        try:
            return list_characters(
                engine, hsk_scheme_code=hsk_scheme, hsk_level=hsk_level,
                page=page, page_size=page_size, sort=sort, order=order,
            )
        except InvalidInventoryQuery as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    return app
