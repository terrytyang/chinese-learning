"""Importing a text from the page: the preview, the file written, the rows (the same as a later build makes), and the refusals."""

import re

from chineselearning import db, texts
from chineselearning.intake import FACT_TABLES

HX = {"HX-Request": "true"}
POEM = {"title": "静夜思", "author": "李白", "period": "唐朝", "tags": "诗词", "body": "床前明月光，疑是地上霜。\r\n举头望明月，低头思故乡。\r\n"}
FILE = "id: {}\ntitle: 静夜思\nauthor: 李白\nperiod: 唐朝\ntags: 诗词\n\n床前明月光，疑是地上霜。\n举头望明月，低头思故乡。\n"  # .format(the next id)
TABLES = ("text", "text_tag", *FACT_TABLES, "lesson", "lesson_character", "lesson_word", "lesson_extra_word", "lesson_note")


def rows(db_path):
    conn = db.connect(db_path, readonly=True)
    return {t: sorted(tuple(r) for r in conn.execute(f"SELECT * FROM {t}")) for t in TABLES}


def test_compose_and_file_name():
    assert texts.compose(6, " 静夜思 ", "诗词", "床前明月光，  \r\n\r\n举头望明月。\n\n", "李白", " ") == "id: 6\ntitle: 静夜思\nauthor: 李白\ntags: 诗词\n\n床前明月光，\n\n举头望明月。\n"
    assert texts.file_name(6, "静夜思") == "006-静夜思.md" and texts.file_name(12, " 绝句 ") == "012-绝句.md"


def test_page_and_preview(site, baseline):
    n = baseline.next_text_id
    page = site.client.get("/texts/import").text
    assert "<h1>Import a text</h1>" in page and 'class="on"' in page.split("<nav")[1].split("</nav>")[0].split("Learn")[0]  # Texts is current
    assert 'hx-post="/texts/import/preview" hx-trigger="input delay:300ms" hx-target="#preview"' in page and 'name="tags" value="诗词"' in page
    assert '<pre id="preview" class="zh">Fill in a title and the body; the file to be written appears here.</pre>' in page
    assert site.client.post("/texts/import/preview", data={**POEM, "body": " "}, headers=HX).text.endswith("appears here.</pre>")
    assert 'href="/texts/import">Import a text</a>' in site.client.get("/texts").text
    r = site.client.post("/texts/import/preview", data=POEM, headers=HX)
    assert r.status_code == 200 and r.text == f'<pre id="preview" class="zh">{FILE.format(n)}</pre>'
    r = site.client.post("/texts/import/preview", data={**POEM, "tags": " "}, headers=HX)
    assert r.text == f'<pre id="preview" class="zh">data/texts/{n:03d}-静夜思.md: empty value for &#39;tags&#39;</pre>'
    assert "no blank line" not in site.client.post("/texts/import/preview", data={**POEM, "body": "正文"}, headers=HX).text


def test_import_writes_the_file_inserts_intakes_and_matches_a_later_build(site, tmp_path, baseline):
    n = baseline.next_text_id
    body = "床前明月光，疑是地上霜。\n举头望明月，低头思故乡。"
    words = sorted(w["simplified"] for w in db.find_words(db.connect(site.db), body))  # what intake finds depends on the supplement
    r = site.client.post("/texts/import", data=POEM, headers=HX)
    assert r.status_code == 200 and r.text.startswith('<div id="import">')
    assert f"Written <code>data/texts/{n:03d}-静夜思.md</code> · intake: 17 characters, {len(words)} words · " in r.text
    assert f'<a href="/texts/{n}">Open <span class="zh">静夜思</span> →</a>' in r.text and 'name="title" value=""' in r.text and 'name="tags" value="诗词"' in r.text
    assert '<pre id="preview" class="zh" hx-swap-oob="true">Fill in a title and the body; the file to be written appears here.</pre>' in r.text
    path = site.data / "texts" / f"{n:03d}-静夜思.md"
    assert path.read_text(encoding="utf-8") == FILE.format(n)
    conn = db.connect(site.db)
    text = db.get_text(conn, n)
    assert (text["title"], text["author"], text["period"], text["tags"], text["body"]) == ("静夜思", "李白", "唐朝", ["诗词"], body)
    assert conn.execute("SELECT count(*) FROM text_reading WHERE text_id = ?", (n,)).fetchone()[0] == 20
    assert sorted(r[0] for r in conn.execute("SELECT surface FROM text_word WHERE text_id = ?", (n,))) == words and {"地上", "故乡"} <= set(words)
    assert [tuple(r) for r in conn.execute("SELECT id, name FROM lesson WHERE text_id = ?", (n,))] == [(1, "Learn 静夜思")]
    assert (site.data / "annotations" / f"{n}.json").is_file() and (site.data / "lessons" / f"{n}-1.json").is_file()
    page = site.client.get(f"/texts/{n}").text
    assert "<ruby>床<rt>chuáng</rt></ruby>" in page and "Learn 静夜思" in page
    before = rows(site.db)
    db.build(tmp_path / "again.sqlite", site.data)
    assert rows(tmp_path / "again.sqlite") == before and before["text"][-1][:2] == (n, "静夜思")
    r = site.client.post("/texts/import", data={**POEM, "title": "春晓二", "body": "春眠不觉晓"}, headers=HX)
    assert r.status_code == 200 and f"Written <code>data/texts/{n + 1:03d}-春晓二.md</code>" in r.text and (site.data / "texts" / f"{n + 1:03d}-春晓二.md").is_file()


def test_import_refuses_before_writing(site, baseline):
    n = baseline.next_text_id
    files = set(p.name for p in (site.data / "texts").glob("*.md"))
    r = site.client.post("/texts/import", data={**POEM, "body": "床前明月光，龘龖。"}, headers=HX)
    assert r.status_code == 422 and 'class="error">characters not in the dictionary: 龘, 龖 — <a href="/dictionary">add them there</a>, then import again</p>' in r.text
    assert 'name="body" rows="8"' in r.text and "龘龖" in r.text and 'name="title" value="静夜思"' in r.text  # the form keeps its values
    r = site.client.post("/texts/import", data={**POEM, "title": "静夜思/一"}, headers=HX)
    assert r.status_code == 422 and 'class="error">the title must not contain /</p>' in r.text
    r = site.client.post("/texts/import", data={**POEM, "title": ""}, headers=HX)
    assert r.status_code == 422 and f"data/texts/{n:03d}-.md: empty value for &#39;title&#39;" in r.text
    r = site.client.post("/texts/import", data={**POEM, "body": "  \n"}, headers=HX)
    assert r.status_code == 422 and "empty body" in r.text
    assert set(p.name for p in (site.data / "texts").glob("*.md")) == files and db.get_text(db.connect(site.db), n) is None
    assert not list((site.data / "annotations").glob(f"{n}.json")) and not list((site.data / "lessons").glob(f"{n}-*.json"))
