"""The one assembled structure every student-facing presentation renders from (design.md, "Modes").

`assemble` joins the body, its stored readings, traditional forms, the master,
the text facts, optionally one lesson, and the learner's state.
"""

from opencc import OpenCC

from . import annotations, db, lessons, progress
from .texts import HAN

_S2T = OpenCC("s2t")


def traditional(body: str) -> list[str]:
    """Traditional form per position: the whole body through s2t (phrase-aware) when the length holds, else character by character."""
    converted = _S2T.convert(body)
    return list(converted) if len(converted) == len(body) else [_S2T.convert(ch) for ch in body]


def spans_of(body: str, surface: str) -> list[list[int]]:
    """Every occurrence of `surface` as [start, end), overlapping ones included, in order."""
    spans, start = [], body.find(surface)
    while start >= 0:
        spans.append([start, start + len(surface)])
        start = body.find(surface, start + 1)
    return spans


def choose_highlight(words) -> list[dict]:
    """Non-overlapping word spans for rendering: leftmost first, longest on a tie."""
    candidates = sorted(((s, e, w["surface"]) for w in words for s, e in w["spans"]), key=lambda t: (t[0], t[0] - t[1]))
    chosen, reach = [], 0
    for start, end, surface in candidates:
        if start >= reach:
            chosen.append({"start": start, "end": end, "surface": surface})
            reach = end
    return chosen


def assemble(conn, text_id, lesson_id=None, learner_id=progress.LEARNER) -> dict:
    """With a lesson: its selections, expansions and notes. Without: every text word, and no study list."""
    text = db.get_text(conn, text_id)
    body = text["body"]
    facts, states = annotations.load(conn, text_id), progress.current(conn, learner_id)
    lesson = lessons.load(conn, lesson_id) if lesson_id is not None else None
    stored = {r["position"]: r for r in facts["readings"]}
    master = {c["char"]: c for c in db.lookup_characters(conn, db.unique_characters(body))}
    fact = {c["char"]: c for c in facts["characters"]}
    selected = {c["char"] for c in lesson["characters"]} if lesson else set()
    trad = traditional(body)
    state = lambda kind, key: states.get((kind, key), "unrecognized")  # noqa: E731

    chars = []
    for i, ch in enumerate(body):
        if not HAN.fullmatch(ch):
            chars.append({"position": i, "char": ch, "han": False})
            continue
        m, f, r = master[ch], fact.get(ch, {}), stored.get(i)
        chars.append({
            "position": i, "char": ch, "han": True,
            "pinyin": r["pinyin"] if r else None, "source": r["origin"] if r else "none", "traditional": trad[i],
            "hsk_level": f.get("hsk_level") or m.get("hsk_level"), "hsk_edition": m.get("hsk_edition"),
            "gloss": f.get("gloss") or m.get("gloss"), "in_master": m["found"],
            "study": ch in selected, "state": state("character", ch),
        })
    first = {}
    for c in chars:
        if c["han"]:
            first.setdefault(c["char"], c)

    def word(w):
        return {"surface": w["surface"], "pinyin": w["pinyin"], "hsk_level": w["hsk_level"], "gloss": w["gloss"],
                "meanings": w["meanings"][:3], "linked": w["word_id"] is not None, "state": state("word", w["surface"])}

    words = [dict(word(w), spans=spans_of(body, w["surface"])) for w in facts["words"] if lesson is None or w["surface"] in lesson["words"]]
    han = [c for c in chars if c["han"]]
    unique = {c["char"]: c["state"] for c in han}
    return {
        "text": {k: text[k] for k in ("id", "title", "author", "period", "tags", "notes")},
        "lesson": {"id": lesson["id"], "name": lesson["name"]} if lesson else None,
        "chars": chars,
        "words": words,
        "highlight": choose_highlight(words),
        "study": [{k: first[c["char"]][k] for k in ("char", "pinyin", "gloss", "hsk_level", "state")} for c in lesson["characters"]] if lesson else [],
        "expansions": [dict(word(e), char=e["char"]) for e in lesson["expansions"]] if lesson else [],
        "notes": [{"anchor": n["anchor"], "note": n["note"]} for n in lesson["notes"]] if lesson else [],
        "counts": {"chars": len(han), "unique": len(unique), **{s: sum(1 for v in unique.values() if v == s) for s in progress.STATES}},
    }
