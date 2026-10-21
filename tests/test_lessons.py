"""Lessons: create, rename, delete, selections and additions, files, and import."""

import json

import pytest

from chineselearning import db, lesson_files, lessons
from chineselearning.annotations import AnnotationError

EXPECTED_FILE = """{
  "lesson_id": 1,
  "text_id": 1,
  "name": "课",
  "characters": [
    "愁"
  ],
  "words": [
    "寒山寺"
  ],
  "expansions": [
    {
      "char": "乌",
      "surface": "乌鸦",
      "hsk_level": 7,
      "gloss": "黑色的鸟",
      "origin": "manual"
    },
    {
      "char": "月",
      "surface": "月亮",
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


def post(site, path, **fields):
    return site.client.post(f"/texts/1/{path}", data=fields)


def lesson_file(site, text_id=1, lesson_id=1):
    return site.data / "lessons" / f"{text_id}-{lesson_id}.json"


def fill_lesson(site):
    r = post(site, "lessons", name="课")
    assert (r.status_code, r.headers["location"]) == (303, "/texts/1?lesson=1#lesson")
    assert post(site, "characters/add", chars=["愁"]).status_code == 303
    assert post(site, "words/new", surface="寒山寺", gloss="苏州城外的寺庙", hsk_level="7").status_code == 303
    assert post(site, "expansions", char="月", surface="月亮").status_code == 303
    assert post(site, "expansions", char="乌", surface="乌鸦").status_code == 200  # not a master word: second form
    assert post(site, "expansions", char="乌", surface="乌鸦", step="2", gloss="黑色的鸟", hsk_level="7").status_code == 303
    assert post(site, "notes", anchor="月落乌啼", note="首句写景").status_code == 303


def test_lesson_round_trip_file_and_rebuild(site, tmp_path):
    fill_lesson(site)
    assert lesson_file(site).read_text(encoding="utf-8") == EXPECTED_FILE
    page = site.client.get("/texts/1").text
    assert '<tr id="char-愁">' in page and '<tr id="word-寒山寺">' in page and '<tr id="expansion-乌-乌鸦">' in page and '<tr id="note-1">' in page
    counts = db.build(tmp_path / "again.sqlite", site.data)
    assert (counts["lesson"], counts["lesson_character"], counts["lesson_word"], counts["lesson_expansion"], counts["lesson_note"]) == (1, 1, 1, 2, 1)
    conn = db.connect(tmp_path / "again.sqlite", readonly=True)
    assert lesson_files.export(conn, 1) == json.loads(EXPECTED_FILE)
    assert {r["surface"]: r["word_id"] is not None for r in conn.execute("SELECT surface, word_id FROM lesson_expansion")} == {"月亮": True, "乌鸦": False}
    before = lesson_file(site).read_bytes()
    lesson_files.write_files(db.connect(site.db), 1, site.data)
    assert lesson_file(site).read_bytes() == before


def test_create_rename_delete(site):
    assert post(site, "lessons", name=" ").status_code == 422
    assert post(site, "lessons", name="一级字").status_code == 303
    r = post(site, "lessons", name="一级字")
    assert r.status_code == 422 and "已有名为「一级字」的课程" in r.text
    assert post(site, "lessons", name="二级字").headers["location"] == "/texts/1?lesson=2#lesson"
    assert sorted(p.name for p in (site.data / "lessons").iterdir()) == ["1-1.json", "1-2.json"]
    assert post(site, "lessons/1/rename", name="重名").status_code == 303
    assert json.loads(lesson_file(site).read_text(encoding="utf-8"))["name"] == "重名"
    assert post(site, "lessons/1/rename", name="二级字").status_code == 422
    assert post(site, "characters/add", chars=["月"]).status_code == 303  # into lesson 1, the default
    r = post(site, "lessons/1/delete")
    assert r.status_code == 422 and "课程不是空的" in r.text
    assert post(site, "characters/月/remove").status_code == 303
    assert post(site, "lessons/1/delete").headers["location"] == "/texts/1#lesson"
    assert [p.name for p in (site.data / "lessons").iterdir()] == ["1-2.json"]
    assert [x["id"] for x in lessons.for_text(db.connect(site.db), 1)] == [2]
    assert post(site, "lessons/1/delete").status_code == 422


def test_lesson_selection_and_links(site):
    assert post(site, "lessons", name="甲").status_code == 303 and post(site, "lessons", name="乙").status_code == 303
    page = site.client.get("/texts/1", params={"lesson": 2}).text
    assert '<a href="/texts/1?lesson=2" class="current">乙</a>' in page and "<h2>学习字 <small>乙</small></h2>" in page
    assert 'action="/texts/1/characters/add?lesson=2"' in page and 'action="/texts/1/lessons/2/rename?lesson=2"' in page
    r = site.client.post("/texts/1/characters/add?lesson=2", data={"chars": ["月"]})
    assert (r.status_code, r.headers["location"]) == (303, "/texts/1?lesson=2#characters")
    assert site.client.post("/texts/1/characters/月/facts?lesson=2", data={"gloss": "月亮"}).status_code == 303
    assert json.loads(lesson_file(site, 1, 2).read_text(encoding="utf-8"))["characters"] == ["月"]
    assert json.loads(lesson_file(site, 1, 1).read_text(encoding="utf-8"))["characters"] == []
    facts = json.loads(site.file.read_text(encoding="utf-8"))
    assert facts["characters"] == [{"char": "月", "hsk_level": None, "gloss": "月亮", "origin": "manual"}]
    assert 'value="月亮"' in site.client.get("/texts/1", params={"lesson": 2}).text.split('id="char-月"')[1].split("</tr>")[0]
    assert '<a href="/texts/1?lesson=1">甲</a> <a href="/texts/1?lesson=2">乙</a>' in site.client.get("/texts").text
    page = site.client.get("/texts/1", params={"lesson": 2, "cmin": "3"}).text
    assert 'action="/texts/1/progress?lesson=2&amp;cmin=3"' in page and '<input type="hidden" name="lesson" value="2">' in page


def test_without_a_lesson_lesson_forms_are_refused(site):
    assert "还没有课程" in site.client.get("/texts/1").text
    r = post(site, "characters/add", chars=["月"])
    assert r.status_code == 422 and "请先新建课程" in r.text
    assert post(site, "notes", note="x").status_code == 422
    assert post(site, "words/new", surface="寒山寺", gloss="寺").status_code == 422
    assert post(site, "readings", p0="yuè").status_code == 303  # readings are facts: no lesson needed


def test_select_requires_a_text_word_and_unselect(site):
    assert post(site, "lessons", name="课").status_code == 303
    r = post(site, "words/add", words=["寒山寺"])
    assert r.status_code == 422 and "还不是课文的词" in r.text
    assert post(site, "words/new", surface="寒山寺", gloss="寺").status_code == 303
    assert post(site, "words/add", words=["寒山寺"]).status_code == 303
    assert json.loads(lesson_file(site).read_text(encoding="utf-8"))["words"] == ["寒山寺"]
    assert 'action="/texts/1/words/寒山寺/remove"' in site.client.get("/texts/1").text
    assert post(site, "words/寒山寺/remove").status_code == 303
    assert json.loads(lesson_file(site).read_text(encoding="utf-8"))["words"] == []
    assert 'name="words" value="寒山寺"' in site.client.get("/texts/1").text


def write_lesson(site, filename, **data):
    folder = site.data / "lessons"
    folder.mkdir(exist_ok=True)
    (folder / filename).write_text(json.dumps(data), encoding="utf-8")


@pytest.mark.parametrize(
    "name, data, message",
    [
        ("9-1.json", {"lesson_id": 1, "text_id": 9, "name": "x"}, "9-1.json: 没有 id 为 9 的课文"),
        ("1-7.json", {"lesson_id": 1, "text_id": 1, "name": "x"}, "1-7.json: 文件名应为 1-1.json"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "characters": ["人"]}, "1-1.json: 「人」不是正文里的单个汉字"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1, "name": "x", "words": ["寒山寺"]}, "1-1.json: 「寒山寺」还不是课文的词"),
        ("1-1.json", {"lesson_id": 1, "text_id": 1}, "1-1.json: 缺少字段 'name'"),
    ],
)
def test_build_rejects_bad_lesson_files(site, tmp_path, name, data, message):
    write_lesson(site, name, **data)
    with pytest.raises(AnnotationError, match=message):
        db.build(tmp_path / "x.sqlite", site.data)


def test_two_files_claiming_one_lesson_id(site, tmp_path):
    write_lesson(site, "1-1.json", lesson_id=1, text_id=1, name="甲")
    write_lesson(site, "2-1.json", lesson_id=1, text_id=2, name="乙")
    with pytest.raises(AnnotationError, match="2-1.json: 课程 id 1 已被占用"):
        db.build(tmp_path / "x.sqlite", site.data)
