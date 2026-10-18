"""Admin routes under /texts: the text page (facts, the selected lesson, learner state) and a JSON character lookup."""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from . import annotation_files, annotations, db, lesson_files, lessons, progress, readings
from .annotations import AnnotationError
from .progress import ProgressError


def router(templates, connection, data_dir) -> APIRouter:
    """`connection` is the app's per-request dependency; `data_dir` is where annotation and lesson files are written."""
    r = APIRouter()

    def edit_fields(gloss: str = Form(""), pinyin: str = Form(""), hsk_level: str = Form(""), surface: str = Form(""), anchor: str = Form(""), note: str = Form("")) -> dict:
        """Every field an in-place edit can carry; each kind reads the ones it owns."""
        return {"gloss": gloss, "pinyin": pinyin, "hsk_level": hsk_level, "surface": surface, "anchor": anchor, "note": note}

    def require_text(conn, text_id) -> dict:
        row = db.get_text(conn, text_id)
        if row is None:
            raise HTTPException(status_code=404, detail="没有这篇课文")
        return row

    def view(request, conn, text_id) -> dict:
        """The page's view state: the selected lesson (default: lowest id), the hide flag, and query suffixes preserving both."""
        available = lessons.for_text(conn, text_id)
        wanted = request.query_params.get("lesson", "")
        lesson = next((x for x in available if str(x["id"]) == wanted), available[0] if available else None)
        params = {}
        if lesson and lesson is not available[0]:
            params["lesson"] = lesson["id"]
        if request.query_params.get("hide_mastered") == "1":
            params["hide_mastered"] = 1
        suffix = urlencode(params)
        return {"lessons": available, "lesson": lesson, "lesson_empty": lesson and lessons.is_empty(conn, lesson["id"]),
                "hide_mastered": "hide_mastered" in params, "q": "?" + suffix if suffix else "", "qa": "&" + suffix if suffix else ""}

    def text_page(request, conn, text_id, status=200, error=None, submitted=None, editing=None, edit_values=None):
        row, v = require_text(conn, text_id), view(request, conn, text_id)
        facts, states = annotations.load(conn, text_id), progress.current(conn)
        content = lessons.load(conn, v["lesson"]["id"]) if v["lesson"] else {"characters": [], "words": set(), "expansions": [], "notes": []}
        stored = readings.by_character([{"char": x["char"], "pinyin": x["pinyin"], "source": x["origin"]} for x in facts["readings"]])
        first = {}
        for x in facts["readings"]:
            first.setdefault(x["char"], x)
        characters = db.lookup_characters(conn, db.unique_characters(row["body"]))
        for c in characters:
            manual = any(p["source"] == "manual" for p in stored.get(c["char"], []))
            c.update(resolved=stored.get(c["char"], []), override=manual, state=states.get(("character", c["char"]), "unrecognized"))
            c["current"] = first[c["char"]]["pinyin"] if c["char"] in first else c.get("pinyin")
        for a in facts["words"]:
            a.update(state=states.get(("word", a["surface"]), "unrecognized"), selected=a["surface"] in content["words"])
        for a in content["characters"]:
            a.update(state=states.get(("character", a["char"]), "unrecognized"), pinyin=first[a["char"]]["pinyin"] if a["char"] in first else None)
        for a in content["expansions"]:
            a["state"] = states.get(("word", a["surface"]), "unrecognized")
        missing, hidden = sum(1 for c in characters if not c["found"]), sum(1 for c in characters if c["state"] == "mastered")
        if v["hide_mastered"]:
            characters = [c for c in characters if c["state"] != "mastered"]
            facts["words"] = [a for a in facts["words"] if a["state"] != "mastered"]
            for kind in ("characters", "expansions"):
                content[kind] = [a for a in content[kind] if a["state"] != "mastered"]
        edit = request.query_params.get("edit", "")
        context = {
            **v, "text": row, "characters": characters, "missing": missing, "hidden": hidden if v["hide_mastered"] else 0,
            "facts": facts, "content": content, "error": error, "submitted": submitted or {},
            "editing": editing or (tuple(edit.split(":", 1)) if ":" in edit else None), "edit_values": edit_values,
        }
        return templates.TemplateResponse(request, "text.html", context, status_code=status)

    def save(request, conn, text_id, change, submitted=None, editing=None, write=True, redirect_to=None):
        """POST → redirect → GET, keeping ?lesson and ?hide_mastered. A validation error re-renders with 422 and the submitted values."""
        require_text(conn, text_id)
        try:
            result = change()
        except (AnnotationError, ProgressError) as e:
            conn.rollback()
            return text_page(request, conn, text_id, 422, str(e), submitted, editing, submitted if editing else None)
        conn.commit()
        if write:
            annotation_files.write_file(conn, text_id, data_dir)
            lesson_files.write_files(conn, text_id, data_dir)
        url = redirect_to(result) if redirect_to else f"/texts/{text_id}{view(request, conn, text_id)['q']}"
        return RedirectResponse(url, status_code=303)

    def in_lesson(request, conn, text_id) -> int:
        lesson = view(request, conn, text_id)["lesson"]
        if lesson is None:
            raise AnnotationError("请先新建课程")
        return lesson["id"]

    def act(request, conn, text_id, kind, action, key, fields):
        """`delete`, `confirm`, `update`, or for words `select`/`unselect`; facts belong to the text, the rest to the selected lesson."""
        lesson_owned = kind in ("expansions", "notes") or action in ("select", "unselect") or (kind == "characters" and action == "delete")
        module = lessons if lesson_owned else annotations
        owner = (lambda: in_lesson(request, conn, text_id)) if lesson_owned else (lambda: text_id)  # resolved inside save(), so 422 not 500
        if kind == "readings" and action == "delete":
            change = lambda: annotations.reset_reading(conn, text_id, key[0])  # noqa: E731
        elif action == "update":
            change = lambda: module.update(conn, owner(), kind, key, fields)  # noqa: E731
            return save(request, conn, text_id, change, fields, editing=(kind, "/".join(map(str, key))))
        elif action == "select":
            change = lambda: lessons.add_word(conn, owner(), key[0])  # noqa: E731
        elif action == "unselect":
            change = lambda: lessons.remove(conn, owner(), "words", key[0])  # noqa: E731
        elif action in ("delete", "confirm"):
            change = lambda: getattr(module, "remove" if action == "delete" else "confirm")(conn, owner(), kind, *key)  # noqa: E731
        else:
            raise HTTPException(status_code=404)
        return save(request, conn, text_id, change)

    @r.get("/texts", response_class=HTMLResponse)
    def texts(request: Request, tag: str = "", author: str = "", period: str = "", conn=Depends(connection)):
        rows = [dict(t, lessons=lessons.for_text(conn, t["id"])) for t in db.list_texts(conn, tag=tag, author=author, period=period)]
        context = {"texts": rows, "options": db.filter_options(conn), "selected": {"tag": tag, "author": author, "period": period}}
        return templates.TemplateResponse(request, "texts.html", context)

    @r.get("/texts/{text_id}", response_class=HTMLResponse)
    def text(request: Request, text_id: int, conn=Depends(connection)):
        return text_page(request, conn, text_id)

    @r.get("/api/characters")
    def api_characters(chars: str = "", conn=Depends(connection)):
        return {"characters": db.lookup_characters(conn, db.unique_characters(chars))}

    # --- lessons ---

    @r.post("/texts/{text_id}/lessons")
    def create_lesson(request: Request, text_id: int, name: str = Form(""), conn=Depends(connection)):
        change = lambda: lessons.create(conn, text_id, name)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "lesson", "name": name}, redirect_to=lambda new_id: f"/texts/{text_id}?lesson={new_id}")

    @r.post("/texts/{text_id}/lessons/{lesson_id}/rename")
    def rename_lesson(request: Request, text_id: int, lesson_id: int, name: str = Form(""), conn=Depends(connection)):
        return save(request, conn, text_id, lambda: lessons.rename(conn, lesson_id, name), {"kind": "lesson", "name": name})

    @r.post("/texts/{text_id}/lessons/{lesson_id}/delete")
    def delete_lesson(request: Request, text_id: int, lesson_id: int, conn=Depends(connection)):
        return save(request, conn, text_id, lambda: lessons.delete(conn, lesson_id), redirect_to=lambda _: f"/texts/{text_id}")

    # --- add forms; field names match the template inputs ---

    @r.post("/texts/{text_id}/characters")
    def add_character(request: Request, text_id: int, char: str = Form(""), gloss: str = Form(""), conn=Depends(connection)):
        def change():
            lessons.add_character(conn, in_lesson(request, conn, text_id), char)
            if gloss.strip():
                annotations.update(conn, text_id, "characters", (char,), {"gloss": gloss})
        return save(request, conn, text_id, change, {"kind": "character", "char": char, "gloss": gloss})

    @r.post("/texts/{text_id}/words")
    def add_word(request: Request, text_id: int, f=Depends(edit_fields), conn=Depends(connection)):
        change = lambda: annotations.add_word(conn, text_id, f["surface"], f["gloss"], f["pinyin"], hsk_level=f["hsk_level"])  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "word", **f})

    @r.post("/texts/{text_id}/expansions")
    def add_expansion(request: Request, text_id: int, char: str = Form(""), f=Depends(edit_fields), conn=Depends(connection)):
        change = lambda: lessons.add_expansion(conn, in_lesson(request, conn, text_id), char, f["surface"], f["gloss"], hsk_level=f["hsk_level"])  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "expansion", "char": char, **f})

    @r.post("/texts/{text_id}/readings")
    def set_reading(request: Request, text_id: int, char: str = Form(""), pinyin: str = Form(""), conn=Depends(connection)):
        change = lambda: annotations.set_reading_everywhere(conn, text_id, char, pinyin)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "reading", "char": char, "pinyin": pinyin})

    @r.post("/texts/{text_id}/notes")
    def add_note(request: Request, text_id: int, anchor: str = Form(""), note: str = Form(""), conn=Depends(connection)):
        change = lambda: lessons.add_note(conn, in_lesson(request, conn, text_id), note, anchor)  # noqa: E731
        return save(request, conn, text_id, change, {"kind": "note", "anchor": anchor, "note": note})

    @r.post("/texts/{text_id}/progress")
    def set_progress(request: Request, text_id: int, kind: str = Form(""), key: str = Form(""), state: str = Form(""), conn=Depends(connection)):
        return save(request, conn, text_id, lambda: progress.set_state(conn, kind, key, state), write=False)

    # --- per-row actions, by natural key ---

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
