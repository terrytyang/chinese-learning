"""Learner progress: one row per key in its own database file, the implicit `exposed` on adding to a lesson, and the admin page's state column."""

import re
from urllib.parse import unquote

import pytest

from chineselearning import db, progress
from chineselearning.intake import intake
from chineselearning.progress import ProgressError


def connect(site):
    return db.connect(site.db, progress_path=site.progress)


def test_default_learner_and_unconfirmed_state(site):
    conn = connect(site)
    assert [tuple(r) for r in conn.execute("SELECT id, name FROM progress.learner")] == [(1, "Student")]
    assert progress.state_of(conn, "character", "月") == "unconfirmed"
    assert progress.current(conn) == {}


def test_set_state_upserts_and_unconfirmed_deletes(site):
    conn = connect(site)
    assert progress.set_state(conn, "character", "月", "recognized") is True
    assert progress.set_state(conn, "character", "月", "recognized") is False
    assert progress.set_state(conn, "character", "月", "mastered") is True
    assert progress.set_state(conn, "word", "寒山寺", "exposed") is True
    conn.commit()
    rows = conn.execute("SELECT kind, key, state, changed_at FROM progress.progress ORDER BY kind, key").fetchall()
    assert [(r["kind"], r["key"], r["state"]) for r in rows] == [("character", "月", "mastered"), ("word", "寒山寺", "exposed")]
    assert all(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", r["changed_at"]) for r in rows)
    assert progress.state_of(conn, "character", "月") == "mastered"
    assert progress.current(conn) == {("character", "月"): "mastered", ("word", "寒山寺"): "exposed"}
    assert progress.set_state(conn, "character", "月", "unconfirmed") is True
    assert progress.set_state(conn, "character", "月", "unconfirmed") is False
    assert conn.execute("SELECT count(*) FROM progress.progress").fetchone()[0] == 1 and progress.state_of(conn, "character", "月") == "unconfirmed"
    with pytest.raises(ProgressError, match="state must be"):
        progress.set_state(conn, "character", "月", "unrecognized")
    with pytest.raises(ProgressError, match="no such"):
        progress.set_state(conn, "sentence", "月", "mastered")
    with pytest.raises(ProgressError, match="a single character is a character; add it in Characters"):
        progress.set_state(conn, "word", "月", "mastered")
    assert progress.current(conn) == {("word", "寒山寺"): "exposed"}


def test_expose_only_lifts_unconfirmed(site):
    conn = connect(site)
    assert progress.expose(conn, "character", "月") is True and progress.state_of(conn, "character", "月") == "exposed"
    assert progress.expose(conn, "character", "月") is False
    progress.set_state(conn, "character", "落", "mastered")
    assert progress.expose(conn, "character", "落") is False and progress.state_of(conn, "character", "落") == "mastered"


def test_adding_to_a_lesson_sets_exposed_and_nothing_else_does(site):
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "mastered"}).status_code == 303
    assert site.client.post("/texts/1/lessons", data={"name": "A"}).status_code == 303
    assert site.client.post("/texts/1/characters/add", data={"chars": ["月", "落"]}).status_code == 303
    conn = connect(site)
    assert (progress.state_of(conn, "character", "月"), progress.state_of(conn, "character", "落"), progress.state_of(conn, "character", "乌")) == ("mastered", "exposed", "unconfirmed")
    assert site.client.post("/texts/1/words/new", data={"surface": "寒山寺", "gloss": "temple", "hsk_level": "7"}).status_code == 303
    assert site.client.post("/texts/1/extra-words", data={"anchor": "月", "surface": "月亮"}).status_code == 303
    assert (progress.state_of(conn, "word", "寒山寺"), progress.state_of(conn, "word", "月亮")) == ("exposed", "exposed")
    assert site.client.post("/texts/1/characters/落/remove").status_code == 303
    assert site.client.post("/texts/1/words/寒山寺/delete").status_code == 303
    assert site.client.post("/texts/1/characters/add?cmin=1&cmax=1", data={"all": "1"}).status_code == 303
    assert (progress.state_of(conn, "character", "落"), progress.state_of(conn, "word", "寒山寺"), progress.state_of(conn, "character", "天")) == ("exposed", "exposed", "exposed")
    assert progress.state_of(conn, "character", "乌") == "unconfirmed"  # level 4: not in the filtered bulk add
    db.build(site.db, site.data)  # a rebuild imports the lesson file without touching progress
    assert progress.state_of(connect(site), "character", "天") == "exposed"


def test_build_leaves_progress_untouched(site):
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "mastered"}).status_code == 303
    before = site.progress.read_bytes()
    db.build(site.db, site.data)
    assert site.progress.read_bytes() == before
    assert progress.state_of(connect(site), "character", "月") == "mastered"
    assert site.client.post("/texts/1/lessons", data={"name": "A"}).status_code == 303
    assert site.client.post("/texts/1/characters/add", data={"chars": ["月"]}).status_code == 303
    assert "<td class=\"state\">mastered" in site.client.get("/texts/1").text


def test_page_state_column_and_buttons(site):
    intake(connect(site), 1, site.data)
    page = site.client.get("/texts/1").text
    assert page.count('<td class="state">exposed') == 28
    r = site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "recognized"})
    assert (r.status_code, unquote(r.headers["location"])) == (303, "/texts/1#char-月")
    page = site.client.get("/texts/1").text
    assert re.search(r'<tr id="char-月">.*?<td class="state">recognized', page, re.S)
    assert '<button name="state" value="recognized" disabled>recognized</button>' in page
    assert '<button name="state" value="unconfirmed">unconfirmed</button>' in page
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "recognized"}).status_code == 303
    assert connect(site).execute("SELECT count(*) FROM progress.progress").fetchone()[0] == 28
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "unconfirmed"}).status_code == 303
    assert connect(site).execute("SELECT count(*) FROM progress.progress").fetchone()[0] == 27
    r = site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "bogus"})
    assert r.status_code == 422 and "state must be" in r.text
    assert site.client.post("/texts/1/progress", data={"kind": "word", "key": "月", "state": "mastered"}).status_code == 422


def test_candidate_filters_by_state_and_level(site):
    intake(connect(site), 1, site.data)
    for ch in ("月", "落", "乌"):
        assert site.client.post(f"/texts/1/characters/{ch}/remove").status_code == 303
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "月", "state": "mastered"}).status_code == 303
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "落", "state": "recognized"}).status_code == 303
    assert site.client.post("/texts/1/progress", data={"kind": "character", "key": "乌", "state": "unconfirmed"}).status_code == 303
    page = site.client.get("/texts/1").text
    assert re.findall(r'name="chars" value="(.)"', page) == ["月", "落", "乌"]
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cstate": "mastered"}).text) == ["月"]
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cstate": "unconfirmed"}).text) == ["乌"]
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cstate": "exposed"}).text) == []
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cmin": "4"}).text) == ["落", "乌"]
    assert re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1", params={"cmin": "4", "cmax": "4"}).text) == ["落"]
    assert '<option value="4" selected>4</option>' in site.client.get("/texts/1", params={"cmin": "4"}).text
