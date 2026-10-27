"""The Characters tab: the lesson's characters with their facts and state, and the rest of the text's characters to add."""

from fastapi import Depends, Form, Request

from .. import annotations, lessons
from . import rows
from .common import filters_of, level_bounds, select_character

DEFAULTS = {"min": "1", "max": "7", "state": "learning", "missing": "1"}
STATE_OPTIONS = (("learning", "unconfirmed or exposed"), ("any", "any"), ("unconfirmed", "unconfirmed"),
                 ("exposed", "exposed"), ("recognized", "recognized"), ("mastered", "mastered"))
PATH = "/texts/{text_id}/lessons/{lesson_id}/characters"


def passes(row, filters) -> bool:
    """Level in range (a character without a level only when `missing` is ticked) and the state filter."""
    lo, hi = level_bounds(filters)
    level, state, wanted = row["hsk_level"], row["state"], filters["state"]
    in_range = filters["missing"] == "1" if not level else lo <= level <= hi
    return in_range and (wanted == "any" or state == wanted or (wanted == "learning" and state in ("unconfirmed", "exposed")))


def context(request, conn, text_id, lesson) -> dict:
    filters, q = filters_of(request, DEFAULTS, checkboxes=("missing",))
    all_rows = rows.character_rows(conn, text_id)
    study = [all_rows[c["char"]] for c in lessons.load(conn, lesson["id"])["characters"]]
    in_lesson = {c["char"] for c in study}
    candidates = [r for ch, r in all_rows.items() if ch not in in_lesson and passes(r, filters)]
    return {"study": study, "candidates": candidates, "filters": filters, "state_options": STATE_OPTIONS, "q": q}


def routes(r, admin, connection):
    def tab(request, conn, text_id, lesson_id, change, form, submitted=None):
        lesson = admin.lesson(conn, text_id, lesson_id)
        return admin.tab_mutate(request, conn, text_id, lesson, "characters", change, form, submitted)

    @r.post(PATH + "/add")
    def add(request: Request, text_id: int, lesson_id: int, chars: list[str] = Form([]), conn=Depends(connection)):
        def change():
            for ch in chars:
                select_character(conn, lesson_id, ch)
        return tab(request, conn, text_id, lesson_id, change, "add")

    @r.post(PATH + "/{char}/remove")
    def remove(request: Request, text_id: int, lesson_id: int, char: str, conn=Depends(connection)):
        return tab(request, conn, text_id, lesson_id, lambda: lessons.remove(conn, lesson_id, "characters", char), "add")

    @r.post(PATH + "/{char}/facts")
    def facts(request: Request, text_id: int, lesson_id: int, char: str, gloss: str = Form(""), hsk_level: str = Form(""), conn=Depends(connection)):
        """The gloss and level of a character the master lacks (the text fact)."""
        fields = {"gloss": gloss, "hsk_level": hsk_level}
        change = lambda: annotations.update(conn, text_id, "characters", (char,), fields)  # noqa: E731
        return tab(request, conn, text_id, lesson_id, change, f"facts:{char}", fields)
