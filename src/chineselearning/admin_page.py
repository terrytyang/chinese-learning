"""Assembles the admin text page: view state (lesson, filters), the body with its readings, lesson rows, candidates."""

from urllib.parse import urlencode

from . import annotations, db, lessons, progress
from .texts import HAN

FILTERS = ("cmin", "cmax", "cstate", "wmin", "wmax", "wstate")
EMPTY = {"characters": [], "words": set(), "expansions": [], "notes": []}


def view(request, conn, text_id) -> dict:
    """The selected lesson (default: lowest id), the candidate filters, and the query suffixes that preserve them."""
    available = lessons.for_text(conn, text_id)
    wanted = request.query_params.get("lesson", "")
    lesson = next((x for x in available if str(x["id"]) == wanted), available[0] if available else None)
    kept = {k: request.query_params[k] for k in FILTERS if request.query_params.get(k)}
    if lesson and lesson is not available[0]:
        kept = {"lesson": str(lesson["id"]), **kept}
    suffix = urlencode(kept)
    return {"lessons": available, "lesson": lesson, "lesson_empty": bool(lesson) and lessons.is_empty(conn, lesson["id"]),
            "kept": kept, "filters": {k: request.query_params.get(k, "") for k in FILTERS},
            "q": "?" + suffix if suffix else "", "qa": "&" + suffix if suffix else ""}


def passes(row, filters, prefix) -> bool:
    """Level range and state filters for a candidate list; a missing level counts as 0."""
    lo, hi, state = filters.get(prefix + "min") or "", filters.get(prefix + "max") or "", filters.get(prefix + "state") or ""
    level = row["hsk_level"] or 0
    return (not lo.isdigit() or level >= int(lo)) and (not hi.isdigit() or level <= int(hi)) and (not state or row["state"] == state)


def character_rows(conn, text_id, body=None) -> dict[str, dict]:
    """Every unique Han character of the text with its first reading, level (fact over master), glosses and state, in body order."""
    body = body or db.get_text(conn, text_id)["body"]
    facts, states = annotations.load(conn, text_id), progress.current(conn)
    fact = {c["char"]: c for c in facts["characters"]}
    first = {}
    for r in facts["readings"]:
        first.setdefault(r["char"], r["pinyin"])
    rows = {}
    for m in db.lookup_characters(conn, db.unique_characters(body)):
        ch, f = m["char"], fact.get(m["char"], {})
        rows[ch] = {"char": ch, "pinyin": first.get(ch), "in_master": m["found"], "hsk_level": f.get("hsk_level") or m.get("hsk_level"),
                    "fact_level": f.get("hsk_level"), "gloss": f.get("gloss"), "master_gloss": m.get("gloss"),
                    "state": states.get(("character", ch), "unrecognized")}
    return rows


def candidate_characters(conn, text_id, lesson_id, filters) -> list[dict]:
    selected = {c["char"] for c in lessons.load(conn, lesson_id)["characters"]}
    return [r for ch, r in character_rows(conn, text_id).items() if ch not in selected and passes(r, filters, "c")]


def word_rows(conn, text_id, lesson_words) -> list[dict]:
    states = progress.current(conn)
    rows = annotations.load(conn, text_id)["words"]
    for a in rows:
        a.update(state=states.get(("word", a["surface"]), "unrecognized"), selected=a["surface"] in lesson_words)
    return rows


def candidate_words(conn, text_id, lesson_id, filters) -> list[dict]:
    rows = word_rows(conn, text_id, lessons.load(conn, lesson_id)["words"])
    return [a for a in rows if not a["selected"] and passes(a, filters, "w")]


def context(request, conn, text_id, v) -> dict:
    """Everything text.html and its includes render."""
    text = db.get_text(conn, text_id)
    body, states = text["body"], progress.current(conn)
    stored = {r["position"]: r for r in annotations.load(conn, text_id)["readings"]}
    master = {c["char"]: c for c in db.lookup_characters(conn, db.unique_characters(body))}
    content = lessons.load(conn, v["lesson"]["id"]) if v["lesson"] else EMPTY
    chars = []
    for i, ch in enumerate(body):
        r = stored.get(i)
        if HAN.fullmatch(ch):
            chars.append({"position": i, "char": ch, "han": True, "pinyin": r["pinyin"] if r else None, "origin": r["origin"] if r else None,
                          "in_master": master[ch]["found"], "readings": master[ch].get("readings") or []})
        else:
            chars.append({"position": i, "char": ch, "han": False, "newline": ch == "\n"})
    rows = character_rows(conn, text_id, body)
    study = [rows[c["char"]] for c in content["characters"]]
    in_lesson = {s["char"] for s in study}
    words = word_rows(conn, text_id, content["words"])
    for e in content["expansions"]:
        e["state"] = states.get(("word", e["surface"]), "unrecognized")
    blocks = [s["char"] for s in study] + sorted({e["char"] for e in content["expansions"]} - in_lesson, key=body.find)
    return {
        **v, "text": text, "base": f"/texts/{text_id}", "chars": chars, "study": study,
        "candidate_chars": [r for ch, r in rows.items() if ch not in in_lesson and passes(r, v["filters"], "c")],
        "lesson_words": [a for a in words if a["selected"]],
        "candidate_words": [a for a in words if not a["selected"] and passes(a, v["filters"], "w")],
        "expansions": [(rows[ch], [e for e in content["expansions"] if e["char"] == ch]) for ch in blocks],
        "notes": content["notes"],
        "counts": {"unique": len(rows), "missing": sum(1 for r in rows.values() if not r["in_master"]), "words": len(words)},
    }
