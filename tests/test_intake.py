"""Intake, reading resolution, and confirm."""

import json
import re

import pytest
from chineselearning import annotations, db, readings
from chineselearning.annotations import AnnotationError
from chineselearning.cli import main
from chineselearning.intake import intake


def test_intake_text_1_two_auto_characters_no_words(site):
    conn = db.connect(site.db)
    assert intake(conn, 1, site.data) == {"words": 0, "characters": 2}
    rows = conn.execute("SELECT char, gloss, origin FROM text_character WHERE text_id = 1 ORDER BY char").fetchall()
    assert [tuple(r) for r in rows] == [("啼", None, "auto"), ("枫", None, "auto")]
    data = json.loads(site.file.read_text(encoding="utf-8"))
    assert list(data) == ["text_id", "characters", "words", "expansions", "readings", "notes"]
    assert data["words"] == [] and all(row["origin"] == "auto" for kind in annotations.KINDS for row in data[kind])


def test_intake_text_5_matches_find_words(site):
    conn = db.connect(site.db)
    expected = [w["simplified"] for w in db.find_words(conn, db.get_text(conn, 5)["body"])]
    counts = intake(conn, 5, site.data)
    assert counts["words"] == len(expected) > 0 and counts["characters"] > 0
    rows = conn.execute("SELECT surface, pinyin, origin FROM text_word WHERE text_id = 5").fetchall()
    assert sorted(r["surface"] for r in rows) == sorted(expected)
    assert all(r["origin"] == "auto" and r["pinyin"] is None for r in rows)
    data = json.loads((site.data / "annotations" / "5.json").read_text(encoding="utf-8"))
    assert all("origin" in row for kind in annotations.KINDS for row in data[kind])
    page = site.client.get("/texts/5").text
    assert page.count("自动") == counts["words"] + counts["characters"]
    assert "peach blossom" in page and f"{len(expected)} 个词" in page and "<h2>词表</h2>" not in page


def test_intake_refuses_rerun_and_force_keeps_manual_rows(site):
    intake(db.connect(site.db), 1, site.data)
    with pytest.raises(AnnotationError, match="已有"):
        intake(db.connect(site.db), 1, site.data)
    assert site.client.post("/texts/1/characters", data={"char": "愁", "gloss": "忧愁"}).status_code == 303
    assert site.client.post("/texts/1/characters/枫/delete").status_code == 303
    assert site.client.post("/texts/1/characters/啼/confirm").status_code == 303
    assert intake(db.connect(site.db), 1, site.data, force=True) == {"words": 0, "characters": 1}
    rows = {r["char"]: r["origin"] for r in db.connect(site.db).execute("SELECT char, origin FROM text_character WHERE text_id = 1")}
    assert rows == {"啼": "manual", "枫": "auto", "愁": "manual"}


def test_cli_intake(site, capsys):
    main(["intake", "5", "--db", str(site.db), "--data", str(site.data)])
    assert capsys.readouterr().out.startswith("text 5: words ")
    with pytest.raises(SystemExit, match="已有"):
        main(["intake", "5", "--db", str(site.db), "--data", str(site.data)])
    main(["intake", "5", "--force", "--db", str(site.db), "--data", str(site.data)])
    with pytest.raises(SystemExit, match="没有 id 为 42"):
        main(["intake", "42", "--db", str(site.db), "--data", str(site.data)])


def test_reading_resolution_primary_then_override(site):
    conn = db.connect(site.db)
    position = db.get_text(conn, 5)["body"].index("便舍船") + 1
    at = lambda: next(r for r in readings.readings_for(conn, 5) if r["position"] == position)  # noqa: E731
    assert (at()["char"], at()["pinyin"], at()["source"]) == ("舍", "shě", "primary")
    annotations.add_reading(conn, 5, "舍", "shè")
    assert (at()["pinyin"], at()["source"]) == ("shè", "override")
    assert all(r["pinyin"] == "shè" for r in readings.readings_for(conn, 5) if r["char"] == "舍")


def test_reading_resolution_from_linked_word(site):
    conn = db.connect(site.db)
    conn.execute("INSERT INTO text (id, title, body) VALUES (99, '银行', '我去银行，\n行不行')")
    annotations.add_word(conn, 99, "银行")
    resolved = [(r["char"], r["pinyin"], r["source"]) for r in readings.readings_for(conn, 99)]
    assert resolved[2:4] == [("银", "yín", "word:银行"), ("行", "háng", "word:银行")]
    assert resolved[4:] == [("行", "xíng", "primary"), ("不", "bù", "primary"), ("行", "xíng", "primary")]
    assert [r["position"] for r in readings.readings_for(conn, 99)] == [0, 1, 2, 3, 6, 7, 8]
    annotations.add_word(conn, 99, "行不", gloss="x")  # local word: reading prefilled per character
    assert tuple(conn.execute("SELECT word_id, pinyin FROM text_word WHERE surface = '行不'").fetchone()) == (None, "xíng bù")


def test_set_reading_on_page_updates_file_and_clears(site):
    assert site.client.post("/texts/5/readings", data={"char": "舍", "pinyin": "shè"}).status_code == 303
    page = site.client.get("/texts/5").text
    assert re.search(r'<td class="char">舍</td>\s*<td class="reading">\s*<span class="pinyin">shè</span> <small>指定</small>', page)
    assert "<option selected>shè</option>" in page and 'action="/texts/5/readings/舍/delete"' in page
    data = json.loads((site.data / "annotations" / "5.json").read_text(encoding="utf-8"))
    assert data["readings"] == [{"char": "舍", "pinyin": "shè", "position": None, "origin": "manual"}]
    assert site.client.post("/texts/5/readings", data={"char": "舍", "pinyin": "shì"}).status_code == 303
    assert "<option selected>shì</option>" in site.client.get("/texts/5").text
    assert site.client.post("/texts/5/readings/舍/delete").status_code == 303
    assert not (site.data / "annotations" / "5.json").exists()
    assert "<small>默认</small>" in site.client.get("/texts/5").text


def test_invalid_reading_lists_allowed_readings(site):
    r = site.client.post("/texts/5/readings", data={"char": "舍", "pinyin": "xx"})
    assert r.status_code == 422 and "「舍」的读音只能是 shě、shè、shì" in r.text
    # 山 has one reading: no pull-down, but a bogus value is still rejected
    assert 'name="char" value="山">\n            <select' not in r.text
    assert "「山」的读音只能是 shān" in site.client.post("/texts/5/readings", data={"char": "山", "pinyin": "shan"}).text


def test_confirm_flips_origin_to_manual(site):
    intake(db.connect(site.db), 5, site.data)
    assert site.client.post("/texts/5/words/桃花/confirm").status_code == 303
    conn = db.connect(site.db, readonly=True)
    assert conn.execute("SELECT origin FROM text_word WHERE text_id = 5 AND surface = '桃花'").fetchone()[0] == "manual"
    data = json.loads((site.data / "annotations" / "5.json").read_text(encoding="utf-8"))
    assert {"surface": "桃花", "pinyin": None, "gloss": None, "origin": "manual"} in data["words"]
    page = site.client.get("/texts/5").text
    assert 'action="/texts/5/words/桃花/confirm"' not in page and page.count("手动") == 1
    assert site.client.post("/texts/5/words/桃花/rename").status_code == 404

