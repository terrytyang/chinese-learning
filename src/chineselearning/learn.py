"""Student-facing pages under /learn: the list and the plain reader, both rendered from material.assemble."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from . import db, material

TINTS = ("none", "level", "state")


def paragraphs(m: dict) -> list[list[list[dict]]]:
    """The body as paragraphs → lines → segments {word, chars}; a segment carries the highlight it lies in, or None."""
    by_start = {h["start"]: h for h in m["highlight"]}
    paras, line, seg, active = [[]], [], None, None
    for c in m["chars"]:
        if c["char"] == "\n":
            if seg:
                line.append(seg)
            if line:
                paras[-1].append(line)
            elif paras[-1]:
                paras.append([])
            line, seg = [], None
            continue
        if active and c["position"] >= active["end"]:
            active = None
        active = by_start.get(c["position"], active)
        if seg is None or seg["word"] is not active:
            if seg:
                line.append(seg)
            seg = {"word": active, "chars": []}
        seg["chars"].append(c)
    if seg:
        line.append(seg)
    if line:
        paras[-1].append(line)
    return [p for p in paras if p]


def router(templates, connection) -> APIRouter:
    r = APIRouter()

    @r.get("/learn", response_class=HTMLResponse)
    def index(request: Request, conn=Depends(connection)):
        rows = [dict(t, counts=material.assemble(conn, t["id"])["counts"]) for t in db.list_texts(conn)]
        return templates.TemplateResponse(request, "learn.html", {"texts": rows})

    @r.get("/learn/{text_id}", response_class=HTMLResponse)
    def reader(
        request: Request, text_id: int, pinyin: int = 0, traditional: int = 0, gloss: int = 0, words: int = 0,
        tint: str = "none", show_mastered: int = 0, conn=Depends(connection),
    ):
        if db.get_text(conn, text_id) is None:
            raise HTTPException(status_code=404, detail="没有这篇课文")
        m = material.assemble(conn, text_id)
        options = {"pinyin": pinyin == 1, "traditional": traditional == 1, "gloss": gloss == 1, "words": words == 1,
                   "tint": tint if tint in TINTS else "none", "show_mastered": show_mastered == 1}
        visible = lambda rows: [x for x in rows if options["show_mastered"] or x["state"] != "mastered"]  # noqa: E731
        context = {
            "m": m, "o": options, "paragraphs": paragraphs(m),
            "by_surface": {w["surface"]: w for w in m["words"]},
            "lists": {"words": visible(m["words"]), "study": visible(m["study"]), "expansions": visible(m["expansions"])},
        }
        return templates.TemplateResponse(request, "reader.html", context)

    return r
