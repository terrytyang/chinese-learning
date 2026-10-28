"""The dictionary page: counts, rows under the filters and the cap, search, state, inline edit (gloss file and supplement), lookup and add."""

import re

from chineselearning import db, progress
from chineselearning.admin.dictionary import CAP

HX = {"HX-Request": "true"}


def get(site, path, **params):
    return site.client.get(path, params=params, headers=HX)


def post(site, path, **fields):
    return site.client.post(path, data=fields, headers=HX)


def items(html):
    return re.findall(r'<tr id="entry-(.*?)"', html)


def rows(site, **filters):
    r = get(site, "/dictionary/rows", **filters)
    assert r.status_code == 200 and r.text.startswith('<div id="rows" class="card">')
    return r.text


def shown(html):
    return re.search(r'<span id="shown" class="muted">(.*?)</span>', html).group(1)


def cell(html, item, column):
    """The text of one column (0-based) of an entry's row."""
    row = html.split(f'<tr id="entry-{item}"')[1].split("</tr>")[0]
    return re.sub(r"<[^>]+>", "", re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)[column]).strip()


def test_page_counts_filters_and_defaults(site, baseline):
    page = site.client.get("/dictionary").text
    unglossed = baseline.unglossed  # every HSK character has a gloss; a supplement character's counts like a supplement word's
    assert f"{baseline.hsk_characters + baseline.characters:,} characters · {baseline.hsk_words:,} HSK words · {baseline.entries} supplement entries · {unglossed} without a gloss" in page
    assert f'<span id="shown" class="muted">{CAP} of {baseline.hsk_characters + baseline.characters + baseline.hsk_words + baseline.words:,} shown — narrow the filters</span>' in page
    assert 'hx-get="/dictionary/rows" hx-trigger="input delay:300ms" hx-target="#rows" hx-swap="outerHTML"' in page and "hx-push-url" not in page
    assert get(site, "/dictionary/rows", q="乌", kind="word").headers["HX-Push-Url"] == "/dictionary?q=%E4%B9%8C&kind=word&source=all&min=1&max=7&state=any&changed=any"
    assert '<option value="all" selected>all</option>' in page and '<option value="any" selected>any</option>' in page and 'name="nogloss" value="1">' in page
    assert len(items(page)) == CAP and items(page)[0] == "一"  # level 1 first, then by item
    assert site.client.get("/dictionary/rows", params={"q": "乌"}).text.count("<h1>Dictionary</h1>") == 1  # a plain request gets the page
    assert 'value="乌"' in site.client.get("/dictionary/rows", params={"q": "乌"}).text


def test_rows_under_each_filter_and_the_cap(site, baseline):
    html = rows(site, q="乌")  # by level, then item; 鸦 matches through its gloss "(乌鸦) crow"
    assert items(html) == ["乌黑", "乌", "乌云", "乌鸦", "鸦"] and shown(html) == "5 shown"
    assert cell(html, "乌鸦", 1) == "wū yā" and cell(html, "乌鸦", 2) == "7–9" and cell(html, "乌鸦", 3) == "supplement" and cell(html, "乌鸦", 4) == "crow"
    assert cell(html, "乌", 3) == "hsk" and cell(html, "乌黑", 4) == "jet-black; dark" and cell(html, "乌黑", 2) == "6"  # an HSK word: its meanings joined
    assert items(rows(site, q="乌", kind="character")) == ["乌", "鸦"] and items(rows(site, q="乌", kind="word")) == ["乌黑", "乌云", "乌鸦"]
    assert items(rows(site, q="乌", source="supplement")) == ["乌鸦"] and items(rows(site, q="乌", source="hsk")) == ["乌黑", "乌", "乌云", "鸦"]
    assert items(rows(site, q="乌", min="1", max="6")) == ["乌黑"] and items(rows(site, q="乌", min="7", max="7")) == ["乌", "乌云", "乌鸦", "鸦"]
    assert items(rows(site, q="乌", state="exposed")) == [] and len(items(rows(site, q="乌", state="unconfirmed"))) == 5
    assert post(site, "/dictionary/state", item="乌云", state="exposed").status_code == 200
    assert items(rows(site, q="乌", state="exposed")) == ["乌云"] and items(rows(site, q="乌", state="unconfirmed")) == ["乌黑", "乌", "乌鸦", "鸦"]
    unglossed = items(rows(site, nogloss="1"))
    assert len(unglossed) == baseline.unglossed and all('<i>no gloss yet</i>' in rows(site, q=u) for u in unglossed[:1])
    assert items(rows(site, kind="character", source="supplement")) == sorted(items(rows(site, kind="character", source="supplement")))
    assert len(items(rows(site, kind="character", source="supplement"))) == baseline.characters
    whole = rows(site, kind="word", source="hsk")
    assert len(items(whole)) == CAP and shown(whole) == f"{CAP} of {baseline.hsk_words:,} shown — narrow the filters"
    assert items(rows(site, q="zzzz")) == [] and "No entries match" in rows(site, q="zzzz")


def test_search_by_item_pinyin_and_gloss(site):
    assert items(rows(site, q="寒山寺")) == [] and "寒山寺" not in rows(site, q="寒山")  # not in the dictionary yet
    assert "乌鸦" in items(rows(site, q="wū yā")) and "乌鸦" in items(rows(site, q="Wū yā")) and items(rows(site, q="yā", kind="word", source="supplement")) == ["乌鸦"]
    assert items(rows(site, q="crow", kind="word", source="supplement")) == ["乌鸦"] and "啼" in items(rows(site, q="Crow")) and items(rows(site, q="%")) == []
    assert cell(rows(site, q="moon, month"), "月", 4) == "moon, month"


def test_state_buttons_write_manual_and_return_the_row(site):
    conn = db.connect(site.db, progress_path=site.progress)
    r = post(site, "/dictionary/state", item="乌鸦", state="recognized")
    assert r.status_code == 200 and r.text.startswith('<tr id="entry-乌鸦"') and r.text.count("<tr") == 1
    assert '<button name="state" value="recognized" class="on">recognized</button>' in r.text and r.text.count('class="on"') == 1
    assert conn.execute("SELECT kind, state, origin FROM progress.progress WHERE key = '乌鸦'").fetchone()[:] == ("word", "recognized", "manual")
    assert post(site, "/dictionary/state", item="乌", state="mastered").status_code == 200
    assert conn.execute("SELECT kind, state, origin FROM progress.progress WHERE key = '乌'").fetchone()[:] == ("character", "mastered", "manual")
    assert post(site, "/dictionary/state", item="乌鸦", state="unconfirmed").status_code == 200 and progress.state_of(conn, "word", "乌鸦") == "unconfirmed"
    r = post(site, "/dictionary/state", item="乌", state="learned")
    assert r.status_code == 422 and 'class="error">state must be unconfirmed, exposed, recognized or mastered</p>' in r.text
    assert post(site, "/dictionary/state", item="龘", state="exposed").status_code == 404


def test_edit_an_hsk_character_gloss_writes_the_tsv(site):
    path = site.data / "character-gloss.tsv"
    before = path.read_text(encoding="utf-8")
    r = get(site, "/dictionary/row/月", edit="1")
    assert r.status_code == 200 and 'hx-post="/dictionary/row/月"' in r.text and '<span class="muted">yuè</span>' in r.text and 'name="pinyin"' not in r.text
    assert 'name="gloss" aria-label="Gloss" value="moon, month"' in r.text and "<select" not in r.text and ">Edit</button>" not in r.text
    r = post(site, "/dictionary/row/月", gloss="moon; month")
    assert r.status_code == 200 and cell(r.text, "月", 4) == "moon; month" and ">Edit</button>" in r.text
    assert path.read_text(encoding="utf-8") == before.replace("月\tmoon, month\n", "月\tmoon; month\n")
    assert db.lookup_character(db.connect(site.db), "月")["gloss"] == "moon; month"
    r = post(site, "/dictionary/row/月", gloss=" ")
    assert r.status_code == 422 and 'class="error">a gloss is required</p>' in r.text and 'aria-label="Gloss" value=" "' in r.text  # the submitted value is kept
    assert post(site, "/dictionary/row/月", gloss="moon, month").status_code == 200 and path.read_text(encoding="utf-8") == before
    assert get(site, "/dictionary/row/月").text.startswith('<tr id="entry-月"') and ">Edit</button>" in get(site, "/dictionary/row/月").text
    assert get(site, "/dictionary/row/龘", edit="1").status_code == 404


def test_edit_a_supplement_entry_writes_supplement_tsv(site):
    path = site.data / "supplement.tsv"
    before = path.read_text(encoding="utf-8")
    r = get(site, "/dictionary/row/乌鸦", edit="1")
    assert 'name="pinyin" aria-label="Pinyin" value="wū yā"' in r.text and '<option value="7" selected>7–9</option>' in r.text and '<option value="">derived</option>' in r.text
    r = post(site, "/dictionary/row/乌鸦", pinyin="wu1 ya1", gloss="crow, raven", level="4")
    assert r.status_code == 200 and (cell(r.text, "乌鸦", 1), cell(r.text, "乌鸦", 2), cell(r.text, "乌鸦", 4)) == ("wū yā", "4", "crow, raven")
    assert path.read_text(encoding="utf-8") == before.replace("乌鸦\twū yā\tcrow\t7\n", "乌鸦\twū yā\tcrow, raven\t4\n")
    word = db.lookup_word(db.connect(site.db), "乌鸦")
    assert (word["pinyin"], word["meanings"], word["hsk_level"]) == ("wū yā", ["crow, raven"], 4)
    r = post(site, "/dictionary/row/乌鸦", pinyin="wū yā", gloss="crow", level="")  # derived: the characters' highest level (乌 and 鸦 are 7)
    assert r.status_code == 200 and cell(r.text, "乌鸦", 2) == "7–9" and path.read_text(encoding="utf-8") == before.replace("乌鸦\twū yā\tcrow\t7\n", "乌鸦\twū yā\tcrow\t\n")
    assert '<option value="" selected>derived</option>' in get(site, "/dictionary/row/乌鸦", edit="1").text
    r = post(site, "/dictionary/row/乌鸦", pinyin="wū yā", gloss="crow", level="9")
    assert r.status_code == 422 and 'class="error">level must be 1 to 7, not “9”</p>' in r.text and 'aria-label="Gloss" value="crow"' in r.text
    r = get(site, "/dictionary/row/啼", edit="1")  # a supplement character: pinyin, gloss, level 1–7, no "derived"
    assert 'name="pinyin" aria-label="Pinyin" value="tí"' in r.text and "derived" not in r.text and '<option value="7" selected>7–9</option>' in r.text
    assert post(site, "/dictionary/row/啼", pinyin="tí", gloss="cry, crow (of birds), weep", level="6").status_code == 200
    assert "啼\ttí\tcry, crow (of birds), weep\t6\n" in path.read_text(encoding="utf-8") and db.lookup_character(db.connect(site.db), "啼")["hsk_level"] == 6


def test_an_hsk_word_is_not_editable(site):
    html = rows(site, q="乌云")
    assert ">Edit</button>" not in html.split('<tr id="entry-乌云"')[1].split("</tr>")[0]
    for r in (get(site, "/dictionary/row/乌云", edit="1"), post(site, "/dictionary/row/乌云", gloss="x")):
        assert r.status_code == 422 and 'class="error">an HSK word is not editable; HSK meanings are read-only</p>' in r.text and 'name="gloss"' not in r.text


def test_lookup_and_add(site, probe, baseline):
    r = post(site, "/dictionary/lookup", item="乌鸦")
    assert r.status_code == 200 and r.text.startswith('<div id="add" class="card"') and 'Already in the dictionary — <a href="/dictionary?q=乌鸦">shown above</a>.' in r.text
    assert 'hx-post="/dictionary/add"' not in r.text and 'name="item" placeholder="character or word" value="乌鸦"' in r.text
    r = post(site, "/dictionary/lookup", item=probe.word)
    assert f'<span class="zh">{probe.word}</span> is not in the dictionary.' in r.text and f'name="pinyin" placeholder="pinyin" value="{probe.pinyin}"' in r.text
    assert '<option value="">derived</option>' in r.text and 'name="gloss" placeholder="gloss" value=""' in r.text
    assert 'value="dá"' in post(site, "/dictionary/lookup", item="龘").text  # pypinyin's reading for a character the dictionary lacks
    assert 'name="pinyin" placeholder="pinyin" value=""' in post(site, "/dictionary/lookup", item="月x").text  # no reading for x: blank
    r = post(site, "/dictionary/lookup", item=" ")
    assert r.status_code == 422 and 'class="error">a character or word is required</p>' in r.text
    path = site.data / "supplement.tsv"
    before = path.read_text(encoding="utf-8")
    r = post(site, "/dictionary/add", item=probe.word, pinyin=probe.pinyin, gloss="probe", level="")
    assert r.status_code == 200 and f"Added to the supplement: <span class=\"zh\">{probe.word}</span>." in r.text and 'hx-post="/dictionary/add"' not in r.text
    assert '<div id="rows" class="card" hx-swap-oob="true">' in r.text and items(r.text) == [probe.word] and shown(r.text) == "1 shown"
    assert path.read_text(encoding="utf-8") == before + f"{probe.word}\t{probe.pinyin}\tprobe\t\n"
    word = db.lookup_word(db.connect(site.db), probe.word)
    assert (word["source"], word["meanings"], word["hsk_level"], word["id"]) == ("supplement", ["probe"], probe.level, 10_000_000 + baseline.lines)
    r = post(site, "/dictionary/add", item="龘鸦", pinyin="", gloss="x", level="")
    assert r.status_code == 422 and "“龘鸦” has characters not in the dictionary: 龘; add them to data/supplement.tsv" in r.text
    assert 'name="gloss" placeholder="gloss" value="x"' in r.text and path.read_text(encoding="utf-8").count("龘") == 0
    r = post(site, "/dictionary/add", item=probe.word, pinyin="", gloss="", level="")
    assert r.status_code == 422 and f"duplicate item “{probe.word}”" in r.text
