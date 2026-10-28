"""Emit per-character context for writing English glosses (docs/prompts/character-gloss.md).

Reads data/hsk.sql and, if present, data/reference/unihan-kdefinition.tsv. For each
character: char, readings (most common first), HSK level/edition, CC-CEDICT meanings of
its standalone entry per reading (from the master word table), and Unihan kDefinition.
Output is TSV, one character per line, sorted by level then character, so batches can be
cut by level. Compare the result against data/character-gloss.tsv with --missing to list
only characters that still have no gloss.

Usage:
  python3 tools/gloss_context.py --max-level 1 > build/gloss-context-1.tsv
  python3 tools/gloss_context.py --missing > build/gloss-context-todo.tsv
"""

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ("char", "readings", "level", "edition", "cedict", "kdefinition")


def load_master(sql_path):
    db = sqlite3.connect(":memory:")
    db.executescript(Path(sql_path).read_text(encoding="utf-8"))
    return db


def load_tsv(path, key=0, value=1):
    if not Path(path).exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        return {row[key]: row[value] for row in csv.reader(f, delimiter="\t") if row and not row[0].startswith("#")}


def context_rows(db, kdefinition):
    rows = []
    sql = "SELECT char, readings, hsk_level, hsk_edition, pinyin, meanings, alt_readings FROM character ORDER BY hsk_level, char"
    for char, readings, level, edition, pinyin, meanings, alt in db.execute(sql):
        cedict = []
        if meanings:
            cedict.append(f"{pinyin}: " + "; ".join(json.loads(meanings)[:6]))
        for r in json.loads(alt or "[]"):
            cedict.append(f"{r['pinyin']}: " + "; ".join(r["meanings"][:6]))
        rows.append({
            "char": char, "readings": " ".join(json.loads(readings)), "level": level, "edition": edition,
            "cedict": " | ".join(cedict), "kdefinition": kdefinition.get(char, ""),
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sql", default=ROOT / "data/hsk.sql")
    ap.add_argument("--kdefinition", default=ROOT / "data/reference/unihan-kdefinition.tsv")
    ap.add_argument("--gloss", default=ROOT / "data/character-gloss.tsv", help="existing glosses, for --missing")
    ap.add_argument("--min-level", type=int, default=1)
    ap.add_argument("--max-level", type=int, default=7)
    ap.add_argument("--missing", action="store_true", help="only characters without a gloss yet")
    args = ap.parse_args()
    db = load_master(args.sql)
    have = load_tsv(args.gloss) if args.missing else {}
    out = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    out.writerow(COLUMNS)
    n = 0
    for row in context_rows(db, load_tsv(args.kdefinition)):
        if args.min_level <= row["level"] <= args.max_level and row["char"] not in have:
            out.writerow([row[c] for c in COLUMNS])
            n += 1
    print(f"{n} characters", file=sys.stderr)


if __name__ == "__main__":
    main()
