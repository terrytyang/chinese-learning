"""The assembled material and the student pages built on it."""

import re

from chineselearning import annotations, db, material, progress


def connect(site):
    return db.connect(site.db, progress_path=site.progress)


def test_assemble_text_1(site):
    conn = connect(site)
    m = material.assemble(conn, 1)
    assert m["text"]["title"] == "枫桥夜泊" and m["counts"] == {"chars": 28, "unique": 28, "unrecognized": 28, "recognized": 0, "mastered": 0}
    assert "".join(c["char"] for c in m["chars"]) == db.get_text(conn, 1)["body"]
    assert m["chars"][7] == {"position": 7, "char": "，", "han": False}
    yue = m["chars"][0]
    assert (yue["char"], yue["pinyin"], yue["source"], yue["traditional"], yue["hsk_level"], yue["gloss"], yue["in_master"], yue["study"], yue["state"]) == (
        "月", "yuè", "primary", "月", 1, "moon, month", True, False, "unrecognized")
    ti = next(c for c in m["chars"] if c["char"] == "啼")
    assert ti["in_master"] is False and ti["pinyin"] is None and ti["source"] == "none" and ti["hsk_level"] is None
    annotations.add_reading(conn, 1, "啼", "tí")
    annotations.add_character(conn, 1, "啼", "鸟叫")
    annotations.add_word(conn, 1, "寒山寺", gloss="苏州的寺")
    m = material.assemble(conn, 1)
    ti = next(c for c in m["chars"] if c["char"] == "啼")
    assert (ti["pinyin"], ti["source"], ti["study"], ti["gloss"]) == ("tí", "override", True, "鸟叫")
    start = db.get_text(conn, 1)["body"].index("寒山寺")
    assert m["words"] == [{"surface": "寒山寺", "pinyin": "hán shān sì", "hsk_level": None, "gloss": "苏州的寺", "meanings": [], "linked": False,
                           "state": "unrecognized", "spans": [[start, start + 3]]}]
    assert m["highlight"] == [{"start": start, "end": start + 3, "surface": "寒山寺"}]
    assert m["study"] == [{"char": "啼", "pinyin": "tí", "gloss": "鸟叫", "hsk_level": None, "state": "unrecognized"}]


def test_highlight_is_non_overlapping_leftmost_longest(site):
    conn = connect(site)
    conn.execute("INSERT INTO text (id, title, body) VALUES (99, 'x', '去银行走路，行走')")
    annotations.add_word(conn, 99, "银行")
    annotations.add_word(conn, 99, "行走", gloss="走")
    m = material.assemble(conn, 99)
    assert [(w["surface"], w["spans"]) for w in m["words"]] == [("银行", [[1, 3]]), ("行走", [[2, 4], [6, 8]])]
    assert m["highlight"] == [{"start": 1, "end": 3, "surface": "银行"}, {"start": 6, "end": 8, "surface": "行走"}]


def test_traditional_uses_phrases_and_keeps_length(site):
    conn = connect(site)
    assert next(c for c in material.assemble(conn, 1)["chars"] if c["char"] == "乌")["traditional"] == "烏"
    conn.execute("INSERT INTO text (id, title, body) VALUES (98, 'x', '我在后面\n头发')")
    forms = {c["char"]: c["traditional"] for c in material.assemble(conn, 98)["chars"] if c["han"]}
    assert forms["后"] == "後" and forms["发"] == "髮" and forms["我"] == "我"
    body = "月落乌啼霜满天，江枫渔火对愁眠。\n姑苏城外寒山寺，夜半钟声到客船。"
    assert len(material.traditional(body)) == len(body)


def reader_body(html):
    return re.search(r'<div class="reader[^"]*">(.*?)</div>', html, re.S).group(1)


def test_reader_toggles(site):
    assert site.client.post("/texts/1/words", data={"surface": "寒山寺", "gloss": "苏州的寺", "hsk_level": "7"}).status_code == 303
    assert site.client.post("/texts/1/characters", data={"char": "愁", "gloss": "忧愁"}).status_code == 303
    plain = site.client.get("/learn/1").text
    assert '<span class="c lvl-1 state-unrecognized">月</span>' in plain and '<span class="c lvl-0 state-unrecognized">啼</span>' in plain
    level = connect(site).execute("SELECT hsk_level FROM character WHERE char = '愁'").fetchone()[0]
    assert f'<span class="c lvl-{level} state-unrecognized study">愁</span>' in plain
    assert "<ruby>" not in plain and "data-gloss" not in plain and 'class="w"' not in plain and 'class="reader tint-none"' in plain
    assert reader_body(plain).count("<br>") == 1 and reader_body(plain).count("<p>") == 1 and "，" in reader_body(plain)
    assert "<h2>学习字</h2>" in plain and "<h2>词语</h2>" not in plain and "忧愁" in plain
    ruby = site.client.get("/learn/1", params={"pinyin": 1}).text
    assert "<ruby>月<rt>yuè</rt></ruby>" in ruby and "<ruby>啼<rt></rt></ruby>" in ruby
    trad = site.client.get("/learn/1", params={"traditional": 1}).text
    assert "烏" in reader_body(trad) and "乌" not in reader_body(trad)
    assert "<ruby>烏<rt>wū</rt></ruby>" in site.client.get("/learn/1", params={"traditional": 1, "pinyin": 1}).text
    glossed = site.client.get("/learn/1", params={"gloss": 1}).text
    assert 'data-gloss="moon, month">月</span>' in glossed and 'data-gloss="忧愁">愁</span>' in glossed
    words = site.client.get("/learn/1", params={"words": 1}).text
    assert '<span class="w" data-gloss="苏州的寺"><span class="c lvl-' in words and "<h2>词语</h2>" in words and '<td class="word">寒山寺</td>' in words
    assert reader_body(words).count('class="w"') == 1
    for tint in ("level", "state"):
        assert f'class="reader tint-{tint}"' in site.client.get("/learn/1", params={"tint": tint}).text
    assert 'class="reader tint-none"' in site.client.get("/learn/1", params={"tint": "bogus"}).text
    form = site.client.get("/learn/1", params={"pinyin": 1, "tint": "level"}).text
    assert 'name="pinyin" value="1" checked' in form and 'name="tint" value="level" checked' in form
    assert site.client.get("/learn/999").status_code == 404


def test_reader_omits_mastered_from_lists_unless_shown(site):
    assert site.client.post("/texts/1/words", data={"surface": "寒山寺", "gloss": "苏州的寺", "hsk_level": "7"}).status_code == 303
    assert site.client.post("/texts/1/characters", data={"char": "愁", "gloss": "忧愁"}).status_code == 303
    assert site.client.post("/texts/1/expansions", data={"char": "月", "surface": "月亮"}).status_code == 303
    for kind, key in (("word", "寒山寺"), ("character", "愁")):
        assert site.client.post("/texts/1/progress", data={"kind": kind, "key": key, "state": "mastered"}).status_code == 303
    page = site.client.get("/learn/1", params={"words": 1}).text
    assert '<td class="word">寒山寺</td>' not in page and '<td class="char">愁</td>' not in page and '<td class="word">月亮</td>' in page
    assert reader_body(page).count('class="w"') == 1 and "state-mastered study" in page
    shown = site.client.get("/learn/1", params={"words": 1, "show_mastered": 1}).text
    assert '<td class="word">寒山寺</td>' in shown and '<td class="char">愁</td>' in shown


def test_learn_index_lists_texts_with_counts(site):
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "mastered"}).status_code == 303
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "落", "state": "recognized"}).status_code == 303
    page = site.client.get("/learn").text
    rows = re.findall(r'<a href="/learn/(\d+)">(.*?)</a>.*?<td class="unique">(\d+)</td>.*?<td class="shares">(.*?)</td>', page, re.S)
    assert [r[0] for r in rows] == ["1", "2", "3", "4", "5"] and rows[0][1] == "枫桥夜泊"
    conn = connect(site)
    for text_id, _, unique, shares in rows:
        c = material.assemble(conn, int(text_id))["counts"]
        assert int(unique) == c["unique"] and shares == f"{c['unrecognized']} / {c['recognized']} / {c['mastered']}"
    assert rows[0][3] == "26 / 1 / 1"
    assert 'class="s-mastered" style="width: ' in page and progress.state_of(conn, "character", "月") == "mastered"
