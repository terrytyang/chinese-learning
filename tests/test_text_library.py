import hashlib
import json
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient
from markupsafe import escape
import pytest

from chineselearning.bootstrap import build_extracted_database
from chineselearning.text_query import get_text, list_texts
from chineselearning.inventory_query import open_inventory_database
from chineselearning.web import create_app
from test_curated_text import BODY, combined

ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "data/hsk-newest-level1.json"


def test_library_and_plain_reader_show_poem_and_chinese_labels(combined, monkeypatch):
    database = combined[0]
    before = hashlib.sha256(database.read_bytes()).digest()
    def forbidden(*args, **kwargs):
        raise AssertionError("Serving text must not build or import data")
    monkeypatch.setattr("chineselearning.bootstrap.build_extracted_database", forbidden)
    monkeypatch.setattr("chineselearning.curated_text.read_rows", forbidden)
    monkeypatch.setattr("chineselearning.extraction.open_source", forbidden)
    with TestClient(create_app(database)) as client:
        library = client.get("/texts")
        assert library.status_code == 200
        assert library.headers["content-type"].startswith("text/html")
        assert 'lang="zh-CN"' in library.text
        assert 'href="http://testserver/texts/1"' in library.text
        for value in ("标题：", "类别：诗词", "作者：张继", "年代：唐朝", "枫桥夜泊"):
            assert value in library.text
        reader = client.get("/texts/1")
        assert reader.status_code == 200
        assert '<h1>标题：枫桥夜泊</h1>' in reader.text
        assert 'class="text-body">' + BODY + '</div>' in reader.text
        assert 'href="http://testserver/texts"' in reader.text and "返回文章库" in reader.text
        assert "类别：诗词" in reader.text and "作者：张继" in reader.text and "年代：唐朝" in reader.text
        css = client.get("/static/texts.css")
        assert css.status_code == 200 and "white-space: pre-wrap" in css.text
        assert "overflow-wrap: anywhere" in css.text
        assert client.get("/").status_code == 200
        assert "20 characters from each first-appearance band" in client.get("/").text
        assert client.get("/api/characters").json()["total"] == 248
        assert client.post("/texts/1").status_code == 405
    assert hashlib.sha256(database.read_bytes()).digest() == before


@pytest.mark.parametrize("text_id", [0, -1, 999, 999999999999999999999999999999])
def test_unknown_text_is_404(combined, text_id):
    with TestClient(create_app(combined[0])) as client:
        assert client.get(f"/texts/{text_id}").status_code == 404


@pytest.mark.parametrize("legacy", [False, True])
def test_empty_library_in_fresh_and_pre_library_databases(tmp_path, legacy):
    database = tmp_path / "empty.sqlite"
    build_extracted_database(EXTRACTED, database)
    if legacy:
        with sqlite3.connect(database) as connection:
            connection.execute("DROP TABLE text_category_assignment")
            connection.execute("DROP TABLE library_text")
            connection.execute("DROP TABLE text_category")
    with TestClient(create_app(database)) as client:
        response = client.get("/texts")
        assert response.status_code == 200 and "暂无文章。" in response.text
        assert client.get("/texts/1").status_code == 404
        assert client.get("/api/characters").json()["total"] == 248


def test_order_escaping_optional_metadata_and_hidden_notes(tmp_path):
    spec = json.loads((ROOT / "data/text-library.json").read_text())
    spec["categories"][0]["label"] = '<em>诗词</em>'
    spec["texts"] = [
        dict(id=20, category_ids=[1], title='<img src=x onerror="alert(1)">',
             author='<script>author</script>', period='<b>period</b>',
             body='<script>alert("x")</script>\n保留标点，换行。', notes="SECRET_EDITORIAL_NOTE"),
        dict(id=2, category_ids=[1], title="先列出", body="  正文\n\n第二行　", author=None, period=""),
    ]
    selection = tmp_path / "texts.json"
    selection.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    database = tmp_path / "texts.sqlite"
    build_extracted_database(EXTRACTED, database, texts_path=selection)
    engine = open_inventory_database(database)
    try:
        assert [record["id"] for record in list_texts(engine)] == [2, 20]
        assert get_text(engine, 2)["body"] == spec["texts"][1]["body"]
        assert "notes" not in get_text(engine, 20)
        assert get_text(engine, 999) is None
    finally:
        engine.dispose()
    with TestClient(create_app(database)) as client:
        library = client.get("/texts").text
        assert library.index("/texts/2") < library.index("/texts/20")
        for field in ("title", "author", "period"):
            assert str(escape(spec["texts"][0][field])) in library
        assert str(escape(spec["categories"][0]["label"])) in library
        reader = client.get("/texts/20").text
        for field in ("title", "author", "period", "body"):
            assert str(escape(spec["texts"][0][field])) in reader
        assert "<script>" not in reader and "<img " not in reader and "<em>" not in reader
        assert "SECRET_EDITORIAL_NOTE" not in reader and "SECRET_EDITORIAL_NOTE" not in library
        minimal = client.get("/texts/2").text
        assert "作者：" not in minimal and "年代：" not in minimal
        assert "None" not in minimal and "Not provided" not in minimal
        assert 'class="text-body">  正文\n\n第二行　</div>' in minimal
