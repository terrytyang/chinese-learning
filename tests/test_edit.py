"""Edit in place, levels for local words, numbered pinyin, and free-text readings for characters absent from the master."""

import json

from chineselearning import db
from chineselearning.intake import intake


def post(site, path, **fields):
    return site.client.post(f"/texts/1/{path}", data=fields)


def facts(site):
    return json.loads(site.file.read_text(encoding="utf-8"))


def lesson(site):
    return json.loads((site.data / "lessons" / "1-1.json").read_text(encoding="utf-8"))


def test_character_facts_gloss_and_level(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    assert {c["char"]: c["gloss"] for c in facts(site)["characters"]} == {"啼": None, "枫": None}
    row = site.client.get("/texts/1").text.split('id="char-啼"')[1].split("</tr>")[0]
    assert 'action="/texts/1/characters/啼/facts"' in row and 'name="hsk_level" form="facts-啼"' in row and '<option value="" selected>—</option>' in row
    assert post(site, "characters/啼/facts", gloss="chirp", hsk_level="5").status_code == 303
    assert {c["char"]: (c["gloss"], c["hsk_level"], c["origin"]) for c in facts(site)["characters"]} == {"啼": ("chirp", 5, "manual"), "枫": (None, None, "auto")}
    assert post(site, "characters/月/facts", gloss="the moon").status_code == 303  # a gloss override for a character the master knows
    assert {c["char"]: c["gloss"] for c in facts(site)["characters"]} == {"啼": "chirp", "月": "the moon", "枫": None}
    page = site.client.get("/texts/1").text
    row = page.split('id="char-月"')[1].split("</tr>")[0]
    assert "<td>1</td>" in row and "moon, month" in row and 'value="the moon"' in row and 'name="hsk_level"' not in row
    assert '<option value="5" selected>5</option>' in page.split('id="char-啼"')[1].split("</tr>")[0]
    assert post(site, "characters/月/facts", gloss="").status_code == 303  # both blank: the fact row goes
    assert "月" not in {c["char"] for c in facts(site)["characters"]}


def test_edit_local_word_pinyin_gloss_level(site):
    assert post(site, "lessons", name="A").status_code == 303
    assert post(site, "words/new", surface="寒山寺", gloss="寺", hsk_level="7").status_code == 303
    page = site.client.get("/texts/1", params={"edit": "words:寒山寺"}).text
    assert 'action="/texts/1/words/寒山寺/facts"' in page and '<input name="pinyin" size="12" value="hán shān sì">' in page and '<option value="7" selected>7–9</option>' in page
    assert post(site, "words/寒山寺/facts", pinyin="Han2 Shan1 Si4", gloss="苏州的寺", hsk_level="5").status_code == 303
    assert facts(site)["words"] == [{"surface": "寒山寺", "pinyin": "Hán Shān Sì", "hsk_level": 5, "gloss": "苏州的寺", "origin": "manual"}]
    assert '<td class="word">寒山寺</td><td>Hán Shān Sì</td><td>5</td><td>苏州的寺</td>' in site.client.get("/texts/1").text
    assert post(site, "words/寒山寺/facts", pinyin="", gloss="寺", hsk_level="").status_code == 303  # blank pinyin is prefilled again
    assert facts(site)["words"] == [{"surface": "寒山寺", "pinyin": "hán shān sì", "hsk_level": None, "gloss": "寺", "origin": "manual"}]


def test_edit_linked_word_has_no_level_field(site):
    intake(db.connect(site.db, progress_path=site.progress), 5, site.data)
    page = site.client.get("/texts/5", params={"edit": "words:桃花"}).text
    form = page.split('action="/texts/5/words/桃花/facts"')[1].split("</form>")[0]
    assert 'name="hsk_level"' not in form
    assert site.client.post("/texts/5/words/桃花/facts", data={"gloss": "春天的花", "pinyin": "", "hsk_level": "3"}).status_code == 303
    row = next(w for w in json.loads((site.data / "annotations" / "5.json").read_text(encoding="utf-8"))["words"] if w["surface"] == "桃花")
    assert row == {"surface": "桃花", "pinyin": None, "gloss": "春天的花", "origin": "manual"}
    assert "<td>5</td><td>春天的花</td>" in site.client.get("/texts/5").text  # the master's level still shows


def test_edit_extra_word_surface_reresolves_and_keeps_anchor(site):
    assert post(site, "lessons", name="A").status_code == 303
    assert post(site, "extra-words", anchor="月", surface="月亮").status_code == 303
    assert db.connect(site.db).execute("SELECT word_id FROM lesson_extra_word WHERE surface = '月亮'").fetchone()[0] is not None
    page = site.client.get("/texts/1", params={"edit": "extra_words:月-月亮"}).text
    assert 'action="/texts/1/extra-words/月亮/update"' in page and '<input name="surface" size="6" value="月亮">' in page and '<input name="pinyin" size="12" value="yuè liang">' in page
    assert post(site, "extra-words/月亮/update", anchor="月", surface="月影", pinyin="", gloss="moon shadow", hsk_level="6").status_code == 303
    rows = [tuple(r) for r in db.connect(site.db).execute("SELECT anchor, surface, word_id, pinyin, hsk_level, gloss, origin FROM lesson_extra_word")]
    assert rows == [("月", "月影", None, "yuè yǐng", 6, "moon shadow", "manual")]
    assert lesson(site)["extra_words"] == [{"anchor": "月", "surface": "月影", "pinyin": "yuè yǐng", "hsk_level": 6, "gloss": "moon shadow", "origin": "manual"}]
    assert post(site, "extra-words/月影/update", anchor="月", surface="月亮", pinyin="yue4 liang", gloss="", hsk_level="2").status_code == 303
    assert lesson(site)["extra_words"] == [{"anchor": "月", "surface": "月亮", "pinyin": "yuè liang", "gloss": None, "origin": "manual"}]
    r = post(site, "extra-words/月亮/update", anchor="月", surface="太阳", gloss="sun")
    assert r.status_code == 422 and "an expansion of “月” must contain it" in r.text and 'action="/texts/1/extra-words/月亮/update"' in r.text
    assert post(site, "extra-words/月亮/update", anchor="", surface="月光", gloss="x").status_code == 422  # no such row without the anchor


def test_edit_note(site):
    assert post(site, "lessons", name="A").status_code == 303
    assert post(site, "notes", anchor="月落乌啼", note="首句写景").status_code == 303
    note_id = db.connect(site.db).execute("SELECT id FROM lesson_note").fetchone()[0]
    page = site.client.get("/texts/1", params={"edit": f"notes:{note_id}"}).text
    assert f'action="/texts/1/notes/{note_id}/update"' in page and '<input name="note" size="40" value="首句写景">' in page
    assert post(site, f"notes/{note_id}/update", anchor="江枫渔火", note="第二句").status_code == 303
    assert lesson(site)["notes"] == [{"anchor": "江枫渔火", "note": "第二句", "origin": "manual"}]


def test_invalid_edit_keeps_form_open_with_422(site):
    assert post(site, "lessons", name="A").status_code == 303
    assert post(site, "words/new", surface="寒山寺", gloss="寺", hsk_level="7").status_code == 303
    r = post(site, "words/寒山寺/facts", pinyin="x", gloss="", hsk_level="7")
    assert r.status_code == 422 and "“寒山寺” is not in the master; a gloss is required" in r.text
    assert 'action="/texts/1/words/寒山寺/facts"' in r.text and '<input name="pinyin" size="12" value="x">' in r.text
    r = post(site, "words/寒山寺/facts", pinyin="", gloss="寺", hsk_level="9")
    assert r.status_code == 422 and "level must be 1 to 7" in r.text
    assert post(site, "notes/1/update", note="x").status_code == 422
    assert post(site, "words/没有/facts", gloss="x").status_code == 422
    assert facts(site)["words"][0]["gloss"] == "寺"


def test_local_level_stored_exported_shown_and_absent_for_linked(site):
    assert post(site, "lessons", name="A").status_code == 303
    assert post(site, "words/new", surface="寒山寺", gloss="寺", hsk_level="4").status_code == 303
    assert post(site, "extra-words", anchor="月", surface="月亮", hsk_level="4").status_code == 303
    assert post(site, "extra-words", anchor="乌", surface="乌鸦", step="2", pinyin="wū yā", gloss="crow", hsk_level="2").status_code == 303
    assert facts(site)["words"][0]["hsk_level"] == 4 and "hsk_level" not in lesson(site)["extra_words"][1]
    assert lesson(site)["extra_words"][0] == {"anchor": "乌", "surface": "乌鸦", "pinyin": "wū yā", "hsk_level": 2, "gloss": "crow", "origin": "manual"}
    page = site.client.get("/texts/1").text
    assert '<td class="word">寒山寺</td><td>hán shān sì</td><td>4</td>' in page and '<td class="word">乌鸦</td><td>wū yā</td><td>2</td>' in page
    assert '<td class="word">月亮</td><td>yuè liang</td><td>3</td>' in page
    assert post(site, "words/new", surface="姑苏城", gloss="城", hsk_level="8").status_code == 422
    db.build(site.db, site.data)
    assert [tuple(r) for r in db.connect(site.db).execute("SELECT surface, hsk_level FROM lesson_extra_word ORDER BY surface")] == [("乌鸦", 2), ("月亮", None)]


def test_missing_character_reading_in_edit_mode(site):
    edit = site.client.get("/texts/1", params={"edit": "pinyin"}).text
    assert '<ruby>枫<rt><input name="p9" size="5" value=""></rt></ruby>' in edit and "<ruby>霜<rt></rt></ruby>" in edit  # no intake: nothing stored yet
    assert post(site, "readings", p9="feng1").status_code == 303
    assert "<ruby>枫<rt>fēng</rt></ruby>" in site.client.get("/texts/1").text
    assert facts(site)["readings"] == [{"position": 9, "char": "枫", "pinyin": "fēng", "origin": "manual"}]
    assert '<ruby>枫<rt><input name="p9" size="5" value="fēng"></rt></ruby>' in site.client.get("/texts/1", params={"edit": "pinyin"}).text
    r = post(site, "readings", p9=" ")
    assert r.status_code == 422 and "a reading for position 9 “枫” is required" in r.text and 'name="p9"' in r.text
