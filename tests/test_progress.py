"""Learner progress: append-only state in its own database file, and the admin page's state column."""

import re
from urllib.parse import unquote

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
    assert site.client.post("/texts/1/lessons", data={"name": "课"}).status_code == 303
    assert site.client.post("/texts/1/characters/add", data={"chars": ["月"]}).status_code == 303
    assert "<td class=\"state\">掌握" in site.client.get("/texts/1").text


def test_page_state_column_and_buttons(site):
    from chineselearning.intake import intake

    intake(connect(site), 1, site.data)
    page = site.client.get("/texts/1").text
    assert page.count('<td class="state">未识') == 28
    r = site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "recognized"})
    assert (r.status_code, unquote(r.headers["location"])) == (303, "/texts/1#char-月")
    page = site.client.get("/texts/1").text
    assert re.search(r'<tr id="char-月">.*?<td class="state">认识', page, re.S)
    assert '<button name="state" value="recognized" disabled>认识</button>' in page
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "recognized"}).status_code == 303
    assert connect(site).execute("SELECT count(*) FROM progress.progress").fetchone()[0] == 1
    r = site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "bogus"})
    assert r.status_code == 422 and "状态只能是" in r.text


def test_candidate_filters_by_state_and_level(site):
    from chineselearning.intake import intake

    intake(connect(site), 1, site.data)
    for ch in ("月", "落", "乌"):
        assert site.client.post(f"/texts/1/characters/{ch}/remove").status_code == 303
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "mastered"}).status_code == 303
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "落", "state": "recognized"}).status_code == 303
    page = site.client.get("/texts/1").text
    assert re.findall(r'name="chars" value="(.)"', page) == ["月", "落", "乌"]
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cstate": "mastered"}).text) == ["月"]
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cstate": "unrecognized"}).text) == ["乌"]
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cmin": "4"}).text) == ["落", "乌"]
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cmin": "4", "cmax": "4"}).text) == ["落"]
    assert '<option value="4" selected>4</option>' in site.client.get("/texts/1", params={"cmin": "4"}).text
