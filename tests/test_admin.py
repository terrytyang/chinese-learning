"""The admin page: shell and fragments, lesson switch, tags, pinyin edit, bulk add, Words in text, two-step extra words, notes, errors at the form."""

import json
import re

from chineselearning import db, progress, supplement
from chineselearning.admin import rows
from chineselearning.intake import intake

HX = {"HX-Request": "true"}


def get(site, path, **params):
    return site.client.get(path, params=params, headers=HX)


def post(site, path, **fields):
    return site.client.post(path, data=fields, headers=HX)


def facts(site, text_id=1):
    return json.loads((site.data / "annotations" / f"{text_id}.json").read_text(encoding="utf-8"))


def lesson(site, text_id=1, lesson_id=1):
    return json.loads((site.data / "lessons" / f"{text_id}-{lesson_id}.json").read_text(encoding="utf-8"))


def form_of(html, action):
    """The HTML of the first form posting to `action` (its query string may follow)."""
    return html.split(f'hx-post="{action}')[1].split("</form>")[0]


def rows_of(html):
    return re.findall(r'<tr id="(?:word|char)-(.*?)">', html)


def test_shell_and_fragments(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    page = site.client.get("/texts/1").text
    assert page.startswith("<!doctype html>") and 'src="/static/htmx.min.js"' in page and '<meta name="htmx-config"' in page
    for region in ("lesson-controls", "tags", "text", "tabs"):
        assert f'id="{region}"' in page
    assert '<a class="tab on" href="/texts/1/lessons/1/characters"' in page and "In this lesson · 28" in page
    assert "<ruby>月<rt>yuè</rt></ruby>" in page and "28 characters · 2 not in HSK (啼, 枫) · 0 without a gloss" in page
    assert '<option value="1" selected>Learn 枫桥夜泊</option>' in page and 'href="/learn/1/1">Open student view' in page
    fragment = get(site, "/texts/1/lessons/1/words").text
    assert fragment.startswith('<div id="tabs"') and "<html" not in fragment and '<a class="tab on" href="/texts/1/lessons/1/words"' in fragment
    assert 'Words in text <span class="muted">0/0</span>' in fragment
    whole = site.client.get("/texts/1/lessons/1/words").text
    assert whole.startswith("<!doctype html>") and '<a class="tab on" href="/texts/1/lessons/1/words"' in whole and 'id="text"' in whole
    restore = site.client.get("/texts/1/lessons/1/notes", headers={**HX, "HX-History-Restore-Request": "true"}).text
    assert restore.startswith("<!doctype html>") and '<a class="tab on" href="/texts/1/lessons/1/notes"' in restore
    assert get(site, "/texts/1/lessons/1/bogus").status_code == 404 and get(site, "/texts/2/lessons/1/characters").status_code == 404
    assert site.client.get("/texts/999").status_code == 404


def test_lesson_select_new_and_rename(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    r = post(site, "/texts/1/lessons", name="Level 1")
    assert r.status_code == 200 and r.headers["hx-push-url"] == "/texts/1/lessons/2/characters"
    assert r.text.startswith('<div id="lesson-controls"') and '<option value="2" selected>Level 1</option>' in r.text
    assert '<div id="tabs" class="card" hx-target="#tabs" hx-swap="outerHTML" hx-swap-oob="true">' in r.text and "In this lesson · 0" in r.text
    assert (site.data / "lessons" / "1-2.json").exists()
    r = post(site, "/texts/1/lessons?lesson=2", name="Level 1")
    assert r.status_code == 422 and "a lesson named “Level 1” already exists" in form_of(r.text, "/texts/1/lessons?lesson=2") and "hx-swap-oob" not in r.text
    r = post(site, "/texts/1/lessons/2/rename", name="Level one")
    assert r.status_code == 200 and r.text.startswith('<div id="lesson-controls"') and 'value="Level one"' in r.text and lesson(site, 1, 2)["name"] == "Level one"
    r = post(site, "/texts/1/lessons/2/rename", name="Learn 枫桥夜泊")
    assert r.status_code == 422 and "already exists" in form_of(r.text, "/texts/1/lessons/2/rename")
    assert post(site, "/texts/1/lessons/2/rename", name=" ").status_code == 422
    r = get(site, "/texts/1", lesson=2)
    assert r.headers["hx-push-url"] == "/texts/1/lessons/2/characters" and r.text.startswith('<div id="tabs"')
    assert 'id="lesson-controls" class="lesson-controls" hx-target="#lesson-controls" hx-swap="outerHTML" hx-swap-oob="true"' in r.text
    assert '<div id="text" class="card" hx-target="#text" hx-swap="outerHTML" hx-swap-oob="true">' in r.text and '<option value="2" selected>' in r.text
    assert '<a class="tab on" href="/texts/1/lessons/2/characters"' in r.text and "In this lesson · 0" in r.text


def test_tags_rewrite_only_the_tags_line(site):
    path = site.data / "texts" / "001-枫桥夜泊.md"
    before = path.read_text(encoding="utf-8")
    r = post(site, "/texts/1/tags/add", tag="七绝")
    assert r.status_code == 200 and r.text.startswith('<div id="tags"') and r.text.count('class="chip"') == 2 and "七绝" in r.text
    after = path.read_text(encoding="utf-8")
    assert after.replace("tags: 诗词, 七绝\n", "tags: 诗词\n") == before
    assert "1 texts" in site.client.get("/texts", params={"tag": "七绝"}).text
    assert post(site, "/texts/1/tags/add", tag="七绝").text.count('class="chip"') == 2  # a duplicate is a no-op
    r = post(site, "/texts/1/tags/remove", tag="七绝")
    assert r.text.count('class="chip"') == 1 and path.read_text(encoding="utf-8") == before
    r = post(site, "/texts/1/tags/remove", tag="诗词")
    assert r.status_code == 422 and "a text needs at least one tag" in form_of(r.text, "/texts/1/tags/add") and path.read_text(encoding="utf-8") == before
    r = post(site, "/texts/1/tags/add", tag=" ")
    assert r.status_code == 422 and "a tag is required" in r.text
    assert site.client.post("/texts/1/tags/rename", data={"tag": "x"}).status_code == 404
    assert site.client.post("/texts/1/info", data={"author": "x"}).status_code == 404


def test_pinyin_edit_round_trip(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    block = get(site, "/texts/1/text").text
    assert block.startswith('<div id="text"') and "<ruby>乌<rt>wū</rt></ruby>" in block and 'hx-get="/texts/1/text/edit">Edit pinyin</button>' in block
    edit = get(site, "/texts/1/text/edit").text
    assert edit.startswith('<form id="text"') and 'hx-post="/texts/1/text"' in edit
    assert '<select name="p2" aria-label="Reading"><option selected>wū</option><option>wù</option></select>' in edit
    assert '<span class="fixed">fēng</span><span>枫</span>' in edit and '<span class="fixed">shuāng</span><span>霜</span>' in edit  # one reading: fixed, supplement or HSK
    assert "Save readings" in edit and 'hx-get="/texts/1/text">Cancel</button>' in edit
    current = {m.group(1): m.group(2) for m in re.finditer(r'<select name="(p\d+)"[^>]*>.*?<option selected>(.*?)</option>', edit)}
    r = post(site, "/texts/1/text", **{**current, "p2": "wù", "p9": "fēng"})
    assert r.status_code == 200 and r.text.startswith('<div id="text"') and "<ruby>乌<rt>wù</rt></ruby>" in r.text and "<ruby>枫<rt>fēng</rt></ruby>" in r.text
    manual = [x for x in facts(site)["readings"] if x["origin"] == "manual"]
    assert manual == [{"position": 2, "char": "乌", "pinyin": "wù", "origin": "manual"}]  # an unchanged reading is not re-stored
    r = post(site, "/texts/1/text", p2="")
    assert r.status_code == 422 and r.text.startswith('<form id="text"') and "a reading for position 2 “乌” is required" in r.text and 'name="p2"' in r.text
    r = post(site, "/texts/1/text", p2="wu")
    assert r.status_code == 422 and "the reading of “乌” must be one of wū, wù" in r.text
    full = site.client.get("/texts/1/text/edit").text
    assert full.startswith("<!doctype html>") and '<form id="text"' in full and 'id="tabs"' in full


def test_bulk_add_and_filters(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    tab = get(site, "/texts/1/lessons/1/characters").text
    assert tab.count('name="chars" value="') == 28 and "Not in this lesson · 28" in tab and '<p class="empty">None</p>' in tab
    assert "data-select-all>Select all shown</button>" in tab and 'form="chars-bulk" class="primary" data-count>Add 0 to lesson</button>' in tab
    assert re.search(r'name="chars" value="月"[^>]*>.*?<td class="gloss">moon, month</td>', tab, re.S) and re.search(r'name="chars" value="啼"[^>]*>.*?<span class="lvl l7">7–9</span>', tab, re.S)
    r = post(site, "/texts/1/lessons/1/characters/add", chars=["月", "落"])
    assert r.status_code == 200 and r.text.startswith('<div id="tabs"') and 'Characters <span class="muted">2</span>' in r.text
    assert '<tr id="char-月">' in r.text and '<tr id="char-落">' in r.text and r.text.count('name="chars" value="') == 26
    assert lesson(site)["characters"] == ["月", "落"]
    conn = db.connect(site.db, progress_path=site.progress)
    assert progress.state_of(conn, "character", "月") == "exposed"
    assert post(site, "/texts/1/lessons/1/characters/progress", kind="character", key="乌", state="mastered").status_code == 200
    all_rows = rows.character_rows(conn, 1)
    low = [ch for ch, row in all_rows.items() if ch not in "月落" and row["hsk_level"] and row["hsk_level"] <= 2]
    filtered = get(site, "/texts/1/lessons/1/characters", min=1, max=2, state="any").text
    assert re.findall(r'name="chars" value="(.)"', filtered) == low and len(low) > 0 and '<option value="2" selected>2</option>' in filtered
    assert re.findall(r'name="chars" value="(.)"', get(site, "/texts/1/lessons/1/characters", state="mastered", min=1, max=7).text) == ["乌"]
    default = re.findall(r'name="chars" value="(.)"', get(site, "/texts/1/lessons/1/characters").text)
    assert "乌" not in default and "啼" in default  # default: unconfirmed or exposed; a supplement character has a level like any other
    without = get(site, "/texts/1/lessons/1/characters", min=1, max=7, state="learning").text  # the form sent no `missing`: unticked
    assert 'name="missing" value="1"> include characters not in the dictionary' in without and 'name="missing" value="1" checked>' in get(site, "/texts/1/lessons/1/characters").text
    r = post(site, "/texts/1/lessons/1/characters/add?min=1&max=2&state=any", chars=low)
    assert sorted(lesson(site)["characters"]) == sorted(["月", "落"] + low) and '<option value="2" selected>2</option>' in r.text
    assert 'hx-get="/texts/1/lessons/1/characters" hx-trigger="change" hx-push-url="true"' in r.text
    r = post(site, "/texts/1/lessons/1/characters/月/remove")
    assert r.status_code == 200 and '<tr id="char-月">' not in r.text and "月" not in lesson(site)["characters"]
    r = post(site, "/texts/1/lessons/1/characters/add", chars=["x"])
    assert r.status_code == 422 and "“x” is not a single character of the text" in form_of(r.text, "/texts/1/lessons/1/characters/add")


def test_words_in_text_filters_and_bulk_actions(site):
    intake(db.connect(site.db, progress_path=site.progress), 5, site.data)
    total = len(facts(site, 5)["words"])
    tab = get(site, "/texts/5/lessons/1/words").text
    assert f'Words in text <span class="muted">{total}/{total}</span>' in tab and '<option value="unreviewed" selected>' in tab and f"{total} shown" in tab
    assert tab.count('aria-label="Include in lesson" checked') == total and '<tr id="word-桃花">' in tab and '<span class="pill auto">auto</span>' in tab
    r = post(site, "/texts/5/lessons/1/words/桃花/include")  # unticked: the selection goes
    assert r.status_code == 200 and f'Words in text <span class="muted">{total - 1}/{total}</span>' in r.text and "桃花" not in lesson(site, 5, 1)["words"]
    r = post(site, "/texts/5/lessons/1/words/桃花/include", **{"in": "1"})
    assert f"{total}/{total}" in r.text and "桃花" in lesson(site, 5, 1)["words"]
    assert post(site, "/texts/5/lessons/1/words/桃花/include").status_code == 200
    excluded = get(site, "/texts/5/lessons/1/words", show="excluded", min=1, max=7).text
    assert rows_of(excluded) == ["桃花"] and "1 shown" in excluded and 'hx-post="/texts/5/lessons/1/words/add-shown?show=excluded&amp;min=1&amp;max=7"' in excluded
    r = post(site, "/texts/5/lessons/1/words/add-shown?show=excluded&min=1&max=7")
    assert r.status_code == 200 and "桃花" in lesson(site, 5, 1)["words"] and "0 shown" in r.text
    low = rows_of(get(site, "/texts/5/lessons/1/words", show="all", min=1, max=3).text)
    assert 0 < len(low) < total
    r = post(site, "/texts/5/lessons/1/words/review-shown?show=unreviewed&min=1&max=3")
    assert r.status_code == 200 and "0 shown" in r.text
    assert {w["surface"] for w in facts(site, 5)["words"] if w["origin"] == "manual"} == set(low)
    unreviewed = rows_of(get(site, "/texts/5/lessons/1/words").text)
    assert len(unreviewed) == total - len(low) and not set(unreviewed) & set(low)
    editing = get(site, "/texts/5/lessons/1/words", show="all", edit="桃花").text
    form = form_of(editing, "/texts/5/lessons/1/words/桃花/save?show=all")
    pinyin = re.search(r'name="pinyin" aria-label="Pinyin" value="(.*?)"', form).group(1)
    assert pinyin and 'name="hsk_level"' not in form and 'hx-get="/texts/5/lessons/1/words?show=all&amp;min=1&amp;max=7">Cancel</button>' in form
    r = post(site, "/texts/5/lessons/1/words/桃花/save?show=all", pinyin=pinyin, gloss="peach blossom")
    assert r.status_code == 200 and '<td class="gloss">peach blossom</td>' in r.text and 'name="pinyin"' not in r.text.split('id="word-桃花"')[1].split("</tr>")[0]
    row = next(w for w in facts(site, 5)["words"] if w["surface"] == "桃花")
    assert row == {"surface": "桃花", "pinyin": None, "gloss": "peach blossom", "origin": "manual"}  # the master's reading is not an override
    r = post(site, "/texts/5/lessons/1/words/桃花/delete?show=all")
    assert r.status_code == 200 and '<tr id="word-桃花">' not in r.text
    assert "桃花" not in [w["surface"] for w in facts(site, 5)["words"]] and "桃花" not in lesson(site, 5, 1)["words"]


def test_add_word_in_text_two_step(site, baseline):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    r = post(site, "/texts/1/lessons/1/words/new", surface="寒山寺")
    assert r.status_code == 200 and "Not an HSK word." in r.text and 'name="pinyin" placeholder="pinyin" value="hán shān sì"' in r.text
    assert '<input type="hidden" name="step" value="2"><input type="hidden" name="surface" value="寒山寺">' in r.text
    assert '<option value="7" selected>7–9</option>' in r.text and '<option value="exposed" selected>' in r.text and 'placeholder="word" value="寒山寺"' in r.text
    r = post(site, "/texts/1/lessons/1/words/new", surface="寒山寺", step="2", pinyin="", gloss="", hsk_level="9", state="exposed")
    assert r.status_code == 422 and "level must be 1 to 7, not “9”" in r.text.split('class="local"')[1].split("</form>")[0] and r.text.count('class="error"') == 1
    r = post(site, "/texts/1/lessons/1/words/new", surface="寒山寺", step="2", pinyin="han2 shan1 si4", gloss="Hanshan Temple", hsk_level="7", state="recognized")
    assert r.status_code == 200 and 'Words in text <span class="muted">1/1</span>' in r.text and "Not an HSK word" not in r.text
    assert (site.data / "supplement.tsv").read_text(encoding="utf-8").endswith("寒山寺\thán shān sì\tHanshan Temple\t7\n")  # the supplement entry
    assert facts(site)["words"] == [{"surface": "寒山寺", "pinyin": None, "gloss": None, "origin": "manual"}]  # linked; nothing contextual
    assert db.connect(site.db).execute("SELECT word_id FROM text_word WHERE surface = '寒山寺'").fetchone()[0] == supplement.WORD_ID_BASE + baseline.lines
    row = get(site, "/texts/1/lessons/1/words", show="all").text.split('id="word-寒山寺"')[1].split("</tr>")[0]
    assert '<td class="py">hán shān sì</td><td><span class="lvl l7">7–9</span></td><td class="gloss"><span class="muted">Hanshan Temple</span></td>' in row
    assert lesson(site)["words"] == ["寒山寺"] and progress.state_of(db.connect(site.db, progress_path=site.progress), "word", "寒山寺") == "recognized"
    shown = get(site, "/texts/1/lessons/1/words", show="included", min=1, max=7).text
    assert '<tr id="word-寒山寺">' in shown and 'value="recognized" class="on"' in shown
    r = post(site, "/texts/1/lessons/1/words/new", surface="太阳")
    assert r.status_code == 422 and "“太阳” does not occur in the text" in form_of(r.text, "/texts/1/lessons/1/words/new") and 'placeholder="word" value="太阳"' in r.text
    r = post(site, "/texts/1/lessons/1/words/new", surface="月")
    assert r.status_code == 422 and "a single character is a character" in r.text
    assert post(site, "/texts/1/lessons/1/words/new", surface="").status_code == 422


def test_extra_words_two_step_expansions_and_related(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    assert post(site, "/texts/1/lessons/1/characters/add", chars=["月"]).status_code == 200
    tab = get(site, "/texts/1/lessons/1/expansions").text
    assert '<div class="block" id="expansions-月">' in tab and 'placeholder="expand 月 into…"' in tab and 'name="step"' not in tab and 'Expansions <span class="muted">0</span>' in tab
    r = post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月亮")
    assert r.status_code == 200 and '<tr id="extra-月-月亮">' in r.text and 'Expansions <span class="muted">1</span>' in r.text and '<td class="py">yuè liang</td>' in r.text
    assert lesson(site)["extra_words"] == [{"anchor": "月", "surface": "月亮", "pinyin": "yuè liang", "gloss": None, "origin": "manual"}]
    r = post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月影")
    assert r.status_code == 200 and '<span class="zh">月影</span> is not an HSK word.' in r.text and 'placeholder="pinyin" value="yuè yǐng"' in r.text
    local = r.text.split('class="local"')[1].split("</form>")[0]
    assert '<input type="hidden" name="step" value="2"><input type="hidden" name="anchor" value="月"><input type="hidden" name="surface" value="月影">' in local and 'name="state"' in local
    r = post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月影", step="2", gloss="", hsk_level="9", state="recognized")
    assert r.status_code == 422 and "level must be 1 to 7, not “9”" in r.text.split('class="local"')[1] and 'name="step" value="2"' in r.text
    r = post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月影", step="2", pinyin="yue4 ying3", gloss="moon shadow", hsk_level="6", state="recognized")
    assert r.status_code == 200 and '<tr id="extra-月-月影">' in r.text and 'name="step"' not in r.text
    assert lesson(site)["extra_words"][1] == {"anchor": "月", "surface": "月影", "pinyin": "yuè yǐng", "gloss": None, "origin": "manual"}
    assert (site.data / "supplement.tsv").read_text(encoding="utf-8").endswith("月影\tyuè yǐng\tmoon shadow\t6\n")
    assert re.search(r'<tr id="extra-月-月影">.*?value="recognized" class="on"', r.text, re.S) and re.search(r'<tr id="extra-月-月亮">.*?value="exposed" class="on"', r.text, re.S)
    r = post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="太阳")
    assert r.status_code == 422 and "an expansion of “月” must contain it; “太阳” does not" in r.text.split('id="expansions-月"')[1] and 'name="step"' not in r.text
    assert "a word is required" in post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="").text
    tab = get(site, "/texts/1/lessons/1/related").text
    assert '<p class="empty">None</p>' in tab and 'placeholder="passage it relates to (optional)" value=""' in tab
    r = post(site, "/texts/1/lessons/1/related/add", anchor="姑苏", surface="苏州")
    assert r.status_code == 200 and "is not an HSK word" in r.text and 'placeholder="passage it relates to (optional)" value="姑苏"' in r.text and 'name="anchor" value="姑苏"' in r.text
    r = post(site, "/texts/1/lessons/1/related/add", anchor="姑苏", surface="苏州", step="2", gloss="Suzhou")
    assert r.status_code == 200 and '<tr id="extra-姑苏-苏州"><td class="zh">姑苏</td><td class="zh word">苏州</td><td class="py">sū zhōu</td>' in r.text
    r = post(site, "/texts/1/lessons/1/related/add", anchor="", surface="半夜")
    assert '<tr id="extra-半夜"><td class="zh">—</td><td class="zh word">半夜</td><td class="py">bàn yè</td>' in r.text and 'Related words <span class="muted">2</span>' in r.text and "extra-月-" not in r.text
    r = post(site, "/texts/1/lessons/1/related/add", anchor="太阳", surface="月亮")
    assert r.status_code == 422 and "“太阳” does not occur in the text" in r.text and 'value="太阳"' in r.text and 'name="step"' not in r.text
    assert [(e["anchor"], e["surface"]) for e in lesson(site)["extra_words"]] == [(None, "半夜"), ("姑苏", "苏州"), ("月", "月亮"), ("月", "月影")]
    editing = get(site, "/texts/1/lessons/1/expansions", edit="月-月影").text
    form = form_of(editing, "/texts/1/lessons/1/expansions/月影/save")
    assert 'name="anchor" value="月"' in form and 'name="hsk_level"' not in form and 'value="yuè yǐng"' in form
    r = post(site, "/texts/1/lessons/1/expansions/月影/save", anchor="月", surface="月影", pinyin="", gloss="shadow of the moon")
    assert r.status_code == 200 and '<td class="gloss">shadow of the moon</td>' in r.text and lesson(site)["extra_words"][3]["gloss"] == "shadow of the moon"
    r = post(site, "/texts/1/lessons/1/expansions/月影/save", anchor="月", surface="月影", pinyin="", gloss="")
    assert r.status_code == 200 and '<span class="muted">moon shadow</span>' in r.text and lesson(site)["extra_words"][3]["gloss"] is None  # back to the dictionary's
    assert post(site, "/texts/1/lessons/1/expansions/月影/delete", anchor="").status_code == 200 and len(lesson(site)["extra_words"]) == 4  # no such row without the anchor
    r = post(site, "/texts/1/lessons/1/expansions/月影/delete", anchor="月")
    assert '<tr id="extra-月-月影">' not in r.text and len(lesson(site)["extra_words"]) == 3


def test_notes_add_and_delete(site):
    assert post(site, "/texts/1/lessons", name="A").status_code == 200
    r = post(site, "/texts/1/lessons/1/notes/add", anchor="月落乌啼", note="Four images.")
    assert r.status_code == 200 and 'Notes <span class="muted">1</span>' in r.text
    assert '<tr id="note-1"><td class="zh">月落乌啼</td><td class="note">Four images.</td><td><span class="pill manual">manual</span></td>' in r.text
    assert lesson(site)["notes"] == [{"anchor": "月落乌啼", "note": "Four images.", "origin": "manual"}]
    r = post(site, "/texts/1/lessons/1/notes/add", anchor="太阳", note="x")
    assert r.status_code == 422 and "“太阳” does not occur in the text" in form_of(r.text, "/texts/1/lessons/1/notes/add") and 'placeholder="anchor (optional)" value="太阳"' in r.text
    assert "a note is required" in post(site, "/texts/1/lessons/1/notes/add", anchor="", note=" ").text
    r = post(site, "/texts/1/lessons/1/notes/1/delete")
    assert r.status_code == 200 and '<tr id="note-1">' not in r.text and lesson(site)["notes"] == []


def test_state_buttons_on_every_tab(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    assert post(site, "/texts/1/lessons/1/expansions/add", anchor="月", surface="月亮").status_code == 200
    for tab, kind, key in (("characters", "character", "月"), ("expansions", "word", "月亮")):
        r = post(site, f"/texts/1/lessons/1/{tab}/progress", kind=kind, key=key, state="mastered")
        assert r.status_code == 200 and f'<a class="tab on" href="/texts/1/lessons/1/{tab}"' in r.text
        assert re.search(rf'name="key" value="{key}">.*?<button name="state" value="mastered" class="on">mastered</button>', r.text, re.S)
    r = post(site, "/texts/1/lessons/1/characters/progress", kind="character", key="月", state="bogus")
    assert r.status_code == 422 and "state must be" in r.text.split('id="char-月"')[1].split("</tr>")[0]
    assert post(site, "/texts/1/lessons/1/words/progress", kind="word", key="月", state="exposed").status_code == 422  # no row to show it at
