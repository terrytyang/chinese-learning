"""Extraction and reconstruction contracts, independently of historical IDs."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from chineselearning.bootstrap import build_extracted_database
from chineselearning.extraction import extract, extract_to_file, write_document
from chineselearning.hsk_source import open_source
from test_bootstrap import logical_snapshot

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "hsk-original/hsk_vocab.sqlite"
SETTINGS = {"scheme": "newest", "levels": [1], "mode": "exact"}
EXTRACTED = ROOT / "data/hsk-newest-level1.json"


@pytest.fixture(scope="module")
def trial():
    return extract(SOURCE, SETTINGS)


@pytest.fixture
def small_source(tmp_path):
    """Multi-level entries, repeated characters, multiple readings and duplicate tags."""
    path = tmp_path / "source.sqlite"
    with sqlite3.connect(path) as source:
        source.executescript((ROOT / "hsk-original/schema.sql").read_text())
        source.execute("INSERT INTO hsk_level_scheme VALUES ('old', 'Old', 6, NULL)")
        source.executemany("INSERT INTO hsk_entry VALUES (?, ?, '', 1)", [
            (100, "行行"), (200, "行"), (300, "银行"),
        ])
        source.executemany("INSERT INTO hsk_entry_level VALUES (?, ?, ?, 'old', ?)", [
            (100, 1, "old-1", 1), (100, 2, "old-2", 2), (100, 3, "old-2", 2),
            (200, 1, "old-2", 2), (300, 1, "old-3", 3),
        ])
        source.executemany("INSERT INTO hsk_entry_char VALUES (?, ?, ?)", [
            (100, 1, "行"), (100, 2, "行"), (200, 1, "行"), (300, 1, "银"), (300, 2, "行"),
        ])
        source.executemany("INSERT INTO hsk_form VALUES (?, ?, ?, ?, ?, ?, '', '', '')", [
            (10, 100, 1, "行行", "xíng xíng", "xing2 xing2"),
            (20, 100, 2, "行行", "háng háng", "hang2 hang2"),
            (30, 200, 1, "行", "xíng", "xing2"),
            (40, 300, 1, "銀行", "yín háng", "yin2 hang2"),
        ])
        source.executemany("INSERT INTO hsk_meaning VALUES (?, ?, ?)", [
            (10, 1, "first reading's meaning\n例子"), (10, 2, "second meaning"),
            (20, 1, "other reading"), (30, 1, "walk"), (40, 1, "bank"),
        ])
    return path


@pytest.mark.parametrize("levels,mode,expected", [
    ([1], "exact", [100]), ([2], "exact", [100, 200]),
    ([3, 1], "exact", [100, 300]), ([3], "cumulative", [100, 200, 300]),
    ([1, 3], "cumulative", [100, 200, 300]),
])
def test_selection_is_union_of_tags_not_first_appearance(small_source, levels, mode, expected):
    spec = extract(small_source, dict(scheme="old", levels=levels, mode=mode))
    assert [w["source_entry_id"] for w in spec["vocabulary"]] == expected
    assert spec["selection"]["levels"] == sorted(levels)


@pytest.mark.parametrize("settings", [
    dict(scheme="unknown", levels=[1], mode="exact"),
    dict(scheme="newest", levels=[], mode="exact"),
    dict(scheme="old", levels=[7], mode="exact"),
    dict(scheme="newest", levels=[0], mode="exact"),
    dict(scheme="newest", levels=[-1], mode="exact"),
    dict(scheme="newest", levels=[1, 1], mode="exact"),
    dict(scheme="newest", levels=[True], mode="exact"),
    dict(scheme="newest", levels=[1.0], mode="exact"),
    dict(scheme="newest", levels=[1], mode="inclusive"),
])
def test_invalid_selections_publish_nothing(tmp_path, settings):
    output = tmp_path / "bad.json"
    with pytest.raises(ValueError):
        extract_to_file(SOURCE, settings, output)
    assert not output.exists()


def test_empty_selection_and_missing_source_are_errors(small_source, tmp_path):
    with pytest.raises(ValueError, match="no vocabulary"):
        extract(small_source, dict(scheme="old", levels=[6], mode="exact"))
    missing = tmp_path / "missing.sqlite"
    with pytest.raises(sqlite3.OperationalError):
        extract(missing, SETTINGS)
    assert not missing.exists()


def test_source_connection_is_read_only(small_source):
    with open_source(small_source) as source:
        with pytest.raises(sqlite3.OperationalError, match="readonly"):
            source.execute("DELETE FROM hsk_entry_level")


def test_deterministic_utf8_and_all_historical_files_unchanged(tmp_path, trial):
    historical = {p: hashlib.sha256(p.read_bytes()).digest()
                  for p in (ROOT / "hsk-original").rglob("*") if p.is_file()}
    first, second = tmp_path / "a.json", tmp_path / "b.json"
    extract_to_file(SOURCE, SETTINGS, first)
    extract_to_file(SOURCE, SETTINGS, second)
    assert first.read_bytes() == second.read_bytes() == EXTRACTED.read_bytes()
    assert "学" in first.read_text(encoding="utf-8")
    assert historical == {p: hashlib.sha256(p.read_bytes()).digest() for p in historical}


def test_extraction_protects_outputs_inputs_settings_and_symlinks(tmp_path, trial):
    output = tmp_path / "selection.json"
    output.write_text("preserve me")
    with pytest.raises(FileExistsError):
        write_document(trial, output)
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(json.dumps(SETTINGS))
    before = settings_path.read_bytes()
    with pytest.raises(ValueError, match="distinct"):
        extract_to_file(SOURCE, SETTINGS, settings_path, settings_path)
    with pytest.raises(ValueError, match="distinct"):
        extract_to_file(SOURCE, SETTINGS, SOURCE)
    alias = tmp_path / "alias"
    alias.symlink_to(SOURCE)
    with pytest.raises(ValueError, match="distinct"):
        extract_to_file(SOURCE, SETTINGS, alias)
    dangling = tmp_path / "dangling"
    target = tmp_path / "not-created"
    dangling.symlink_to(target)
    with pytest.raises(FileExistsError):
        write_document(trial, dangling)
    assert not target.exists()
    assert output.read_text() == "preserve me"
    assert settings_path.read_bytes() == before


def test_independent_counts_and_all_reading_meaning_associations(trial):
    with open_source(SOURCE) as source:
        words = source.execute("""SELECT entry_id, simplified FROM hsk_entry
            WHERE entry_id IN (SELECT entry_id FROM hsk_entry_level WHERE scheme='newest' AND level=1)
            ORDER BY entry_id""").fetchall()
        assert len(words) == 294
        assert len(set("".join(word for _, word in words))) == 248
        assert len(trial["vocabulary"]) == 294 and len(trial["characters"]) == 248
        assert sum(len(word) == 1 for _, word in words) == 137
        assert sum(len(w["constituents"]) for w in trial["vocabulary"]) == 470
        assert sum(len(w["readings"]) for w in trial["vocabulary"]) == 396
        assert sum(len(r["meanings"]) for w in trial["vocabulary"] for r in w["readings"]) == 1115
        for word, (entry_id, simplified) in zip(trial["vocabulary"], words):
            assert word["simplified"] == simplified
            actual = []
            for reading in word["readings"]:
                actual.append(tuple(reading[k] for k in (
                    "traditional", "pinyin", "numeric", "wadegiles", "bopomofo", "romatzyh"
                )))
            assert actual == source.execute("""SELECT traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh
                FROM hsk_form WHERE entry_id=? ORDER BY form_seq""", (entry_id,)).fetchall()
            form_ids = [r[0] for r in source.execute(
                "SELECT form_id FROM hsk_form WHERE entry_id=? ORDER BY form_seq", (entry_id,)
            )]
            for reading, form_id in zip(word["readings"], form_ids):
                assert reading["meanings"] == [r[0] for r in source.execute(
                    "SELECT meaning FROM hsk_meaning WHERE form_id=? ORDER BY meaning_seq", (form_id,)
                )]


def test_repeated_constituents_duplicate_memberships_and_readings_survive(small_source, tmp_path):
    spec = extract(small_source, dict(scheme="old", levels=[1], mode="exact"))
    selection = tmp_path / "extracted.json"
    write_document(spec, selection)
    database, sql = tmp_path / "app.sqlite", tmp_path / "app.sql"
    build_extracted_database(selection, database, sql)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT id, simplified FROM vocabulary_entry").fetchall() == [(1, "行行")]
        assert connection.execute("SELECT position, character_id FROM vocabulary_character ORDER BY position").fetchall() == [(1, 1), (2, 1)]
        assert connection.execute("SELECT level FROM vocabulary_hsk_level ORDER BY position").fetchall() == [(1,), (2,), (2,)]
        assert connection.execute("""SELECT r.position, r.traditional, r.pinyin, m.position, m.meaning
            FROM vocabulary_reading r JOIN vocabulary_meaning m ON m.reading_id=r.id
            ORDER BY r.position, m.position""").fetchall() == [
                (1, "行行", "xíng xíng", 1, "first reading's meaning\n例子"),
                (1, "行行", "xíng xíng", 2, "second meaning"),
                (2, "行行", "háng háng", 1, "other reading"),
            ]
    restored = tmp_path / "restored.sqlite"
    with sqlite3.connect(restored) as connection:
        connection.executescript(sql.read_text())
    assert logical_snapshot(database) == logical_snapshot(restored)


def test_json_build_and_sql_restore_need_no_historical_source(tmp_path, monkeypatch):
    # Copy only the JSON to an unrelated working directory and forbid source access.
    selection = tmp_path / "input.json"
    selection.write_bytes(EXTRACTED.read_bytes())
    def forbidden(*args, **kwargs):
        raise AssertionError("Historical source must not be opened")
    monkeypatch.setattr("chineselearning.extraction.open_source", forbidden)
    monkeypatch.setattr("chineselearning.bootstrap.prepare_rows", forbidden)
    database, sql = tmp_path / "app.sqlite", tmp_path / "app.sql"
    counts = build_extracted_database(selection, database, sql)
    assert counts == {
        "hanzi_character": 248, "hsk_scheme": 3, "learning_status": 3,
        "character_hsk_level": 744, "character_learning": 248,
        "vocabulary_entry": 294, "vocabulary_reading": 396, "vocabulary_meaning": 1115,
        "vocabulary_hsk_level": 799, "vocabulary_character": 470,
        "text_category": 0, "library_text": 0,
    }
    assert sql.read_bytes() == (ROOT / "data/hsk-newest-level1.sqlite.sql").read_bytes()
    restored = tmp_path / "restored.sqlite"
    with sqlite3.connect(restored) as connection:
        connection.executescript(sql.read_text(encoding="utf-8"))
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert connection.execute("SELECT count(*) FROM hanzi_character WHERE english_gloss IS NOT NULL").fetchone() == (0,)
    assert logical_snapshot(database) == logical_snapshot(restored)
    second, second_sql = tmp_path / "second.sqlite", tmp_path / "second.sql"
    build_extracted_database(selection, second, second_sql)
    assert logical_snapshot(database) == logical_snapshot(second)
    assert second_sql.read_bytes() == sql.read_bytes()
    # Exercise the actual command in a directory with no hsk-original/ tree.
    result = subprocess.run([sys.executable, "-m", "chineselearning.bootstrap",
                             "--extracted", str(selection), "--output", "cli.sqlite"],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert logical_snapshot(tmp_path / "cli.sqlite") == logical_snapshot(database)


def test_manual_vocabulary_can_have_no_hsk_membership(tmp_path, trial):
    spec = deepcopy(trial)
    word = deepcopy(spec["vocabulary"][0])
    word.update(source_entry_id=None, simplified=word["simplified"] * 2, hsk_levels=[])
    word["constituents"] *= 2
    spec["vocabulary"].append(word)
    selection = tmp_path / "manual.json"
    write_document(spec, selection)
    database = tmp_path / "manual.sqlite"
    build_extracted_database(selection, database)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT count(*) FROM vocabulary_entry").fetchone() == (295,)
        assert connection.execute("SELECT count(*) FROM vocabulary_hsk_level WHERE vocabulary_id=295").fetchone() == (0,)
        connection.execute("INSERT INTO vocabulary_entry VALUES (999, '手动词语')")
        connection.commit()


@pytest.mark.parametrize("problem", ["version", "missing", "constituents", "meaning", "level", "gloss"])
def test_bad_json_publishes_no_database_or_sql(tmp_path, trial, problem):
    spec = deepcopy(trial)
    if problem == "version":
        spec["version"] = 999
    elif problem == "missing":
        spec["characters"].pop(0)
    elif problem == "constituents":
        spec["vocabulary"][0]["constituents"].reverse()
        spec["vocabulary"][0]["constituents"].append("行")
    elif problem == "meaning":
        spec["vocabulary"][0]["readings"][0]["meanings"] = "flattened"
    elif problem == "level":
        spec["vocabulary"][0]["hsk_levels"][0]["level"] = 999
    else:
        spec["characters"][0]["english_gloss"] = "copied word definition"
    selection = tmp_path / "bad.json"
    selection.write_text(json.dumps(spec))
    database, sql = tmp_path / "bad.sqlite", tmp_path / "bad.sql"
    with pytest.raises(ValueError):
        build_extracted_database(selection, database, sql)
    assert not database.exists() and not sql.exists()


def test_build_overwrite_input_protection_and_failure_cleanup(tmp_path, trial, monkeypatch):
    selection = tmp_path / "input.json"
    write_document(trial, selection)
    before = selection.read_bytes()
    database, sql = tmp_path / "app.sqlite", tmp_path / "app.sql"
    with pytest.raises(ValueError):
        build_extracted_database(selection, selection)
    with pytest.raises(ValueError):
        build_extracted_database(selection, database, database)
    sql.write_text("keep")
    with pytest.raises(FileExistsError):
        build_extracted_database(selection, database, sql)
    assert not database.exists() and sql.read_text() == "keep"
    # Fail the second publication after the DB transaction succeeded.
    import os
    real_link = os.link
    calls = []
    def fail_second(source, target):
        calls.append(target)
        if len(calls) == 2:
            raise OSError("simulated SQL publication failure")
        real_link(source, target)
    monkeypatch.setattr("chineselearning.bootstrap.os.link", fail_second)
    with pytest.raises(OSError, match="simulated"):
        build_extracted_database(selection, database, tmp_path / "failed.sql")
    assert not database.exists() and not (tmp_path / "failed.sql").exists()
    assert not list(tmp_path.glob(".chineselearning-*"))
    assert selection.read_bytes() == before


def test_database_transaction_failure_publishes_nothing(tmp_path, trial, monkeypatch):
    selection = tmp_path / "input.json"
    write_document(trial, selection)
    from chineselearning.bootstrap import prepare_extracted_rows
    rows = prepare_extracted_rows(selection)
    rows["vocabulary_character"][0]["character_id"] = 99999
    monkeypatch.setattr("chineselearning.bootstrap.prepare_extracted_rows", lambda path: rows)
    from sqlalchemy.exc import IntegrityError
    database, sql = tmp_path / "failed.sqlite", tmp_path / "failed.sql"
    with pytest.raises(IntegrityError):
        build_extracted_database(selection, database, sql)
    assert not database.exists() and not sql.exists()
    assert not list(tmp_path.glob(".chineselearning-*"))


def test_vocabulary_constraints(tmp_path):
    from chineselearning.bootstrap import sqlite_engine
    from sqlalchemy.exc import IntegrityError
    database = tmp_path / "app.sqlite"
    build_extracted_database(EXTRACTED, database)
    engine = sqlite_engine(database)
    try:
        for statement in (
            "INSERT INTO vocabulary_entry VALUES (999, '')",
            "INSERT INTO vocabulary_character VALUES (1, 0, 1)",
            "INSERT INTO vocabulary_character VALUES (1, 999, 99999)",
            "INSERT INTO vocabulary_meaning VALUES (99999, 1, 'missing reading')",
            "INSERT INTO vocabulary_hsk_level VALUES (1, 999, 1, 0)",
            "UPDATE vocabulary_reading SET position=0 WHERE id=1",
        ):
            with pytest.raises(IntegrityError), engine.begin() as connection:
                connection.exec_driver_sql(statement)
    finally:
        engine.dispose()


def test_extraction_cli_settings_and_explicit_flags_match(small_source, tmp_path):
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps(dict(scheme="old", levels=[2], mode="exact")))
    for name, options in (
        ("settings.json.out", ["--settings", str(settings)]),
        ("flags.json.out", ["--scheme", "old", "--levels", "2", "--mode", "exact"]),
    ):
        result = subprocess.run([sys.executable, "-m", "chineselearning.extraction",
                                 "--source", str(small_source), "--output", str(tmp_path / name), *options],
                                capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    assert (tmp_path / "settings.json.out").read_bytes() == (tmp_path / "flags.json.out").read_bytes()
    result = subprocess.run([sys.executable, "-m", "chineselearning.extraction",
                             "--source", str(small_source), "--scheme", "old", "--levels", "0",
                             "--mode", "exact", "--output", str(tmp_path / "bad.json")],
                            capture_output=True, text=True)
    assert result.returncode != 0 and "positive integers" in result.stderr
    assert "Traceback" not in result.stderr and not (tmp_path / "bad.json").exists()
