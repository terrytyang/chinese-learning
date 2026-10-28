"""Reading resolution, used by intake to fill `text_reading` and by the reset of a character's readings.

Pages never resolve: they read the stored rows. Order: a stored reading > the reading
of a text word covering the position (leftmost-longest) > the dictionary's primary reading > none.
"""

from .texts import HAN


def syllables(pinyin, length):
    """A word reading split per character, or None when the syllable count differs."""
    parts = (pinyin or "").split()
    return parts if len(parts) == length else None


def resolve(conn, text_id, ignore_stored=()) -> list[dict]:
    """{position, char, pinyin, source} for every Han position; stored rows of the characters in `ignore_stored` are skipped."""
    body = conn.execute("SELECT body FROM text WHERE id = ?", (text_id,)).fetchone()[0]
    chars = sorted(set(HAN.findall(body)))
    primary = dict(conn.execute(f"SELECT char, pinyin FROM character WHERE char IN ({','.join('?' * len(chars))})", chars).fetchall())
    stored = {r["position"]: r["pinyin"] for r in conn.execute("SELECT position, char, pinyin FROM text_reading WHERE text_id = ?", (text_id,)) if r["char"] not in ignore_stored}
    cover = {}  # position -> (start, -length, surface, pinyin): min() picks leftmost, then longest
    sql = "SELECT t.surface, coalesce(t.pinyin, w.pinyin) FROM text_word t JOIN word w ON w.id = t.word_id WHERE t.text_id = ?"
    for surface, pinyin in conn.execute(sql, (text_id,)).fetchall():
        start = body.find(surface)
        while start >= 0:
            for p in range(start, start + len(surface)):
                cover[p] = min(cover.get(p, (start, -len(surface), surface, pinyin)), (start, -len(surface), surface, pinyin))
            start = body.find(surface, start + 1)
    result = []
    for i, ch in enumerate(body):
        if not HAN.fullmatch(ch):
            continue
        parts = syllables(cover[i][3], -cover[i][1]) if i in cover else None
        if i in stored:
            pinyin, source = stored[i], "stored"
        elif parts:
            pinyin, source = parts[i - cover[i][0]], f"word:{cover[i][2]}"
        elif ch in primary:
            pinyin, source = primary[ch], "primary"
        else:
            pinyin, source = None, "none"
        result.append({"position": i, "char": ch, "pinyin": pinyin, "source": source})
    return result


def default_pinyin(conn, text_id, surface) -> str | None:
    """A word's reading from the text's readings at its first occurrence (the prefill for a new supplement word); None if any is unknown."""
    body = conn.execute("SELECT body FROM text WHERE id = ?", (text_id,)).fetchone()[0]
    start = body.find(surface)
    at = {r["position"]: r["pinyin"] for r in resolve(conn, text_id)}
    parts = [at.get(p) for p in range(start, start + len(surface))]
    return " ".join(parts) if all(parts) else None


def by_character(rows) -> dict[str, list[dict]]:
    """Distinct {pinyin, source} pairs per character, in the rows' order."""
    out: dict[str, list[dict]] = {}
    for r in rows:
        pair = {"pinyin": r["pinyin"], "source": r["source"]}
        if pair not in out.setdefault(r["char"], []):
            out[r["char"]].append(pair)
    return out
