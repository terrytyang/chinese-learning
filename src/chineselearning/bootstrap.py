"""Build a fresh database and optional SQL snapshot from a fixed seed selection."""

import argparse
import json
import os
from pathlib import Path
import sqlite3
import tempfile

from sqlalchemy import create_engine, event, insert
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateTable
from sqlalchemy.exc import SQLAlchemyError

from chineselearning.schema import metadata
from chineselearning.hsk_source import open_source, traditional_candidate
from chineselearning.inventory_selection import validate_manifest, verify_source_bands


def read_selection(path):
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(spec, dict) or set(spec) not in (
        {"characters"}, {"inventory", "characters"}
    ):
        raise ValueError("Seed must contain characters and optional inventory metadata")
    if "inventory" in spec:
        validate_manifest(spec)
        records = [{k: v for k, v in record.items() if k != "hsk_level"}
                   for record in spec["characters"]]
    else:
        records = spec["characters"]
    if not isinstance(records, list) or not records:
        raise ValueError("Select at least one character")
    seen = set()
    for record in records:
        if not isinstance(record, dict) or set(record) != {
            "simplified", "english_gloss", "usage_note"
        }:
            raise ValueError("Each character needs simplified, english_gloss, usage_note")
        char = record["simplified"]
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("Each simplified value must be one Unicode code point")
        if char in seen:
            raise ValueError(f"Duplicate character: {char}")
        seen.add(char)
        for key in ("english_gloss", "usage_note"):
            if record[key] is not None and not isinstance(record[key], str):
                raise ValueError(f"{key} must be text or null")
    return records


def prepare_rows(source_path, selection_path):
    records = read_selection(selection_path)
    rows = {table.name: [] for table in metadata.sorted_tables}
    with open_source(source_path) as source:
        spec = json.loads(Path(selection_path).read_text(encoding="utf-8"))
        if "inventory" in spec:
            verify_source_bands(source, spec["characters"])
        scheme_ids = {}
        for scheme_id, (code, label, max_level) in enumerate(
            source.execute(
                "SELECT scheme, label, max_level FROM hsk_level_scheme ORDER BY scheme"
            ),
            start=1,
        ):
            scheme_ids[code] = scheme_id
            rows["hsk_scheme"].append(
                dict(id=scheme_id, code=code, label=label, max_level=max_level)
            )
        for character_id, record in enumerate(records, start=1):
            char = record["simplified"]
            if not source.execute(
                "SELECT 1 FROM hsk_entry_char WHERE char = ? LIMIT 1", (char,)
            ).fetchone():
                raise ValueError(f"Character absent from source: {char}")
            rows["hanzi_character"].append(
                dict(id=character_id, traditional=traditional_candidate(source, char), **record)
            )
            for code, level in source.execute(
                "SELECT scheme, level FROM hsk_char_min_level WHERE char = ? ORDER BY scheme",
                (char,),
            ):
                maximum = next(r["max_level"] for r in rows["hsk_scheme"] if r["code"] == code)
                if not 1 <= level <= maximum:
                    raise ValueError(f"Invalid source level: {char} {code} {level}")
                rows["character_hsk_level"].append(
                    dict(character_id=character_id, hsk_scheme_id=scheme_ids[code], level=level)
                )
            rows["character_learning"].append(
                dict(character_id=character_id, recognition_status_id=1, production_status_id=1)
            )
    rows["learning_status"] = learning_status_rows()
    return rows


def prepare_extracted_rows(extraction_path):
    """Prepare application rows using only a validated, self-contained JSON file."""
    from chineselearning.extraction import READING_FIELDS, validate_document

    spec = validate_document(json.loads(Path(extraction_path).read_text(encoding="utf-8")))
    rows = {table.name: [] for table in metadata.sorted_tables}
    rows["learning_status"] = learning_status_rows()
    scheme_ids = {}
    for scheme_id, scheme in enumerate(spec["schemes"], 1):
        scheme_ids[scheme["code"]] = scheme_id
        rows["hsk_scheme"].append(dict(id=scheme_id, **scheme))
    character_ids = {}
    for character_id, record in enumerate(spec["characters"], 1):
        character_ids[record["simplified"]] = character_id
        rows["hanzi_character"].append(dict(
            id=character_id, **{key: value for key, value in record.items() if key != "hsk_levels"}
        ))
        for membership in record["hsk_levels"]:
            rows["character_hsk_level"].append(dict(
                character_id=character_id, hsk_scheme_id=scheme_ids[membership["scheme"]],
                level=membership["level"],
            ))
        rows["character_learning"].append(dict(
            character_id=character_id, recognition_status_id=1, production_status_id=1,
        ))
    reading_id = 0
    for vocabulary_id, word in enumerate(spec["vocabulary"], 1):
        rows["vocabulary_entry"].append(dict(id=vocabulary_id, simplified=word["simplified"]))
        for position, membership in enumerate(word["hsk_levels"], 1):
            rows["vocabulary_hsk_level"].append(dict(
                vocabulary_id=vocabulary_id, position=position,
                hsk_scheme_id=scheme_ids[membership["scheme"]], level=membership["level"],
            ))
        for position, char in enumerate(word["constituents"], 1):
            rows["vocabulary_character"].append(dict(
                vocabulary_id=vocabulary_id, position=position, character_id=character_ids[char],
            ))
        for position, reading in enumerate(word["readings"], 1):
            reading_id += 1
            rows["vocabulary_reading"].append(dict(
                id=reading_id, vocabulary_id=vocabulary_id, position=position,
                **{key: reading[key] for key in READING_FIELDS},
            ))
            for meaning_position, meaning in enumerate(reading["meanings"], 1):
                rows["vocabulary_meaning"].append(dict(
                    reading_id=reading_id, position=meaning_position, meaning=meaning,
                ))
    return rows


def learning_status_rows():
    return [
        dict(id=1, code="not_encountered", label="Not yet encountered"),
        dict(id=2, code="learning", label="Learning"),
        dict(id=3, code="known", label="Known"),
    ]


def schema_sql(dialect_name="sqlite"):
    dialect = {"sqlite": sqlite.dialect, "postgresql": postgresql.dialect}[dialect_name]()
    return "\n\n".join(
        str(CreateTable(table).compile(dialect=dialect)).strip() + ";"
        for table in metadata.sorted_tables
    )


def snapshot_sql(rows):
    parts = [
        "-- Generated from the preliminary SQLAlchemy schema and selected seed data.",
        "-- SQLite snapshot. Import into a fresh database; no source database is needed.",
        "PRAGMA foreign_keys = ON;",
        "BEGIN;",
        schema_sql(),
    ]
    for table in metadata.sorted_tables:
        for record in rows[table.name]:
            statement = insert(table).values(**record).compile(
                dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True}
            )
            parts.append(str(statement) + ";")
    parts.append("COMMIT;")
    return "\n\n".join(parts) + "\n"


def sqlite_engine(path):
    engine = create_engine("sqlite+pysqlite:///" + str(Path(path).resolve()))

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys = ON")

    return engine


def build_database(source_path, selection_path, output_path, sql_path=None):
    return _build_database(
        lambda: prepare_rows(source_path, selection_path),
        [source_path, selection_path], output_path, sql_path,
    )


def build_extracted_database(extraction_path, output_path, sql_path=None):
    return _build_database(
        lambda: prepare_extracted_rows(extraction_path),
        [extraction_path], output_path, sql_path,
    )


def _build_database(prepare, input_paths, output_path, sql_path):
    output = Path(output_path).absolute()
    sql_output = Path(sql_path).absolute() if sql_path is not None else None
    protected = {Path(path).resolve() for path in input_paths}
    outputs = [output] + ([sql_output] if sql_output else [])
    resolved = [path.resolve() for path in outputs]
    if len(set(resolved)) != len(outputs) or any(path in protected for path in resolved):
        raise ValueError("Outputs must be distinct from each other and the inputs")
    for path in outputs:
        if path.exists() or path.is_symlink():
            raise FileExistsError(f"Refusing to overwrite: {path}")
    rows = prepare()
    sql_text = snapshot_sql(rows) if sql_output else None
    temporary = []
    published = []
    try:
        for path in outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            handle, name = tempfile.mkstemp(prefix=".chineselearning-", dir=path.parent)
            os.close(handle)
            temporary.append(Path(name))
        engine = sqlite_engine(temporary[0])
        try:
            with engine.begin() as connection:
                metadata.create_all(connection)
                for table in metadata.sorted_tables:
                    if rows[table.name]:
                        connection.execute(insert(table), rows[table.name])
            with engine.connect() as connection:
                if connection.exec_driver_sql("PRAGMA integrity_check").scalar() != "ok":
                    raise ValueError("Generated database failed integrity check")
                if connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall():
                    raise ValueError("Generated database has broken foreign keys")
        finally:
            engine.dispose()
        if sql_output:
            temporary[1].write_text(sql_text, encoding="utf-8")
        for staged, path in zip(temporary, outputs):
            os.link(staged, path)  # Exclusive publication: never replace an existing file.
            published.append(path)
    except BaseException:
        for path in published:
            path.unlink()
        raise
    finally:
        for path in temporary:
            path.unlink(missing_ok=True)
    return {name: len(records) for name, records in rows.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--seed", type=Path)
    inputs.add_argument("--extracted", type=Path, help="Self-contained extracted JSON; no historical source access")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sql-output", type=Path)
    parser.add_argument("--print-schema", choices=("sqlite", "postgresql"))
    args = parser.parse_args()
    if args.print_schema:
        if args.output or args.sql_output:
            parser.error("--print-schema cannot be combined with output arguments")
        print(schema_sql(args.print_schema))
        return
    if args.output is None:
        parser.error("--output is required for a build")
    if args.extracted and args.source:
        parser.error("--extracted cannot be combined with --source")
    try:
        if args.extracted:
            counts = build_extracted_database(args.extracted, args.output, args.sql_output)
        else:
            counts = build_database(
                args.source or Path("hsk-original/hsk_vocab.sqlite"),
                args.seed or Path("data/bootstrap.json"), args.output, args.sql_output,
            )
    except (OSError, ValueError, sqlite3.Error, SQLAlchemyError) as error:
        parser.exit(1, f"Initialization failed: {error}\n")
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
