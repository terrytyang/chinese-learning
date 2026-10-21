"""Admin routes under /texts: the text page (info, lessons, readings, characters, words, expansions, notes, learner state) and a JSON lookup."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from . import admin_page, annotation_files, annotations, db, lesson_files, lessons, progress, texts
from .annotations import AnnotationError
from .progress import ProgressError
from .texts import TextFileError


def router(templates, connection, data_dir) -> APIRouter:
    """`connection` is the app's per-request dependency; `data_dir` holds the text, annotation and lesson files."""
    r = APIRouter()

    async def raw_form(request: Request) -> dict:
        """Raw form fields, for the pinyin edit form whose field names are body positions."""
        return dict(await request.form())

    def edit_fields(gloss: str = Form(""), pinyin: str = Form(""), hsk_level: str = Form(""), surface: str = Form(""), anchor: str = Form(""), note: str = Form("")) -> dict:
        return {"gloss": gloss, "pinyin": pinyin, "hsk_level": hsk_level, "surface": surface, "anchor": anchor, "note": note}

    def require_text(conn, text_id) -> dict:
        row = db.get_text(conn, text_id)
        if row is None:
            raise HTTPException(status_code=404, detail="没有这篇课文")
        return row

    def page(request, conn, text_id, status=200, error=None, submitted=None, editing=None, pending=None):
        require_text(conn, text_id)
        edit = request.query_params.get("edit", "")
        editing = editing or (("pinyin",) if edit == "pinyin" else tuple(edit.split(":", 1)) if ":" in edit else None)
        context = {**admin_page.context(request, conn, text_id, admin_page.view(request, conn, text_id)), "error": error,
                   "submitted": submitted or {}, "editing": editing, "edit_values": submitted if error and editing else None, "pending": pending}
        return templates.TemplateResponse(request, "text.html", context, status_code=status)

    def save(request, conn, text_id, change, fragment, submitted, editing=None, pending=None, write=True):
        """POST → redirect to the page at `fragment`, keeping lesson and filters; a validation error re-renders with 422, the message at its form."""
        require_text(conn, text_id)
        try:
            result = change()
        except (AnnotationError, ProgressError, TextFileError) as e:
            conn.rollback()
            return page(request, conn, text_id, 422, {"form": submitted["form"], "message": str(e)}, submitted, editing, pending)
        conn.commit()
        if write:
            annotation_files.write_file(conn, text_id, data_dir)
            lesson_files.write_files(conn, text_id, data_dir)
        target = fragment(result) if callable(fragment) else fragment
        query = target if target.startswith("?") else admin_page.view(request, conn, text_id)["q"] + "#" + target
        return RedirectResponse(f"/texts/{text_id}{query}", status_code=303)

    def in_lesson(request, conn, text_id) -> int:
        lesson = admin_page.view(request, conn, text_id)["lesson"]
        if lesson is None:
            raise AnnotationError("请先新建课程")
        return lesson["id"]

    @r.get("/texts", response_class=HTMLResponse)
    def index(request: Request, tag: str = "", author: str = "", period: str = "", conn=Depends(connection)):
        rows = [dict(t, lessons=lessons.for_text(conn, t["id"])) for t in db.list_texts(conn, tag=tag, author=author, period=period)]
        context = {"texts": rows, "options": db.filter_options(conn), "selected": {"tag": tag, "author": author, "period": period}}
        return templates.TemplateResponse(request, "texts.html", context)

    @r.get("/texts/{text_id}", response_class=HTMLResponse)
    def text(request: Request, text_id: int, conn=Depends(connection)):
        return page(request, conn, text_id)

    @r.get("/api/characters")
    def api_characters(chars: str = "", conn=Depends(connection)):
        return {"characters": db.lookup_characters(conn, db.unique_characters(chars))}

    @r.post("/texts/{text_id}/info")
    def info(request: Request, text_id: int, author: str = Form(""), period: str = Form(""), tags: str = Form(""), conn=Depends(connection)):
        def change():
            text = texts.write_header(texts.path_for(data_dir / "texts", text_id), author=author, period=period, tags=tags)
            db.update_text_info(conn, text_id, text.author, text.period, text.tags)
        return save(request, conn, text_id, change, "info", {"form": "info", "author": author, "period": period, "tags": tags}, write=False)

    @r.post("/texts/{text_id}/lessons")
    def lesson_create(request: Request, text_id: int, name: str = Form(""), conn=Depends(connection)):
        return save(request, conn, text_id, lambda: lessons.create(conn, text_id, name), lambda new: f"?lesson={new}#lesson", {"form": "lesson", "name": name})

    @r.post("/texts/{text_id}/lessons/{lesson_id}/{action}")
    def lesson_action(request: Request, text_id: int, lesson_id: int, action: str, name: str = Form(""), conn=Depends(connection)):
        if action == "rename":
            return save(request, conn, text_id, lambda: lessons.rename(conn, lesson_id, name), "lesson", {"form": "lesson", "name": name})
        if action == "delete":
            return save(request, conn, text_id, lambda: lessons.delete(conn, lesson_id), "lesson", {"form": "lesson"})
        raise HTTPException(status_code=404)

    @r.post("/texts/{text_id}/readings")
    def readings_save(request: Request, text_id: int, fields=Depends(raw_form), conn=Depends(connection)):
        values = {int(k[1:]): v.strip() for k, v in fields.items() if k[:1] == "p" and k[1:].isdigit()}

        def change():
            body = require_text(conn, text_id)["body"]
            stored = {x["position"]: x["pinyin"] for x in annotations.load(conn, text_id)["readings"]}
            for position, value in sorted(values.items()):
                if not value:
                    raise AnnotationError(f"位置 {position}「{body[position]}」的读音不能为空")
                if value != stored.get(position):
                    annotations.set_reading(conn, text_id, position, body[position], value)
        return save(request, conn, text_id, change, "reading", {"form": "pinyin", **fields}, editing=("pinyin",))

    @r.post("/texts/{text_id}/characters/add")
    def characters_add(request: Request, text_id: int, chars: list[str] = Form([]), all: str = Form(""), conn=Depends(connection)):
        def change():
            lesson_id, v = in_lesson(request, conn, text_id), admin_page.view(request, conn, text_id)
            for ch in [c["char"] for c in admin_page.candidate_characters(conn, text_id, lesson_id, v["filters"])] if all else chars:
                lessons.add_character(conn, lesson_id, ch)
        return save(request, conn, text_id, change, "characters", {"form": "chars-add"})

    @r.post("/texts/{text_id}/characters/{char}/{action}")
    def character_action(request: Request, text_id: int, char: str, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        if action == "remove":
            return save(request, conn, text_id, lambda: lessons.remove(conn, in_lesson(request, conn, text_id), "characters", char), "characters", {"form": "chars"})
        if action == "facts":
            change = lambda: annotations.update(conn, text_id, "characters", (char,), f)  # noqa: E731
            return save(request, conn, text_id, change, f"char-{char}", {"form": f"char-facts:{char}", **f})
        raise HTTPException(status_code=404)

    @r.post("/texts/{text_id}/words/add")
    def words_add(request: Request, text_id: int, words: list[str] = Form([]), all: str = Form(""), conn=Depends(connection)):
        def change():
            lesson_id, v = in_lesson(request, conn, text_id), admin_page.view(request, conn, text_id)
            for surface in [w["surface"] for w in admin_page.candidate_words(conn, text_id, lesson_id, v["filters"])] if all else words:
                lessons.add_word(conn, lesson_id, surface)
        return save(request, conn, text_id, change, "words", {"form": "words-add"})

    @r.post("/texts/{text_id}/words/new")
    def word_new(request: Request, text_id: int, f=Depends(edit_fields), conn=Depends(connection)):
        def change():
            lesson_id = in_lesson(request, conn, text_id)
            annotations.add_word(conn, text_id, f["surface"], f["gloss"], f["pinyin"], hsk_level=f["hsk_level"])
            lessons.add_word(conn, lesson_id, f["surface"])
        return save(request, conn, text_id, change, f"word-{f['surface'].strip()}", {"form": "word-new", **f})

    @r.post("/texts/{text_id}/words/{word}/{action}")
    def word_action(request: Request, text_id: int, word: str, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        if action == "remove":
            return save(request, conn, text_id, lambda: lessons.remove(conn, in_lesson(request, conn, text_id), "words", word), "words", {"form": "words"})
        if action == "delete":
            return save(request, conn, text_id, lambda: annotations.remove(conn, text_id, "words", word), "words", {"form": "words"})
        if action == "facts":
            change = lambda: annotations.update(conn, text_id, "words", (word,), f)  # noqa: E731
            return save(request, conn, text_id, change, f"word-{word}", {"form": f"word-facts:{word}", **f}, editing=("words", word))
        raise HTTPException(status_code=404)

    @r.post("/texts/{text_id}/expansions")
    def expansion_add(
        request: Request, text_id: int, char: str = Form(""), surface: str = Form(""), gloss: str = Form(""), hsk_level: str = Form(""),
        state: str = Form(""), step: str = Form(""), conn=Depends(connection),
    ):
        """Two steps: a master word links at once; otherwise the page returns asking for gloss, level and state (step 2)."""
        word = surface.strip()
        local = step == "2"
        submitted = {"form": f"expansion-{'local' if local else 'add'}:{char}", "char": char, "surface": surface, "gloss": gloss, "hsk_level": hsk_level, "state": state}
        pending = {"char": char, "surface": word} if local else None
        if not local and word and not conn.execute("SELECT 1 FROM word WHERE simplified = ?", (word,)).fetchone():
            return page(request, conn, text_id, 200, None, {**submitted, "form": f"expansion-local:{char}"}, pending={"char": char, "surface": word})

        def change():
            lessons.add_expansion(conn, in_lesson(request, conn, text_id), char, surface, gloss if local else None, hsk_level=hsk_level if local else None)
            if local and state and state != "unrecognized":
                progress.set_state(conn, "word", word, state)
        return save(request, conn, text_id, change, f"expansion-{char}-{word}", submitted, pending=pending)

    @r.post("/texts/{text_id}/expansions/{char}/{word}/{action}")
    def expansion_action(request: Request, text_id: int, char: str, word: str, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        key = f"{char}/{word}"
        if action == "update":
            change = lambda: lessons.update(conn, in_lesson(request, conn, text_id), "expansions", (char, word), f)  # noqa: E731
            return save(request, conn, text_id, change, f"expansion-{char}-{f['surface'].strip()}", {"form": f"expansion-edit:{key}", **f}, editing=("expansions", key))
        if action == "delete":
            return save(request, conn, text_id, lambda: lessons.remove(conn, in_lesson(request, conn, text_id), "expansions", char, word), "expansions", {"form": "expansions"})
        raise HTTPException(status_code=404)

    @r.post("/texts/{text_id}/notes")
    def note_add(request: Request, text_id: int, anchor: str = Form(""), note: str = Form(""), conn=Depends(connection)):
        change = lambda: lessons.add_note(conn, in_lesson(request, conn, text_id), note, anchor)  # noqa: E731
        return save(request, conn, text_id, change, lambda new: f"note-{new}", {"form": "note-add", "anchor": anchor, "note": note})

    @r.post("/texts/{text_id}/notes/{note_id}/{action}")
    def note_action(request: Request, text_id: int, note_id: int, action: str, f=Depends(edit_fields), conn=Depends(connection)):
        if action == "update":
            change = lambda: lessons.update(conn, in_lesson(request, conn, text_id), "notes", (note_id,), f)  # noqa: E731
            return save(request, conn, text_id, change, f"note-{note_id}", {"form": f"note-edit:{note_id}", **f}, editing=("notes", str(note_id)))
        if action == "delete":
            return save(request, conn, text_id, lambda: lessons.remove(conn, in_lesson(request, conn, text_id), "notes", note_id), "notes", {"form": "notes"})
        raise HTTPException(status_code=404)

    @r.post("/texts/{text_id}/progress")
    def set_progress(request: Request, text_id: int, kind: str = Form(""), key: str = Form(""), state: str = Form(""), conn=Depends(connection)):
        fragment = f"{'char' if kind == 'character' else 'word'}-{key}"
        return save(request, conn, text_id, lambda: progress.set_state(conn, kind, key, state), fragment, {"form": f"state:{kind}:{key}"}, write=False)

    return r
