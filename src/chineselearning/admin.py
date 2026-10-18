"""Admin routes under /texts: the text page (reader, annotation forms, learner state) and a JSON character lookup."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from . import annotation_files, annotations, db, progress, readings
from .annotations import AnnotationError
from .progress import ProgressError


def router(templates, connection, data_dir) -> APIRouter:
    """`connection` is the app's per-request dependency; `data_dir` is where annotation files are written."""
    r = APIRouter()

    def edit_fields(
        gloss: str = Form(""), pinyin: str = Form(""), hsk_level: str = Form(""), surface: str = Form(""), anchor: str = Form(""), note: str = Form("")
    ) -> dict:
        """Every field an in-place edit can carry; each kind reads the ones it owns."""
        return {"gloss": gloss, "pinyin": pinyin, "hsk_level": hsk_level, "surface": surface, "anchor": anchor, "note": note}

    def require_text(conn, text_id) -> dict:
        row = db.get_text(conn, text_id)
        if row is None:
            raise HTTPException(status_code=404, detail="没有这篇课文")
        return row

    def text_page(request, conn, text_id, status=200, error=None, submitted=None, editing=None, edit_values=None):
        row = require_text(conn, text_id)
        hide = request.query_params.get("hide_mastered") == "1"
        current, states = annotations.load(conn, text_id), progress.current(conn)
        overrides = {r["char"]: r["pinyin"] for r in current["readings"] if r["position"] is None}
        resolved = readings.by_character(readings.readings_for(conn, text_id))
        characters = db.lookup_characters(conn, db.unique_characters(row["body"]))
        for c in characters:
            c.update(resolved=resolved.get(c["char"], []), override=overrides.get(c["char"]), state=states.get(("character", c["char"]), "unrecognized"))
            c["current"] = c["override"] or c.get("pinyin")
        for a in current["words"] + current["expansions"]:
            a["state"] = states.get(("word", a["surface"]), "unrecognized")
        missing, hidden = sum(1 for c in characters if not c["found"]), sum(1 for c in characters if c["state"] == "mastered")
        if hide:
            characters = [c for c in characters if c["state"] != "mastered"]
            for kind in ("words", "expansions"):
                current[kind] = [a for a in current[kind] if a["state"] != "mastered"]
        edit = request.query_params.get("edit", "")
        context = {
            "text": row,
            "characters": characters,
            "missing": missing,
            "hidden": hidden if hide else 0,
            "hide_mastered": hide,
            "q": "?hide_mastered=1" if hide else "",  # appended to every action so a save returns to the same view
            "annotations": current,
            "error": error,
            "submitted": submitted or {},
            "editing": editing or (tuple(edit.split(":", 1)) if ":" in edit else None),
            "edit_values": edit_values,
        }
        return templates.TemplateResponse(request, "text.html", context, status_code=status)

    def save(request, conn, text_id, change, submitted=None, editing=None, write=True):
        """POST → redirect → GET, keeping ?hide_mastered. On a validation error, 422 with the page, message and submitted values."""
        require_text(conn, text_id)
        try:
            change()
        except (AnnotationError, ProgressError) as e:
            conn.rollback()
            return text_page(request, conn, text_id, 422, str(e), submitted, editing, submitted if editing else None)
        conn.commit()
        if write:
            annotation_files.write_file(conn, text_id, data_dir)
        suffix = "?hide_mastered=1" if request.query_params.get("hide_mastered") == "1" else ""
        return RedirectResponse(f"/texts/{text_id}{suffix}", status_code=303)

    def act(request, conn, text_id, kind, action, key, fields):
        """`delete`, `confirm` or `update` one annotation row identified by its natural key."""
        if action == "update":
            change = lambda: annotations.update(conn, text_id, kind, key, fields)  # noqa: E731
            return save(request, conn, text_id, change, fields, editing=(kind, "/".join(map(str, key))))
        if action not in ("delete", "confirm"):
            raise HTTPException(status_code=404)
        change = annotations.remove if action == "delete" else annotations.confirm
        return save(request, conn, text_id, lambda: change(conn, text_id, kind, *key))

    @r.get("/health")
    def health():
        return {"status": "ok"}

    @r.get("/texts", response_class=HTMLResponse)
    def texts(request: Request, tag: str = "", author: str = "", period: str = "", conn=Depends(connection)):
        context = {
            "texts": db.list_texts(conn, tag=tag, author=author, period=period),
            "options": db.filter_options(conn),
            "selected": {"tag": tag, "author": author, "period": period},
        }
        return templates.TemplateResponse(request, "texts.html", context)

    @r.get("/texts/{text_id}", response_class=HTMLResponse)
    def text(request: Request, text_id: int, conn=Depends(connection)):
        return text_page(request, conn, text_id)

    @r.get("/api/characters")
    def api_characters(chars: str = "", conn=Depends(connection)):
        return {"characters": db.lookup_characters(conn, db.unique_characters(chars))}

    # --- add forms; field names match the template inputs ---

    @r.post("/texts/{text_id}/characters")
    def add_character(request: Request, text_id: int, char: str = Form(""), gloss: str = Form(""), conn=Depends(connection)):
        change = lambda: annotations.add_character(conn, text_id, char, gloss)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "character", "char": char, "gloss": gloss})

    @r.post("/texts/{text_id}/words")
    def add_word(request: Request, text_id: int, f=Depends(edit_fields), conn=Depends(connection)):
        change = lambda: annotations.add_word(conn, text_id, f["surface"], f["gloss"], f["pinyin"], hsk_level=f["hsk_level"])  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "word", **f})

    @r.post("/texts/{text_id}/expansions")
    def add_expansion(request: Request, text_id: int, char: str = Form(""), f=Depends(edit_fields), conn=Depends(connection)):
        change = lambda: annotations.add_expansion(conn, text_id, char, f["surface"], f["gloss"], hsk_level=f["hsk_level"])  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "expansion", "char": char, **f})

    @r.post("/texts/{text_id}/readings")
    def add_reading(request: Request, text_id: int, char: str = Form(""), pinyin: str = Form(""), conn=Depends(connection)):
        change = lambda: annotations.add_reading(conn, text_id, char, pinyin)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "reading", "char": char, "pinyin": pinyin})

    @r.post("/texts/{text_id}/notes")
    def add_note(request: Request, text_id: int, anchor: str = Form(""), note: str = Form(""), conn=Depends(connection)):
        change = lambda: annotations.add_note(conn, text_id, note, anchor)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "note", "anchor": anchor, "note": note})

    @r.post("/texts/{text_id}/progress")
    def set_progress(request: Request, text_id: int, kind: str = Form(""), key: str = Form(""), state: str = Form(""), conn=Depends(connection)):
        return save(request, conn, text_id, lambda: progress.set_state(conn, kind, key, state), write=False)

    # --- delete / confirm / update, by natural key ---

    @r.post("/texts/{text_id}/characters/{char}/{action}")
    def character_action(request: Request, text_id: int, char: str, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        return act(request, conn, text_id, "characters", action, (char,), f)

    @r.post("/texts/{text_id}/words/{word}/{action}")  # path param named `word`: `surface` is a form field
    def word_action(request: Request, text_id: int, word: str, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        return act(request, conn, text_id, "words", action, (word,), f)

    @r.post("/texts/{text_id}/expansions/{char}/{word}/{action}")
    def expansion_action(request: Request, text_id: int, char: str, word: str, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        return act(request, conn, text_id, "expansions", action, (char, word), f)

    @r.post("/texts/{text_id}/readings/{char}/{action}")
    def reading_action(request: Request, text_id: int, char: str, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        return act(request, conn, text_id, "readings", action, (char,), f)

    @r.post("/texts/{text_id}/notes/{note_id}/{action}")
    def note_action(request: Request, text_id: int, note_id: int, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        return act(request, conn, text_id, "notes", action, (note_id,), f)

    return r
