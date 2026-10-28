"""Rows for the admin fragments: the text's lines and positions, its characters, its words, a lesson's extra words."""

from .. import annotations, db, lessons, progress, readings
from ..annotations import AnnotationError
from ..texts import HAN


def text_lines(conn, text_id, body) -> list[list[dict]]:
    """The body as lines of positions; a Han position carries its stored reading and the dictionary's readings."""
    stored = {r["position"]: r for r in annotations.load(conn, text_id)["readings"]}
    master = {c["char"]: c for c in db.lookup_characters(conn, db.unique_characters(body))}
    lines = [[]]
    for i, ch in enumerate(body):
        if ch == "\n":
            lines.append([])
        elif HAN.fullmatch(ch):
            r = stored.get(i)
            lines[-1].append({"position": i, "char": ch, "han": True, "pinyin": r["pinyin"] if r else None,
                              "in_master": master[ch]["found"], "readings": master[ch].get("readings") or []})
        else:
            lines[-1].append({"position": i, "char": ch, "han": False})
    return lines


def character_rows(conn, text_id, body=None) -> dict[str, dict]:
    """Every unique Han character of the text, in body order: first stored reading, level, gloss (the text's over the dictionary's), state."""
    body = body or annotations.body_of(conn, text_id)
    facts, states = annotations.load(conn, text_id), progress.current(conn)
    fact = {c["char"]: c for c in facts["characters"]}
    first = {}
    for r in facts["readings"]:
        first.setdefault(r["char"], r["pinyin"])
    out = {}
    for m in db.lookup_characters(conn, db.unique_characters(body)):
        ch, f = m["char"], fact.get(m["char"], {})
        out[ch] = {"char": ch, "pinyin": first.get(ch), "in_master": m["found"], "in_hsk": m.get("source") == "hsk", "hsk_level": m.get("hsk_level"),
                   "fact_gloss": f.get("gloss"), "gloss": f.get("gloss") or m.get("gloss"), "state": states.get(("character", ch), "unconfirmed")}
    return out


def summary(rows) -> str:
    """The text block's line: characters, those outside HSK (supplement or missing), those still without a gloss."""
    missing = [r["char"] for r in rows.values() if not r["in_hsk"]]
    unglossed = sum(1 for r in rows.values() if not r["gloss"])
    listed = f" ({', '.join(missing)})" if missing else ""
    return f"{len(rows)} characters · {len(missing)} not in HSK{listed} · {unglossed} without a gloss"


def word_rows(conn, text_id, lesson_words) -> list[dict]:
    """The text's words in body order, each with its state and whether the lesson includes it."""
    states = progress.current(conn)
    rows = annotations.load(conn, text_id)["words"]
    for a in rows:
        a.update(state=states.get(("word", a["surface"]), "unconfirmed"), selected=a["surface"] in lesson_words)
    return rows


def with_state(conn, extra) -> list[dict]:
    """A lesson's extra words with their state and the page's row key."""
    states = progress.current(conn)
    for e in extra:
        e.update(state=states.get(("word", e["surface"]), "unconfirmed"), key=lessons.extra_key(e["anchor"], e["surface"]))
    return extra


def prefill_pinyin(conn, text_id, surface) -> str:
    """The second form's reading for a word the dictionary lacks: from the text's readings when it occurs there, else the
    characters' primary readings; blank when a character is unknown."""
    if surface in annotations.body_of(conn, text_id):
        return readings.default_pinyin(conn, text_id, surface) or ""
    try:
        return lessons.characters_pinyin(conn, surface)
    except AnnotationError:
        return ""
