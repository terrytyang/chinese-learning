from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from chineselearning.bootstrap import (
    build_database, build_extracted_database, schema_sql, sqlite_engine,
)
from chineselearning.curated_text import read_rows
from chineselearning.schema import library_text, text_category
from test_bootstrap import logical_snapshot

ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "data/hsk-newest-level1.json"
TEXTS = ROOT / "data/text-library.json"
BODY = "月落乌啼霜满天，江枫渔火对愁眠。\n姑苏城外寒山寺，夜半钟声到客船。"


@pytest.fixture(scope="module")
def combined(tmp_path_factory):
    directory = tmp_path_factory.mktemp("combined-library")
    database, sql = directory / "application.sqlite", directory / "application.sql"
    counts = build_extracted_database(EXTRACTED, database, sql, texts_path=TEXTS)
    return database, sql, counts


def test_sample_combined_build_preserves_records_and_counts(combined):
    database, _, counts = combined
    assert counts["text_category"] == 5 and counts["library_text"] == 1
    assert counts["vocabulary_entry"] == 294 and counts["hanzi_character"] == 248
    assert counts["vocabulary_reading"] == 396 and counts["vocabulary_meaning"] == 1115
    assert counts["vocabulary_character"] == 470 and counts["vocabulary_hsk_level"] == 799
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT * FROM text_category ORDER BY id").fetchall() == [
            (1, "诗词"), (2, "文言"), (3, "散文"), (4, "节选"), (5, "讲解"),
        ]
        assert connection.execute("SELECT * FROM library_text").fetchall() == [
            (1, 1, "张继", "唐朝", "枫桥夜泊", BODY, None),
        ]


def test_explicit_nonsequential_ids_and_exact_content_survive_rebuild_and_sql(tmp_path):
    spec = json.loads(TEXTS.read_text())
    spec["categories"] = [{"id": 42, "label": "诗词"}, {"id": 7, "label": "新类别"}]
    spec["texts"] = [
        dict(id=207, category_id=42, title="  枫桥夜泊　", body="\n" + BODY + "\r\n\t ",
             notes="editor's note\n保留"),
        dict(id=11, category_id=7, title="新作", body="原文", author=None, period=None),
    ]
    selection = tmp_path / "texts.json"
    selection.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    database, sql = tmp_path / "app.sqlite", tmp_path / "app.sql"
    build_extracted_database(EXTRACTED, database, sql, texts_path=selection)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT id, category_id FROM library_text ORDER BY id").fetchall() == [(11, 7), (207, 42)]
        assert connection.execute("SELECT title, body, author, period, notes FROM library_text WHERE id=207").fetchone() == (
            spec["texts"][0]["title"], spec["texts"][0]["body"], None, None, spec["texts"][0]["notes"],
        )
    restored = tmp_path / "restored.sqlite"
    with sqlite3.connect(restored) as connection:
        # Avoid text-mode newline translation inside SQL string literals.
        connection.executescript(sql.read_bytes().decode("utf-8"))
    assert logical_snapshot(database) == logical_snapshot(restored)
    # Input ordering has no effect on supplied identities or the generated snapshot.
    spec["categories"].reverse()
    spec["texts"].reverse()
    selection.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    second, second_sql = tmp_path / "second.sqlite", tmp_path / "second.sql"
    build_extracted_database(EXTRACTED, second, second_sql, texts_path=selection)
    assert sql.read_bytes() == second_sql.read_bytes()


@pytest.mark.parametrize("problem", [
    "format", "version", "bool_version", "root", "missing_list", "list_type",
    "duplicate_category", "duplicate_text", "missing_category", "category_id_type",
    "category_label", "category_label_type", "id_type", "bool_id", "oversize_id",
    "missing_id", "missing_title", "blank_title", "unicode_blank_body", "body_type",
    "author_type", "period_type", "notes_type", "unknown_field",
])
def test_invalid_curated_input_publishes_no_outputs(tmp_path, problem):
    spec = json.loads(TEXTS.read_text())
    text = spec["texts"][0]
    if problem == "format":
        spec["format"] = "chineselearning-hsk-extraction"
    elif problem == "version":
        spec["version"] = 2
    elif problem == "bool_version":
        spec["version"] = True
    elif problem == "root":
        spec = []
    elif problem == "missing_list":
        del spec["categories"]
    elif problem == "list_type":
        spec["texts"] = {}
    elif problem == "duplicate_category":
        spec["categories"].append(deepcopy(spec["categories"][0]))
    elif problem == "duplicate_text":
        spec["texts"].append(deepcopy(text))
    elif problem == "missing_category":
        text["category_id"] = 99
    elif problem == "category_id_type":
        text["category_id"] = "1"
    elif problem == "category_label":
        spec["categories"][0]["label"] = " \t\n"
    elif problem == "category_label_type":
        spec["categories"][0]["label"] = 1
    elif problem == "id_type":
        text["id"] = "1"
    elif problem == "bool_id":
        spec["categories"][0]["id"] = True
    elif problem == "oversize_id":
        text["id"] = 2**63
    elif problem == "missing_id":
        del text["id"]
    elif problem == "missing_title":
        del text["title"]
    elif problem == "blank_title":
        text["title"] = "\t \n"
    elif problem == "unicode_blank_body":
        text["body"] = "\u3000\n\r\t"
    elif problem == "body_type":
        text["body"] = [BODY]
    elif problem == "unknown_field":
        text["commentary"] = "unexpected"
    else:
        text[problem.removesuffix("_type")] = 99
    selection = tmp_path / "bad.json"
    selection.write_text(json.dumps(spec))
    before = selection.read_bytes()
    database, sql = tmp_path / "bad.sqlite", tmp_path / "bad.sql"
    with pytest.raises(ValueError):
        build_extracted_database(EXTRACTED, database, sql, texts_path=selection)
    assert not database.exists() and not sql.exists()
    assert selection.read_bytes() == before
    assert not list(tmp_path.glob(".chineselearning-*"))


def test_optional_values_and_empty_lists_are_supported(tmp_path):
    selection = tmp_path / "empty.json"
    selection.write_text(json.dumps(dict(format="chineselearning-curated-texts", version=1, categories=[], texts=[])))
    assert read_rows(selection) == {"text_category": [], "library_text": []}
    rows = read_rows(TEXTS)
    assert rows["library_text"][0]["notes"] is None


def test_combined_sql_snapshot_restores_every_table_without_inputs(combined, tmp_path, monkeypatch):
    database, sql, _ = combined
    assert sql.read_bytes() == (ROOT / "data/hsk-text-library.sqlite.sql").read_bytes()
    def forbidden(*args, **kwargs):
        raise AssertionError("SQL restore must not read inputs")
    monkeypatch.setattr("chineselearning.bootstrap.prepare_extracted_rows", forbidden)
    monkeypatch.setattr("chineselearning.curated_text.read_rows", forbidden)
    restored = tmp_path / "restored.sqlite"
    with sqlite3.connect(restored) as connection:
        connection.executescript(sql.read_text(encoding="utf-8"))
        assert connection.execute("PRAGMA foreign_keys").fetchone() == (1,)
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    assert logical_snapshot(database) == logical_snapshot(restored)


def test_curated_input_and_existing_outputs_are_protected(tmp_path):
    selection = tmp_path / "texts.json"
    selection.write_bytes(TEXTS.read_bytes())
    before = selection.read_bytes()
    database, sql = tmp_path / "app.sqlite", tmp_path / "app.sql"
    with pytest.raises(ValueError, match="inputs"):
        build_extracted_database(EXTRACTED, selection, texts_path=selection)
    with pytest.raises(ValueError, match="inputs"):
        build_extracted_database(EXTRACTED, database, selection, texts_path=selection)
    alias = tmp_path / "alias.json"
    alias.symlink_to(selection)
    with pytest.raises(ValueError, match="inputs"):
        build_extracted_database(EXTRACTED, alias, texts_path=selection)
    sql.write_text("preserve")
    with pytest.raises(FileExistsError):
        build_extracted_database(EXTRACTED, database, sql, texts_path=selection)
    database.write_text("preserve database")
    with pytest.raises(FileExistsError):
        build_extracted_database(EXTRACTED, database, texts_path=selection)
    assert selection.read_bytes() == before
    assert database.read_text() == "preserve database" and sql.read_text() == "preserve"


def test_text_failure_in_database_transaction_and_publication_cleans_outputs(tmp_path, monkeypatch):
    from chineselearning.curated_text import read_rows as real_read_rows
    rows = real_read_rows(TEXTS)
    rows["library_text"][0]["category_id"] = 999
    database, sql = tmp_path / "app.sqlite", tmp_path / "app.sql"
    with monkeypatch.context() as patch:
        patch.setattr("chineselearning.curated_text.read_rows", lambda _: rows)
        with pytest.raises(IntegrityError):
            build_extracted_database(EXTRACTED, database, sql, texts_path=TEXTS)
    assert not database.exists() and not sql.exists()
    import os
    real_link = os.link
    calls = []
    def fail_second(source, target):
        calls.append(target)
        if len(calls) == 2:
            raise OSError("simulated publication failure")
        real_link(source, target)
    monkeypatch.setattr("chineselearning.bootstrap.os.link", fail_second)
    with pytest.raises(OSError, match="simulated"):
        build_extracted_database(EXTRACTED, database, sql, texts_path=TEXTS)
    assert not database.exists() and not sql.exists()
    assert not list(tmp_path.glob(".chineselearning-*"))


def test_character_fixture_can_optionally_include_texts(tmp_path):
    database = tmp_path / "eight.sqlite"
    counts = build_database(ROOT / "hsk-original/hsk_vocab.sqlite", ROOT / "data/bootstrap.json",
                            database, texts_path=TEXTS)
    assert counts["hanzi_character"] == 8 and counts["vocabulary_entry"] == 0
    assert counts["text_category"] == 5 and counts["library_text"] == 1


def test_combined_cli_build_needs_only_copied_json_inputs(tmp_path):
    extraction, texts = tmp_path / "hsk.json", tmp_path / "texts.json"
    extraction.write_bytes(EXTRACTED.read_bytes())
    texts.write_bytes(TEXTS.read_bytes())
    result = subprocess.run([sys.executable, "-m", "chineselearning.bootstrap",
                             "--extracted", "hsk.json", "--texts", "texts.json",
                             "--output", "app.sqlite", "--sql-output", "app.sql"],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["library_text"] == 1
    assert (tmp_path / "app.sql").read_bytes() == (ROOT / "data/hsk-text-library.sqlite.sql").read_bytes()


def test_text_constraints_and_category_extensibility(combined, tmp_path):
    database = tmp_path / "constraints.sqlite"
    with sqlite3.connect(database) as connection:
        connection.executescript(combined[1].read_text())
    engine = sqlite_engine(database)
    try:
        for record in (
            dict(id=2, category_id=999, title="未知类别", body="内容"),
            dict(id=2, category_id=1, title=" ", body="内容"),
            dict(id=2, category_id=1, title="标题", body=""),
            dict(id=1, category_id=1, title="重复", body="内容"),
        ):
            with pytest.raises(IntegrityError), engine.begin() as connection:
                connection.execute(insert(library_text), record)
        with engine.begin() as connection:
            connection.execute(insert(text_category), dict(id=99, label="新增类别"))
            connection.execute(insert(library_text), dict(id=82, category_id=99, title="新文", body="新内容"))
    finally:
        engine.dispose()


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_ddl_has_no_trailing_whitespace(dialect):
    assert all(line == line.rstrip() for line in schema_sql(dialect).splitlines())
