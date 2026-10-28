"""Shared by the admin modules: lookups that 404, fragment-or-shell rendering, the mutate-then-render step, the tab registry.

A page is a shell rendered once; its regions (lesson controls, tags, text block, the tab card) are fragments with their own
URLs. An htmx request gets the fragment, any other request the shell with that fragment in place (design.md, Modes).
"""

from urllib.parse import urlencode

from fastapi import HTTPException
from fastapi.responses import HTMLResponse

from .. import annotation_files, db, lesson_files, lessons, progress
from ..annotations import AnnotationError
from ..progress import ProgressError
from ..supplement import SupplementError
from ..texts import TextFileError

TABS = {"characters": "Characters", "words": "Words in text", "expansions": "Expansions", "related": "Related words", "notes": "Notes"}
ERRORS = (AnnotationError, ProgressError, SupplementError, TextFileError)
TAB_STATE = {"error": None, "submitted": {}, "editing": None, "pending": None, "q": ""}


def is_fragment(request) -> bool:
    """htmx asks for the fragment; a plain request, or htmx restoring history, wants the whole page."""
    return request.headers.get("HX-Request") == "true" and request.headers.get("HX-History-Restore-Request") != "true"


def filters_of(request, defaults, checkboxes=()) -> tuple[dict, str]:
    """A tab's filter values and the query string that carries them to the tab's actions.

    A bare URL means the defaults; once any filter is in the URL the form sent them all, so an absent checkbox is unticked.
    """
    params = request.query_params
    explicit = any(k in params for k in defaults)
    values = {k: params.get(k) if k in params else ("" if explicit and k in checkboxes else d) for k, d in defaults.items()}
    return values, "?" + urlencode({k: v for k, v in values.items() if v})


def level_bounds(filters) -> tuple[int, int]:
    lo, hi = filters.get("min", ""), filters.get("max", "")
    return (int(lo) if lo.isdigit() else 1, int(hi) if hi.isdigit() else 7)


def in_dictionary(conn, surface) -> bool:
    """Whether the word has a dictionary row, HSK or supplement; any other word gets the second form."""
    return db.lookup_word(conn, surface) is not None


def select_character(conn, lesson_id, char):
    """Adding to a lesson is the one implicit state change: unconfirmed becomes exposed."""
    lessons.add_character(conn, lesson_id, char)
    progress.expose(conn, "character", char.strip())


def select_word(conn, lesson_id, surface):
    lessons.add_word(conn, lesson_id, surface)
    progress.expose(conn, "word", surface.strip())


def tab_counts(conn, text_id, lesson) -> dict:
    """The numbers in the tab labels; Words in text is included/total."""
    content = lessons.load(conn, lesson["id"])
    total = conn.execute("SELECT count(*) FROM text_word WHERE text_id = ?", (text_id,)).fetchone()[0]
    kinds = [e["kind"] for e in content["extra_words"]]
    return {"characters": len(content["characters"]), "words": f"{len(content['words'])}/{total}",
            "expansions": kinds.count("expansion"), "related": kinds.count("related"), "notes": len(content["notes"])}


class Admin:
    """What every admin module needs: the templates, the data directory, and the region and tab builders the package registers."""

    def __init__(self, templates, data_dir):
        self.templates, self.data_dir = templates, data_dir
        self.regions = {}  # a context key that marks the region -> builder(request, conn, text_id, lesson), for the shell
        self.tabs = {}  # tab -> builder(request, conn, text_id, lesson) -> the tab's rows and filters

    def text(self, conn, text_id) -> dict:
        row = db.get_text(conn, text_id)
        if row is None:
            raise HTTPException(status_code=404, detail="no such text")
        return row

    def lesson(self, conn, text_id, lesson_id) -> dict:
        lesson = lessons.get(conn, lesson_id)
        if lesson is None or lesson["text_id"] != text_id:
            raise HTTPException(status_code=404, detail="no such lesson")
        return lesson

    def current_lesson(self, request, conn, text_id) -> dict | None:
        """The lesson `?lesson=` names, else the text's first; None when it has none."""
        available = lessons.for_text(conn, text_id)
        wanted = request.query_params.get("lesson", "")
        return next((x for x in available if str(x["id"]) == wanted), available[0] if available else None)

    def respond(self, request, conn, text_id, lesson, region, context, status=200, push=None):
        """Render `region`'s template for htmx (pushing `push` as the URL), else the shell with that region's context in place."""
        text = self.text(conn, text_id)
        ctx = {"request": request, "text": text, "base": f"/texts/{text_id}", "lesson": lesson,
               "lesson_base": f"/texts/{text_id}/lessons/{lesson['id']}" if lesson else None, **context}
        if is_fragment(request):
            html = self.templates.get_template(f"admin/{region}.html").render(ctx).strip()
            return HTMLResponse(html, status_code=status, headers={"HX-Push-Url": push} if push else {})
        for marker, build in self.regions.items():
            if marker not in ctx:
                ctx = {**build(request, conn, text_id, lesson), **ctx}
        return self.templates.TemplateResponse(request, "admin/shell.html", ctx, status_code=status)

    def tab_context(self, request, conn, text_id, lesson, tab, **state) -> dict:
        rows = self.tabs[tab](request, conn, text_id, lesson) if lesson else {}
        return {**TAB_STATE, "tab": tab, "counts": tab_counts(conn, text_id, lesson) if lesson else {}, **rows, **state}

    def tab(self, request, conn, text_id, lesson, tab, status=200, push=None, **state):
        """The tab card: the tab bar with its counts and the active tab."""
        return self.respond(request, conn, text_id, lesson, "tabs", self.tab_context(request, conn, text_id, lesson, tab, **state), status, push)

    def mutate(self, conn, text_id, change, write=True):
        """Run `change` and commit, rewriting the text's annotation and lesson files. A validation error rolls back; its message is returned."""
        try:
            result = change()
        except ERRORS as e:
            conn.rollback()
            return None, str(e)
        conn.commit()
        if write:
            annotation_files.write_file(conn, text_id, self.data_dir)
            lesson_files.write_files(conn, text_id, self.data_dir)
        return result, None

    def tab_mutate(self, request, conn, text_id, lesson, tab, change, form, submitted=None, write=True, **on_error):
        """A tab action: the tab re-rendered, or on a validation error the same tab with the message at `form` and status 422."""
        _, message = self.mutate(conn, text_id, change, write)
        if message is None:
            return self.tab(request, conn, text_id, lesson, tab)
        error, kept = {"form": form, "message": message}, {"form": form, **(submitted or {})}
        return self.tab(request, conn, text_id, lesson, tab, 422, error=error, submitted=kept, **on_error)
