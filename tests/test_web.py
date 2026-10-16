import re


def count(html):
    return int(re.search(r"共 (\d+) 篇", html).group(1))


def missing_chars(html):
    return re.findall(r'<tr class="missing"><td class="char">(.)</td>', html)


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
    assert "月落乌啼霜满天，江枫渔火对愁眠。\n姑苏城外寒山寺，夜半钟声到客船。" in r.text
    assert set(missing_chars(r.text)) >= {"啼", "枫"}
    assert "28 字，" in r.text and "0 个词" in r.text
    assert re.search(r'<td class="char">月</td><td>yuè</td><td>1</td><td>新</td>', r.text)


def test_text_5_finds_words(client):
    r = client.get("/texts/5")
    words = re.findall(r'<td class="word">(.*?)</td>', r.text)
    assert words and words[0] == "桃花" and len(words) == len(set(words))
    assert "peach blossom" in r.text
    assert f"{len(words)} 个词" in r.text


def test_unknown_text_is_404(client):
    assert client.get("/texts/999").status_code == 404


def test_api_characters(client):
    rows = client.get("/api/characters", params={"chars": "月落乌啼月"}).json()["characters"]
    assert [c["char"] for c in rows] == ["月", "落", "乌", "啼"]
    assert rows[0]["pinyin"] == "yuè" and rows[0]["hsk_level"] == 1 and rows[0]["found"]
    assert rows[3] == {"char": "啼", "found": False}
