"""Text facts through the admin page: round trip to data/annotations/<id>.json, validation, import errors."""

import json

import pytest
from fastapi.testclient import TestClient

from chineselearning import annotation_files, annotations, db
from chineselearning.annotations import AnnotationError
from chineselearning.web import create_app

EXPECTED_FILE = """{
  "text_id": 1,
  "readings": [
    {
      "position": 2,
      "char": "乌",
      "pinyin": "wù",
      "origin": "manual"
    }
  ],
  "characters": [
    {
      "char": "愁",
      "hsk_level": null,
      "gloss": "忧愁",
      "origin": "manual"
    }
  ],
  "words": [
    {
      "surface": "寒山寺",
      "pinyin": "hán shān sì",
      "hsk_level": 7,
      "gloss": "苏州城外的寺庙",
      "origin": "manual"
    }
  ]
}
"""


def post(site, path, **fields):
    return site.client.post(f"/texts/1/{path}", data=fields)


def annotate_text_1(site):
    responses = [
        post(site, "lessons", name="课"),
        post(site, "characters/add", chars=["愁"]),
        post(site, "characters/愁/facts", gloss="忧愁"),
        post(site, "words/new", surface="寒山寺", gloss="苏州城外的寺庙", hsk_level="7"),
        post(site, "readings", p2="wù"),
    ]
    assert [r.status_code for r in responses] == [303] * 5


def test_round_trip_page_file_and_rebuild(site, tmp_path):
    annotate_text_1(site)
    page = site.client.get("/texts/1").text
    for fragment in ('value="忧愁"', "苏州城外的寺庙", "hán shān sì", "<ruby>乌<rt>wù</rt></ruby>"):
        assert fragment in page
    assert site.file.read_text(encoding="utf-8") == EXPECTED_FILE

    rebuilt = tmp_path / "again.sqlite"
    counts = db.build(rebuilt, site.data)
    assert (counts["text_reading"], counts["text_character"], counts["text_word"], counts["lesson"], counts["lesson_character"], counts["lesson_word"]) == (1, 1, 1, 1, 1, 1)
    conn = db.connect(rebuilt, readonly=True)
    assert tuple(conn.execute("SELECT word_id, gloss FROM text_word WHERE surface = '寒山寺'").fetchone()) == (None, "苏州城外的寺庙")
    assert annotation_files.export(conn, 1) == json.loads(EXPECTED_FILE)
    assert TestClient(create_app(rebuilt, site.data, site.progress)).get("/texts/1").text == page


def test_rewrite_of_unchanged_content_is_byte_identical(site):
    annotate_text_1(site)
    before = site.file.read_bytes()
    annotation_files.write_file(db.connect(site.db), 1, site.data)
    assert site.file.read_bytes() == before


@pytest.mark.parametrize(
    "path, fields, message",
    [
        ("words/new", {"surface": "月亮"}, "「月亮」没有出现在正文里"),
        ("words/new", {"surface": "寒山寺"}, "字库里没有「寒山寺」，请填写释义"),
        ("words/new", {"surface": "寒山寺", "gloss": "寺", "hsk_level": "9"}, "级只能是 1 到 7"),
        ("readings", {"p2": "wu"}, "「乌」的读音只能是 wū、wù"),
        ("readings", {"p7": "x"}, "位置 7 不是汉字"),
        ("readings", {"p9": " "}, "位置 9「枫」的读音不能为空"),
    ],
)
def test_validation_returns_422_with_message(site, path, fields, message):
    assert post(site, "lessons", name="课").status_code == 303
    r = post(site, path, **fields)
    assert r.status_code == 422 and message in r.text
    assert not site.file.exists()


def test_validation_keeps_submitted_values(site):
    assert post(site, "lessons", name="课").status_code == 303
    r = post(site, "words/new", surface="寒山寺", gloss="")
    assert 'name="surface" placeholder="词" size="8" value="寒山寺"' in r.text


def test_duplicate_add_is_a_noop(site):
    assert post(site, "lessons", name="课").status_code == 303
    assert post(site, "words/new", surface="寒山寺", gloss="寺").status_code == 303
    assert post(site, "words/new", surface="寒山寺", gloss="别的").status_code == 303
    conn = db.connect(site.db, readonly=True)
    assert [r[0] for r in conn.execute("SELECT gloss FROM text_word WHERE text_id = 1")] == ["寺"]


def test_delete_removes_fact_and_selection(site):
    annotate_text_1(site)
    assert post(site, "words/寒山寺/delete").status_code == 303
    assert json.loads(site.file.read_text(encoding="utf-8"))["words"] == []
    assert json.loads((site.data / "lessons" / "1-1.json").read_text(encoding="utf-8"))["words"] == []


def test_unknown_text_is_404(site):
    assert site.client.post("/texts/999/words/new", data={"surface": "月"}).status_code == 404
    assert site.client.post("/texts/999/words/x/delete").status_code == 404


def write_facts(site, text_id, **data):
    folder = site.data / "annotations"
    folder.mkdir(exist_ok=True)
    (folder / f"{text_id}.json").write_text(json.dumps({"text_id": text_id, **data}), encoding="utf-8")


@pytest.mark.parametrize(
    "text_id, data, message",
    [
        (99, {"characters": [{"char": "月"}]}, "99.json: 没有 id 为 99 的课文"),
        (1, {"words": [{"surface": "寒山寺", "gloss": None}]}, "1.json: 字库里没有「寒山寺」"),
        (1, {"readings": [{"position": 3, "char": "月", "pinyin": "yuè"}]}, "1.json: 位置 3 的字是「啼」，不是「月」；请重新 intake"),
        (1, {"readings": [{"position": 7, "char": "，", "pinyin": "x"}]}, "1.json: 位置 7 不是汉字"),
        (1, {"characters": [{"char": "愁", "origin": "guess"}]}, "1.json: origin 必须是"),
        (1, {"characters": [{"gloss": "x"}]}, "1.json: 缺少字段 'char'"),
    ],
)
def test_build_rejects_bad_facts_files(site, tmp_path, text_id, data, message):
    write_facts(site, text_id, **data)
    with pytest.raises(AnnotationError, match=message):
        db.build(tmp_path / "x.sqlite", site.data)


def test_import_defaults_origin_and_keeps_character_facts(site, tmp_path):
    write_facts(site, 1, characters=[{"char": "啼", "hsk_level": 7, "gloss": "鸟叫"}], words=[{"surface": "寒山寺", "gloss": "寺"}])
    db.build(tmp_path / "a.sqlite", site.data)
    conn = db.connect(tmp_path / "a.sqlite", readonly=True)
    assert tuple(conn.execute("SELECT hsk_level, gloss, origin FROM text_character").fetchone()) == (7, "鸟叫", "manual")
    assert tuple(conn.execute("SELECT origin, pinyin FROM text_word").fetchone()) == ("manual", "hán shān sì")
    assert annotations.load(conn, 1)["characters"][0]["gloss"] == "鸟叫"
