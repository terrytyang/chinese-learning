"""Lessons: create, rename, delete, selections, extra words (expansions and related words), files, and import."""

import json

import pytest

from chineselearning import db, lesson_files, lessons, supplement
from chineselearning.annotations import AnnotationError

EXPECTED_FILE = """{
  "lesson_id": 1,
  "text_id": 1,
  "name": "A",
  "characters": [
    "愁"
  ],
  "words": [
    "寒山寺"
  ],
  "extra_words": [
    {
      "anchor": null,
      "surface": "半夜",
      "pinyin": "bàn yè",
      "gloss": null,
      "origin": "manual"
    },
    {
      "anchor": "乌",
      "surface": "乌鸦",
      "pinyin": "wū yā",
      "gloss": null,
      "origin": "manual"
    },
    {
      "anchor": "姑苏",
      "surface": "苏州",
      "pinyin": "sū zhōu",
      "gloss": null,
      "origin": "manual"
    },
    {
      "anchor": "月",
      "surface": "月亮",
      "pinyin": "yuè liang",
      "gloss": null,
      "origin": "manual"
    }
  ],
  "notes": [
    {
      "anchor": "月落乌啼",
      "note": "首句写景",
      "origin": "manual"
    }
  ]
}
"""


HX = {"HX-Request": "true"}


def post(site, path, **fields):
    return site.client.post(f"/texts/1/{path}", data=fields, headers=HX)


def tab(site, path, **params):
    return site.client.get(f"/texts/1/lessons/{path}", params=params, headers=HX).text


def lesson_file(site, text_id=1, lesson_id=1):
    return site.data / "lessons" / f"{text_id}-{lesson_id}.json"


def fill_lesson(site):
    assert post(site, "lessons", name="A").status_code == 200
    assert post(site, "lessons/1/characters/add", chars=["愁"]).status_code == 200
    assert post(site, "lessons/1/words/new", surface="寒山寺", step="2", gloss="苏州城外的寺庙", hsk_level="7").status_code == 200
    assert post(site, "lessons/1/expansions/add", anchor="月", surface="月亮").status_code == 200
    assert post(site, "lessons/1/expansions/add", anchor="乌", surface="乌鸦").status_code == 200  # not a dictionary word: nothing added yet
    assert post(site, "lessons/1/expansions/add", anchor="乌", surface="乌鸦", step="2", pinyin="wu1 ya1", gloss="crow").status_code == 200
    assert post(site, "lessons/1/related/add", anchor="姑苏", surface="苏州", step="2", gloss="Suzhou", hsk_level="4").status_code == 200
    assert post(site, "lessons/1/related/add", anchor="", surface="半夜").status_code == 200
    assert post(site, "lessons/1/notes/add", anchor="月落乌啼", note="首句写景").status_code == 200


def test_lesson_round_trip_file_and_rebuild(site, tmp_path):
    fill_lesson(site)
    assert lesson_file(site).read_text(encoding="utf-8") == EXPECTED_FILE
    assert '<tr id="char-愁">' in tab(site, "1/characters") and '<tr id="word-寒山寺">' in tab(site, "1/words", show="all")
    assert '<tr id="extra-乌-乌鸦">' in tab(site, "1/expansions") and '<tr id="extra-半夜">' in tab(site, "1/related") and '<tr id="note-1">' in tab(site, "1/notes")
    counts = db.build(tmp_path / "again.sqlite", site.data)
    assert (counts["lesson"], counts["lesson_character"], counts["lesson_word"], counts["lesson_extra_word"], counts["lesson_note"]) == (1, 1, 1, 4, 1)
    conn = db.connect(tmp_path / "again.sqlite", readonly=True)
    assert lesson_files.export(conn, 1) == json.loads(EXPECTED_FILE)
    assert {r["surface"]: r["word_id"] >= 10_000_000 for r in conn.execute("SELECT surface, word_id FROM lesson_extra_word")} == {"月亮": False, "乌鸦": True, "苏州": True, "半夜": False}
    assert (site.data / "supplement.tsv").read_text(encoding="utf-8").endswith("寒山寺\t\t苏州城外的寺庙\t7\n乌鸦\twū yā\tcrow\t\n苏州\t\tSuzhou\t4\n")
    assert [(e["surface"], e["kind"]) for e in lessons.load(conn, 1)["extra_words"]] == [("月亮", "expansion"), ("乌鸦", "expansion"), ("苏州", "related"), ("半夜", "related")]
    before = lesson_file(site).read_bytes()
    lesson_files.write_files(db.connect(site.db), 1, site.data)
    assert lesson_file(site).read_bytes() == before


def test_create_rename_delete(site):
    assert post(site, "lessons", name=" ").status_code == 422
    assert post(site, "lessons", name="Level 1").status_code == 200
    r = post(site, "lessons", name="Level 1")
    assert r.status_code == 422 and "a lesson named “Level 1” already exists" in r.text
    assert post(site, "lessons", name="Level 2").headers["hx-push-url"] == "/texts/1/lessons/2/characters"
    assert sorted(p.name for p in (site.data / "lessons").iterdir()) == ["1-1.json", "1-2.json"]
    assert post(site, "lessons/1/rename", name="Renamed").status_code == 200
    assert json.loads(lesson_file(site).read_text(encoding="utf-8"))["name"] == "Renamed"
    assert post(site, "lessons/1/rename", name="Level 2").status_code == 422
    assert post(site, "lessons/1/characters/add", chars=["月"]).status_code == 200
    conn = db.connect(site.db)
    with pytest.raises(AnnotationError, match="the lesson is not empty"):
        lessons.delete(conn, 1)
    assert post(site, "lessons/1/characters/月/remove").status_code == 200
    lessons.delete(conn, 1)  # deletion is a data-layer operation; the page has no delete control
    conn.commit()
    lesson_files.write_files(conn, 1, site.data)
    assert [p.name for p in (site.data / "lessons").iterdir()] == ["1-2.json"]
    assert [x["id"] for x in lessons.for_text(conn, 1)] == [2]
    with pytest.raises(AnnotationError, match="no such lesson"):
        lessons.delete(conn, 1)


def test_lesson_selection_and_links(site):
    assert post(site, "lessons", name="A").status_code == 200 and post(site, "lessons", name="B").status_code == 200
    page = site.client.get("/texts/1", params={"lesson": 2}).text
    assert '<option value="2" selected>B</option>' in page and '<a class="tab on" href="/texts/1/lessons/2/characters"' in page
    assert 'hx-post="/texts/1/lessons/2/characters/add' in page and 'hx-post="/texts/1/lessons/2/rename"' in page and 'href="/learn/1/2">Open student view' in page
    assert post(site, "lessons/2/characters/add", chars=["月"]).status_code == 200
    assert json.loads(lesson_file(site, 1, 2).read_text(encoding="utf-8"))["characters"] == ["月"]
    assert json.loads(lesson_file(site, 1, 1).read_text(encoding="utf-8"))["characters"] == []
    assert "<td>moon, month</td>" in tab(site, "2/characters").split('id="char-月"')[1].split("</tr>")[0]
    assert '<a href="/texts/1?lesson=1">A</a> <a href="/texts/1?lesson=2">B</a>' in site.client.get("/texts").text
    filtered = tab(site, "2/characters", min=3, max=7, state="any")
    assert 'hx-post="/texts/1/lessons/2/characters/progress?min=3&amp;max=7&amp;state=any"' in filtered
    assert 'hx-get="/texts/1/lessons/2/characters" hx-trigger="change" hx-push-url="true"' in filtered


def test_without_a_lesson_the_tab_routes_are_404(site):
    assert "No lessons yet" in site.client.get("/texts/1").text
    assert post(site, "lessons/1/characters/add", chars=["月"]).status_code == 404
    assert post(site, "lessons/1/notes/add", note="x").status_code == 404
    assert site.client.get("/texts/1/lessons/1/words").status_code == 404
    assert site.client.post("/texts/1/text", data={"p0": "yuè"}, headers=HX).status_code == 200  # readings are facts: no lesson needed


def test_select_requires_a_text_word_and_unselect(site):
    assert post(site, "lessons", name="A").status_code == 200
    r = post(site, "lessons/1/words/寒山寺/include", **{"in": "1"})
    assert r.status_code == 422 and "is not yet a word of the text" in r.text
    assert post(site, "lessons/1/words/new", surface="寒山寺", step="2", gloss="寺").status_code == 200  # a new word is selected at once
    assert json.loads(lesson_file(site).read_text(encoding="utf-8"))["words"] == ["寒山寺"]
    row = tab(site, "1/words", show="all", min=1, max=7).split('id="word-寒山寺"')[1].split("</tr>")[0]
    assert 'aria-label="Include in lesson" checked hx-post="/texts/1/lessons/1/words/寒山寺/include?show=all&amp;min=1&amp;max=7"' in row
    assert post(site, "lessons/1/words/寒山寺/include").status_code == 200
    assert json.loads(lesson_file(site).read_text(encoding="utf-8"))["words"] == []
    assert 'aria-label="Include in lesson" hx-post=' in tab(site, "1/words", show="excluded")


def test_extra_word_validation(site):
    assert post(site, "lessons", name="A").status_code == 200 and post(site, "lessons/1/characters/add", chars=["月"]).status_code == 200
    conn = db.connect(site.db)
    with pytest.raises(AnnotationError, match="“太阳” does not occur in the text"):
        lessons.add_extra_word(conn, 1, "太阳", anchor="太阳", gloss="sun")
    with pytest.raises(AnnotationError, match="an expansion of “月” must contain it; “太阳” does not"):
        lessons.add_extra_word(conn, 1, "太阳", anchor="月")
    with pytest.raises(AnnotationError, match="“月影” is not in the dictionary; add it to data/supplement.tsv"):
        lessons.add_extra_word(conn, 1, "月影", anchor="月")
    with pytest.raises(AnnotationError, match="a single character is a character; add it in Characters"):
        lessons.add_extra_word(conn, 1, "月", anchor="月")
    with pytest.raises(AnnotationError, match="a word is required"):
        lessons.add_extra_word(conn, 1, " ")
    supplement.add(conn, site.data, "月影", "", "", "")
    lessons.add_extra_word(conn, 1, "月影", anchor="月", gloss="moon shadow")  # a supplement word: pinyin from the dictionary, gloss contextual
    lessons.add_extra_word(conn, 1, "月亮", anchor="月", pinyin="yue4 liang5")  # pinyin as given
    lessons.add_extra_word(conn, 1, "半夜", anchor="夜半")
    rows = [tuple(r) for r in conn.execute("SELECT e.surface, e.anchor, w.source, e.pinyin, w.hsk_level, e.gloss FROM lesson_extra_word e JOIN word w ON w.id = e.word_id ORDER BY e.surface")]
    assert rows == [("半夜", "夜半", "hsk", "bàn yè", 5, None), ("月亮", "月", "hsk", "yuè liang", 3, None), ("月影", "月", "supplement", "yuè yǐng", 1, "moon shadow")]  # level derived from 月 and 影
    r = post(site, "lessons/1/related/add", anchor="太阳", surface="月亮")
    assert r.status_code == 422 and "“太阳” does not occur in the text" in r.text
    r = post(site, "lessons/1/expansions/add", anchor="月", surface="")
    assert r.status_code == 422 and "a word is required" in r.text
    r = post(site, "lessons/1/related/add", anchor="", surface="月")
    assert r.status_code == 422 and "a single character is a character; add it in Characters" in r.text


def write_lesson(site, filename, **data):
    folder = site.data / "lessons"
    folder.mkdir(exist_ok=True)
    (folder / filename).write_text(json.dumps(data), encoding="utf-8")


@pytest.mark.parametrize(
    "name, data, message",
    [
        ("9-1.json", {"lesson_id": 1, "text_id": 9, "name": "x"}, "9-1.json: no text with id 9"),
        ("1-7.json", {"lesson_id": 1, "text_id": 1, "name": "x"}, "1-7.json: the file name should be 1-1.json"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "characters": ["人"]}, "1-1.json: “人” is not a single character of the text"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "words": ["寒山寺"]}, "1-1.json: “寒山寺” is not yet a word of the text"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "words": ["月"]}, "1-1.json: a single character is a character; add it in Characters"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "extra_words": [{"surface": "月", "anchor": "月"}]}, "1-1.json: a single character is a character"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "extra_words": [{"surface": "太阳", "anchor": "月"}]}, "1-1.json: an expansion of “月” must contain it"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "extra_words": [{"surface": "月影", "anchor": "月"}]}, "1-1.json: “月影” is not in the dictionary; add it to data/supplement.tsv"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "extra_words": [{"surface": "月亮", "anchor": "太阳"}]}, "1-1.json: “太阳” does not occur in the text"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "extra_words": [{"anchor": "月"}]}, "1-1.json: missing field 'surface'"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1}, "1-1.json: missing field 'name'"),
    ],
)
def test_build_rejects_bad_lesson_files(site, tmp_path, name, data, message):
    write_lesson(site, name, **data)
    with pytest.raises(AnnotationError, match=message):
        db.build(tmp_path / "x.sqlite", site.data)


def test_two_files_claiming_one_lesson_id(site, tmp_path):
    write_lesson(site, "1-1.json", lesson_id=1, text_id=1, name="A")
    write_lesson(site, "2-1.json", lesson_id=1, text_id=2, name="B")
    with pytest.raises(AnnotationError, match="2-1.json: lesson id 1 is already taken"):
        db.build(tmp_path / "x.sqlite", site.data)
