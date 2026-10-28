"""Edit in place: supplement characters on the Characters tab, contextual pinyin and gloss on words and extra words, 422 keeps the form open, readings for characters the dictionary lacks."""

import json
import re

from chineselearning import db, supplement
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


def supplement_text(site):
    return (site.data / "supplement.tsv").read_text(encoding="utf-8")


def form_of(html, action):
    return html.split(f'hx-post="{action}')[1].split("</form>")[0]


def row_of(html, row_id):
    return html.split(f'id="{row_id}"')[1].split("</tr>")[0]


def add_text_6(site):
    """A text with a character the dictionary lacks (龘); intake refuses it, the page still shows it."""
    (site.data / "texts" / "099-龘.md").write_text("id: 99\ntitle: 龘\ntags: 诗词\n\n龘飞\n", encoding="utf-8")
    db.build(site.db, site.data)


def test_characters_tab_shows_dictionary_data_for_supplement_characters(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    assert facts(site)["characters"] == []
    page = get(site, "/texts/1/lessons/1/characters").text
    row = row_of(page, "char-啼")
    assert '<span class="lvl l7">7–9</span>' in row and '<td class="gloss">cry, crow (of birds), weep</td>' in row and 'name="gloss"' not in row and "/facts" not in page
    row = row_of(page, "char-月")
    assert '<span class="lvl l1">1</span>' in row and '<td class="gloss">moon, month</td>' in row
    assert post(site, "/texts/1/lessons/1/characters/啼/facts", gloss="chirp").status_code == 404


def test_character_the_dictionary_lacks_is_flagged_and_filtered(site):
    add_text_6(site)
    assert post(site, "/texts/99/lessons", name="A").status_code == 200
    assert post(site, "/texts/99/lessons/1/characters/add", chars=["龘"]).status_code == 200
    page = get(site, "/texts/99/lessons/1/characters").text
    row = row_of(page, "char-龘")
    assert '<span class="lvl l0">n/a</span>' in row and "not in the dictionary — add it to data/supplement.tsv" in row
    assert "2 characters · 1 not in HSK (龘) · 1 without a gloss" in site.client.get("/texts/99").text
    assert post(site, "/texts/99/lessons/1/characters/龘/remove").status_code == 200
    shown = lambda **params: re.findall(r'name="chars" value="(.)"', get(site, "/texts/99/lessons/1/characters", **params).text)  # noqa: E731
    assert shown() == ["龘", "飞"] and shown(min=1, max=7, state="learning") == ["飞"] and shown(min=1, max=7, state="learning", missing=1) == ["龘", "飞"]


def test_edit_supplement_word_pinyin_and_gloss_are_contextual(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    assert post(site, "/texts/1/lessons/1/words/new", surface="寒山寺", step="2", gloss="寺", hsk_level="4").status_code == 200
    assert supplement_text(site).endswith("寒山寺\t\t寺\t4\n")
    assert facts(site)["words"] == [{"surface": "寒山寺", "pinyin": None, "gloss": None, "origin": "manual"}]
    form = form_of(get(site, "/texts/1/lessons/1/words", show="all", edit="寒山寺").text, "/texts/1/lessons/1/words/寒山寺/save?show=all")
    assert 'name="hsk_level"' not in form and 'name="pinyin" aria-label="Pinyin" value="hán shān sì"' in form and 'name="gloss" aria-label="Gloss" value=""' in form
    assert post(site, "/texts/1/lessons/1/words/寒山寺/save", pinyin="Han2 Shan1 Si4", gloss="苏州的寺").status_code == 200
    assert facts(site)["words"] == [{"surface": "寒山寺", "pinyin": "Hán Shān Sì", "gloss": "苏州的寺", "origin": "manual"}]
    row = row_of(get(site, "/texts/1/lessons/1/words", show="all").text, "word-寒山寺")
    assert '<td class="zh word">寒山寺</td><td class="py">Hán Shān Sì</td><td><span class="lvl l4">4</span></td><td class="gloss">苏州的寺</td>' in row
    assert post(site, "/texts/1/lessons/1/words/寒山寺/save", pinyin="hán shān sì", gloss="").status_code == 200  # the dictionary's own reading and gloss: no override
    assert facts(site)["words"] == [{"surface": "寒山寺", "pinyin": None, "gloss": None, "origin": "manual"}]
    row = row_of(get(site, "/texts/1/lessons/1/words", show="all").text, "word-寒山寺")
    assert '<td class="py">hán shān sì</td><td><span class="lvl l4">4</span></td><td class="gloss"><span class="muted">寺</span></td>' in row
    assert supplement_text(site).endswith("寒山寺\t\t寺\t4\n")  # the page never edits the supplement


def test_edit_linked_word_has_no_level_field_and_no_pinyin_override(site):
    intake(db.connect(site.db, progress_path=site.progress), 5, site.data)
    form = form_of(get(site, "/texts/5/lessons/1/words", show="all", edit="桃花").text, "/texts/5/lessons/1/words/桃花/save")
    assert 'name="hsk_level"' not in form
    pinyin = re.search(r'name="pinyin" aria-label="Pinyin" value="(.*?)"', form).group(1)
    assert post(site, "/texts/5/lessons/1/words/桃花/save", gloss="春天的花", pinyin=pinyin).status_code == 200
    stored = lambda: next(w for w in json.loads((site.data / "annotations" / "5.json").read_text(encoding="utf-8"))["words"] if w["surface"] == "桃花")  # noqa: E731
    assert stored() == {"surface": "桃花", "pinyin": None, "gloss": "春天的花", "origin": "manual"}  # the dictionary's reading, unchanged, is not an override
    assert post(site, "/texts/5/lessons/1/words/桃花/save", gloss="春天的花", pinyin="tao2 hua1 x").status_code == 200
    assert stored()["pinyin"] == "táo huā x"
    row = row_of(get(site, "/texts/5/lessons/1/words", show="all").text, "word-桃花")
    assert '<span class="lvl l5">5</span>' in row and '<td class="gloss">春天的花</td>' in row  # the dictionary's level still shows


def test_edit_extra_word_keeps_anchor(site, probe):
    word, anchor = probe.word, probe.anchor
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月亮").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor=anchor, surface=word, step="2", pinyin=probe.pinyin, gloss="test", hsk_level="2").status_code == 200
    assert supplement_text(site).endswith(f"{word}\t{probe.pinyin}\ttest\t2\n")
    conn = db.connect(site.db)
    form = form_of(get(site, "/texts/1/lessons/1/expansions", edit="月-月亮").text, "/texts/1/lessons/1/expansions/月亮/save")
    assert '<input type="hidden" name="anchor" value="月"><input type="hidden" name="surface" value="月亮">' in form and 'name="hsk_level"' not in form and 'value="yuè liang"' in form
    form = form_of(get(site, "/texts/1/lessons/1/expansions", edit=f"{anchor}-{word}").text, f"/texts/1/lessons/1/expansions/{word}/save")
    assert 'name="hsk_level"' not in form and f'value="{probe.pinyin}"' in form and 'aria-label="Gloss" value=""' in form
    assert post(site, f"/texts/1/lessons/1/expansions/{word}/save", anchor=anchor, surface=word, pinyin=probe.pinyin, gloss="in context").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/月亮/save", anchor="月", surface="月亮", pinyin="yue4 liang", gloss="the moon").status_code == 200
    rows = [tuple(r) for r in conn.execute("SELECT anchor, surface, word_id >= 10000000, pinyin, gloss, origin FROM lesson_extra_word ORDER BY surface")]
    assert rows == sorted([(anchor, word, 1, probe.pinyin, "in context", "manual"), ("月", "月亮", 0, "yuè liang", "the moon", "manual")], key=lambda r: r[1])
    assert lesson(site)["extra_words"] == sorted([{"anchor": anchor, "surface": word, "pinyin": probe.pinyin, "gloss": "in context", "origin": "manual"},
                                                  {"anchor": "月", "surface": "月亮", "pinyin": "yuè liang", "gloss": "the moon", "origin": "manual"}], key=lambda e: (e["anchor"], e["surface"]))
    assert post(site, f"/texts/1/lessons/1/expansions/{word}/save", anchor=anchor, surface=word, pinyin="", gloss="").status_code == 200  # blank: the dictionary's reading, no contextual gloss
    assert [e for e in lesson(site)["extra_words"] if e["surface"] == word] == [{"anchor": anchor, "surface": word, "pinyin": probe.pinyin, "gloss": None, "origin": "manual"}]
    assert post(site, f"/texts/1/lessons/1/expansions/{word}/save", anchor="", surface=word, gloss="x").status_code == 422  # no such row without the anchor
    row = row_of(get(site, "/texts/1/lessons/1/expansions").text, f"extra-{anchor}-{word}")
    assert '<span class="lvl l2">2</span>' in row and '<span class="muted">test</span>' in row


def test_invalid_add_keeps_form_open_with_422(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    before = supplement_text(site)
    r = post(site, "/texts/1/lessons/1/words/new", surface="姑苏城", step="2", pinyin="x", gloss="城", hsk_level="9")
    assert r.status_code == 422 and r.text.startswith('<div id="tabs"')
    local = r.text.split('class="local"')[1].split("</form>")[0]
    assert "level must be 1 to 7, not “9”" in local and 'name="step" value="2"' in local and 'placeholder="pinyin" value="x"' in local and 'placeholder="gloss" value="城"' in local
    assert r.text.count('class="error"') == 1 and supplement_text(site) == before and not site.file.exists()
    assert post(site, "/texts/1/lessons/1/words/没有/save", gloss="x").status_code == 422


def test_supplement_word_level_shows_everywhere(site, baseline, probe):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    assert post(site, "/texts/1/lessons/1/words/new", surface="寒山寺", step="2", gloss="寺", hsk_level="").status_code == 200  # blank level: derived, 寺 is 7
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月亮").status_code == 200
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor=probe.anchor, surface=probe.word, step="2", pinyin=probe.pinyin, gloss="test", hsk_level="2").status_code == 200
    assert supplement_text(site).endswith(f"寒山寺\t\t寺\t\n{probe.word}\t{probe.pinyin}\ttest\t2\n")
    assert db.connect(site.db).execute("SELECT word_id FROM text_word WHERE surface = '寒山寺'").fetchone()[0] == supplement.WORD_ID_BASE + baseline.lines
    words = get(site, "/texts/1/lessons/1/words", show="all").text
    assert '<td class="zh word">寒山寺</td><td class="py">hán shān sì</td><td><span class="lvl l7">7–9</span></td>' in words
    expansions = get(site, "/texts/1/lessons/1/expansions").text
    assert f'<td class="zh word">{probe.word}</td><td class="py">{probe.pinyin}</td><td><span class="lvl l2">2</span></td>' in expansions
    assert '<td class="zh word">月亮</td><td class="py">yuè liang</td><td><span class="lvl l3">3</span></td>' in expansions
    assert '<td class="word">寒山寺</td><td>hán shān sì</td><td>7–9</td><td>寺</td>' in site.client.get("/learn/1/1", params={"words": 1}).text
    db.build(site.db, site.data)
    rows = db.connect(site.db).execute("SELECT e.surface, w.hsk_level, w.source FROM lesson_extra_word e JOIN word w ON w.id = e.word_id ORDER BY e.surface")
    assert [tuple(r) for r in rows] == sorted([(probe.word, 2, "supplement"), ("月亮", 3, "hsk")])


def test_reading_of_a_character_the_dictionary_lacks_is_typed(site):
    add_text_6(site)
    edit = get(site, "/texts/99/text/edit").text
    assert '<input name="p0" aria-label="Reading" placeholder="pinyin" value="">' in edit and '<span class="fixed"></span><span>飞</span>' in edit
    assert post(site, "/texts/99/text", p0="da2").status_code == 200
    assert "<ruby>龘<rt>dá</rt></ruby>" in get(site, "/texts/99/text").text
    assert json.loads((site.data / "annotations" / "99.json").read_text(encoding="utf-8"))["readings"] == [{"position": 0, "char": "龘", "pinyin": "dá", "origin": "manual"}]
    assert 'name="p0" aria-label="Reading" placeholder="pinyin" value="dá"' in get(site, "/texts/99/text/edit").text
    r = post(site, "/texts/99/text", p0=" ")
    assert r.status_code == 422 and "a reading for position 0 “龘” is required" in r.text and 'name="p0"' in r.text
    assert '<span class="fixed"></span><span>枫</span>' in get(site, "/texts/1/text/edit").text  # a supplement character with one reading is fixed
