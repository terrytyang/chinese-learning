"""The dictionary page (/dictionary): every character and word under filters, the learner's state, inline edit of an HSK
character's gloss or a supplement entry, and adding a supplement entry. Matches docs/mockups/dictionary-page.dc.html."""

from urllib.parse import urlencode

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse

from .. import gloss_file, progress, supplement
from .. import pinyin as pinyin_
from .common import ERRORS, filters_of, is_fragment, level_bounds

DEFAULTS = {"q": "", "kind": "all", "source": "all", "min": "1", "max": "7", "state": "any", "nogloss": ""}
KIND_OPTIONS = (("all", "all"), ("character", "characters"), ("word", "words"))
SOURCE_OPTIONS = (("all", "all"), ("hsk", "HSK"), ("supplement", "supplement"))
STATE_OPTIONS = ("any", *progress.STATES)
CAP = 200
NOT_EDITABLE = "an HSK word is not editable; HSK meanings are read-only"
# One query over both tables: a character's gloss, a word's meanings joined (a supplement word's is [gloss] or []).
ENTRIES = """FROM (SELECT char AS item, 'character' AS kind, pinyin, hsk_level AS level, source, gloss FROM character
                   UNION ALL
                   SELECT simplified, 'word', pinyin, hsk_level, source, (SELECT group_concat(value, '; ') FROM json_each(meanings)) FROM word) d
             LEFT JOIN progress.progress p ON p.learner_id = ? AND p.kind = d.kind AND p.key = d.item"""
COLUMNS = "d.item, d.kind, d.pinyin, d.level, d.source, d.gloss, coalesce(p.state, 'unconfirmed') AS state"


def where(filters) -> tuple[str, list]:
    """The WHERE clause for the filters; `q` is a case-insensitive substring of the item, the pinyin or the gloss."""
    lo, hi = level_bounds(filters)
    clauses, params = ["d.level BETWEEN ? AND ?"], [lo, hi]
    for key, options in (("kind", KIND_OPTIONS), ("source", SOURCE_OPTIONS)):
        if filters[key] in dict(options) and filters[key] != "all":
            clauses.append(f"d.{key} = ?")
            params.append(filters[key])
    if filters["state"] in progress.STATES:
        clauses.append("coalesce(p.state, 'unconfirmed') = ?")
        params.append(filters["state"])
    if filters["nogloss"] == "1":
        clauses.append("coalesce(d.gloss, '') = ''")
    if filters["q"].strip():
        like = "%" + filters["q"].strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        clauses.append("(d.item LIKE ? ESCAPE '\\' OR d.pinyin LIKE ? ESCAPE '\\' OR d.gloss LIKE ? ESCAPE '\\')")
        params += [like, like, like]
    return " WHERE " + " AND ".join(clauses), params


def entries(conn, filters, learner_id=progress.LEARNER) -> tuple[list[dict], int]:
    """(the rows shown, up to the cap, by level then item; the total under the filters)."""
    clause, params = where(filters)
    total = conn.execute(f"SELECT count(*) {ENTRIES}{clause}", [learner_id, *params]).fetchone()[0]
    rows = conn.execute(f"SELECT {COLUMNS} {ENTRIES}{clause} ORDER BY d.level, d.item LIMIT ?", [learner_id, *params, CAP]).fetchall()
    return [dict(r) for r in rows], total


def entry(conn, item, learner_id=progress.LEARNER) -> dict:
    row = conn.execute(f"SELECT {COLUMNS} {ENTRIES} WHERE d.item = ?", (learner_id, item)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="no such entry")
    return dict(row)


def shown_label(rows, total) -> str:
    return f"{CAP} of {total:,} shown — narrow the filters" if total > len(rows) else f"{len(rows):,} shown"


def header(conn) -> str:
    """Characters (all sources), HSK words, supplement entries, and entries without a gloss (characters and supplement words)."""
    one = lambda sql: conn.execute(sql).fetchone()[0]  # noqa: E731
    characters, hsk_words = one("SELECT count(*) FROM character"), one("SELECT count(*) FROM word WHERE source = 'hsk'")
    entries = one("SELECT count(*) FROM character WHERE source = 'supplement'") + one("SELECT count(*) FROM word WHERE source = 'supplement'")
    unglossed = one("SELECT count(*) FROM character WHERE gloss IS NULL") + one("SELECT count(*) FROM word WHERE source = 'supplement' AND json_array_length(meanings) = 0")
    return f"{characters:,} characters · {hsk_words:,} HSK words · {entries:,} supplement entries · {unglossed:,} without a gloss"


def file_level(data_dir, item) -> int | None:
    """A supplement entry's level as the file says it: None when derived."""
    for line in supplement.file_path(data_dir).read_text(encoding="utf-8").split("\n"):
        e = supplement.parse_line(line)
        if e and e["item"] == item:
            return e["level"]
    return None


def prefill_pinyin(conn, item) -> str:
    """For the add form: each character's primary reading from the dictionary, else pypinyin's; blank when one has neither."""
    marks = ",".join("?" * len(item))
    known = dict(conn.execute(f"SELECT char, pinyin FROM character WHERE char IN ({marks})", list(item)).fetchall())
    parts = [known.get(ch) or (pinyin_.readings_of(ch) or [""])[0] for ch in item]
    return " ".join(parts) if all(parts) else ""


def routes(r, admin, connection):
    templates = admin.templates

    def fragment(name, ctx, status=200):
        return HTMLResponse(templates.get_template(f"admin/dictionary_{name}.html").render(ctx).strip(), status_code=status)

    def rows_context(conn, filters, **state) -> dict:
        rows, total = entries(conn, filters)
        query = "?" + urlencode({k: v for k, v in filters.items() if v})
        return {"rows": rows, "filters": filters, "q": query, "shown": shown_label(rows, total), "STATES": progress.STATES, **state}

    def page(request, conn):
        """The shell: the header counts, the filter form, the rows for the URL's filters, the add card."""
        filters, _ = filters_of(request, DEFAULTS, checkboxes=("nogloss",))
        ctx = {**rows_context(conn, filters), "header": header(conn), "kind_options": KIND_OPTIONS, "source_options": SOURCE_OPTIONS,
               "state_options": STATE_OPTIONS, "lookup": None, "added": None}
        return templates.TemplateResponse(request, "admin/dictionary.html", ctx)

    def row(request, conn, item, status=200, editing=False, error=None, submitted=None):
        e = entry(conn, item)
        if submitted and submitted.get("form") == "edit":
            level = submitted["level"]
        else:  # a supplement word's level as the file says it (None = derived); a character's is its row's
            level = file_level(admin.data_dir, item) if e["source"] == "supplement" and e["kind"] == "word" else e["level"]
        ctx = {"request": request, "r": e, "editing": editing, "form_level": level, "STATES": progress.STATES,
               "error": error, "submitted": submitted}
        return fragment("row", ctx, status)

    def add_card(request, conn, status=200, lookup=None, added=None, error=None, submitted=None, oob_rows=False):
        ctx = {"request": request, "lookup": lookup, "added": added, "error": error, "submitted": submitted, "oob": False}
        if oob_rows:
            ctx.update(rows_context(conn, {**DEFAULTS, "q": added}, oob=True, fragment=True))
        return fragment("add", ctx, status)

    @r.get("/dictionary", response_class=HTMLResponse)
    def index(request: Request, conn=Depends(connection)):
        return page(request, conn)

    @r.get("/dictionary/rows", response_class=HTMLResponse)
    def rows(request: Request, conn=Depends(connection)):
        """The results card for the filters in the query string; a non-htmx request gets the whole page."""
        if not is_fragment(request):
            return page(request, conn)
        filters, _ = filters_of(request, DEFAULTS, checkboxes=("nogloss",))
        return fragment("rows", {"request": request, **rows_context(conn, filters, oob=False, fragment=True)})

    @r.get("/dictionary/row/{item}", response_class=HTMLResponse)
    def show(request: Request, item: str, edit: str = "", conn=Depends(connection)):
        """The row; `?edit=1` opens its inline edit (an HSK word has none)."""
        if edit and entry(conn, item)["source"] == "hsk" and len(item) > 1:
            return row(request, conn, item, 422, error={"form": "edit", "message": NOT_EDITABLE})
        return row(request, conn, item, editing=bool(edit))

    @r.post("/dictionary/row/{item}", response_class=HTMLResponse)
    def save(request: Request, item: str, pinyin: str = Form(""), gloss: str = Form(""), level: str = Form(""), conn=Depends(connection)):
        """An HSK character's gloss goes to data/character-gloss.tsv, a supplement entry's pinyin, gloss and level to data/supplement.tsv."""
        e = entry(conn, item)
        submitted = {"form": "edit", "pinyin": pinyin, "gloss": gloss, "level": level}
        if e["source"] == "hsk" and e["kind"] == "word":
            return row(request, conn, item, 422, error={"form": "edit", "message": NOT_EDITABLE})
        try:
            if e["source"] == "hsk":
                gloss_file.update(conn, admin.data_dir, item, gloss)
            else:
                supplement.update(conn, admin.data_dir, item, pinyin, gloss, level)
        except ERRORS as err:
            conn.rollback()
            return row(request, conn, item, 422, editing=True, error={"form": "edit", "message": str(err)}, submitted=submitted)
        conn.commit()
        return row(request, conn, item)

    @r.post("/dictionary/state", response_class=HTMLResponse)
    def set_state(request: Request, item: str = Form(""), state: str = Form(""), conn=Depends(connection)):
        """The four state buttons: origin `manual`; the response is the row."""
        item = item.strip()
        entry(conn, item)
        try:
            progress.set_state(conn, "character" if len(item) == 1 else "word", item, state, "manual")
        except ERRORS as err:
            conn.rollback()
            return row(request, conn, item, 422, error={"form": "state", "message": str(err)})
        conn.commit()
        return row(request, conn, item)

    @r.post("/dictionary/lookup", response_class=HTMLResponse)
    def lookup(request: Request, item: str = Form(""), conn=Depends(connection)):
        """Look up: an entry already in the dictionary is pointed at; any other gets the details form."""
        item = item.strip()
        if not item:
            return add_card(request, conn, 422, error={"form": "lookup", "message": "a character or word is required"})
        if supplement.source_of(conn, item):
            return add_card(request, conn, lookup={"item": item, "found": True})
        return add_card(request, conn, lookup={"item": item, "found": False, "pinyin": prefill_pinyin(conn, item)})

    @r.post("/dictionary/add", response_class=HTMLResponse)
    def add(request: Request, item: str = Form(""), pinyin: str = Form(""), gloss: str = Form(""), level: str = Form(""), conn=Depends(connection)):
        """The details form makes the supplement entry; the rows region is re-rendered for the item, out of band."""
        item = item.strip()
        submitted = {"form": "add", "pinyin": pinyin, "gloss": gloss, "level": level}
        try:
            supplement.add(conn, admin.data_dir, item, pinyin, gloss, level)
        except ERRORS as err:
            conn.rollback()
            return add_card(request, conn, 422, lookup={"item": item, "found": False, "pinyin": pinyin}, error={"form": "add", "message": str(err)}, submitted=submitted)
        conn.commit()
        return add_card(request, conn, added=item, oob_rows=True)
