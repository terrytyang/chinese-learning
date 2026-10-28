"""Text facts through the admin page: round trip to data/annotations/<id>.json, validation, import errors."""

import json

import pytest
from fastapi.testclient import TestClient

from chineselearning import annotation_files, annotations, db, supplement
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
      "gloss": "忧愁",
      "origin": "manual"
    }
  ],
  "words": [
    {
      "surface": "寒山寺",
      "pinyin": null,
      "gloss": null,
      "origin": "manual"
    }
  ]
}
"""


def post(site, path, **fields):
    return site.client.post(f"/texts/1/{path}", data=fields)


def annotate_text_1(site):
    """The page adds the word (its gloss goes to the supplement) and the reading; a contextual character gloss is set in the data layer."""
    responses = [
        post(site, "lessons", name="A"),
        post(site, "lessons/1/characters/add", chars=["愁"]),
        post(site, "lessons/1/words/new", surface="寒山寺", step="2", gloss="苏州城外的寺庙", hsk_level="7"),
        post(site, "text", p2="wu4"),
    ]
    assert [r.status_code for r in responses] == [200] * 4
    conn = db.connect(site.db)
    annotations.update(conn, 1, "characters", ("愁",), {"gloss": "忧愁"})
    conn.commit()
    annotation_files.write_file(conn, 1, site.data)
    conn.close()


def test_round_trip_page_file_and_rebuild(site, tmp_path, baseline):
    annotate_text_1(site)
    page = site.client.get("/texts/1").text
    assert '<td class="gloss">忧愁</td>' in page and "<ruby>乌<rt>wù</rt></ruby>" in page
    words = site.client.get("/texts/1/lessons/1/words", params={"show": "all"}).text
    assert "苏州城外的寺庙" in words and "hán shān sì" in words
    assert site.file.read_text(encoding="utf-8") == EXPECTED_FILE

    rebuilt = tmp_path / "again.sqlite"
    counts = db.build(rebuilt, site.data)
    assert (counts["text_reading"], counts["text_character"], counts["text_word"], counts["lesson"], counts["lesson_character"], counts["lesson_word"]) == (1, 1, 1, 1, 1, 1)
    conn = db.connect(rebuilt, readonly=True)
    assert tuple(conn.execute("SELECT t.word_id, t.gloss, w.meanings FROM text_word t JOIN word w ON w.id = t.word_id WHERE surface = '寒山寺'").fetchone()) == (supplement.WORD_ID_BASE + baseline.lines, None, '["苏州城外的寺庙"]')
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
        ("lessons/1/words/new", {"surface": "月亮"}, "“月亮” does not occur in the text"),
        ("lessons/1/words/new", {"surface": "寒山寺", "step": "2", "gloss": "寺", "hsk_level": "9"}, "level must be 1 to 7, not “9”"),
        ("lessons/1/words/new", {"surface": "月", "gloss": "moon"}, "a single character is a character; add it in Characters"),
        ("lessons/1/words/new", {"surface": " "}, "a word is required"),
        ("text", {"p2": "wu"}, "the reading of “乌” must be one of wū, wù"),
        ("text", {"p7": "x"}, "position 7 is not a Han character"),
        ("text", {"p9": " "}, "a reading for position 9 “枫” is required"),
    ],
)
def test_validation_returns_422_with_message(site, path, fields, message):
    assert post(site, "lessons", name="A").status_code == 200
    r = post(site, path, **fields)
    assert r.status_code == 422 and message in r.text
    assert not site.file.exists() and "寒山寺" not in (site.data / "supplement.tsv").read_text(encoding="utf-8")


def test_validation_keeps_submitted_values(site):
    assert post(site, "lessons", name="A").status_code == 200
    r = post(site, "lessons/1/words/new", surface="寒山寺", step="2", gloss="寺", hsk_level="9")
    assert r.status_code == 422 and 'name="surface" placeholder="word" value="寒山寺"' in r.text and 'name="surface" value="寒山寺"' in r.text and 'placeholder="gloss" value="寺"' in r.text


def test_duplicate_add_is_a_noop(site):
    assert post(site, "lessons", name="A").status_code == 200
    assert post(site, "lessons/1/words/new", surface="寒山寺", step="2", gloss="寺").status_code == 200
    assert post(site, "lessons/1/words/new", surface="寒山寺", step="2", gloss="别的").status_code == 200
    conn = db.connect(site.db, readonly=True)
    assert [tuple(r) for r in conn.execute("SELECT t.gloss, w.meanings FROM text_word t JOIN word w ON w.id = t.word_id WHERE text_id = 1")] == [(None, '["寺"]')]
    assert (site.data / "supplement.tsv").read_text(encoding="utf-8").count("寒山寺") == 1


def test_delete_removes_fact_and_selection(site):
    annotate_text_1(site)
    assert post(site, "lessons/1/words/寒山寺/delete").status_code == 200
    assert json.loads(site.file.read_text(encoding="utf-8"))["words"] == []
    assert json.loads((site.data / "lessons" / "1-1.json").read_text(encoding="utf-8"))["words"] == []


def test_unknown_text_is_404(site):
    assert site.client.post("/texts/999/lessons/1/words/new", data={"surface": "月"}).status_code == 404
    assert site.client.post("/texts/999/lessons/1/words/x/delete").status_code == 404
    assert site.client.post("/texts/999/text", data={"p0": "x"}).status_code == 404


def write_facts(site, text_id, **data):
    folder = site.data / "annotations"
    folder.mkdir(exist_ok=True)
    (folder / f"{text_id}.json").write_text(json.dumps({"text_id": text_id, **data}), encoding="utf-8")


@pytest.mark.parametrize(
    "text_id, data, message",
    [
        (99, {"characters": [{"char": "月"}]}, "99.json: no text with id 99"),
        (1, {"words": [{"surface": "寒山寺", "gloss": "寺"}]}, "1.json: “寒山寺” is not in the dictionary; add it to data/supplement.tsv"),
        (1, {"words": [{"surface": "月", "gloss": "moon"}]}, "1.json: a single character is a character; add it in Characters"),
        (1, {"readings": [{"position": 3, "char": "月", "pinyin": "yuè"}]}, "1.json: position 3 is “啼”, not “月”; re-run intake"),
        (1, {"readings": [{"position": 7, "char": "，", "pinyin": "x"}]}, "1.json: position 7 is not a Han character"),
        (1, {"characters": [{"char": "愁", "origin": "guess"}]}, "1.json: origin must be"),
        (1, {"characters": [{"gloss": "x"}]}, "1.json: missing field 'char'"),
    ],
)
def test_build_rejects_bad_facts_files(site, tmp_path, text_id, data, message):
    write_facts(site, text_id, **data)
    with pytest.raises(AnnotationError, match=message):
        db.build(tmp_path / "x.sqlite", site.data)


def test_import_defaults_origin_and_keeps_character_facts(site, tmp_path):
    with (site.data / "supplement.tsv").open("a", encoding="utf-8") as f:
        f.write("寒山寺\t\t\t\n")
    write_facts(site, 1, characters=[{"char": "啼", "gloss": "鸟叫"}], words=[{"surface": "寒山寺", "gloss": "寺", "pinyin": "han2 shan1 si4"}])
    db.build(tmp_path / "a.sqlite", site.data)
    conn = db.connect(tmp_path / "a.sqlite", readonly=True)
    assert tuple(conn.execute("SELECT gloss, origin FROM text_character").fetchone()) == ("鸟叫", "manual")
    assert tuple(conn.execute("SELECT origin, pinyin FROM text_word").fetchone()) == ("manual", "hán shān sì")
    assert annotations.load(conn, 1)["characters"][0]["gloss"] == "鸟叫"
