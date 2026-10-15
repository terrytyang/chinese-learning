from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlparse

from fastapi.testclient import TestClient
from markupsafe import escape
import pytest

from chineselearning.bootstrap import build_extracted_database
from chineselearning.inventory_query import open_inventory_database
from chineselearning.text_query import get_text, library_choices, list_texts
from chineselearning.web import create_app
from test_curated_text import combined

ROOT = Path(__file__).resolve().parents[1]


class LibraryPage(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.selects = {}
        self.text_ids = []
        self.current_select = None
        self.current_option = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            match = re.fullmatch(r"/texts/([0-9]+)", urlparse(attrs.get("href", "")).path)
            if match:
                self.text_ids.append(int(match.group(1)))
        if tag == "select":
            self.current_select = attrs["name"]
            self.selects[self.current_select] = {}
        if tag == "option":
            self.current_option = dict(value=attrs["value"], label="", selected="selected" in attrs)

    def handle_data(self, data):
        if self.current_option is not None:
            self.current_option["label"] += data

    def handle_endtag(self, tag):
        if tag == "option":
            option = self.current_option
            self.selects[self.current_select][option["value"]] = option
            self.current_option = None
        if tag == "select":
            self.current_select = None


@pytest.fixture(scope="module")
def filter_database(tmp_path_factory):
    directory = tmp_path_factory.mktemp("filter-library")
    spec = json.loads((ROOT / "data/text-library.json").read_text())
    spec["texts"] = [
        dict(id=20, category_ids=[5, 3, 1], title="多类文章", body="正文", author="李白", period="唐朝"),
        dict(id=2, category_ids=[2], title="文言文章", body="第一段。\n\n第二段。", author="陶渊明", period="东晋"),
        dict(id=7, category_ids=[1], title="同名作者测试", body="正文", author="李白", period="宋朝"),
        dict(id=30, category_ids=[4], title="缺少信息", body="正文", author="\t　", period=""),
        dict(id=31, category_ids=[4], title="未提供信息", body="正文", author=None, period=None),
    ]
    source = directory / "texts.json"
    source.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    database = directory / "application.sqlite"
    build_extracted_database(ROOT / "data/hsk-newest-level1.json", database, texts_path=source)
    return database


def test_many_categories_are_ordered_and_displayed_once(filter_database):
    engine = open_inventory_database(filter_database)
    try:
        records = list_texts(engine)
        assert [r["id"] for r in records] == [2, 7, 20, 30, 31]
        assert get_text(engine, 20)["categories"] == [
            dict(id=1, label="诗词"), dict(id=3, label="散文"), dict(id=5, label="讲解"),
        ]
        assert [r["id"] for r in list_texts(engine, category_id=5)] == [20]
    finally:
        engine.dispose()
    with TestClient(create_app(filter_database)) as client:
        library = client.get("/texts").text
        assert LibraryPage(library).text_ids == [2, 7, 20, 30, 31]
        assert "类别：诗词、散文、讲解" in library
        assert "类别：诗词、散文、讲解" in client.get("/texts/20").text


@pytest.mark.parametrize("params,expected", [
    ({}, [2, 7, 20, 30, 31]),
    ({"category_id": "1"}, [7, 20]),
    ({"category_id": "3"}, [20]),
    ({"category_id": "5"}, [20]),
    ({"author": "李白"}, [7, 20]),
    ({"period": "唐朝"}, [20]),
    ({"author": "陶渊明", "period": "东晋"}, [2]),
    ({"category_id": "1", "author": "李白", "period": "唐朝"}, [20]),
    ({"category_id": "2", "author": "李白"}, []),
    ({"category_id": "999"}, []),
    ({"author": "李"}, []),
    ({"period": "唐"}, []),
    ({"author": "李白' OR 1=1 --"}, []),
    ({"category_id": "", "author": "", "period": ""}, [2, 7, 20, 30, 31]),
])
def test_filters_use_exact_and_semantics_without_duplicate_texts(filter_database, params, expected):
    with TestClient(create_app(filter_database)) as client:
        response = client.get("/texts", params=params)
        assert response.status_code == 200
        page = LibraryPage(response.text)
        assert page.text_ids == expected
        assert f"共 {len(expected)} 篇文章" in response.text
        if not expected:
            assert "没有符合筛选条件的文章。" in response.text


def test_choices_are_unfiltered_ordered_distinct_and_nonblank(filter_database):
    engine = open_inventory_database(filter_database)
    try:
        choices = library_choices(engine)
        assert choices == dict(
            categories=[dict(id=i, label=label) for i, label in enumerate(("诗词", "文言", "散文", "节选", "讲解"), 1)],
            authors=["李白", "陶渊明"], periods=["东晋", "唐朝", "宋朝"],
        )
    finally:
        engine.dispose()
    with TestClient(create_app(filter_database)) as client:
        baseline = LibraryPage(client.get("/texts").text)
        response = client.get("/texts", params=dict(category_id=1, author="李白", period="唐朝"))
        filtered = LibraryPage(response.text)
        for key in ("category_id", "author", "period"):
            assert list(filtered.selects[key]) == list(baseline.selects[key])
            assert filtered.selects[key][""]["label"] == "全部"
        for key, value in (("category_id", "1"), ("author", "李白"), ("period", "唐朝")):
            assert filtered.selects[key][value]["selected"]
        assert '<form method="get"' in response.text
        assert '<button type="submit">筛选</button>' in response.text and ">重置</a>" in response.text


def test_sample_choices_exclude_unused_categories(combined):
    with TestClient(create_app(combined[0])) as client:
        page = LibraryPage(client.get("/texts?author=李白").text)
        assert list(page.selects["category_id"]) == ["", "1", "2"]
        assert len(page.selects["author"]) == 6
        assert list(page.selects["period"]) == ["", "东晋", "唐朝"]
        assert page.text_ids == [3]


@pytest.mark.parametrize("value", ["bad", "1.5", "-1", "0", " ", "1 OR 1=1", "١", "9223372036854775808"])
def test_malformed_category_filter_is_clear_422(combined, value):
    with TestClient(create_app(combined[0])) as client:
        response = client.get("/texts", params={"category_id": value})
        assert response.status_code == 422
        assert "category_id" in response.json()["detail"]


def test_unknown_filter_values_are_retained_and_escaped(filter_database):
    payload = '\"><script>alert(1)</script>&'
    with TestClient(create_app(filter_database)) as client:
        response = client.get("/texts", params=dict(category_id="999", author=payload, period=payload))
        assert response.status_code == 200
        assert "<script>" not in response.text and str(escape(payload)) in response.text
        page = LibraryPage(response.text)
        assert page.text_ids == []
        for key, value in (("category_id", "999"), ("author", payload), ("period", payload)):
            assert page.selects[key][value]["selected"]
        assert "李白" in page.selects["author"] and "东晋" in page.selects["period"]


def test_health_is_constant_and_does_no_database_or_source_work(combined, monkeypatch):
    from sqlalchemy.engine import Engine
    app = create_app(combined[0])  # Startup validation still runs before serving.
    def forbidden(*args, **kwargs):
        raise AssertionError("Liveness must not access a database or source")
    monkeypatch.setattr(Engine, "connect", forbidden)
    monkeypatch.setattr("sqlite3.connect", forbidden)
    monkeypatch.setattr("chineselearning.extraction.open_source", forbidden)
    with TestClient(app) as client:
        for _ in range(2):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("application/json")
            assert response.json() == {"status": "ok"}
            assert response.text == '{"status":"ok"}'


def test_older_text_database_requires_rebuild(tmp_path):
    import sqlite3
    database = tmp_path / "older.sqlite"
    build_extracted_database(ROOT / "data/hsk-newest-level1.json", database)
    with sqlite3.connect(database) as connection:
        connection.execute("DROP TABLE text_category_assignment")
    before = database.read_bytes()
    with pytest.raises(ValueError, match="rebuild"):
        create_app(database)
    assert database.read_bytes() == before


def test_all_five_readers_preserve_full_saved_bodies(combined):
    spec = json.loads((ROOT / "data/text-library.json").read_text())
    with TestClient(create_app(combined[0])) as client:
        assert LibraryPage(client.get("/texts").text).text_ids == [1, 2, 3, 4, 5]
        for record in spec["texts"]:
            response = client.get(f"/texts/{record['id']}")
            assert response.status_code == 200
            for field in ("title", "author", "period", "body"):
                assert str(escape(record[field])) in response.text
            assert 'class="text-body">' + str(escape(record["body"])) + '</div>' in response.text
