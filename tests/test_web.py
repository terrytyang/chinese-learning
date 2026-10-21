import re


def count(html):
    return int(re.search(r"共 (\d+) 篇", html).group(1))


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
    assert "28 字，" in r.text and "0 个词" in r.text
    assert "<ruby>月<rt></rt></ruby>" in r.text and "还没有课程" in r.text  # no intake yet: no readings, no lesson


def test_text_page_no_longer_computes_candidates(client):
    r = client.get("/texts/5")
    assert "<h2>词表</h2>" not in r.text and "peach blossom" not in r.text
    edit = client.get("/texts/5", params={"edit": "pinyin"}).text
    assert re.search(r'<ruby>舍<rt><select name="p\d+"><option>shě</option><option>shè</option><option>shì</option></select></rt></ruby>', edit)


def test_unknown_text_is_404(client):
    assert client.get("/texts/999").status_code == 404


def test_api_characters(client):
    rows = client.get("/api/characters", params={"chars": "月落乌啼月"}).json()["characters"]
    assert [c["char"] for c in rows] == ["月", "落", "乌", "啼"]
    assert rows[0]["pinyin"] == "yuè" and rows[0]["hsk_level"] == 1 and rows[0]["found"]
    assert rows[0]["gloss"] == "moon, month"
    assert rows[3] == {"char": "啼", "found": False}
