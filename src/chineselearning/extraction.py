"""Explicit HSK extraction to versioned, self-contained UTF-8 JSON."""

import argparse
import json
import os
from pathlib import Path
import tempfile
import sqlite3

from chineselearning.hsk_source import open_source, traditional_candidate

FORMAT = "chineselearning-hsk-extraction"
VERSION = 1
READING_FIELDS = ("traditional", "pinyin", "numeric", "wadegiles", "bopomofo", "romatzyh")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fields(value, expected, context):
    require(isinstance(value, dict) and set(value) == set(expected), f"Invalid {context} fields")


def validate_settings(settings, schemes=None):
    fields(settings, ("scheme", "levels", "mode"), "selection")
    require(isinstance(settings["scheme"], str) and bool(settings["scheme"]), "Scheme must be nonempty text")
    require(settings["mode"] in ("exact", "cumulative"), "Mode must be exact or cumulative")
    levels = settings["levels"]
    require(isinstance(levels, list) and bool(levels), "Select at least one level")
    require(all(type(level) is int and level > 0 for level in levels), "Levels must be positive integers")
    require(len(set(levels)) == len(levels), "Duplicate selected levels")
    if schemes is not None:
        maximums = {s["code"]: s["max_level"] for s in schemes}
        require(settings["scheme"] in maximums, f"Unknown scheme: {settings['scheme']}")
        require(max(levels) <= maximums[settings["scheme"]], "Selected level exceeds scheme maximum")
    return {**settings, "levels": sorted(levels)}


def selected_levels(settings):
    """Exact is a union of tags; cumulative is 1..max(levels), inclusive."""
    return (settings["levels"] if settings["mode"] == "exact"
            else list(range(1, max(settings["levels"]) + 1)))


def select_entries(source, settings):
    levels = selected_levels(settings)
    placeholders = ",".join("?" for _ in levels)
    entries = source.execute(
        f"""SELECT entry_id, simplified FROM hsk_entry
            WHERE entry_id IN (SELECT entry_id FROM hsk_entry_level
                              WHERE scheme = ? AND level IN ({placeholders}))
            ORDER BY entry_id""",
        (settings["scheme"], *levels),
    ).fetchall()
    require(bool(entries), "Selection contains no vocabulary entries")
    return entries


def read_source(source, entries):
    """Read selected records, retaining source form/meaning and constituent order."""
    vocabulary = []
    for entry_id, simplified in entries:
        constituents = [r[0] for r in source.execute(
            "SELECT char FROM hsk_entry_char WHERE entry_id = ? ORDER BY position", (entry_id,)
        )]
        require(constituents == list(simplified), f"Source constituents disagree: {simplified}")
        memberships = [dict(scheme=scheme, level=level) for scheme, level in source.execute(
            "SELECT scheme, level FROM hsk_entry_level WHERE entry_id = ? ORDER BY tag_seq", (entry_id,)
        )]
        readings = []
        for row in source.execute(
            """SELECT form_id, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh
               FROM hsk_form WHERE entry_id = ? ORDER BY form_seq""", (entry_id,)
        ):
            readings.append(dict(zip(READING_FIELDS, row[1:]), meanings=[r[0] for r in source.execute(
                "SELECT meaning FROM hsk_meaning WHERE form_id = ? ORDER BY meaning_seq", (row[0],)
            )]))
        require(bool(readings), f"Source vocabulary has no readings: {simplified}")
        vocabulary.append(dict(source_entry_id=entry_id, simplified=simplified,
                               hsk_levels=memberships, readings=readings, constituents=constituents))
    characters = []
    for char in sorted({char for word in vocabulary for char in word["constituents"]}):
        characters.append(dict(
            simplified=char, traditional=traditional_candidate(source, char),
            english_gloss=None, usage_note=None,
            hsk_levels=[dict(scheme=scheme, level=level) for scheme, level in source.execute(
                "SELECT scheme, level FROM hsk_char_min_level WHERE char = ? ORDER BY scheme", (char,)
            )],
        ))
    return characters, vocabulary


def transform(settings, schemes, characters, vocabulary):
    return dict(format=FORMAT, version=VERSION, selection=settings, schemes=schemes,
                characters=characters, vocabulary=vocabulary)


def validate_document(spec):
    """Validate the interchange contract before publication or database construction."""
    fields(spec, ("format", "version", "selection", "schemes", "characters", "vocabulary"), "document")
    require(spec["format"] == FORMAT and type(spec["version"]) is int and spec["version"] == VERSION,
            "Unsupported extraction format/version")
    require(isinstance(spec["schemes"], list) and bool(spec["schemes"]), "Schemes must be a nonempty list")
    schemes = {}
    for scheme in spec["schemes"]:
        fields(scheme, ("code", "label", "max_level"), "scheme")
        require(all(isinstance(scheme[k], str) and scheme[k] for k in ("code", "label")), "Invalid scheme text")
        require(type(scheme["max_level"]) is int and scheme["max_level"] > 0, "Invalid scheme maximum")
        require(scheme["code"] not in schemes, "Duplicate scheme")
        schemes[scheme["code"]] = scheme["max_level"]
    validate_settings(spec["selection"], spec["schemes"])

    def memberships(records, unique=False):
        require(isinstance(records, list), "HSK memberships must be a list")
        seen = set()
        for record in records:
            fields(record, ("scheme", "level"), "membership")
            code, level = record["scheme"], record["level"]
            require(isinstance(code, str) and code in schemes, "Unknown membership scheme")
            require(type(level) is int and 1 <= level <= schemes[code], "Invalid membership level")
            require(not unique or code not in seen, "Duplicate character scheme")
            seen.add(code)

    require(isinstance(spec["characters"], list) and bool(spec["characters"]), "Characters must be a nonempty list")
    characters = set()
    for record in spec["characters"]:
        fields(record, ("simplified", "traditional", "english_gloss", "usage_note", "hsk_levels"), "character")
        char = record["simplified"]
        require(isinstance(char, str) and len(char) == 1, "Character must be one Unicode code point")
        require(char not in characters, f"Duplicate character: {char}")
        characters.add(char)
        traditional = record["traditional"]
        require(traditional is None or isinstance(traditional, str) and len(traditional) == 1,
                "Traditional character must be one code point or null")
        require(record["english_gloss"] is None, "Extracted character gloss must remain null")
        require(record["usage_note"] is None or isinstance(record["usage_note"], str), "Invalid usage note")
        memberships(record["hsk_levels"], unique=True)
    require(isinstance(spec["vocabulary"], list) and bool(spec["vocabulary"]), "Vocabulary must be a nonempty list")
    source_ids = set()
    for word in spec["vocabulary"]:
        fields(word, ("source_entry_id", "simplified", "hsk_levels", "readings", "constituents"), "vocabulary")
        source_id = word["source_entry_id"]
        require(source_id is None or type(source_id) is int and source_id > 0, "Invalid source entry ID")
        if source_id is not None:
            require(source_id not in source_ids, "Duplicate source entry ID")
            source_ids.add(source_id)
        require(isinstance(word["simplified"], str) and bool(word["simplified"]), "Vocabulary must be nonempty text")
        require(word["constituents"] == list(word["simplified"]), "Constituents must reproduce vocabulary in order")
        require(all(char in characters for char in word["constituents"]), "Missing constituent character")
        memberships(word["hsk_levels"])
        require(isinstance(word["readings"], list), "Readings must be a list")
        for reading in word["readings"]:
            fields(reading, (*READING_FIELDS, "meanings"), "reading")
            require(all(isinstance(reading[k], str) for k in READING_FIELDS), "Reading values must be text")
            require(isinstance(reading["meanings"], list) and all(isinstance(m, str) for m in reading["meanings"]),
                    "Meanings must be an ordered list of text")
    return spec


def extract(source_path, settings):
    settings = validate_settings(settings)
    with open_source(source_path) as source:
        schemes = [dict(code=code, label=label, max_level=maximum) for code, label, maximum in source.execute(
            "SELECT scheme, label, max_level FROM hsk_level_scheme ORDER BY scheme"
        )]
        settings = validate_settings(settings, schemes)
        entries = select_entries(source, settings)
        characters, vocabulary = read_source(source, entries)
    return validate_document(transform(settings, schemes, characters, vocabulary))


def write_document(spec, output_path, protected_paths=()):
    """Stage complete JSON and publish exclusively; never truncate an input/output."""
    output = Path(output_path).absolute()
    require(output.resolve() not in {Path(p).resolve() for p in protected_paths},
            "Output must be distinct from all inputs")
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Refusing to overwrite: {output}")
    validate_document(spec)
    content = json.dumps(spec, ensure_ascii=False, indent=2) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=".chineselearning-extract-", dir=output.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as staged:
            staged.write(content)
        os.link(name, output)
    finally:
        Path(name).unlink(missing_ok=True)


def extract_to_file(source_path, settings, output_path, settings_path=None):
    protected = [source_path] + ([settings_path] if settings_path is not None else [])
    spec = extract(source_path, settings)
    write_document(spec, output_path, protected)
    return spec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("hsk-original/hsk_vocab.sqlite"))
    parser.add_argument("--settings", type=Path, help="JSON containing scheme, levels, mode")
    parser.add_argument("--scheme")
    parser.add_argument("--levels", type=int, nargs="+")
    parser.add_argument("--mode", choices=("exact", "cumulative"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.settings and any(value is not None for value in (args.scheme, args.levels, args.mode)):
        parser.error("Use either --settings or --scheme/--levels/--mode")
    if not args.settings and any(value is None for value in (args.scheme, args.levels, args.mode)):
        parser.error("--scheme, --levels, and --mode are required without --settings")
    try:
        settings = (json.loads(args.settings.read_text(encoding="utf-8")) if args.settings else
                    dict(scheme=args.scheme, levels=args.levels, mode=args.mode))
        spec = extract_to_file(args.source, settings, args.output, args.settings)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Extraction failed: {error}\n")
    print(json.dumps(dict(vocabulary=len(spec["vocabulary"]), characters=len(spec["characters"]))))


if __name__ == "__main__":
    main()
