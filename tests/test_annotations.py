"""Admin annotation round trip through the test client, the JSON file, and a rebuild."""

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from chineselearning import annotations, db
from chineselearning.annotations import AnnotationError
from chineselearning.web import create_app

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

EXPECTED_FILE = """{
  "text_id": 1,
  "characters": [
    {
      "char": "愁",
      "gloss": "忧愁"
    }
  ],
  "words": [
    {
      "surface": "寒山寺",
      "gloss": "苏州城外的寺庙"
    }
  ],
  "expansions": [
    {
      "char": "乌",
      "surface": "乌鸦",
      "gloss": "黑色的鸟"
    },
    {
      "char": "月",
      "surface": "月亮",
      "gloss": null
    }
  ],
  "notes": [
    {
      "anchor": "月落乌啼",
      "note": "首句写景"
    }
  ]
}
"""


@pytest.fixture
def site(tmp_path):
    """A private copy of data/ (without annotations) and a database built from it."""
    data = tmp_path / "data"
    shutil.copytree(DATA_DIR, data)
    shutil.rmtree(data / "annotations", ignore_errors=True)
    db_path = tmp_path / "content.sqlite"
    db.build(db_path, data)
    client = TestClient(create_app(db_path, data), follow_redirects=False)
    return SimpleNamespace(data=data, db=db_path, client=client, file=data / "annotations" / "1.json")


def post(site, path, **fields):
    return site.client.post(f"/texts/1/{path}", data=fields)


def annotate_text_1(site):
    responses = [
        post(site, "characters", char="愁", gloss="忧愁"),
        post(site, "words", surface="寒山寺", gloss="苏州城外的寺庙"),
        post(site, "expansions", char="月", surface="月亮"),
        post(site, "expansions", char="乌", surface="乌鸦", gloss="黑色的鸟"),
        post(site, "notes", anchor="月落乌啼", note="首句写景"),
    ]
    assert [(r.status_code, r.headers["location"]) for r in responses] == [(303, "/texts/1")] * 5


def test_round_trip_page_file_and_rebuild(site, tmp_path):
    annotate_text_1(site)
    page = site.client.get("/texts/1").text
    for fragment in ("忧愁", "苏州城外的寺庙", "月亮", "yuè liang", "乌鸦", "黑色的鸟", "月落乌啼", "首句写景"):
        assert fragment in page
    assert site.file.read_text(encoding="utf-8") == EXPECTED_FILE

    rebuilt = tmp_path / "again.sqlite"
    counts = db.build(rebuilt, site.data)
    assert (counts["text_character"], counts["text_word"], counts["text_expansion"], counts["text_note"]) == (1, 1, 2, 1)
    conn = db.connect(rebuilt, readonly=True)
    expansions = {r["surface"]: r["word_id"] for r in conn.execute("SELECT surface, word_id FROM text_expansion WHERE text_id = 1")}
    assert expansions["月亮"] is not None and expansions["乌鸦"] is None
    assert tuple(conn.execute("SELECT word_id, gloss FROM text_word WHERE surface = '寒山寺'").fetchone()) == (None, "苏州城外的寺庙")
    assert conn.execute("SELECT gloss FROM text_character WHERE char = '愁'").fetchone()[0] == "忧愁"
    assert annotations.export(conn, 1) == json.loads(EXPECTED_FILE)
    assert TestClient(create_app(rebuilt, site.data)).get("/texts/1").text == page


def test_rewrite_of_unchanged_content_is_byte_identical(site):
    annotate_text_1(site)
    before = site.file.read_bytes()
    conn = db.connect(site.db)
    annotations.write_file(conn, 1, site.data)
    assert site.file.read_bytes() == before


@pytest.mark.parametrize(
    "path, fields, message",
    [
        ("characters", {"char": "人"}, "「人」不是正文里的单个汉字"),
        ("characters", {"char": "月落"}, "不是正文里的单个汉字"),
        ("expansions", {"char": "人", "surface": "人民"}, "「人」不是正文里的单个汉字"),
        ("expansions", {"char": "月", "surface": ""}, "请填写扩展词"),
        ("expansions", {"char": "月", "surface": "月饼饼"}, "字库里没有「月饼饼」，请填写释义"),
        ("words", {"surface": "月亮"}, "「月亮」没有出现在正文里"),
        ("words", {"surface": "寒山寺"}, "字库里没有「寒山寺」，请填写释义"),
        ("notes", {"anchor": "月落乌啼", "note": "  "}, "请填写注"),
        ("notes", {"anchor": "太阳", "note": "x"}, "「太阳」没有出现在正文里"),
    ],
)
def test_validation_returns_422_with_message(site, path, fields, message):
    r = post(site, path, **fields)
    assert r.status_code == 422
    assert message in r.text
    assert not site.file.exists()


def test_validation_keeps_submitted_values(site):
    r = post(site, "words", surface="寒山寺", gloss="")
    assert 'name="surface" placeholder="词" size="8" value="寒山寺"' in r.text
    r = post(site, "expansions", char="月", surface="月饼饼", gloss="")
    assert 'name="surface" placeholder="词" size="5" value="月饼饼"' in r.text
    assert r.text.count('value="月饼饼"') == 1


def test_duplicate_add_is_a_noop(site):
    assert post(site, "characters", char="愁", gloss="忧愁").status_code == 303
    assert post(site, "characters", char="愁", gloss="别的").status_code == 303
    assert post(site, "notes", anchor="月落乌啼", note="首句写景").status_code == 303
    assert post(site, "notes", anchor="月落乌啼", note="首句写景").status_code == 303
    conn = db.connect(site.db, readonly=True)
    assert [r[0] for r in conn.execute("SELECT gloss FROM text_character WHERE text_id = 1")] == ["忧愁"]
    assert conn.execute("SELECT count(*) FROM text_note").fetchone()[0] == 1


def test_delete_removes_row_and_rewrites_file(site):
    annotate_text_1(site)
    note_id = db.connect(site.db).execute("SELECT id FROM text_note").fetchone()[0]
    for path in ("characters/愁/delete", "expansions/月/月亮/delete", "expansions/乌/乌鸦/delete", f"notes/{note_id}/delete"):
        assert post(site, path).status_code == 303
    data = json.loads(site.file.read_text(encoding="utf-8"))
    assert (data["characters"], data["expansions"], data["notes"]) == ([], [], [])
    assert data["words"] == [{"surface": "寒山寺", "gloss": "苏州城外的寺庙"}]
    assert post(site, "words/寒山寺/delete").status_code == 303
    assert not site.file.exists()
    conn = db.connect(site.db, readonly=True)
    assert all(conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] == 0 for t in ("text_character", "text_word", "text_expansion", "text_note"))


def test_unknown_text_is_404(site):
    assert site.client.post("/texts/999/characters", data={"char": "月"}).status_code == 404
    assert site.client.post("/texts/999/notes/1/delete").status_code == 404


def test_build_rejects_bad_annotation_files(site, tmp_path):
    folder = site.data / "annotations"
    folder.mkdir()
    bad = folder / "99.json"
    bad.write_text(json.dumps({"text_id": 99, "characters": [{"char": "月"}]}), encoding="utf-8")
    with pytest.raises(AnnotationError, match="99.json: 没有 id 为 99 的课文"):
        db.build(tmp_path / "x.sqlite", site.data)
    bad.unlink()
    bad = folder / "1.json"
    bad.write_text(json.dumps({"text_id": 1, "words": [{"surface": "寒山寺", "gloss": None}]}), encoding="utf-8")
    with pytest.raises(AnnotationError, match="1.json: 字库里没有「寒山寺」"):
        db.build(tmp_path / "y.sqlite", site.data)
