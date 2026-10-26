import re


def count(html):
    return int(re.search(r'<p class="count">(\d+) texts</p>', html).group(1))


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_texts_list_and_filters(client):
    page = client.get("/texts").text
    assert count(page) == 5 and "枫桥夜泊" in page and "桃花源记" in page
    assert count(client.get("/texts", params={"tag": "诗词"}).text) == 4
    assert count(client.get("/texts", params={"author": "李白"}).text) == 1
    assert count(client.get("/texts", params={"period": "东晋"}).text) == 1
    assert count(client.get("/texts", params={"tag": "诗词", "period": "东晋"}).text) == 0
    assert count(client.get("/texts", params={"tag": "", "author": "", "period": ""}).text) == 5


def test_text_1_flags_missing_characters_and_finds_no_words(client):
    r = client.get("/texts/1")
    assert r.status_code == 200
    assert "枫桥夜泊" in r.text and "张继" in r.text and "唐朝" in r.text and "诗词" in r.text
    body = re.search(r'<div class="body ruby">(.*?)</div>', r.text, re.S).group(1)
    assert body.count("<ruby>") == 28 and body.count("<br>") == 1 and "，" in body and body.startswith("<ruby>月<rt></rt></ruby>")
    assert "<ruby>啼<rt></rt></ruby>" in body and "<ruby>枫<rt></rt></ruby>" in body  # absent from the master, no reading stored
    assert "28 characters, 2 not in HSK, 0 words" in r.text
    assert "<ruby>月<rt></rt></ruby>" in r.text and "No lessons yet" in r.text  # no intake yet: no readings, no lesson


def test_pages_are_english_with_chinese_content(client):
    """Labels, headings, buttons and placeholders are English; titles, bodies and tags stay Chinese."""
    pages = {url: client.get(url).text for url in ("/texts", "/texts/5", "/learn", "/learn/5")}
    for url, html in pages.items():
        assert '<html lang="en">' in html and "Chinese Learning" in html and '<a href="/texts">Texts</a> <a href="/learn">Learn</a>' in html
        for label in ("课文", "课程", "学习", "候选", "释义", "拼音", "状态", "筛选", "全部", "暂无", "添加", "删除", "编辑", "保存", "字数", "进度"):
            assert label not in re.sub(r"<(td|a|option|h1|title)[^>]*>[^<]*</\1>", "", html), (url, label)
        assert "桃花源记" in html
    assert "<th>Title</th><th>Author</th><th>Period</th><th>Tags</th>" in pages["/texts"] and "<option value=\"\">any</option>" in pages["/texts"]
    assert "<h2>Lessons</h2>" in pages["/texts/5"] and '<button>Edit pinyin</button>' not in pages["/texts/5"] and 'class="button">Edit pinyin</a>' in pages["/texts/5"]
    assert "<h1>Learn</h1>" in pages["/learn"] and "<th>Progress</th>" in pages["/learn"]
    assert "Tint:" in pages["/learn/5"] and "<button>Apply</button>" in pages["/learn/5"] and "> Show mastered</label>" in pages["/learn/5"]


def test_pinyin_edit_mode(client):
    edit = client.get("/texts/5", params={"edit": "pinyin"}).text
    assert re.search(r'<ruby>舍<rt><select name="p\d+"><option>shě</option><option>shè</option><option>shì</option></select></rt></ruby>', edit)
    assert "<button>Save readings</button>" in edit


def test_unknown_text_is_404(client):
    assert client.get("/texts/999").status_code == 404
    assert client.post("/texts/1/info", data={"author": "x"}).status_code == 404  # author and period are edited in the file


def test_api_characters(client):
    rows = client.get("/api/characters", params={"chars": "月落乌啼月"}).json()["characters"]
    assert [c["char"] for c in rows] == ["月", "落", "乌", "啼"]
    assert rows[0]["pinyin"] == "yuè" and rows[0]["hsk_level"] == 1 and rows[0]["found"]
    assert rows[0]["gloss"] == "moon, month" and rows[0]["readings"][0] == "yuè"
    assert rows[0]["meanings"][:2] == ["moon", "month"] and rows[0]["pos"] == "n,t" and rows[0]["word_level"] == 1 and rows[0]["alt_readings"] == []
    assert isinstance(rows[0]["frequency_rank"], int)
    assert rows[3] == {"char": "啼", "found": False}
