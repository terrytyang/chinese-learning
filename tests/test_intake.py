"""Intake: auto facts, stored readings for every position (pypinyin for characters the master lacks), the default lesson, and reading edits on the page."""

import json

import pytest

from chineselearning import annotations, db, progress, readings
from chineselearning.annotations import AnnotationError
from chineselearning.cli import main
from chineselearning.intake import intake
from chineselearning.texts import HAN


def connect(site):
    return db.connect(site.db, progress_path=site.progress)


def facts(site, text_id=1):
    return json.loads((site.data / "annotations" / f"{text_id}.json").read_text(encoding="utf-8"))


def lesson(site, text_id=1, lesson_id=1):
    return json.loads((site.data / "lessons" / f"{text_id}-{lesson_id}.json").read_text(encoding="utf-8"))


def test_intake_text_1_readings_facts_and_default_lesson(site):
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "mastered"}).status_code == 303
    conn = connect(site)
    assert intake(conn, 1, site.data) == {"words": 0, "characters": 2, "readings": 28, "lesson": 1}
    body = db.get_text(conn, 1)["body"]
    stored = {r["position"]: r for r in facts(site)["readings"]}
    assert set(stored) == {i for i, ch in enumerate(body) if HAN.fullmatch(ch)}
    assert all(r["origin"] == "auto" and r["char"] == body[r["position"]] for r in stored.values())
    assert (stored[0]["pinyin"], stored[3]["pinyin"], stored[9]["pinyin"]) == ("yuè", "tí", "fēng") and list(facts(site)) == ["text_id", "readings", "characters", "words"]
    assert [(c["char"], c["origin"]) for c in facts(site)["characters"]] == [("啼", "auto"), ("枫", "auto")]
    data = lesson(site)
    assert (data["lesson_id"], data["text_id"], data["name"], data["words"], data["extra_words"], data["notes"]) == (1, 1, "Learn 枫桥夜泊", [], [], [])
    assert len(data["characters"]) == 27 and "月" not in data["characters"] and "啼" in data["characters"]
    assert list(data) == ["lesson_id", "text_id", "name", "characters", "words", "extra_words", "notes"]
    states = progress.current(conn)
    assert states[("character", "月")] == "mastered" and all(states[("character", ch)] == "exposed" for ch in data["characters"])


def test_default_selection_excludes_recognized_and_mastered(site):
    conn = connect(site)
    progress.set_state(conn, "character", "月", "mastered")
    progress.set_state(conn, "character", "落", "recognized")
    progress.set_state(conn, "character", "乌", "exposed")
    progress.set_state(conn, "word", "桃花", "recognized")
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
    assert counts["words"] == len(expected) > 0 and counts["characters"] > 0 and counts["lesson"] == 1
    assert sorted(w["surface"] for w in facts(site, 5)["words"]) == expected and lesson(site, 5, 1)["words"] == expected
    page = site.client.get("/texts/5").text
    assert page.count('<tr id="word-') == counts["words"] and "<h2>Words in text <small>Learn 桃花源记</small></h2>" in page


def test_intake_refuses_rerun_and_force_leaves_lessons_and_manual_rows(site):
    conn = connect(site)
    intake(conn, 1, site.data)
    with pytest.raises(AnnotationError, match="already has"):
        intake(conn, 1, site.data)
    assert site.client.post("/texts/1/readings", data={"p2": "wù"}).status_code == 303
    assert site.client.post("/texts/1/characters/落/remove").status_code == 303
    assert site.client.post("/texts/1/lessons", data={"name": "Two"}).status_code == 303
    assert intake(connect(site), 1, site.data, force=True) == {"words": 0, "characters": 2, "readings": 27, "lesson": None}
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
    annotations.add_word(conn, 99, "行不", gloss="x")  # local word: reading prefilled from the stored and resolved readings
    assert conn.execute("SELECT pinyin FROM text_word WHERE surface = '行不'").fetchone()[0] == "hàng bù"


def test_edit_mode_sets_one_position(site):
    conn = connect(site)
    intake(conn, 5, site.data)
    body = db.get_text(conn, 5)["body"]
    positions = [i for i, ch in enumerate(body) if ch == "舍"]
    assert len(positions) > 1
    assert site.client.post("/texts/5/readings", data={f"p{positions[0]}": "shè"}).status_code == 303
    stored = {r["position"]: r for r in facts(site, 5)["readings"]}
    assert (stored[positions[0]]["pinyin"], stored[positions[0]]["origin"]) == ("shè", "manual")
    assert all(stored[p]["pinyin"] == "shě" and stored[p]["origin"] == "auto" for p in positions[1:])
    page = site.client.get("/texts/5").text
    assert page.count("<ruby>舍<rt>shè</rt></ruby>") == 1 and page.count("<ruby>舍<rt>shě</rt></ruby>") == len(positions) - 1


def test_invalid_reading_lists_allowed_readings(site):
    position = db.get_text(connect(site), 5)["body"].index("舍")
    r = site.client.post("/texts/5/readings", data={f"p{position}": "xx"})
    assert r.status_code == 422 and "the reading of “舍” must be one of shě, shè, shì" in r.text and f'name="p{position}"' in r.text


def test_auto_false_positive_is_deleted_from_candidates(site):
    intake(connect(site), 5, site.data)
    assert site.client.post("/texts/5/words/无论/remove").status_code == 303
    page = site.client.get("/texts/5").text
    assert 'name="words" value="无论"' in page and '<span class="origin origin-auto">auto</span>' in page and 'formaction="/texts/5/words/无论/delete"' in page
    assert site.client.post("/texts/5/words/无论/delete").status_code == 303
    assert "无论" not in [w["surface"] for w in facts(site, 5)["words"]] and "无论" not in lesson(site, 5, 1)["words"]
    assert site.client.post("/texts/5/words/桃花/rename").status_code == 404
