"""The Expansions and Related words tabs: a lesson's extra words, by the kind their anchor gives them; the two-step add."""

from fastapi import Depends, Form, Request

from .. import annotations, lessons, progress, supplement
from . import rows
from .common import in_dictionary

PATH = "/texts/{text_id}/lessons/{lesson_id}/"


def load(conn, lesson) -> tuple[dict, list[dict]]:
    content = lessons.load(conn, lesson["id"])
    return content, rows.with_state(conn, content["extra_words"])


def expansions_context(request, conn, text_id, lesson) -> dict:
    """One block per lesson character, in lesson order, then any other character that already has expansions."""
    content, extra = load(conn, lesson)
    body = annotations.body_of(conn, text_id)
    expansions = [e for e in extra if e["kind"] == "expansion"]
    chars = [c["char"] for c in content["characters"]]
    chars += sorted({e["anchor"] for e in expansions} - set(chars), key=body.find)
    all_rows = rows.character_rows(conn, text_id, body)
    return {"blocks": [(all_rows[ch], [e for e in expansions if e["anchor"] == ch]) for ch in chars]}


def related_context(request, conn, text_id, lesson) -> dict:
    return {"related": [e for e in load(conn, lesson)[1] if e["kind"] == "related"]}


def routes(r, admin, connection):
    for tab in ("expansions", "related"):
        register(r, admin, connection, tab)


def register(r, admin, connection, tab):
    """The same actions under each tab's path, so a response is the tab the form is on."""
    path = PATH + tab

    def respond(request, conn, text_id, lesson, change, form, submitted=None, **on_error):
        return admin.tab_mutate(request, conn, text_id, lesson, tab, change, form, submitted, **on_error)

    @r.post(path + "/add")
    def add(
        request: Request, text_id: int, lesson_id: int, anchor: str = Form(""), surface: str = Form(""), pinyin: str = Form(""),
        gloss: str = Form(""), hsk_level: str = Form(""), state: str = Form(""), step: str = Form(""), conn=Depends(connection),
    ):
        """Look up & add: a dictionary word links at once; any other word gets the second form (pinyin, gloss, level, state) as
        step 2, which makes its supplement entry first."""
        lesson = admin.lesson(conn, text_id, lesson_id)
        word, anchor, local = surface.strip(), anchor.strip(), step == "2"
        form = f"{'local' if local else 'add'}:{anchor}"
        submitted = {"anchor": anchor, "surface": surface, "pinyin": pinyin, "gloss": gloss, "hsk_level": hsk_level, "state": state}
        body = admin.text(conn, text_id)["body"]
        anchor_ok = not anchor or (anchor in body and (len(anchor) != 1 or anchor in word))
        if not local and len(word) > 1 and anchor_ok and not in_dictionary(conn, word):
            pending = {"anchor": anchor, "surface": word, "pinyin": rows.prefill_pinyin(conn, text_id, word)}
            return admin.tab(request, conn, text_id, lesson, tab, pending=pending)

        def change():
            if local and not in_dictionary(conn, word):
                supplement.add(conn, admin.data_dir, word, pinyin, gloss, hsk_level)
            lessons.add_extra_word(conn, lesson_id, surface, anchor)
            progress.expose(conn, "word", word)
            if local and state and state != "unconfirmed":
                progress.set_state(conn, "word", word, state, "manual")
        pending = {"anchor": anchor, "surface": word, "pinyin": pinyin} if local else None
        return respond(request, conn, text_id, lesson, change, form, submitted, pending=pending)

    @r.post(path + "/{word}/save")
    def save(
        request: Request, text_id: int, lesson_id: int, word: str, anchor: str = Form(""), surface: str = Form(""),
        pinyin: str = Form(""), gloss: str = Form(""), conn=Depends(connection),
    ):
        """Inline edit of pinyin and gloss; the row is (word, anchor), both carried as hidden fields."""
        lesson = admin.lesson(conn, text_id, lesson_id)
        anchor, key = anchor.strip(), lessons.extra_key(anchor.strip(), word)
        fields = {"surface": surface or word, "pinyin": pinyin, "gloss": gloss}
        change = lambda: lessons.update(conn, lesson_id, "extra_words", (word, anchor), fields)  # noqa: E731
        return respond(request, conn, text_id, lesson, change, f"edit:{key}", fields, editing=key)

    @r.post(path + "/{word}/delete")
    def delete(request: Request, text_id: int, lesson_id: int, word: str, anchor: str = Form(""), conn=Depends(connection)):
        lesson = admin.lesson(conn, text_id, lesson_id)
        return respond(request, conn, text_id, lesson, lambda: lessons.remove(conn, lesson_id, "extra_words", word, anchor.strip()), "add:")
