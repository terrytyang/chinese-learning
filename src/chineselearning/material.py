"""The one assembled structure every student-facing presentation renders from (design.md, "Modes").

`assemble` joins the body, its resolved readings, traditional forms, the master,
the annotations and the learner's state. Presentations are templates over it.
"""

from opencc import OpenCC

from . import annotations, db, progress, readings
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


def assemble(conn, text_id, learner_id=progress.LEARNER) -> dict:
    text = db.get_text(conn, text_id)
    body = text["body"]
    current, states = annotations.load(conn, text_id), progress.current(conn, learner_id)
    resolved = {r["position"]: r for r in readings.readings_for(conn, text_id)}
    master = {c["char"]: c for c in db.lookup_characters(conn, db.unique_characters(body))}
    study_gloss = {a["char"]: a["gloss"] for a in current["characters"]}
    trad = traditional(body)
    state = lambda kind, key: states.get((kind, key), "unrecognized")  # noqa: E731

    chars = []
    for i, ch in enumerate(body):
        if not HAN.fullmatch(ch):
            chars.append({"position": i, "char": ch, "han": False})
            continue
        m = master[ch]
        chars.append({
            "position": i, "char": ch, "han": True,
            "pinyin": resolved[i]["pinyin"], "source": resolved[i]["source"], "traditional": trad[i],
            "hsk_level": m.get("hsk_level"), "hsk_edition": m.get("hsk_edition"),
            "gloss": study_gloss.get(ch) or m.get("gloss"), "in_master": m["found"],
            "study": ch in study_gloss, "state": state("character", ch),
        })
    first = {}
    for c in chars:
        if c["han"]:
            first.setdefault(c["char"], c)

    def word(w):
        return {"surface": w["surface"], "pinyin": w["pinyin"], "hsk_level": w["hsk_level"], "gloss": w["gloss"],
                "meanings": w["meanings"][:3], "linked": w["word_id"] is not None, "state": state("word", w["surface"])}

    words = [dict(word(w), spans=spans_of(body, w["surface"])) for w in current["words"]]
    han = [c for c in chars if c["han"]]
    unique = {c["char"]: c["state"] for c in han}
    return {
        "text": {k: text[k] for k in ("id", "title", "author", "period", "tags", "notes")},
        "chars": chars,
        "words": words,
        "highlight": choose_highlight(words),
        "study": [{"char": a["char"], "pinyin": first[a["char"]]["pinyin"], "gloss": first[a["char"]]["gloss"],
                   "hsk_level": first[a["char"]]["hsk_level"], "state": first[a["char"]]["state"]} for a in current["characters"]],
        "expansions": [dict(word(e), char=e["char"]) for e in current["expansions"]],
        "notes": [{"anchor": n["anchor"], "note": n["note"]} for n in current["notes"]],
        "counts": {"chars": len(han), "unique": len(unique), **{s: sum(1 for v in unique.values() if v == s) for s in progress.STATES}},
    }
