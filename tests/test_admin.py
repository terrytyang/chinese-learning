"""The reworked admin page: header edit, pinyin edit mode, bulk selection, filters, two-step expansions, fragments, errors at the row."""

import json
import re
from urllib.parse import unquote

from chineselearning import db
from chineselearning.intake import intake


def post(site, path, **fields):
    return site.client.post(f"/texts/1/{path}", data=fields)


def location(r):
    return unquote(r.headers["location"])


def facts(site, text_id=1):
    return json.loads((site.data / "annotations" / f"{text_id}.json").read_text(encoding="utf-8"))


def lesson(site, text_id=1, lesson_id=1):
    return json.loads((site.data / "lessons" / f"{text_id}-{lesson_id}.json").read_text(encoding="utf-8"))


def form_of(html, action):
    """The HTML of the form posting to `action`."""
    return html.split(f'action="{action}"')[1].split("</form>")[0]


def test_info_rewrites_header_only(site):
    path = site.data / "texts" / "001-枫桥夜泊.md"
    before = path.read_text(encoding="utf-8")
    r = post(site, "info", author="张继", period="唐", tags="诗词, 七绝")
    assert (r.status_code, location(r)) == (303, "/texts/1#info")
    after = path.read_text(encoding="utf-8")
    assert after.split("\n\n", 1)[1] == before.split("\n\n", 1)[1] and "period: 唐\n" in after and "tags: 诗词, 七绝\n" in after and "id: 1\n" in after
    page = site.client.get("/texts/1").text
    assert 'name="period" size="6" value="唐"' in page and 'name="tags" size="12" value="诗词, 七绝"' in page
    assert "七绝" in site.client.get("/texts", params={"tag": "七绝"}).text and "共 1 篇" in site.client.get("/texts", params={"tag": "七绝"}).text
    r = post(site, "info", author="张继", period="唐", tags="")
    assert r.status_code == 422 and "missing header key" in form_of(r.text, "/texts/1/info") and path.read_text(encoding="utf-8") == after


def test_pinyin_edit_mode_writes_only_changed_positions(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    page = site.client.get("/texts/1").text
    assert "<ruby>月<rt>yuè</rt></ruby>" in page and 'href="/texts/1?edit=pinyin#reading"' in page and 'name="p2"' not in page
    edit = site.client.get("/texts/1", params={"edit": "pinyin"}).text
    assert '<ruby>乌<rt><select name="p2"><option selected>wū</option><option>wù</option></select></rt></ruby>' in edit
    assert '<ruby>枫<rt><input name="p9" size="5" value=""></rt></ruby>' in edit and "<ruby>霜<rt>shuāng</rt></ruby>" in edit
    current = {int(m.group(1)): m.group(2) for m in re.finditer(r'<select name="p(\d+)">.*?<option selected>(.*?)</option>', edit)}
    r = post(site, "readings", **{**{f"p{k}": v for k, v in current.items()}, "p2": "wù", "p9": "fēng"})
    assert (r.status_code, location(r)) == (303, "/texts/1#reading")
    manual = [x for x in facts(site)["readings"] if x["origin"] == "manual"]
    assert manual == [{"position": 2, "char": "乌", "pinyin": "wù", "origin": "manual"}, {"position": 9, "char": "枫", "pinyin": "fēng", "origin": "manual"}]
    assert "<ruby>乌<rt>wù</rt></ruby>" in site.client.get("/texts/1").text and "<ruby>枫<rt>fēng</rt></ruby>" in site.client.get("/texts/1").text
    r = post(site, "readings", p9="")
    assert r.status_code == 422 and "位置 9「枫」的读音不能为空" in form_of(r.text, "/texts/1/readings") and 'name="p9"' in r.text
    r = post(site, "readings", p2="wu")
    assert r.status_code == 422 and "「乌」的读音只能是 wū、wù" in r.text and '<option selected>wu</option>' not in r.text


def test_bulk_add_remove_and_filters(site):
    assert location(post(site, "lessons", name="课")) == "/texts/1?lesson=1#lesson"
    page = site.client.get("/texts/1").text
    assert page.count('name="chars" value="') == 28 and '<p class="empty">暂无</p>' in page
    assert re.search(r'name="chars" value="月">.*?<td>moon, month</td>', page, re.S) and re.search(r'name="chars" value="啼">.*?不在字库', page, re.S)
    r = post(site, "characters/add", chars=["月", "落"])
    assert (r.status_code, location(r)) == (303, "/texts/1#characters")
    assert lesson(site)["characters"] == ["月", "落"]
    page = site.client.get("/texts/1").text
    assert '<tr id="char-月">' in page and '<tr id="char-落">' in page and page.count('name="chars" value="') == 26
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "乌", "state": "mastered"}).status_code == 303
    from chineselearning import admin_page

    rows = admin_page.character_rows(db.connect(site.db, progress_path=site.progress), 1)
    low = [ch for ch, row in rows.items() if ch not in "月落" and row["hsk_level"] and row["hsk_level"] <= 2]
    filtered = site.client.get("/texts/1", params={"cmin": "1", "cmax": "2"}).text
    assert re.findall(r'name="chars" value="(.)"', filtered) == low and len(low) > 0
    assert '<option value="1" selected>1</option>' in form_of(filtered, "/texts/1#characters")
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cstate": "mastered"}).text) == ["乌"]
    r = site.client.post("/texts/1/characters/add?cmin=1&cmax=2", data={"all": "1"})
    assert location(r) == "/texts/1?cmin=1&cmax=2#characters"
    assert sorted(lesson(site)["characters"]) == sorted(["月", "落"] + low)
    r = post(site, "characters/月/remove")
    assert location(r) == "/texts/1#characters" and "月" not in lesson(site)["characters"]
    assert '<tr id="char-月">' not in site.client.get("/texts/1").text


def test_words_bulk_new_and_delete(site):
    intake(db.connect(site.db, progress_path=site.progress), 5, site.data)
    page = site.client.get("/texts/5").text
    assert 'name="words" value="' not in page and '<tr id="word-桃花">' in page
    r = site.client.post("/texts/5/words/桃花/remove")
    assert location(r) == "/texts/5#words"
    page = site.client.get("/texts/5").text
    assert 'name="words" value="桃花"' in page and 'formaction="/texts/5/words/桃花/delete"' in page and '<tr id="word-桃花">' not in page
    assert "桃花" not in lesson(site, 5, 1)["words"]
    r = site.client.post("/texts/5/words/add", data={"words": ["桃花"]})
    assert location(r) == "/texts/5#words" and "桃花" in lesson(site, 5, 1)["words"]
    assert site.client.post("/texts/5/words/桃花/remove").status_code == 303
    r = site.client.post("/texts/5/words/桃花/delete")
    assert location(r) == "/texts/5#words" and "桃花" not in [w["surface"] for w in facts(site, 5)["words"]]
    section = site.client.get("/texts/5").text.split('id="words"')[1].split('id="expansions"')[0]
    assert '<td class="word">桃花</td>' not in section and 'value="桃花"' not in section  # the lesson name 桃花源记 still appears in the heading
    r = site.client.post("/texts/5/words/new", data={"surface": "桃花", "gloss": "", "pinyin": "", "hsk_level": "7"})
    assert location(r) == "/texts/5#word-桃花"
    assert "桃花" in lesson(site, 5, 1)["words"] and next(w["origin"] for w in facts(site, 5)["words"] if w["surface"] == "桃花") == "manual"
    unmastered = site.client.get("/texts/5", params={"wstate": "recognized"}).text
    assert 'name="words" value="' not in unmastered
    assert site.client.post("/texts/5/words/鲜美/remove").status_code == 303
    assert site.client.post("/texts/5/progress", data={"kind": "word", "key": "鲜美", "state": "recognized"}).status_code == 303
    assert re.findall(r'name="words" value="(.*?)"', site.client.get("/texts/5", params={"wstate": "recognized"}).text) == ["鲜美"]


def test_expansion_two_step_and_many_per_character(site):
    assert post(site, "lessons", name="课").status_code == 303
    assert post(site, "characters/add", chars=["月"]).status_code == 303
    page = site.client.get("/texts/1").text
    assert '<div class="block" id="expansions-月">' in page and 'name="step"' not in page
    r = post(site, "expansions", char="月", surface="月亮")
    assert (r.status_code, location(r)) == (303, "/texts/1#expansion-月-月亮")
    assert lesson(site)["expansions"] == [{"char": "月", "surface": "月亮", "gloss": None, "origin": "manual"}]
    r = post(site, "expansions", char="月", surface="月影")
    assert r.status_code == 200 and "字库里没有「月影」" in r.text
    second = form_of(r.text, "/texts/1/expansions").split('name="step"')
    assert 'name="surface" size="6" value="月影"' in r.text and '<option value="7" selected>7–9</option>' in r.text and 'name="state"' in r.text
    r = post(site, "expansions", char="月", surface="月影", step="2", gloss="", hsk_level="6", state="recognized")
    assert r.status_code == 422 and "请填写释义" in r.text and 'name="step" value="2"' in r.text and 'name="hsk_level"' in r.text
    r = post(site, "expansions", char="月", surface="月影", step="2", gloss="月亮的影子", hsk_level="6", state="recognized")
    assert location(r) == "/texts/1#expansion-月-月影"
    assert lesson(site)["expansions"][1] == {"char": "月", "surface": "月影", "hsk_level": 6, "gloss": "月亮的影子", "origin": "manual"}
    page = site.client.get("/texts/1").text
    assert '<tr id="expansion-月-月亮">' in page and '<tr id="expansion-月-月影">' in page and page.count('<tr id="expansion-月-') == 2
    assert re.search(r'<tr id="expansion-月-月影">.*?<td class="state">认识', page, re.S)
    r = post(site, "expansions", char="月", surface="")
    assert r.status_code == 422 and "请填写扩展词" in form_of(r.text, "/texts/1/expansions")


def test_every_post_redirects_to_its_fragment(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    steps = [
        ("info", {"author": "张继", "period": "唐朝", "tags": "诗词"}, "#info"),
        ("lessons", {"name": "二"}, "?lesson=2#lesson"),
        ("lessons/2/rename", {"name": "三"}, "#lesson"),
        ("lessons/2/delete", {}, "#lesson"),
        ("readings", {"p0": "yuè"}, "#reading"),
        ("characters/add", {"chars": ["月"]}, "#characters"),
        ("characters/月/facts", {"gloss": "月亮"}, "#char-月"),
        ("characters/落/remove", {}, "#characters"),
        ("words/new", {"surface": "寒山寺", "gloss": "寺", "hsk_level": "7"}, "#word-寒山寺"),
        ("words/寒山寺/facts", {"gloss": "古寺", "pinyin": "", "hsk_level": "7"}, "#word-寒山寺"),
        ("words/寒山寺/remove", {}, "#words"),
        ("words/add", {"words": ["寒山寺"]}, "#words"),
        ("words/寒山寺/delete", {}, "#words"),
        ("expansions", {"char": "月", "surface": "月亮"}, "#expansion-月-月亮"),
        ("expansions/月/月亮/update", {"surface": "月光", "gloss": "月亮的光"}, "#expansion-月-月光"),
        ("expansions/月/月光/delete", {}, "#expansions"),
        ("notes", {"anchor": "月落乌啼", "note": "首句"}, "#note-1"),
        ("notes/1/update", {"anchor": "", "note": "首句写景"}, "#note-1"),
        ("notes/1/delete", {}, "#notes"),
        ("progress", {"kind": "character", "key": "月", "state": "recognized"}, "#char-月"),
        ("progress", {"kind": "word", "key": "寒山寺", "state": "recognized"}, "#word-寒山寺"),
    ]
    for path, data, fragment in steps:
        r = post(site, path, **data)
        assert r.status_code == 303, (path, re.findall(r'class="error">(.*?)</p>', r.text))
        assert location(r) == "/texts/1" + fragment, path


def test_errors_render_at_the_row(site):
    intake(db.connect(site.db, progress_path=site.progress), 1, site.data)
    assert post(site, "words/new", surface="寒山寺", gloss="寺", hsk_level="7").status_code == 303
    r = post(site, "words/寒山寺/facts", pinyin="x", gloss="", hsk_level="7")
    assert r.status_code == 422
    assert "字库里没有「寒山寺」，请填写释义" in form_of(r.text, "/texts/1/words/寒山寺/facts") and r.text.count('class="error"') == 1
    r = post(site, "characters/啼/facts", gloss="x", hsk_level="9")
    assert r.status_code == 422 and "级只能是 1 到 7" in form_of(r.text, "/texts/1/characters/啼/facts")
    r = post(site, "lessons/1/delete")
    assert r.status_code == 422 and "课程不是空的" in r.text.split('id="lesson"')[1].split("</section>")[0]
    r = post(site, "notes", anchor="太阳", note="x")
    assert r.status_code == 422 and "「太阳」没有出现在正文里" in form_of(r.text, "/texts/1/notes") and 'name="anchor" placeholder="锚（正文片段）" size="10" value="太阳"' in r.text
    r = post(site, "progress", kind="character", key="月", state="bogus")
    assert r.status_code == 422 and "状态只能是" in r.text.split('id="char-月"')[1].split("</tr>")[0]
