"""Learner progress: one row per key in its own database file, the implicit `exposed` on adding to a lesson, and the admin page's state column."""

import re

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
    assert progress.set_state(conn, "character", "月", "recognized", "manual") is True
    assert progress.set_state(conn, "character", "月", "recognized", "manual") is False
    assert progress.set_state(conn, "character", "月", "mastered", "manual") is True
    assert progress.set_state(conn, "word", "寒山寺", "exposed", "manual") is True
    conn.commit()
    rows = conn.execute("SELECT kind, key, state, changed_at FROM progress.progress ORDER BY kind, key").fetchall()
    assert [(r["kind"], r["key"], r["state"]) for r in rows] == [("character", "月", "mastered"), ("word", "寒山寺", "exposed")]
    assert [r[0] for r in conn.execute("SELECT origin FROM progress.progress ORDER BY kind")] == ["manual", "manual"]
    assert all(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", r["changed_at"]) for r in rows)
    assert progress.state_of(conn, "character", "月") == "mastered"
    assert progress.current(conn) == {("character", "月"): "mastered", ("word", "寒山寺"): "exposed"}
    assert progress.set_state(conn, "character", "月", "mastered", "manual") is False  # same state, same origin: nothing
    before = conn.execute("SELECT changed_at FROM progress.progress WHERE key = '月'").fetchone()[0]
    assert progress.set_state(conn, "character", "月", "mastered", "import", changed_at="2026-09-01") is True  # same state, another origin: origin and date
    assert tuple(conn.execute("SELECT origin, changed_at FROM progress.progress WHERE key = '月'").fetchone()) == ("import", "2026-09-01") and before != "2026-09-01"
    assert progress.set_state(conn, "character", "月", "unconfirmed", "manual") is True
    assert progress.set_state(conn, "character", "月", "unconfirmed", "manual") is False
    assert progress.set_state(conn, "character", "月", "unconfirmed", "auto") is False  # no row: origin is moot
    assert conn.execute("SELECT count(*) FROM progress.progress").fetchone()[0] == 1 and progress.state_of(conn, "character", "月") == "unconfirmed"
    with pytest.raises(ProgressError, match="state must be"):
        progress.set_state(conn, "character", "月", "unrecognized", "manual")
    with pytest.raises(ProgressError, match="origin must be auto, manual or import"):
        progress.set_state(conn, "character", "月", "mastered", "page")
    with pytest.raises(ProgressError, match="no such"):
        progress.set_state(conn, "sentence", "月", "mastered", "manual")
    with pytest.raises(ProgressError, match="a single character is a character; add it in Characters"):
        progress.set_state(conn, "word", "月", "mastered", "manual")
    assert progress.current(conn) == {("word", "寒山寺"): "exposed"}


def test_expose_only_lifts_unconfirmed(site):
    conn = connect(site)
    assert progress.expose(conn, "character", "月") is True and progress.state_of(conn, "character", "月") == "exposed"
    assert conn.execute("SELECT origin FROM progress.progress WHERE key = '月'").fetchone()[0] == "auto"
    assert progress.expose(conn, "character", "月") is False
    progress.set_state(conn, "character", "落", "mastered", "manual")
    assert progress.expose(conn, "character", "落") is False and progress.state_of(conn, "character", "落") == "mastered"


def test_adding_to_a_lesson_sets_exposed_and_removing_undoes_it(site):
    """Adding sets exposed from unconfirmed; removing an item from its last lesson undoes an automatic exposure and nothing else."""
    conn = connect(site)
    progress.set_state(conn, "character", "月", "mastered", "manual")
    conn.commit()
    assert site.client.post("/texts/1/lessons", data={"name": "A"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/characters/add", data={"chars": ["月", "落"]}).status_code == 200
    assert (progress.state_of(conn, "character", "月"), progress.state_of(conn, "character", "落"), progress.state_of(conn, "character", "乌")) == ("mastered", "exposed", "unconfirmed")
    assert site.client.post("/texts/1/lessons/1/words/new", data={"surface": "寒山寺", "step": "2", "gloss": "temple", "hsk_level": "7"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/expansions/add", data={"anchor": "月", "surface": "月亮"}).status_code == 200
    assert (progress.state_of(conn, "word", "寒山寺"), progress.state_of(conn, "word", "月亮")) == ("exposed", "exposed")
    assert site.client.post("/texts/1/lessons/1/characters/落/remove").status_code == 200
    assert site.client.post("/texts/1/lessons/1/words/寒山寺/delete").status_code == 200
    level_1 = re.findall(r'name="chars" value="(.)"', site.client.get("/texts/1/lessons/1/characters", params={"min": 1, "max": 1, "state": "any"}).text)
    assert "天" in level_1 and "乌" not in level_1
    assert site.client.post("/texts/1/lessons/1/characters/add", data={"chars": level_1}).status_code == 200
    assert (progress.state_of(conn, "character", "落"), progress.state_of(conn, "word", "寒山寺"), progress.state_of(conn, "character", "天")) == ("unconfirmed", "unconfirmed", "exposed")
    assert progress.state_of(conn, "character", "乌") == "unconfirmed"  # not in the filtered bulk add
    assert site.client.post("/texts/1/lessons/1/characters/add", data={"chars": ["落"]}).status_code == 200
    assert site.client.post("/texts/1/lessons", data={"name": "B"}).status_code == 200
    assert site.client.post("/texts/1/lessons/2/characters/add", data={"chars": ["落"]}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/characters/落/remove").status_code == 200
    assert progress.state_of(conn, "character", "落") == "exposed"  # lesson B still holds it
    assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": "天", "state": "exposed"}).status_code == 200  # the lit button: origin manual
    assert site.client.post("/texts/1/lessons/1/characters/天/remove").status_code == 200
    assert progress.state_of(conn, "character", "天") == "exposed"  # a manual row survives removal
    db.build(site.db, site.data)  # a rebuild imports the lesson file without touching progress
    assert progress.state_of(connect(site), "character", "天") == "exposed"


def test_build_leaves_progress_untouched(site):
    conn = connect(site)
    progress.set_state(conn, "character", "月", "mastered", "manual")
    conn.commit()
    conn.close()
    before = site.progress.read_bytes()
    db.build(site.db, site.data)
    assert site.progress.read_bytes() == before
    assert progress.state_of(connect(site), "character", "月") == "mastered"
    assert site.client.post("/texts/1/lessons", data={"name": "A"}).status_code == 200
    assert site.client.post("/texts/1/lessons/1/characters/add", data={"chars": ["月"]}).status_code == 200
    assert re.search(r'<tr id="char-月">.*?value="mastered" class="on"', site.client.get("/texts/1").text, re.S)


def test_page_state_column_and_buttons(site):
    intake(connect(site), 1, site.data)
    page = site.client.get("/texts/1").text
    assert page.count('value="exposed" class="on"') == 28
    r = site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": "月", "state": "recognized"}, headers={"HX-Request": "true"})
    assert r.status_code == 200 and r.text.startswith('<div id="tabs"')
    assert re.search(r'<tr id="char-月">.*?<button name="state" value="recognized" class="on">recognized</button>', r.text, re.S)
    assert '<button name="state" value="unconfirmed">unconfirmed</button>' in r.text
    assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": "月", "state": "recognized"}).status_code == 200
    assert connect(site).execute("SELECT count(*) FROM progress.progress").fetchone()[0] == 28
    assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": "月", "state": "unconfirmed"}).status_code == 200
    assert connect(site).execute("SELECT count(*) FROM progress.progress").fetchone()[0] == 27
    r = site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": "月", "state": "bogus"})
    assert r.status_code == 422 and "state must be" in r.text
    assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "word", "key": "月", "state": "mastered"}).status_code == 422


def test_candidate_filters_by_state_and_level(site):
    intake(connect(site), 1, site.data)
    for ch in ("月", "落", "乌"):
        assert site.client.post(f"/texts/1/lessons/1/characters/{ch}/remove").status_code == 200
    for ch, state in (("月", "mastered"), ("落", "recognized"), ("乌", "unconfirmed")):
        assert site.client.post("/texts/1/lessons/1/characters/progress", data={"kind": "character", "key": ch, "state": state}).status_code == 200
    tab = "/texts/1/lessons/1/characters"
    shown = lambda **params: re.findall(r'name="chars" value="(.)"', site.client.get(tab, params=params).text)  # noqa: E731
    assert shown() == ["乌"] and shown(state="any") == ["月", "落", "乌"]  # default: unconfirmed or exposed
    assert shown(state="mastered") == ["月"] and shown(state="unconfirmed") == ["乌"] and shown(state="exposed") == []
    assert shown(state="any", min=4) == ["落", "乌"] and shown(state="any", min=4, max=4) == ["落"]
    assert '<option value="4" selected>4</option>' in site.client.get(tab, params={"min": "4"}).text


def test_release_undoes_only_an_automatic_exposure(site):
    conn = connect(site)
    assert progress.expose(conn, "character", "月") and progress.release(conn, "character", "月") and progress.state_of(conn, "character", "月") == "unconfirmed"
    progress.set_state(conn, "character", "落", "exposed", "manual")
    progress.set_state(conn, "word", "银行", "exposed", "import")
    progress.set_state(conn, "character", "乌", "recognized", "auto")
    assert not progress.release(conn, "character", "落") and not progress.release(conn, "word", "银行") and not progress.release(conn, "character", "乌")
    assert not progress.release(conn, "character", "天")  # no row
    assert {k: s for (_, k), s in progress.current(conn).items()} == {"落": "exposed", "银行": "exposed", "乌": "recognized"}
