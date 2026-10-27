"""Edit in place: character facts, local and linked words, extra words (anchor and level kept), 422 keeps the form open, readings for characters the master lacks."""

import json
import re

from chineselearning import db
from chineselearning.intake import intake

HX = {"HX-Request": "true"}


def get(site, path, **params):
    return site.client.get(path, params=params, headers=HX)


def post(site, path, **fields):
    return site.client.post(path, data=fields, headers=HX)


def facts(site):
    return json.loads(site.file.read_text(encoding="utf-8"))


def lesson(site):
    return json.loads((site.data / "lessons" / "1-1.json").read_text(encoding="utf-8"))


def form_of(html, action):
    return html.split(f'hx-post="{action}')[1].split("</form>")[0]


def row_of(html, row_id):
    return html.split(f'id="{row_id}"')[1].split("</tr>")[0]


def test_character_facts_gloss_and_level(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    assert {c["char"]: c["gloss"] for c in facts(site)["characters"]} == {"啼": None, "枫": None}
    row = row_of(get(site, "/texts/1/lessons/1/characters").text, "char-啼")
    assert 'hx-post="/texts/1/lessons/1/characters/啼/facts' in row and 'placeholder="gloss — not in HSK, please fill" value=""' in row and '<option value="7" selected>7–9</option>' in row
    assert post(site, "/texts/1/lessons/1/characters/啼/facts", gloss="chirp", hsk_level="5").status_code == 200
    assert {c["char"]: (c["gloss"], c["hsk_level"], c["origin"]) for c in facts(site)["characters"]} == {"啼": ("chirp", 5, "manual"), "枫": (None, None, "auto")}
    page = get(site, "/texts/1/lessons/1/characters").text
    row = row_of(page, "char-啼")
    assert 'value="chirp"' in row and '<option value="5" selected>5</option>' in row and '<span class="lvl l5">5</span>' in row
    row = row_of(page, "char-月")
    assert '<span class="lvl l1">1</span>' in row and "<td>moon, month</td>" in row and 'name="gloss"' not in row  # the master's data is not edited here
    assert post(site, "/texts/1/lessons/1/characters/月/facts", gloss="the moon").status_code == 200  # a gloss override is still a fact
    assert {c["char"]: c["gloss"] for c in facts(site)["characters"]} == {"啼": "chirp", "月": "the moon", "枫": None}
    assert "<td>the moon</td>" in row_of(get(site, "/texts/1/lessons/1/characters").text, "char-月")
    assert post(site, "/texts/1/lessons/1/characters/月/facts", gloss="").status_code == 200  # both blank: the fact row goes
    assert "月" not in {c["char"] for c in facts(site)["characters"]}
    r = post(site, "/texts/1/lessons/1/characters/啼/facts", gloss="x", hsk_level="9")
    assert r.status_code == 422 and "level must be 1 to 7" in row_of(r.text, "char-啼") and 'value="x"' in r.text


def test_edit_local_word_pinyin_gloss_keeps_level(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    assert post(site, "/texts/1/lessons/1/words/new", surface="寒山寺", step="2", gloss="寺", hsk_level="4").status_code == 200
    form = form_of(get(site, "/texts/1/lessons/1/words", show="all", edit="寒山寺").text, "/texts/1/lessons/1/words/寒山寺/save?show=all")
    assert '<input type="hidden" name="hsk_level" value="4">' in form and 'name="pinyin" aria-label="Pinyin" value="hán shān sì"' in form and 'name="gloss" aria-label="Gloss" value="寺"' in form
    assert post(site, "/texts/1/lessons/1/words/寒山寺/save", pinyin="Han2 Shan1 Si4", gloss="苏州的寺", hsk_level="4").status_code == 200
    assert facts(site)["words"] == [{"surface": "寒山寺", "pinyin": "Hán Shān Sì", "hsk_level": 4, "gloss": "苏州的寺", "origin": "manual"}]
    row = row_of(get(site, "/texts/1/lessons/1/words", show="all").text, "word-寒山寺")
    assert '<td class="zh word">寒山寺</td><td>Hán Shān Sì</td><td><span class="lvl l4">4</span></td><td>苏州的寺</td>' in row
    assert post(site, "/texts/1/lessons/1/words/寒山寺/save", pinyin="", gloss="寺", hsk_level="4").status_code == 200  # blank pinyin is prefilled again
    assert facts(site)["words"] == [{"surface": "寒山寺", "pinyin": "hán shān sì", "hsk_level": 4, "gloss": "寺", "origin": "manual"}]


def test_edit_linked_word_has_no_level_field_and_no_pinyin_override(site):
    intake(db.connect(site.db, progress_path=site.progress), 5, site.data)
    form = form_of(get(site, "/texts/5/lessons/1/words", show="all", edit="桃花").text, "/texts/5/lessons/1/words/桃花/save")
    assert 'name="hsk_level"' not in form
    pinyin = re.search(r'name="pinyin" aria-label="Pinyin" value="(.*?)"', form).group(1)
    assert post(site, "/texts/5/lessons/1/words/桃花/save", gloss="春天的花", pinyin=pinyin).status_code == 200
    stored = lambda: next(w for w in json.loads((site.data / "annotations" / "5.json").read_text(encoding="utf-8"))["words"] if w["surface"] == "桃花")  # noqa: E731
    assert stored() == {"surface": "桃花", "pinyin": None, "gloss": "春天的花", "origin": "manual"}  # the master's reading, unchanged, is not an override
    assert post(site, "/texts/5/lessons/1/words/桃花/save", gloss="春天的花", pinyin="tao2 hua1 x").status_code == 200
    assert stored()["pinyin"] == "táo huā x"
    row = row_of(get(site, "/texts/5/lessons/1/words", show="all").text, "word-桃花")
    assert '<span class="lvl l5">5</span>' in row and "<td>春天的花</td>" in row  # the master's level still shows


def test_edit_extra_word_keeps_anchor_and_level(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月亮").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor="乌", surface="乌鸦", step="2", pinyin="wū yā", gloss="crow", hsk_level="2").status_code == 200
    conn = db.connect(site.db)
    assert conn.execute("SELECT word_id FROM lesson_extra_word WHERE surface = '月亮'").fetchone()[0] is not None
    form = form_of(get(site, "/texts/1/lessons/1/expansions", edit="月-月亮").text, "/texts/1/lessons/1/expansions/月亮/save")
    assert '<input type="hidden" name="anchor" value="月"><input type="hidden" name="surface" value="月亮">' in form and 'name="hsk_level"' not in form and 'value="yuè liang"' in form
    form = form_of(get(site, "/texts/1/lessons/1/expansions", edit="乌-乌鸦").text, "/texts/1/lessons/1/expansions/乌鸦/save")
    assert '<input type="hidden" name="hsk_level" value="2">' in form
    assert post(site, "/texts/1/lessons/1/expansions/乌鸦/save", anchor="乌", surface="乌鸦", pinyin="wu1 ya1", gloss="a crow", hsk_level="2").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/月亮/save", anchor="月", surface="月亮", pinyin="yue4 liang", gloss="the moon").status_code == 200
    rows = [tuple(r) for r in conn.execute("SELECT anchor, surface, word_id IS NOT NULL, pinyin, hsk_level, gloss, origin FROM lesson_extra_word ORDER BY surface")]
    assert rows == [("乌", "乌鸦", 0, "wū yā", 2, "a crow", "manual"), ("月", "月亮", 1, "yuè liang", None, "the moon", "manual")]
    assert lesson(site)["extra_words"] == [{"anchor": "乌", "surface": "乌鸦", "pinyin": "wū yā", "hsk_level": 2, "gloss": "a crow", "origin": "manual"},
                                           {"anchor": "月", "surface": "月亮", "pinyin": "yuè liang", "gloss": "the moon", "origin": "manual"}]
    r = post(site, "/texts/1/lessons/1/expansions/乌鸦/save", anchor="乌", surface="乌鸦", pinyin="", gloss="", hsk_level="2")
    assert r.status_code == 422 and "“乌鸦” is not in the master; a gloss is required" in form_of(r.text, "/texts/1/lessons/1/expansions/乌鸦/save") and r.text.count('class="error"') == 1
    assert post(site, "/texts/1/lessons/1/expansions/乌鸦/save", anchor="", surface="乌鸦", gloss="x").status_code == 422  # no such row without the anchor
    assert lesson(site)["extra_words"][0]["gloss"] == "a crow"


def test_invalid_edit_keeps_form_open_with_422(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    assert post(site, "/texts/1/lessons/1/words/new", surface="寒山寺", step="2", gloss="寺", hsk_level="7").status_code == 200
    r = post(site, "/texts/1/lessons/1/words/寒山寺/save?show=all", pinyin="x", gloss="", hsk_level="7")
    assert r.status_code == 422 and r.text.startswith('<div id="tabs"')
    form = form_of(r.text, "/texts/1/lessons/1/words/寒山寺/save")
    assert "“寒山寺” is not in the master; a gloss is required" in form and 'name="pinyin" aria-label="Pinyin" value="x"' in form
    r = post(site, "/texts/1/lessons/1/words/寒山寺/save?show=all", pinyin="", gloss="寺", hsk_level="9")
    assert r.status_code == 422 and "level must be 1 to 7" in r.text
    assert post(site, "/texts/1/lessons/1/words/没有/save", gloss="x").status_code == 422
    assert facts(site)["words"][0]["gloss"] == "寺"


def test_local_level_stored_exported_shown_and_absent_for_linked(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    assert post(site, "/texts/1/lessons/1/words/new", surface="寒山寺", step="2", gloss="寺", hsk_level="4").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月亮", hsk_level="4").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor="乌", surface="乌鸦", step="2", pinyin="wū yā", gloss="crow", hsk_level="2").status_code == 200
    assert facts(site)["words"][0]["hsk_level"] == 4 and "hsk_level" not in lesson(site)["extra_words"][1]
    assert lesson(site)["extra_words"][0] == {"anchor": "乌", "surface": "乌鸦", "pinyin": "wū yā", "hsk_level": 2, "gloss": "crow", "origin": "manual"}
    words = get(site, "/texts/1/lessons/1/words", show="all").text
    assert '<td class="zh word">寒山寺</td><td>hán shān sì</td><td><span class="lvl l4">4</span></td>' in words
    expansions = get(site, "/texts/1/lessons/1/expansions").text
    assert '<td class="zh word">乌鸦</td><td>wū yā</td><td><span class="lvl l2">2</span></td>' in expansions
    assert '<td class="zh word">月亮</td><td>yuè liang</td><td><span class="lvl l3">3</span></td>' in expansions
    assert post(site, "/texts/1/lessons/1/words/new", surface="姑苏城", step="2", gloss="城", hsk_level="8").status_code == 422
    db.build(site.db, site.data)
    assert [tuple(r) for r in db.connect(site.db).execute("SELECT surface, hsk_level FROM lesson_extra_word ORDER BY surface")] == [("乌鸦", 2), ("月亮", None)]


def test_missing_character_reading_in_edit_mode(site):
    edit = get(site, "/texts/1/text/edit").text
    assert '<input name="p9" aria-label="Reading" placeholder="pinyin" value="">' in edit and '<span class="fixed"></span><span>霜</span>' in edit  # no intake: nothing stored yet
    assert post(site, "/texts/1/text", p9="feng1").status_code == 200
    assert "<ruby>枫<rt>fēng</rt></ruby>" in get(site, "/texts/1/text").text
    assert facts(site)["readings"] == [{"position": 9, "char": "枫", "pinyin": "fēng", "origin": "manual"}]
    assert 'name="p9" aria-label="Reading" placeholder="pinyin" value="fēng"' in get(site, "/texts/1/text/edit").text
    r = post(site, "/texts/1/text", p9=" ")
    assert r.status_code == 422 and "a reading for position 9 “枫” is required" in r.text and 'name="p9"' in r.text
