"""Explicit, one-time sampling for the trial inventory; never run during rebuilds."""

import argparse
from collections import Counter
import json
from pathlib import Path
import random
import sqlite3

SCHEME = "newest"
SCHEME_LABEL = "HSK 3.0 (2026 syllabus)"
RANDOM_SEED = 20261014
PER_BAND = 20
SELECTION_METADATA = {
    "scheme": SCHEME,
    "label": SCHEME_LABEL,
    "random_seed": RANDOM_SEED,
    "per_band": PER_BAND,
    "sampling": "Python random.Random.sample over Unicode-sorted candidates, bands 1–7",
}


def generate_selection(source_path):
    rng = random.Random(RANDOM_SEED)
    records = []
    source = sqlite3.connect(Path(source_path).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        for level in range(1, 8):
            candidates = sorted(row[0] for row in source.execute(
                "SELECT char FROM hsk_char_min_level WHERE scheme = ? AND level = ?",
                (SCHEME, level),
            ))
            for char in rng.sample(candidates, PER_BAND):
                records.append({
                    "simplified": char, "english_gloss": None, "usage_note": None,
                    "hsk_level": level,
                })
    finally:
        source.close()
    return {"inventory": dict(SELECTION_METADATA), "characters": records}


def validate_manifest(spec):
    if spec["inventory"] != SELECTION_METADATA:
        raise ValueError("Inventory metadata must match the fixed trial selection")
    records = spec["characters"]
    if not isinstance(records, list) or len(records) != 140:
        raise ValueError("Inventory must contain 140 characters")
    for record in records:
        if not isinstance(record, dict) or set(record) != {
            "simplified", "english_gloss", "usage_note", "hsk_level"
        }:
            raise ValueError("Invalid inventory character fields")
        if type(record["hsk_level"]) is not int or record["hsk_level"] not in range(1, 8):
            raise ValueError("Inventory band must be an integer from 1 to 7")
        if record["english_gloss"] is not None or record["usage_note"] is not None:
            raise ValueError("Inventory glosses and usage notes must remain null")
    if Counter(record["hsk_level"] for record in records) != dict.fromkeys(range(1, 8), 20):
        raise ValueError("Inventory must contain 20 characters per band")


def verify_source_bands(source, records):
    for record in records:
        actual = source.execute(
            "SELECT level FROM hsk_char_min_level WHERE scheme = ? AND char = ?",
            (SCHEME, record["simplified"]),
        ).fetchone()
        if actual != (record["hsk_level"],):
            raise ValueError(f"Inventory band disagrees with source: {record['simplified']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("hsk-original/hsk_vocab.sqlite"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    spec = generate_selection(args.source)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(spec, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
