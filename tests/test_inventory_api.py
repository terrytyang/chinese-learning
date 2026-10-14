import hashlib
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import insert
from sqlalchemy.exc import OperationalError

from chineselearning.bootstrap import sqlite_engine
from chineselearning.inventory_query import open_inventory_database
from chineselearning.schema import (
    character_hsk_level, character_learning, hanzi_character, hsk_scheme,
    learning_status, metadata,
)
from chineselearning.web import create_app


@pytest.fixture
def application_db(tmp_path):
    path = tmp_path / "targeted.sqlite"
    engine = sqlite_engine(path)
    metadata.create_all(engine)
    # Deliberately shuffled IDs and characters: pages must follow the requested
    # whole-result order, never insertion order or a sorted subset of a page.
    chars = list("银行学后么服发客中上下左右人大小天地日月水火山田木")
    rows = [dict(id=100 - index, simplified=char,
                 traditional="學" if char == "学" else None,
                 english_gloss=None, usage_note=None)
            for index, char in enumerate(chars)]
    with engine.begin() as connection:
        connection.execute(insert(hsk_scheme), [
            dict(id=1, code="newest", label="HSK 3.0 (2026 syllabus)", max_level=7),
            dict(id=2, code="new", label="HSK 3.0 (2021 standard)", max_level=7),
            dict(id=3, code="old", label="HSK 2.0", max_level=6),
        ])
        connection.execute(insert(learning_status), [
            dict(id=1, code="not_encountered", label="Not yet encountered"),
            dict(id=2, code="known", label="Known"),
            dict(id=3, code="learning", label="Learning"),
        ])
        connection.execute(insert(hanzi_character), rows)
        connection.execute(insert(character_hsk_level), [
            dict(character_id=row["id"], hsk_scheme_id=1, level=(1, 2, 7)[index % 3])
            for index, row in enumerate(rows)
        ] + [dict(character_id=rows[0]["id"], hsk_scheme_id=3, level=6)])
        connection.execute(insert(character_learning), [
            dict(character_id=row["id"], recognition_status_id=2 if index == 0 else 1,
                 production_status_id=3 if index == 0 else 1)
            for index, row in enumerate(rows[:-1])
        ])
    engine.dispose()
    return path, rows


@pytest.fixture
def client(application_db):
    with TestClient(create_app(application_db[0])) as client:
        yield client


def test_defaults_and_null_values_and_separate_statuses(client, application_db):
    result = client.get("/api/characters").json()
    assert result["hsk_scheme"] == {"code": "newest", "label": "HSK 3.0 (2026 syllabus)"}
    assert (result["total"], result["page"], result["page_size"], result["total_pages"]) == (25, 1, 20, 2)
    assert [row["simplified"] for row in result["items"]] == sorted(row["simplified"] for row in application_db[1])[:20]
    all_items = client.get("/api/characters?page_size=100").json()["items"]
    silver = next(item for item in all_items if item["simplified"] == "银")
    assert silver["recognition_status"] == "known"
    assert silver["production_status"] == "learning"
    assert silver["traditional"] is None
    assert silver["english_gloss"] is None and silver["usage_note"] is None
    missing_status = next(item for item in all_items if item["simplified"] == "木")
    assert missing_status["recognition_status"] is None and missing_status["production_status"] is None
    assert next(item for item in all_items if item["simplified"] == "学")["traditional"] == "學"


@pytest.mark.parametrize("sort", ["simplified", "hsk_level"])
@pytest.mark.parametrize("order", ["asc", "desc"])
def test_whole_result_sorting_and_deterministic_band_ties(client, application_db, sort, order):
    expected = [(row["id"], row["simplified"], (1, 2, 7)[index % 3])
                for index, row in enumerate(application_db[1])]
    key = (lambda r: (r[1], r[0])) if sort == "simplified" else (lambda r: (r[2], r[1], r[0]))
    expected.sort(key=key, reverse=order == "desc")
    collected = []
    for page in range(1, 4):
        url = f"/api/characters?sort={sort}&order={order}&page_size=10&page={page}"
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data == client.get(url).json()
        assert data["total"] == 25 and data["total_pages"] == 3
        collected.extend((item["id"], item["simplified"], item["hsk_level"]) for item in data["items"])
    assert collected == expected


@pytest.mark.parametrize("level,count,label", [(1, 9, "1"), (2, 8, "2"), (7, 8, "7–9")])
def test_exact_band_filter_and_counts(client, level, count, label):
    data = client.get(f"/api/characters?hsk_level={level}").json()
    assert data["total"] == count and data["total_pages"] == 1
    assert len(data["items"]) == count
    assert all(item["hsk_level"] == level and item["hsk_level_label"] == label for item in data["items"])


def test_scheme_selection_is_not_cross_scheme_or_cumulative(client):
    data = client.get("/api/characters?hsk_scheme=old&hsk_level=6").json()
    assert data["hsk_scheme"] == {"code": "old", "label": "HSK 2.0"}
    assert data["total"] == 1
    assert data["items"][0]["simplified"] == "银"
    assert data["items"][0]["hsk_level_label"] == "6"


@pytest.mark.parametrize("size,pages", [(10, 3), (20, 2), (50, 1), (100, 1)])
def test_page_sizes_and_counts(client, size, pages):
    data = client.get(f"/api/characters?page_size={size}").json()
    assert data["page_size"] == size and data["total_pages"] == pages
    assert len(data["items"]) == min(size, 25)


@pytest.mark.parametrize("query,total,pages,page", [
    ("hsk_level=3", 0, 0, 1),
    ("hsk_scheme=new&page=5", 0, 0, 5),
    ("page=3", 25, 2, 3),
    ("page=999999999999999999999999999999", 25, 2, 999999999999999999999999999999),
])
def test_empty_and_out_of_range_pages_are_not_clamped(client, query, total, pages, page):
    response = client.get("/api/characters?" + query)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert (data["total"], data["total_pages"], data["page"]) == (total, pages, page)


@pytest.mark.parametrize("query", [
    "hsk_scheme=unknown", "hsk_level=0", "hsk_level=8", "hsk_level=7–9",
    "hsk_scheme=old&hsk_level=7", "page=0", "page=-1", "page=1.5", "page_size=15",
    "page_size=0", "page_size=twenty", "sort=english_gloss", "sort=id;DROP TABLE hanzi_character",
    "order=up", "order=ASC",
])
def test_invalid_parameters_return_422(client, query):
    assert client.get("/api/characters?" + query).status_code == 422


def test_configurable_read_only_database_and_no_historical_reads(application_db, monkeypatch):
    path = application_db[0]
    before = hashlib.sha256(path.read_bytes()).digest()
    monkeypatch.setenv("CHINESELEARNING_DATABASE", str(path))
    def forbidden(*args):
        raise AssertionError("HTTP must not invoke data preparation")
    monkeypatch.setattr("chineselearning.bootstrap.prepare_rows", forbidden)
    with TestClient(create_app()) as client:
        assert client.get("/api/characters").json()["total"] == 25
        assert client.post("/api/characters").status_code == 405
    engine = open_inventory_database(path)
    try:
        with engine.begin() as connection, pytest.raises(OperationalError):
            connection.execute(hanzi_character.delete())
    finally:
        engine.dispose()
    assert hashlib.sha256(path.read_bytes()).digest() == before


def test_missing_or_incompatible_db_fails_without_initializing(tmp_path):
    missing = tmp_path / "missing.sqlite"
    with pytest.raises(ValueError, match="does not exist"):
        create_app(missing)
    assert not missing.exists()
    incompatible = tmp_path / "incompatible.sqlite"
    with sqlite3.connect(incompatible) as connection:
        connection.execute("CREATE TABLE example (id INTEGER)")
    before = incompatible.read_bytes()
    with pytest.raises(ValueError, match="not an initialized"):
        create_app(incompatible)
    assert incompatible.read_bytes() == before


def test_historical_database_is_rejected_without_modification():
    historical = Path(__file__).resolve().parents[1] / "hsk-original/hsk_vocab.sqlite"
    before = hashlib.sha256(historical.read_bytes()).digest()
    with pytest.raises(ValueError, match="not an initialized"):
        create_app(historical)
    assert hashlib.sha256(historical.read_bytes()).digest() == before


def test_inventory_snapshot_serves_all_140_characters_without_historical_source(tmp_path):
    # Restoring the application SQL is sufficient for all HTTP operations.
    root = Path(__file__).resolve().parents[1]
    path = tmp_path / "inventory.sqlite"
    with sqlite3.connect(path) as connection:
        connection.executescript((root / "data/inventory.sqlite.sql").read_text())
    with TestClient(create_app(path)) as client:
        first = client.get("/api/characters").json()
        assert (first["total"], first["total_pages"], len(first["items"])) == (140, 7, 20)
        seen = set()
        for level in range(1, 8):
            data = client.get(f"/api/characters?hsk_level={level}").json()
            assert data["total"] == 20 and data["total_pages"] == 1
            assert all(item["hsk_level"] == level for item in data["items"])
            assert all(item["english_gloss"] is None and item["usage_note"] is None
                       for item in data["items"])
            assert all(item["recognition_status"] == item["production_status"] == "not_encountered"
                       for item in data["items"])
            seen.update(item["simplified"] for item in data["items"])
        assert len(seen) == 140
