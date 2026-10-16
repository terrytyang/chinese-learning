"""Edit in place, levels for local words, and free-text readings for characters absent from the master."""

import json

from chineselearning import db
from chineselearning.intake import intake


def post(site, path, **fields):
    return site.client.post(f"/texts/1/{path}", data=fields)


def file(site):
    return json.loads(site.file.read_text(encoding="utf-8"))


def test_edit_character_gloss_sets_origin_manual(site):
    intake(db.connect(site.db), 1, site.data)
    assert file(site)["characters"][0] == {"char": "啼", "gloss": None, "origin": "auto"}
    page = site.client.get("/texts/1", params={"edit": "characters:啼"}).text
    assert 'action="/texts/1/characters/啼/update"' in page and '<input name="gloss" size="20" value="">' in page and ">取消</a>" in page
    assert post(site, "characters/啼/update", gloss="鸟叫").status_code == 303
    assert file(site)["characters"][0] == {"char": "啼", "gloss": "鸟叫", "origin": "manual"}
    assert "鸟叫" in site.client.get("/texts/1").text and 'action="/texts/1/characters/啼/update"' not in site.client.get("/texts/1").text


def test_edit_local_word_pinyin_gloss_level(site):
    assert post(site, "words", surface="寒山寺", gloss="寺", hsk_level="7").status_code == 303
    page = site.client.get("/texts/1", params={"edit": "words:寒山寺"}).text
    assert '<input name="pinyin" size="12" value="hán shān sì">' in page and '<option value="7" selected>7–9</option>' in page
    assert post(site, "words/寒山寺/update", pinyin="Hán Shān Sì", gloss="苏州的寺", hsk_level="5").status_code == 303
    assert file(site)["words"] == [{"surface": "寒山寺", "pinyin": "Hán Shān Sì", "hsk_level": 5, "gloss": "苏州的寺", "origin": "manual"}]
    page = site.client.get("/texts/1").text
    assert '<td class="word">寒山寺</td><td>Hán Shān Sì</td><td>5</td><td>苏州的寺</td>' in page
    assert post(site, "words/寒山寺/update", pinyin="", gloss="寺", hsk_level="").status_code == 303  # blank pinyin is prefilled again
    assert file(site)["words"] == [{"surface": "寒山寺", "pinyin": "hán shān sì", "hsk_level": None, "gloss": "寺", "origin": "manual"}]


def test_edit_linked_word_has_no_level_field(site):
    intake(db.connect(site.db), 5, site.data)
    page = site.client.get("/texts/5", params={"edit": "words:桃花"}).text
    assert 'action="/texts/5/words/桃花/update"' in page and 'name="hsk_level"' not in page.split('action="/texts/5/words/桃花/update"')[1].split("</form>")[0]
    assert site.client.post("/texts/5/words/桃花/update", data={"gloss": "春天的花", "pinyin": "", "hsk_level": "3"}).status_code == 303
    row = next(w for w in json.loads((site.data / "annotations" / "5.json").read_text(encoding="utf-8"))["words"] if w["surface"] == "桃花")
    assert row == {"surface": "桃花", "pinyin": None, "gloss": "春天的花", "origin": "manual"}
    assert "<td>5</td><td>春天的花</td>" in site.client.get("/texts/5").text  # the master's level still shows


def test_edit_expansion_surface_reresolves(site):
    assert post(site, "expansions", char="月", surface="月亮").status_code == 303
    conn = db.connect(site.db)
    assert conn.execute("SELECT word_id FROM text_expansion WHERE surface = '月亮'").fetchone()[0] is not None
    page = site.client.get("/texts/1", params={"edit": "expansions:月/月亮"}).text
    assert 'action="/texts/1/expansions/月/月亮/update"' in page and '<input name="surface" size="6" value="月亮">' in page
    assert post(site, "expansions/月/月亮/update", surface="月影", gloss="月亮的影子", hsk_level="6").status_code == 303
    rows = [tuple(r) for r in db.connect(site.db).execute("SELECT char, surface, word_id, hsk_level, gloss, origin FROM text_expansion")]
    assert rows == [("月", "月影", None, 6, "月亮的影子", "manual")]
    assert file(site)["expansions"] == [{"char": "月", "surface": "月影", "hsk_level": 6, "gloss": "月亮的影子", "origin": "manual"}]
    assert post(site, "expansions/月/月影/update", surface="月亮", gloss="", hsk_level="2").status_code == 303
    rows = [tuple(r) for r in db.connect(site.db).execute("SELECT surface, word_id, hsk_level FROM text_expansion")]
    assert rows[0][0] == "月亮" and rows[0][1] is not None and rows[0][2] is None
    assert "hsk_level" not in file(site)["expansions"][0]


def test_edit_note(site):
    assert post(site, "notes", anchor="月落乌啼", note="首句写景").status_code == 303
    note_id = db.connect(site.db).execute("SELECT id FROM text_note").fetchone()[0]
    page = site.client.get("/texts/1", params={"edit": f"notes:{note_id}"}).text
    assert f'action="/texts/1/notes/{note_id}/update"' in page and '<input name="note" size="40" value="首句写景">' in page
    assert post(site, f"notes/{note_id}/update", anchor="江枫渔火", note="第二句").status_code == 303
    assert file(site)["notes"] == [{"anchor": "江枫渔火", "note": "第二句", "origin": "manual"}]


def test_invalid_edit_keeps_form_open_with_422(site):
    assert post(site, "words", surface="寒山寺", gloss="寺", hsk_level="7").status_code == 303
    r = post(site, "words/寒山寺/update", pinyin="x", gloss="", hsk_level="7")
    assert r.status_code == 422 and "字库里没有「寒山寺」，请填写释义" in r.text
    assert 'action="/texts/1/words/寒山寺/update"' in r.text and '<input name="pinyin" size="12" value="x">' in r.text
    r = post(site, "words/寒山寺/update", pinyin="", gloss="寺", hsk_level="9")
    assert r.status_code == 422 and "级只能是 1 到 7" in r.text
    assert post(site, "notes/1/update", note="x").status_code == 422
    assert post(site, "words/没有/update", gloss="x").status_code == 422
    assert file(site)["words"][0]["gloss"] == "寺"


def test_local_level_stored_exported_shown_and_absent_for_linked(site):
    assert post(site, "words", surface="寒山寺", gloss="寺", hsk_level="4").status_code == 303
    assert post(site, "expansions", char="月", surface="月亮", hsk_level="4").status_code == 303
    assert post(site, "expansions", char="乌", surface="乌鸦", gloss="鸟", hsk_level="2").status_code == 303
    data = file(site)
    assert data["words"][0]["hsk_level"] == 4 and "hsk_level" not in data["expansions"][1]
    assert data["expansions"][0] == {"char": "乌", "surface": "乌鸦", "hsk_level": 2, "gloss": "鸟", "origin": "manual"}
    page = site.client.get("/texts/1").text
    assert '<td class="word">寒山寺</td><td>hán shān sì</td><td>4</td>' in page and '<td class="word">乌鸦</td><td></td><td>2</td>' in page
    assert '<td class="word">月亮</td><td>yuè liang</td><td>3</td>' in page
    assert post(site, "words", surface="姑苏城", gloss="城", hsk_level="8").status_code == 422
    rebuilt = db.build(site.db, site.data)
    assert rebuilt["text_word"] == 1
    assert [tuple(r) for r in db.connect(site.db).execute("SELECT surface, hsk_level FROM text_expansion ORDER BY surface")] == [("乌鸦", 2), ("月亮", None)]


def test_missing_character_pinyin_set_and_cleared(site):
    page = site.client.get("/texts/1").text
    assert '<input type="hidden" name="char" value="枫">\n            <input name="pinyin" placeholder="拼音" size="6" value="">' in page
    assert post(site, "readings", char="枫", pinyin="fēng").status_code == 303
    page = site.client.get("/texts/1").text
    assert '<span class="pinyin">fēng</span> <small>指定</small>' in page and 'action="/texts/1/readings/枫/delete"' in page
    assert 'name="pinyin" placeholder="拼音" size="6" value="fēng"' in page
    assert file(site)["readings"] == [{"char": "枫", "pinyin": "fēng", "position": None, "origin": "manual"}]
    assert post(site, "readings", char="枫", pinyin=" ").status_code == 422
    assert post(site, "readings/枫/delete").status_code == 303
    assert '<span class="pinyin">—</span> <small>无</small>' in site.client.get("/texts/1").text and not site.file.exists()
