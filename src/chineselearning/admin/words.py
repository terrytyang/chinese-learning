"""The Words in text tab: the text's word list with lesson inclusion, review, inline edit, delete, and the two-step add."""

from fastapi import Depends, Form, Request

from .. import annotations, lessons, progress, supplement
from .. import pinyin as pinyin_
from . import rows
from .common import filters_of, in_dictionary, level_bounds, select_word

DEFAULTS = {"show": "unreviewed", "min": "1", "max": "7"}
SHOW_OPTIONS = (("all", "all"), ("unreviewed", "not yet reviewed (auto / suggested)"), ("included", "in this lesson"), ("excluded", "not in this lesson"))
PATH = "/texts/{text_id}/lessons/{lesson_id}/words"


def passes(row, filters) -> bool:
    """Level in range (a word without a level always) and the Show filter."""
    lo, hi = level_bounds(filters)
    level, show = row["hsk_level"], filters["show"]
    in_range = level is None or lo <= level <= hi
    return in_range and (show == "all" or (show == "unreviewed" and row["origin"] != "manual")
                         or (show == "included" and row["selected"]) or (show == "excluded" and not row["selected"]))


def shown(request, conn, text_id, lesson) -> tuple[list[dict], dict, str]:
    filters, q = filters_of(request, DEFAULTS)
    all_rows = rows.word_rows(conn, text_id, lessons.load(conn, lesson["id"])["words"])
    return [a for a in all_rows if passes(a, filters)], filters, q


def context(request, conn, text_id, lesson) -> dict:
    words, filters, q = shown(request, conn, text_id, lesson)
    return {"words": words, "filters": filters, "show_options": SHOW_OPTIONS, "q": q}


def routes(r, admin, connection):
    def tab(request, conn, text_id, lesson, change, form, submitted=None, **on_error):
        return admin.tab_mutate(request, conn, text_id, lesson, "words", change, form, submitted, **on_error)

    @r.post(PATH + "/add-shown")
    def add_shown(request: Request, text_id: int, lesson_id: int, conn=Depends(connection)):
        lesson = admin.lesson(conn, text_id, lesson_id)

        def change():
            for a in shown(request, conn, text_id, lesson)[0]:
                select_word(conn, lesson_id, a["surface"])
        return tab(request, conn, text_id, lesson, change, "shown")

    @r.post(PATH + "/review-shown")
    def review_shown(request: Request, text_id: int, lesson_id: int, conn=Depends(connection)):
        """The admin vouches for every shown row: origin becomes manual."""
        lesson = admin.lesson(conn, text_id, lesson_id)

        def change():
            for a in shown(request, conn, text_id, lesson)[0]:
                annotations.confirm(conn, text_id, "words", a["surface"])
        return tab(request, conn, text_id, lesson, change, "shown")

    @r.post(PATH + "/{word}/include")
    def include(request: Request, text_id: int, lesson_id: int, word: str, included: str = Form("", alias="in"), conn=Depends(connection)):
        """The row's checkbox: ticked selects the word for the lesson, unticked removes the selection."""
        lesson = admin.lesson(conn, text_id, lesson_id)
        change = (lambda: select_word(conn, lesson_id, word)) if included else (lambda: lessons.remove(conn, lesson_id, "words", word))
        return tab(request, conn, text_id, lesson, change, "shown")

    @r.post(PATH + "/{word}/save")
    def save(request: Request, text_id: int, lesson_id: int, word: str, pinyin: str = Form(""), gloss: str = Form(""), conn=Depends(connection)):
        """Inline edit of pinyin and gloss; the dictionary's own reading, left as it was, is not stored as an override."""
        lesson = admin.lesson(conn, text_id, lesson_id)
        master = conn.execute("SELECT w.pinyin FROM text_word t JOIN word w ON w.id = t.word_id WHERE t.text_id = ? AND t.surface = ?", (text_id, word)).fetchone()
        fields = {"pinyin": "" if master and pinyin_.to_marks(pinyin.strip()) == master[0] else pinyin, "gloss": gloss}
        change = lambda: annotations.update(conn, text_id, "words", (word,), fields)  # noqa: E731
        return tab(request, conn, text_id, lesson, change, f"edit:{word}", fields, editing=word)

    @r.post(PATH + "/{word}/delete")
    def delete(request: Request, text_id: int, lesson_id: int, word: str, conn=Depends(connection)):
        """Drops the text fact (and with it every lesson's selection of the word)."""
        lesson = admin.lesson(conn, text_id, lesson_id)
        return tab(request, conn, text_id, lesson, lambda: annotations.remove(conn, text_id, "words", word), "shown")

    @r.post(PATH + "/new")
    def new(
        request: Request, text_id: int, lesson_id: int, surface: str = Form(""), pinyin: str = Form(""), gloss: str = Form(""),
        hsk_level: str = Form(""), state: str = Form(""), step: str = Form(""), conn=Depends(connection),
    ):
        """Look up: a dictionary word is added and selected at once; any other word of the text gets the second form (step 2),
        whose pinyin, gloss and level make its supplement entry."""
        lesson = admin.lesson(conn, text_id, lesson_id)
        word, local = surface.strip(), step == "2"
        form = "new-local" if local else "new"
        submitted = {"surface": surface, "pinyin": pinyin, "gloss": gloss, "hsk_level": hsk_level, "state": state}
        body = admin.text(conn, text_id)["body"]
        if not local and len(word) > 1 and word in body and not in_dictionary(conn, word):
            pending = {"surface": word, "pinyin": rows.prefill_pinyin(conn, text_id, word)}
            return admin.tab(request, conn, text_id, lesson, "words", pending=pending, submitted={"form": "new", **submitted})

        def change():
            if local and not in_dictionary(conn, word):
                supplement.add(conn, admin.data_dir, word, pinyin, gloss, hsk_level)
            annotations.add_word(conn, text_id, surface)
            select_word(conn, lesson_id, word)
            if local and state and state != "unconfirmed":
                progress.set_state(conn, "word", word, state)
        pending = {"surface": word, "pinyin": pinyin} if local else None
        return tab(request, conn, text_id, lesson, change, form, submitted, pending=pending)
