"""Derive the master HSK tables from the reference dataset.

Reads hsk-original/hsk_vocab.sqlite (never modified) and writes data/hsk.sql,
a plain SQLite dump of two flat tables, `character` and `word`.

This is deliberately lossy. Rules:
  * One HSK level per word. The 2026 edition wins; otherwise the newest edition
    that lists the word. `hsk_edition` is 'latest' (2026) or 'old' (anything else).
  * Level 7 means the combined 7-9 band.
  * Readings are ordered by commonness (pypinyin), not source order. The first
    one is the primary and is denormalized into `pinyin` / `meanings`.
  * Characters get their readings from pypinyin; their level is the lowest level
    of any word containing them, with the same edition rule.
  * Traditional forms for characters are a majority vote over all words
    containing the character (positional, equal-length forms only); may be null.
  * `gloss` comes from `data/character-gloss.tsv` (curated, char<TAB>gloss); a character
    missing from that file gets null. The SQL output is the complete master.
  * Dropped: Wade-Giles, Bopomofo, Gwoyeu Romatzyh, numeric pinyin, radicals,
    classifiers, per-edition membership, import provenance.
  * IDs: character.id is the Unicode code point; word.id is the source entry id.
    Both are fixed by the committed SQL file from now on.

Usage:
  python3 tools/derive_hsk.py                       # full set -> data/hsk.sql
  python3 tools/derive_hsk.py --db build/hsk.sqlite # also repave a SQLite file
  python3 tools/derive_hsk.py --edition latest --max-level 3 --output build/hsk-1-3.sql

Filters apply to words; characters are those occurring in the kept words, with
their level and edition still computed from the whole source. Outputs are
always overwritten.
"""

import argparse
import csv
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

from pypinyin import Style, pinyin

EDITION = {"newest": "latest", "new": "old", "old": "old"}
PREFERENCE = ("newest", "new", "old")

SCHEMA = """\
CREATE TABLE character (
  id INTEGER PRIMARY KEY,          -- Unicode code point
  char TEXT NOT NULL UNIQUE,
  traditional TEXT,                -- best-effort, may be null
  pinyin TEXT NOT NULL,            -- most common reading
  readings TEXT NOT NULL,          -- JSON list of readings, most common first
  hsk_level INTEGER NOT NULL,      -- 1-7; 7 = bands 7-9
  hsk_edition TEXT NOT NULL,       -- 'latest' or 'old'
  gloss TEXT                       -- from data/character-gloss.tsv; null when not yet written
);
CREATE TABLE word (
  id INTEGER PRIMARY KEY,          -- source entry id, fixed by this file
  simplified TEXT NOT NULL UNIQUE,
  traditional TEXT NOT NULL,
  pinyin TEXT NOT NULL,            -- primary reading
  meanings TEXT NOT NULL,          -- JSON list, primary reading only
  readings TEXT NOT NULL,          -- JSON [{pinyin, traditional, meanings}], primary first
  pos TEXT,                        -- comma-separated source part-of-speech codes
  frequency_rank INTEGER,          -- lower is more common
  hsk_level INTEGER NOT NULL,
  hsk_edition TEXT NOT NULL
);
CREATE INDEX word_hsk_level ON word (hsk_level);
CREATE INDEX character_hsk_level ON character (hsk_level);
"""


def normalize(py):
    return re.sub(r"\s+", " ", py.strip().lower()).replace("u:", "ü")


def pick_level(levels_by_scheme):
    """levels_by_scheme: {scheme: min_level}. Returns (level, edition)."""
    for scheme in PREFERENCE:
        if scheme in levels_by_scheme:
            return levels_by_scheme[scheme], EDITION[scheme]
    raise ValueError("no level")


def load_glosses(path):
    """char -> gloss from the curated TSV; '#' lines skipped; duplicates and bad lines are errors."""
    glosses = {}
    if not path or not Path(path).exists():
        return glosses
    with open(path, encoding="utf-8", newline="") as f:
        for n, row in enumerate(csv.reader(f, delimiter="\t"), 1):
            if not row or row[0].startswith("#"):
                continue
            if len(row) != 2 or not row[1].strip():
                raise SystemExit(f"{path}:{n}: expected char<TAB>gloss")
            if row[0] in glosses:
                raise SystemExit(f"{path}:{n}: duplicate character {row[0]}")
            glosses[row[0]] = row[1].strip()
    return glosses


def derive(source_path, keep_edition="all", max_level=None, gloss_path=None):
    src = sqlite3.connect(f"file:{Path(source_path).resolve()}?mode=ro", uri=True)
    q = lambda sql, *a: src.execute(sql, a).fetchall()

    levels = defaultdict(dict)  # entry_id -> {scheme: min level}
    for entry_id, scheme, level in q("SELECT entry_id, scheme, min(level) FROM hsk_entry_level GROUP BY entry_id, scheme"):
        levels[entry_id][scheme] = level
    pos = defaultdict(list)
    for entry_id, code in q("SELECT entry_id, pos FROM hsk_entry_pos ORDER BY entry_id, pos_seq"):
        pos[entry_id].append(code)
    meanings = defaultdict(list)
    for form_id, m in q("SELECT form_id, meaning FROM hsk_meaning ORDER BY form_id, meaning_seq"):
        meanings[form_id].append(m)
    forms = defaultdict(list)
    for form_id, entry_id, trad, py in q("SELECT form_id, entry_id, traditional, pinyin FROM hsk_form ORDER BY entry_id, form_seq"):
        forms[entry_id].append(dict(pinyin=py, traditional=trad, meanings=meanings[form_id]))
    entries = q("SELECT entry_id, simplified, frequency FROM hsk_entry ORDER BY entry_id")

    # Traditional form per character: majority vote over every form of every word containing it
    # (equal-length forms only), ties broken by the more common word. Single-character entries
    # alone are unreliable: they carry rare variants such as 甦 for 苏 or 亱 for 夜.
    votes = defaultdict(lambda: defaultdict(lambda: [0, 10**9]))
    for entry_id, simp, freq in entries:
        for form in forms[entry_id]:
            if len(form["traditional"]) != len(simp):
                continue
            for ch, tr in zip(simp, form["traditional"]):
                v = votes[ch][tr]
                v[0] += 1
                v[1] = min(v[1], freq or 10**9)
    traditional = {ch: max(c, key=lambda t: (c[t][0], -c[t][1])) for ch, c in votes.items()}

    # Primary reading per word: the form matching pypinyin's reading of the whole word; among
    # equals, lowercase (common) beats capitalized (proper noun), and the form whose traditional
    # agrees with the per-character vote wins (後 over 后 for hòu).
    def reading_key(simp, expected):
        def key(form):
            return (
                normalize(form["pinyin"]) != expected,
                form["pinyin"][:1].isupper(),
                sum(a != traditional.get(ch) for ch, a in zip(simp, form["traditional"]))
                if len(form["traditional"]) == len(simp) else len(simp),
            )
        return key

    words, stats = [], dict(reordered=0, unmatched=[], polyphones=0)
    for entry_id, simp, freq in entries:
        level, edition = pick_level(levels[entry_id])
        readings = forms[entry_id]
        if len(readings) > 1:
            stats["polyphones"] += 1
            expected = normalize(" ".join(s[0] for s in pinyin(simp, style=Style.TONE)))
            ordered = sorted(readings, key=reading_key(simp, expected))
            if not any(normalize(r["pinyin"]) == expected for r in readings):
                stats["unmatched"].append((simp, expected, [r["pinyin"] for r in readings]))
            if ordered[0] is not readings[0]:
                stats["reordered"] += 1
            readings = ordered
        primary = readings[0]
        words.append(dict(
            id=entry_id, simplified=simp, traditional=primary["traditional"], pinyin=primary["pinyin"],
            meanings=json.dumps(primary["meanings"], ensure_ascii=False),
            readings=json.dumps(readings, ensure_ascii=False),
            pos=",".join(pos[entry_id]) or None, frequency_rank=freq,
            hsk_level=level, hsk_edition=edition,
        ))

    char_levels = defaultdict(dict)  # char -> {scheme: min level over ALL words containing it}
    for w in words:
        for ch in w["simplified"]:
            for scheme, level in levels[w["id"]].items():
                char_levels[ch][scheme] = min(level, char_levels[ch].get(scheme, 99))
    words = [w for w in words
             if (keep_edition == "all" or w["hsk_edition"] == keep_edition)
             and (max_level is None or w["hsk_level"] <= max_level)]
    kept = {ch for w in words for ch in w["simplified"]}
    glosses = load_glosses(gloss_path)
    unknown = sorted(set(glosses) - set(char_levels))
    if unknown:
        raise SystemExit(f"{gloss_path}: characters not in the master: {''.join(unknown)}")
    characters = []
    for ch in sorted(kept):
        level, edition = pick_level(char_levels[ch])
        readings = pinyin(ch, style=Style.TONE, heteronym=True)[0]
        characters.append(dict(
            id=ord(ch), char=ch, traditional=traditional.get(ch), pinyin=readings[0],
            readings=json.dumps(readings, ensure_ascii=False), hsk_level=level, hsk_edition=edition,
            gloss=glosses.get(ch),
        ))
    stats["glossed"] = sum(1 for c in characters if c["gloss"])
    src.close()
    return characters, words, stats


def load(characters, words, path=":memory:"):
    """Create the two tables at `path` (repaved if it is a file) and return the connection."""
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).unlink(missing_ok=True)
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    db.executemany("INSERT INTO character VALUES (:id,:char,:traditional,:pinyin,:readings,:hsk_level,:hsk_edition,:gloss)", characters)
    db.executemany("INSERT INTO word VALUES (:id,:simplified,:traditional,:pinyin,:meanings,:readings,:pos,:frequency_rank,:hsk_level,:hsk_edition)", words)
    db.commit()
    return db


def write_sql(db, output_path):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as f:
        f.write("-- Generated by tools/derive_hsk.py from hsk-original/hsk_vocab.sqlite. Do not edit.\n")
        for line in db.iterdump():
            f.write(line + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default="hsk-original/hsk_vocab.sqlite", help="reference dataset (read-only)")
    ap.add_argument("--output", default="data/hsk.sql", help="SQL dump to write (overwritten)")
    ap.add_argument("--db", help="also repave a SQLite file with the same tables")
    ap.add_argument("--edition", choices=("all", "latest", "old"), default="all",
                    help="keep only words of this edition (default: all)")
    ap.add_argument("--max-level", type=int, choices=range(1, 8), metavar="1-7",
                    help="keep only words at or below this level")
    ap.add_argument("--gloss", default="data/character-gloss.tsv", help="curated character glosses (char<TAB>gloss)")
    args = ap.parse_args()
    characters, words, stats = derive(args.source, args.edition, args.max_level, args.gloss)
    db = load(characters, words, args.db or ":memory:")
    write_sql(db, args.output)
    db.close()
    where = args.output + (f" and {args.db}" if args.db else "")
    print(f"characters: {len(characters)} ({stats['glossed']} glossed)   words: {len(words)}   -> {where}")
    print(f"polyphone words: {stats['polyphones']}, primary reading reordered: {stats['reordered']}, "
          f"no pypinyin match (source order kept): {len(stats['unmatched'])}")
    for simp, expected, have in stats["unmatched"][:15]:
        print(f"  {simp}: pypinyin={expected!r} source={have}")


if __name__ == "__main__":
    main()
