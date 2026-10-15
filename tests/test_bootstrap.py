import hashlib
import json
from pathlib import Path
import sqlite3

import pytest
from sqlalchemy import insert, update
from sqlalchemy.exc import IntegrityError

from chineselearning.bootstrap import build_database, schema_sql, sqlite_engine
from chineselearning.schema import character_learning, hanzi_character, metadata

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "hsk-original" / "hsk_vocab.sqlite"
SEED = ROOT / "data/bootstrap.json"


def logical_snapshot(path):
    with sqlite3.connect(path) as connection:
        return {
            table.name: connection.execute(
                f'SELECT * FROM "{table.name}" ORDER BY '
                + ", ".join(column.name for column in table.primary_key)
            ).fetchall()
            for table in metadata.sorted_tables
        }


@pytest.fixture
def built(tmp_path):
    output = tmp_path / "application.sqlite"
    sql_output = tmp_path / "bootstrap.sql"
    counts = build_database(SOURCE, SEED, output, sql_output)
    return output, sql_output, counts


def test_selected_characters_have_independent_ids_and_blank_glosses(built):
    output, _, counts = built
    assert counts == {
        "hanzi_character": 8, "hsk_scheme": 3, "learning_status": 3,
        "character_hsk_level": 24, "character_learning": 8,
        "vocabulary_entry": 0, "vocabulary_reading": 0, "vocabulary_meaning": 0,
        "vocabulary_hsk_level": 0, "vocabulary_character": 0,
        "text_category": 0, "library_text": 0,
    }
    with sqlite3.connect(output) as connection:
        actual = connection.execute(
            "SELECT id, simplified, english_gloss, usage_note FROM hanzi_character ORDER BY id"
        ).fetchall()
    selection = json.loads(SEED.read_text())["characters"]
    assert actual == [(i, r["simplified"], None, None) for i, r in enumerate(selection, 1)]


def test_bound_characters_and_best_effort_traditional_forms(built):
    output, _, _ = built
    with sqlite3.connect(output) as connection:
        forms = dict(connection.execute("SELECT simplified, traditional FROM hanzi_character"))
    assert forms == {"学": "學", "银": "銀", "行": "行", "客": "客", "发": "發", "后": "后", "么": "麼", "服": "服"}


def test_levels_are_derived_from_words_and_kept_per_scheme(built):
    output, _, _ = built
    with sqlite3.connect(output) as connection:
        levels = connection.execute(
            """SELECT s.code, l.level FROM character_hsk_level l
               JOIN hanzi_character c ON c.id = l.character_id
               JOIN hsk_scheme s ON s.id = l.hsk_scheme_id
               WHERE c.simplified = '银' ORDER BY s.code"""
        ).fetchall()
    assert levels == [("new", 2), ("newest", 3), ("old", 3)]


def test_recognition_and_production_can_differ(built):
    output, _, _ = built
    engine = sqlite_engine(output)
    try:
        with engine.begin() as connection:
            assert connection.execute(character_learning.select()).all() == [
                (i, 1, 1) for i in range(1, 9)
            ]
            connection.execute(
                update(character_learning).where(character_learning.c.character_id == 1)
                .values(recognition_status_id=3, production_status_id=2)
            )
            assert connection.execute(
                character_learning.select().where(character_learning.c.character_id == 1)
            ).one() == (1, 3, 2)
    finally:
        engine.dispose()


def test_constraints_reject_invalid_rows(built):
    output, _, _ = built
    engine = sqlite_engine(output)
    try:
        for record in [dict(id=9, simplified="学"), dict(id=9, simplified="学生")]:
            with pytest.raises(IntegrityError), engine.begin() as connection:
                connection.execute(insert(hanzi_character), record)
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.execute(update(character_learning).values(recognition_status_id=999))
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO character_hsk_level VALUES (999, 1, 1)"
            )
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO character_hsk_level VALUES (1, 1, 1)"
            )
    finally:
        engine.dispose()


def test_sql_import_recreates_the_same_database_without_source(built, tmp_path):
    output, sql_output, _ = built
    restored = tmp_path / "restored.sqlite"
    with sqlite3.connect(restored) as connection:
        connection.executescript(sql_output.read_text(encoding="utf-8"))
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert connection.execute("PRAGMA foreign_keys").fetchone() == (1,)
    assert logical_snapshot(output) == logical_snapshot(restored)


def test_repeated_builds_match_and_source_is_unchanged(built, tmp_path):
    output, sql_output, _ = built
    before = hashlib.sha256(SOURCE.read_bytes()).digest()
    second = tmp_path / "second.sqlite"
    second_sql = tmp_path / "second.sql"
    build_database(SOURCE, SEED, second, second_sql)
    assert logical_snapshot(output) == logical_snapshot(second)
    assert sql_output.read_bytes() == second_sql.read_bytes()
    assert hashlib.sha256(SOURCE.read_bytes()).digest() == before


def test_existing_outputs_and_inputs_are_protected(built, tmp_path):
    output, sql_output, _ = built
    before = output.read_bytes()
    with pytest.raises(FileExistsError):
        build_database(SOURCE, SEED, output)
    with pytest.raises(FileExistsError):
        build_database(SOURCE, SEED, tmp_path / "new.sqlite", sql_output)
    assert not (tmp_path / "new.sqlite").exists()
    assert output.read_bytes() == before
    with pytest.raises(ValueError):
        build_database(SOURCE, SEED, SOURCE)
    with pytest.raises(ValueError):
        build_database(SOURCE, SEED, tmp_path / "same", tmp_path / "same")


@pytest.mark.parametrize("characters", [
    [{"simplified": "龘", "english_gloss": None, "usage_note": None}],
    [{"simplified": "学", "english_gloss": None, "usage_note": None}] * 2,
    [{"simplified": "学生", "english_gloss": None, "usage_note": None}],
])
def test_invalid_selection_does_not_publish_outputs(tmp_path, characters):
    seed = tmp_path / "invalid.json"
    seed.write_text(json.dumps({"characters": characters}), encoding="utf-8")
    output = tmp_path / "bad.sqlite"
    sql_output = tmp_path / "bad.sql"
    with pytest.raises(ValueError):
        build_database(SOURCE, seed, output, sql_output)
    assert not output.exists()
    assert not sql_output.exists()


def test_curated_text_survives_sql_escaping(tmp_path):
    seed = tmp_path / "curated.json"
    seed.write_text(json.dumps({"characters": [
        {"simplified": "学", "english_gloss": "learner's gloss\nsecond line", "usage_note": "例子"}
    ]}), encoding="utf-8")
    output, sql_output = tmp_path / "curated.sqlite", tmp_path / "curated.sql"
    build_database(SOURCE, seed, output, sql_output)
    restored = tmp_path / "curated-restored.sqlite"
    with sqlite3.connect(restored) as connection:
        connection.executescript(sql_output.read_text(encoding="utf-8"))
    assert logical_snapshot(output) == logical_snapshot(restored)


def test_postgresql_schema_compiles_with_explicit_keys():
    sql = schema_sql("postgresql")
    assert all(f"CREATE TABLE {table.name}" in sql for table in metadata.sorted_tables)
    assert "SERIAL" not in sql
    assert "FOREIGN KEY" in sql


def test_checked_in_sql_matches_current_schema_and_seed(built):
    _, sql_output, _ = built
    assert sql_output.read_bytes() == (ROOT / "data/bootstrap.sqlite.sql").read_bytes()
