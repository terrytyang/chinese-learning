"""The assembled material, with and without a lesson, and the student pages built on it."""

import re

from chineselearning import annotations, db, lessons, material, progress
from chineselearning.intake import intake


def connect(site):
    return db.connect(site.db, progress_path=site.progress)


def test_assemble_text_1_without_and_with_a_lesson(site):
    conn = connect(site)
    m = material.assemble(conn, 1)
    assert m["lesson"] is None and m["study"] == [] and m["extra_words"] == [] and m["notes"] == []
    assert m["counts"] == {"chars": 28, "unique": 28, "unconfirmed": 28, "exposed": 0, "recognized": 0, "mastered": 0}
    assert "".join(c["char"] for c in m["chars"]) == db.get_text(conn, 1)["body"] and m["chars"][7] == {"position": 7, "char": "，", "han": False}
    yue = m["chars"][0]
    assert (yue["pinyin"], yue["source"], yue["traditional"], yue["hsk_level"], yue["gloss"], yue["in_master"], yue["study"]) == (None, "none", "月", 1, "moon, month", True, False)
    assert (yue["meanings"][:2], yue["pos"], yue["word_level"], yue["alt_readings"]) == (["moon", "month"], "n,t", 1, []) and isinstance(yue["frequency_rank"], int)
    assert {k: m["chars"][3][k] for k in ("char", "meanings", "pos", "word_level", "frequency_rank")} == {"char": "啼", "meanings": None, "pos": None, "word_level": None, "frequency_rank": None}
    intake(conn, 1, site.data)
    annotations.set_reading(conn, 1, 3, "啼", "tì")
    annotations.update(conn, 1, "characters", ("啼",), {"gloss": "鸟叫"})
    annotations.add_word(conn, 1, "寒山寺", gloss="苏州的寺")
    lesson_id = lessons.for_text(conn, 1)[0]["id"]
    lessons.add_word(conn, lesson_id, "寒山寺")
    lessons.add_extra_word(conn, lesson_id, "月亮", "月")
    lessons.add_extra_word(conn, lesson_id, "苏州", "姑苏", gloss="Suzhou")
    lessons.add_note(conn, lesson_id, "首句写景", "月落乌啼")
    plain, with_lesson = material.assemble(conn, 1), material.assemble(conn, 1, lesson_id)
    assert plain["chars"][0]["pinyin"] == "yuè" and plain["chars"][0]["source"] == "auto"
    ti = next(c for c in with_lesson["chars"] if c["char"] == "啼")
    assert (ti["pinyin"], ti["source"], ti["in_master"], ti["study"], ti["gloss"], ti["state"]) == ("tì", "manual", False, True, "鸟叫", "exposed")
    assert plain["chars"][3]["study"] is False and [w["surface"] for w in plain["words"]] == ["寒山寺"] and plain["highlight"][0]["surface"] == "寒山寺"
    start = db.get_text(conn, 1)["body"].index("寒山寺")
    assert with_lesson["lesson"] == {"id": lesson_id, "name": "Learn 枫桥夜泊"} and with_lesson["words"][0]["spans"] == [[start, start + 3]]
    assert len(with_lesson["study"]) == 28 and with_lesson["study"][3] == {"char": "啼", "pinyin": "tì", "gloss": "鸟叫", "hsk_level": None, "state": "exposed"}
    extra = with_lesson["extra_words"]
    assert [(e["surface"], e["anchor"], e["kind"], e["linked"], e["pinyin"]) for e in extra] == [("月亮", "月", "expansion", True, "yuè liang"), ("苏州", "姑苏", "related", False, "sū zhōu")]
    assert with_lesson["notes"] == [{"anchor": "月落乌啼", "note": "首句写景"}]
    lessons.remove(conn, lesson_id, "words", "寒山寺")
    assert material.assemble(conn, 1, lesson_id)["words"] == [] and material.assemble(conn, 1)["words"] != []


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


def test_reader_toggles_on_text_and_lesson(site):
    plain = site.client.get("/learn/1").text
    assert '<span class="c lvl-1 state-unconfirmed">月</span>' in plain and '<span class="c lvl-0 state-unconfirmed">啼</span>' in plain
    intake(connect(site), 1, site.data)
    assert site.client.post("/texts/1/lessons/1/words/new", data={"surface": "寒山寺", "step": "2", "gloss": "苏州的寺", "hsk_level": "7"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/characters/愁/facts", data={"gloss": "忧愁"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/expansions/add", data={"anchor": "月", "surface": "月亮"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/related/add", data={"anchor": "姑苏", "surface": "苏州", "step": "2", "gloss": "Suzhou"}).status_code == 200
    plain = site.client.get("/learn/1").text
    assert '<span class="c lvl-1 state-exposed">月</span>' in plain and '<span class="c lvl-0 state-exposed">啼</span>' in plain
    assert "study" not in reader_body(plain) and "<h2>Characters</h2>" not in plain and "<ruby>" not in plain and 'class="reader tint-none"' in plain
    level = connect(site).execute("SELECT hsk_level FROM character WHERE char = '愁'").fetchone()[0]
    with_lesson = site.client.get("/learn/1/1").text
    assert f'<span class="c lvl-{level} state-exposed study">愁</span>' in with_lesson and "<h2>Characters</h2>" in with_lesson and "忧愁" in with_lesson
    assert '<small class="lesson-name">Learn 枫桥夜泊</small>' in with_lesson and 'action="/learn/1/1"' in with_lesson
    assert "<h2>Expansions</h2>" in with_lesson and '<td class="char">月</td><td class="word">月亮</td><td>yuè liang</td><td>the moon</td>' in with_lesson
    assert "<h2>Related words</h2>" in with_lesson and '<td class="">姑苏</td><td class="word">苏州</td><td>sū zhōu</td><td>Suzhou</td>' in with_lesson
    ruby = site.client.get("/learn/1/1", params={"pinyin": 1}).text
    assert "<ruby>月<rt>yuè</rt></ruby>" in ruby and "<ruby>啼<rt>tí</rt></ruby>" in ruby
    trad = site.client.get("/learn/1", params={"traditional": 1}).text
    assert "烏" in reader_body(trad) and "乌" not in reader_body(trad)
    glossed = site.client.get("/learn/1", params={"gloss": 1}).text
    assert 'data-gloss="moon, month">月</span>' in glossed and 'data-gloss="忧愁">愁</span>' in glossed
    for path in ("/learn/1", "/learn/1/1"):
        words = site.client.get(path, params={"words": 1}).text
        assert '<span class="w" data-gloss="苏州的寺"><span class="c lvl-' in words and '<td class="word">寒山寺</td>' in words and "<h2>Words</h2>" in words
    for tint in ("level", "state"):
        assert f'class="reader tint-{tint}"' in site.client.get("/learn/1", params={"tint": tint}).text
    assert site.client.get("/learn/999").status_code == 404 and site.client.get("/learn/1/9").status_code == 404
    assert site.client.get("/learn/2/1").status_code == 404  # lesson 1 belongs to text 1


def test_reader_omits_mastered_from_lists_unless_shown(site):
    intake(connect(site), 1, site.data)
    assert site.client.post("/texts/1/lessons/1/words/new", data={"surface": "寒山寺", "step": "2", "gloss": "苏州的寺", "hsk_level": "7"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/expansions/add", data={"anchor": "月", "surface": "月亮"}).status_code == 200
    for kind, key in (("word", "寒山寺"), ("character", "愁")):
        assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": kind, "key": key, "state": "mastered"}).status_code == 200
    page = site.client.get("/learn/1/1", params={"words": 1}).text
    assert '<td class="word">寒山寺</td>' not in page and '<td class="char">愁</td>' not in page and '<td class="word">月亮</td>' in page
    assert reader_body(page).count('class="w"') == 1 and "state-mastered study" in page
    shown = site.client.get("/learn/1/1", params={"words": 1, "show_mastered": 1}).text
    assert '<td class="word">寒山寺</td>' in shown and '<td class="char">愁</td>' in shown


def test_learn_index_lists_texts_and_lessons_with_counts(site):
    intake(connect(site), 1, site.data)
    assert site.client.post("/texts/1/lessons", data={"name": "Level 1"}).status_code == 200
    assert site.client.post("/texts/1/lessons/2/characters/add", data={"chars": ["月"]}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": "月", "state": "mastered"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": "落", "state": "recognized"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": "乌", "state": "unconfirmed"}).status_code == 200
    page = site.client.get("/learn").text
    assert "<th>unconfirmed / exposed / recognized / mastered</th>" in page
    texts = re.findall(r'<tr class="text">.*?<a href="/learn/(\d+)">(.*?)</a> <a class="original" href="/learn/\d+">text only</a>.*?<td class="unique">(\d+)</td>.*?<td class="shares">(.*?)</td>', page, re.S)
    assert [t[0] for t in texts] == ["1", "2", "3", "4", "5"] and texts[0][1:] == ("枫桥夜泊", "28", "1 / 25 / 1 / 1")
    owned = re.findall(r'<tr class="lesson">.*?<a href="/learn/(\d+)/(\d+)">(.*?)</a>.*?<td class="unique">(\d+)</td>.*?<td class="shares">(.*?)</td>', page, re.S)
    assert owned == [("1", "1", "Learn 枫桥夜泊", "28", "1 / 25 / 1 / 1"), ("1", "2", "Level 1", "1", "0 / 0 / 0 / 1")]
    conn = connect(site)
    for text_id, _, unique, shares in texts:
        c = material.assemble(conn, int(text_id))["counts"]
        assert int(unique) == c["unique"] and shares == " / ".join(str(c[s]) for s in progress.STATES)
    assert progress.state_of(conn, "character", "月") == "mastered" and site.client.get("/learn/1/2").status_code == 200
