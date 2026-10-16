"""Learner progress: append-only state in its own database file, and the admin page's state column."""

import re

import pytest

from chineselearning import db, progress
from chineselearning.progress import ProgressError


def connect(site):
    return db.connect(site.db, progress_path=site.progress)


def test_default_learner_and_unrecognized_state(site):
    conn = connect(site)
    assert [tuple(r) for r in conn.execute("SELECT id, name FROM progress.learner")] == [(1, "学生")]
    assert progress.state_of(conn, "character", "月") == "unrecognized"
    assert progress.current(conn) == {}


def test_set_state_appends_rows_and_latest_wins(site):
    conn = connect(site)
    assert progress.set_state(conn, "character", "月", "recognized") is True
    assert progress.set_state(conn, "character", "月", "recognized") is False
    assert progress.set_state(conn, "character", "月", "mastered") is True
    assert progress.set_state(conn, "word", "寒山寺", "recognized") is True
    conn.commit()
    rows = conn.execute("SELECT kind, key, state, changed_at FROM progress.progress ORDER BY id").fetchall()
    assert [(r["kind"], r["key"], r["state"]) for r in rows] == [("character", "月", "recognized"), ("character", "月", "mastered"), ("word", "寒山寺", "recognized")]
    assert all(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", r["changed_at"]) for r in rows)
    assert progress.state_of(conn, "character", "月") == "mastered"
    assert progress.current(conn) == {("character", "月"): "mastered", ("word", "寒山寺"): "recognized"}
    with pytest.raises(ProgressError):
        progress.set_state(conn, "character", "月", "known")
    with pytest.raises(ProgressError):
        progress.set_state(conn, "sentence", "月", "mastered")


def test_build_leaves_progress_untouched(site):
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "mastered"}).status_code == 303
    before = site.progress.read_bytes()
    db.build(site.db, site.data)
    assert site.progress.read_bytes() == before
    assert progress.state_of(connect(site), "character", "月") == "mastered"
    assert "<td class=\"state\">掌握" in site.client.get("/texts/1").text


def test_page_state_column_and_buttons(site):
    page = site.client.get("/texts/1").text
    assert page.count('<td class="state">未识') == 28
    r = site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "recognized"})
    assert (r.status_code, r.headers["location"]) == (303, "/texts/1")
    page = site.client.get("/texts/1").text
    assert re.search(r'<td class="char">月</td>.*?<td class="state">认识', page, re.S)
    assert '<button name="state" value="recognized" disabled>认识</button>' in page
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "recognized"}).status_code == 303
    assert connect(site).execute("SELECT count(*) FROM progress.progress").fetchone()[0] == 1
    r = site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "bogus"})
    assert r.status_code == 422 and "状态只能是" in r.text


def test_hide_mastered_omits_rows_and_adjusts_counts(site):
    assert site.client.post("/texts/1/words", data={"surface": "寒山寺", "gloss": "寺", "hsk_level": "7"}).status_code == 303
    assert site.client.post("/texts/1/expansions", data={"char": "月", "surface": "月亮"}).status_code == 303
    for kind, key in (("character", "月"), ("character", "落"), ("word", "寒山寺")):
        assert site.client.post("/texts/1/progress", data={"kind": kind, "key": key, "state": "mastered"}).status_code == 303
    page = site.client.get("/texts/1").text
    assert "28 字，" in page and '<td class="char">月</td>' in page and '<td class="word">寒山寺</td>' in page
    page = site.client.get("/texts/1", params={"hide_mastered": "1"}).text
    assert "26 字（已掌握 2 个已隐藏），2 个不在字库，0 个词" in page
    assert re.findall(r'<td class="char">(.)</td>', page).count("月") == 1  # only the 扩展 row, not the 字表
    assert '<td class="char">落</td>' not in page and '<td class="word">寒山寺</td>' not in page
    assert '<td class="word">月亮</td>' in page and '<input type="checkbox" name="hide_mastered" value="1" checked>' in page
    assert 'action="/texts/1/progress?hide_mastered=1"' in page and 'action="/texts/1/words?hide_mastered=1"' in page
    assert "?edit=expansions:月/月亮&amp;hide_mastered=1" in page  # autoescaped in the href
    r = site.client.post("/texts/1/progress?hide_mastered=1", data={"kind": "character", "key": "乌", "state": "mastered"})
    assert (r.status_code, r.headers["location"]) == (303, "/texts/1?hide_mastered=1")
