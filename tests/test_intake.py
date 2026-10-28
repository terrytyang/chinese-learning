"""Intake: auto words, stored readings for every position, the default lesson, the dictionary check, `--new`, and reading edits on the page."""

import json
import re

import pytest

from chineselearning import annotations, db, progress, readings, supplement
from chineselearning.annotations import AnnotationError
from chineselearning.cli import main
from chineselearning.intake import intake, new_texts
from chineselearning.texts import HAN

HX = {"HX-Request": "true"}


def connect(site):
    return db.connect(site.db, progress_path=site.progress)


def facts(site, text_id=1):
    return json.loads((site.data / "annotations" / f"{text_id}.json").read_text(encoding="utf-8"))


def lesson(site, text_id=1, lesson_id=1):
    return json.loads((site.data / "lessons" / f"{text_id}-{lesson_id}.json").read_text(encoding="utf-8"))


def test_intake_text_1_readings_facts_and_default_lesson(site):
    conn = connect(site)
    progress.set_state(conn, "character", "月", "mastered", "manual")
    conn.commit()
    assert intake(conn, 1, site.data) == {"words": 0, "readings": 28, "lesson": 1}
    body = db.get_text(conn, 1)["body"]
    stored = {r["position"]: r for r in facts(site)["readings"]}
    assert set(stored) == {i for i, ch in enumerate(body) if HAN.fullmatch(ch)}
    assert all(r["origin"] == "auto" and r["char"] == body[r["position"]] for r in stored.values())
    assert (stored[0]["pinyin"], stored[3]["pinyin"], stored[9]["pinyin"]) == ("yuè", "tí", "fēng") and list(facts(site)) == ["text_id", "readings", "characters", "words"]
    assert facts(site)["characters"] == []  # 啼 and 枫 are supplement characters: their readings come from the dictionary
    data = lesson(site)
    assert (data["lesson_id"], data["text_id"], data["name"], data["words"], data["extra_words"], data["notes"]) == (1, 1, "Learn 枫桥夜泊", [], [], [])
    assert len(data["characters"]) == 27 and "月" not in data["characters"] and "啼" in data["characters"]
    assert list(data) == ["lesson_id", "text_id", "name", "characters", "words", "extra_words", "notes"]
    states = progress.current(conn)
    assert states[("character", "月")] == "mastered" and all(states[("character", ch)] == "exposed" for ch in data["characters"])


def test_default_selection_excludes_recognized_and_mastered(site):
    conn = connect(site)
    progress.set_state(conn, "character", "月", "mastered", "manual")
    progress.set_state(conn, "character", "落", "recognized", "manual")
    progress.set_state(conn, "character", "乌", "exposed", "manual")
    progress.set_state(conn, "word", "桃花", "recognized", "manual")
    conn.commit()
    intake(conn, 1, site.data)
    chars = lesson(site)["characters"]
    assert len(chars) == 26 and "乌" in chars and "月" not in chars and "落" not in chars
    assert (progress.state_of(conn, "character", "月"), progress.state_of(conn, "character", "落"), progress.state_of(conn, "character", "乌")) == ("mastered", "recognized", "exposed")
    counts = intake(conn, 5, site.data)
    assert "桃花" in [w["surface"] for w in facts(site, 5)["words"]] and "桃花" not in lesson(site, 5, counts["lesson"])["words"]
    assert progress.state_of(conn, "word", "桃花") == "recognized" and progress.state_of(conn, "word", "鲜美") == "exposed"


def test_intake_text_5_words_and_lesson_words(site):
    conn = connect(site)
    expected = sorted(w["simplified"] for w in db.find_words(conn, db.get_text(conn, 5)["body"]))
    counts = intake(conn, 5, site.data)
    assert counts["words"] == len(expected) > 0 and counts["lesson"] == 1
    assert sorted(w["surface"] for w in facts(site, 5)["words"]) == expected and lesson(site, 5, 1)["words"] == expected
    tab = site.client.get("/texts/5/lessons/1/words", params={"show": "all", "min": 1, "max": 7}, headers=HX).text
    assert tab.count('<tr id="word-') == counts["words"] and f'Words in text <span class="muted">{counts["words"]}/{counts["words"]}</span>' in tab


def test_intake_refuses_rerun_and_force_leaves_lessons_and_manual_rows(site):
    conn = connect(site)
    intake(conn, 1, site.data)
    with pytest.raises(AnnotationError, match="already has"):
        intake(conn, 1, site.data)
    assert site.client.post("/texts/1/text", data={"p2": "wù"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/characters/落/remove").status_code == 200
    assert site.client.post("/texts/1/lessons", data={"name": "Two"}).status_code == 200
    assert intake(connect(site), 1, site.data, force=True) == {"words": 0, "readings": 27, "lesson": None}
    stored = {r["position"]: r for r in facts(site)["readings"]}
    assert (stored[2]["pinyin"], stored[2]["origin"], stored[1]["origin"]) == ("wù", "manual", "auto")
    assert "落" not in lesson(site)["characters"] and sorted(p.name for p in (site.data / "lessons").iterdir()) == ["1-1.json", "1-2.json"]


def test_cli_intake(site, capsys):
    args = ["--db", str(site.db), "--data", str(site.data), "--progress", str(site.progress)]
    main(["intake", "5", *args])
    assert capsys.readouterr().out.startswith("text 5: words ")
    with pytest.raises(SystemExit, match="already has"):
        main(["intake", "5", *args])
    main(["intake", "5", "--force", *args])
    with pytest.raises(SystemExit, match="no text with id 42"):
        main(["intake", "42", *args])


def test_resolver_uses_stored_rows_then_words_then_primary(site):
    conn = connect(site)
    conn.execute("INSERT INTO text (id, title, body) VALUES (99, '银行', '我去银行，\n行不行')")
    annotations.add_word(conn, 99, "银行")
    resolved = [(r["char"], r["pinyin"], r["source"]) for r in readings.resolve(conn, 99)]
    assert resolved[2:5] == [("银", "yín", "word:银行"), ("行", "háng", "word:银行"), ("行", "xíng", "primary")]
    annotations.set_reading(conn, 99, 6, "行", "hang4")  # numbered pinyin is accepted everywhere
    assert [(r["pinyin"], r["source"]) for r in readings.resolve(conn, 99) if r["position"] == 6] == [("hàng", "stored")]
    assert readings.default_pinyin(conn, 99, "行不") == "hàng bù"  # the prefill for a new supplement word: the text's readings
    with pytest.raises(AnnotationError, match="“行不” is not in the dictionary; add it to data/supplement.tsv"):
        annotations.add_word(conn, 99, "行不")
    supplement.add(conn, site.data, "行不", "", "x", "")
    annotations.add_word(conn, 99, "行不")
    assert tuple(conn.execute("SELECT t.pinyin, w.pinyin FROM text_word t JOIN word w ON w.id = t.word_id WHERE surface = '行不'").fetchone()) == (None, "xíng bù")


def test_intake_refuses_a_character_the_dictionary_lacks(site):
    (site.data / "texts" / "006-龘.md").write_text("id: 6\ntitle: 龘\ntags: 诗词\n\n龘飞龘\n", encoding="utf-8")
    db.build(site.db, site.data)
    conn = connect(site)
    with pytest.raises(AnnotationError, match="text 6 has characters not in the dictionary: 龘; add them to data/supplement.tsv"):
        intake(conn, 6, site.data)
    assert not (site.data / "annotations" / "6.json").exists() and not list((site.data / "lessons").glob("6-*.json"))
    supplement.add(conn, site.data, "龘", "da2", "dragons flying", "")
    assert intake(conn, 6, site.data) == {"words": 0, "readings": 3, "lesson": 1}
    assert [r["pinyin"] for r in facts(site, 6)["readings"]] == ["dá", "fēi", "dá"]


def test_intake_new_picks_only_texts_without_facts_or_lesson(site, capsys):
    conn = connect(site)
    assert new_texts(conn) == [1, 2, 3, 4, 5]
    assert site.client.post("/texts/3/lessons", data={"name": "A"}).status_code == 200  # a lesson alone also excludes the text
    intake(conn, 1, site.data)
    assert new_texts(conn) == [2, 4, 5]
    args = ["--db", str(site.db), "--data", str(site.data), "--progress", str(site.progress)]
    main(["intake", "--new", *args])
    out = capsys.readouterr().out
    assert [line.split(":")[0] for line in out.splitlines()] == ["text 2", "text 4", "text 5"] and "readings 20, lesson 3" in out
    assert new_texts(connect(site)) == [] and sorted(p.name for p in (site.data / "annotations").iterdir()) == ["1.json", "2.json", "4.json", "5.json"]
    main(["intake", "--new", *args])
    assert capsys.readouterr().out == "nothing to intake: every text has facts or a lesson\n"
    for argv in (["intake", *args], ["intake", "1", "--new", *args]):
        with pytest.raises(SystemExit):
            main(argv)


def test_edit_mode_sets_one_position(site):
    conn = connect(site)
    intake(conn, 5, site.data)
    body = db.get_text(conn, 5)["body"]
    positions = [i for i, ch in enumerate(body) if ch == "舍"]
    assert len(positions) > 1
    assert site.client.post("/texts/5/text", data={f"p{positions[0]}": "shè"}).status_code == 200
    stored = {r["position"]: r for r in facts(site, 5)["readings"]}
    assert (stored[positions[0]]["pinyin"], stored[positions[0]]["origin"]) == ("shè", "manual")
    assert all(stored[p]["pinyin"] == "shě" and stored[p]["origin"] == "auto" for p in positions[1:])
    page = site.client.get("/texts/5").text
    assert page.count("<ruby>舍<rt>shè</rt></ruby>") == 1 and page.count("<ruby>舍<rt>shě</rt></ruby>") == len(positions) - 1


def test_invalid_reading_lists_allowed_readings(site):
    position = db.get_text(connect(site), 5)["body"].index("舍")
    r = site.client.post("/texts/5/text", data={f"p{position}": "xx"})
    assert r.status_code == 422 and "the reading of “舍” must be one of shě, shè, shì" in r.text and f'name="p{position}"' in r.text


def test_auto_false_positive_is_deleted_from_candidates(site):
    intake(connect(site), 5, site.data)
    assert site.client.post("/texts/5/lessons/1/words/无论/include", headers=HX).status_code == 200  # unticked
    tab = site.client.get("/texts/5/lessons/1/words", params={"show": "excluded", "min": 1, "max": 7}, headers=HX).text
    assert re.findall(r'<tr id="word-(.*?)">', tab) == ["无论"] and '<span class="pill auto">auto</span>' in tab and 'hx-post="/texts/5/lessons/1/words/无论/delete' in tab
    assert site.client.post("/texts/5/lessons/1/words/无论/delete", headers=HX).status_code == 200
    assert "无论" not in [w["surface"] for w in facts(site, 5)["words"]] and "无论" not in lesson(site, 5, 1)["words"]
    assert site.client.post("/texts/5/lessons/1/words/桃花/rename").status_code == 404


def test_intake_accepts_a_words_neutral_tone_reading(site):
    """地上 reads 上 as "shang", which the character's list (shàng, shǎng) lacks; a word's reading may be the neutral-tone form, a typed one may not."""
    conn = connect(site)
    conn.execute("INSERT INTO text (id, title, body) VALUES (9, '地上', '地上霜')")
    conn.execute("INSERT INTO text_tag VALUES (9, '诗词')")
    conn.commit()
    assert intake(conn, 9, site.data)["readings"] == 3
    assert [(r["char"], r["pinyin"]) for r in facts(site, 9)["readings"]] == [("地", "dì"), ("上", "shang"), ("霜", "shuāng")]
    with pytest.raises(AnnotationError, match="the reading of “上” must be one of shàng, shǎng"):
        annotations.set_reading(conn, 9, 1, "上", "shang")
    annotations.set_reading(conn, 9, 1, "上", "shang", "suggested")
