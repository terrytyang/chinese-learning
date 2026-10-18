"""Intake: auto facts, stored readings for every position, the default lesson, and reading edits on the page."""

import json

import pytest

from chineselearning import annotations, db, readings
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
    assert intake(conn, 1, site.data) == {"words": 0, "characters": 2, "readings": 26, "lesson": 1}
    body = db.get_text(conn, 1)["body"]
    stored = {r["position"]: r for r in facts(site)["readings"]}
    assert set(stored) == {i for i, ch in enumerate(body) if HAN.fullmatch(ch) and ch not in "啼枫"}
    assert all(r["origin"] == "auto" and r["char"] == body[r["position"]] for r in stored.values())
    assert stored[0]["pinyin"] == "yuè" and list(facts(site)) == ["text_id", "readings", "characters", "words"]
    assert [(c["char"], c["origin"]) for c in facts(site)["characters"]] == [("啼", "auto"), ("枫", "auto")]
    data = lesson(site)
    assert (data["lesson_id"], data["text_id"], data["name"], data["words"], data["expansions"], data["notes"]) == (1, 1, "枫桥夜泊", [], [], [])
    assert len(data["characters"]) == 27 and "月" not in data["characters"] and "啼" in data["characters"]
    assert list(data) == ["lesson_id", "text_id", "name", "characters", "words", "expansions", "notes"]


def test_intake_text_5_words_and_lesson_words(site):
    conn = connect(site)
    expected = sorted(w["simplified"] for w in db.find_words(conn, db.get_text(conn, 5)["body"]))
    counts = intake(conn, 5, site.data)
    assert counts["words"] == len(expected) > 0 and counts["characters"] > 0 and counts["lesson"] == 1
    assert sorted(w["surface"] for w in facts(site, 5)["words"]) == expected and lesson(site, 5, 1)["words"] == expected
    page = site.client.get("/texts/5").text
    assert page.count("自动") == counts["words"] and "<h2>课程：桃花源记</h2>" in page and "已选" in page


def test_intake_refuses_rerun_and_force_leaves_lessons_and_manual_rows(site):
    conn = connect(site)
    intake(conn, 1, site.data)
    with pytest.raises(AnnotationError, match="已有"):
        intake(conn, 1, site.data)
    assert site.client.post("/texts/1/readings", data={"char": "乌", "pinyin": "wù"}).status_code == 303
    assert site.client.post("/texts/1/characters/落/delete").status_code == 303
    assert site.client.post("/texts/1/lessons", data={"name": "二"}).status_code == 303
    assert intake(connect(site), 1, site.data, force=True) == {"words": 0, "characters": 2, "readings": 25, "lesson": None}
    stored = {r["position"]: r for r in facts(site)["readings"]}
    assert (stored[2]["pinyin"], stored[2]["origin"], stored[1]["origin"]) == ("wù", "manual", "auto")
    assert "落" not in lesson(site)["characters"] and sorted(p.name for p in (site.data / "lessons").iterdir()) == ["1-1.json", "1-2.json"]


def test_cli_intake(site, capsys):
    args = ["--db", str(site.db), "--data", str(site.data), "--progress", str(site.progress)]
    main(["intake", "5", *args])
    assert capsys.readouterr().out.startswith("text 5: words ")
    with pytest.raises(SystemExit, match="已有"):
        main(["intake", "5", *args])
    main(["intake", "5", "--force", *args])
    with pytest.raises(SystemExit, match="没有 id 为 42"):
        main(["intake", "42", *args])


def test_resolver_uses_stored_rows_then_words_then_primary(site):
    conn = connect(site)
    conn.execute("INSERT INTO text (id, title, body) VALUES (99, '银行', '我去银行，\n行不行')")
    annotations.add_word(conn, 99, "银行")
    resolved = [(r["char"], r["pinyin"], r["source"]) for r in readings.resolve(conn, 99)]
    assert resolved[2:5] == [("银", "yín", "word:银行"), ("行", "háng", "word:银行"), ("行", "xíng", "primary")]
    annotations.set_reading(conn, 99, 6, "行", "hàng")
    assert [(r["pinyin"], r["source"]) for r in readings.resolve(conn, 99) if r["position"] == 6] == [("hàng", "stored")]
    annotations.add_word(conn, 99, "行不", gloss="x")  # local word: reading prefilled from the stored and resolved readings
    assert conn.execute("SELECT pinyin FROM text_word WHERE surface = '行不'").fetchone()[0] == "hàng bù"


def test_set_reading_everywhere_then_reset(site):
    conn = connect(site)
    intake(conn, 5, site.data)
    body = db.get_text(conn, 5)["body"]
    positions = [i for i, ch in enumerate(body) if ch == "舍"]
    assert site.client.post("/texts/5/readings", data={"char": "舍", "pinyin": "shè"}).status_code == 303
    stored = {r["position"]: r for r in facts(site, 5)["readings"]}
    assert all(stored[p]["pinyin"] == "shè" and stored[p]["origin"] == "manual" for p in positions) and len(positions) > 1
    page = site.client.get("/texts/5").text
    assert '<span class="pinyin">shè</span> <small>指定</small>' in page and "<option selected>shè</option>" in page
    assert 'action="/texts/5/readings/舍/delete"' in page
    assert site.client.post("/texts/5/readings/舍/delete").status_code == 303
    stored = {r["position"]: r for r in facts(site, 5)["readings"]}
    assert all(stored[p]["pinyin"] == "shě" and stored[p]["origin"] == "auto" for p in positions)
    assert '<span class="pinyin">shě</span> <small>默认</small>' in site.client.get("/texts/5").text


def test_invalid_reading_lists_allowed_readings(site):
    r = site.client.post("/texts/5/readings", data={"char": "舍", "pinyin": "xx"})
    assert r.status_code == 422 and "「舍」的读音只能是 shě、shè、shì" in r.text


def test_confirm_flips_origin_to_manual(site):
    intake(connect(site), 5, site.data)
    assert site.client.post("/texts/5/words/桃花/confirm").status_code == 303
    assert next(w for w in facts(site, 5)["words"] if w["surface"] == "桃花")["origin"] == "manual"
    page = site.client.get("/texts/5").text
    assert 'action="/texts/5/words/桃花/confirm"' not in page and page.count("手动") == 1
    assert site.client.post("/texts/5/words/桃花/rename").status_code == 404
