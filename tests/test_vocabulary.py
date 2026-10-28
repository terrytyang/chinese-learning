"""Vocabulary lessons: creation and default names, members from the dictionary, files of both shapes, the symmetric exposure rule,
the dictionary page's Add all shown and Changed filter, and the lesson page."""

import json
import re
from datetime import datetime, timezone

import pytest

from chineselearning import db, lesson_files, lessons, progress
from chineselearning.annotations import AnnotationError

HX = {"HX-Request": "true"}
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def connect(site):
    return db.connect(site.db, progress_path=site.progress)


def get(site, path, **params):
    return site.client.get(path, params=params, headers=HX)


def post(site, path, **fields):
    return site.client.post(path, data=fields, headers=HX)


def states(conn):
    return {k: s for (_, k), s in progress.current(conn).items()}


def test_create_default_names_and_duplicates(site):
    conn = connect(site)
    assert lessons.default_name(conn) == f"Vocabulary {TODAY}"
    first = lessons.create(conn, None, lessons.default_name(conn))
    assert lessons.default_name(conn) == f"Vocabulary {TODAY} (2)"
    second = lessons.create(conn, None, lessons.default_name(conn))
    assert lessons.default_name(conn) == f"Vocabulary {TODAY} (3)"
    assert lessons.vocabulary(conn) == [{"id": second, "text_id": None, "name": f"Vocabulary {TODAY} (2)"}, {"id": first, "text_id": None, "name": f"Vocabulary {TODAY}"}]
    with pytest.raises(AnnotationError, match=f"a lesson named “Vocabulary {TODAY}” already exists"):
        lessons.create(conn, None, f"Vocabulary {TODAY}")
    with pytest.raises(AnnotationError, match="already exists"):
        lessons.rename(conn, second, f"Vocabulary {TODAY}")
    lessons.create(conn, 1, f"Vocabulary {TODAY}")  # a text lesson may share the name
    assert lessons.for_text(conn, 1)[0]["name"] == f"Vocabulary {TODAY}" and lessons.get(conn, first)["text_id"] is None


def test_members_come_from_the_dictionary(site, probe):
    conn = connect(site)
    lesson = lessons.create(conn, None, "V")
    lessons.add_character(conn, lesson, "月")
    lessons.add_character(conn, lesson, "啼")  # a supplement character
    lessons.add_word(conn, lesson, "银行")
    lessons.add_word(conn, lesson, "乌鸦")  # a supplement word
    lessons.add_word(conn, lesson, "乌鸦")  # a duplicate is a no-op
    for args, message in [(("add_character", "龘"), "“龘” is not in the dictionary"), (("add_character", "月亮"), "“月亮” is not a single character"),
                          (("add_word", probe.word), f"“{probe.word}” is not a dictionary word"), (("add_word", "月"), "a single character is a character")]:
        with pytest.raises(AnnotationError, match=message):
            getattr(lessons, args[0])(conn, lesson, args[1])
    with pytest.raises(AnnotationError, match="a vocabulary lesson's words are members; add it as a word"):
        lessons.add_extra_word(conn, lesson, "月亮", "月")
    note = lessons.add_note(conn, lesson, "a note")
    with pytest.raises(AnnotationError, match="a vocabulary lesson's notes have no anchor"):
        lessons.add_note(conn, lesson, "another", "月")
    with pytest.raises(AnnotationError, match="a vocabulary lesson's notes have no anchor"):
        lessons.update(conn, lesson, "notes", (note,), {"note": "edited", "anchor": "月"})
    content = lessons.load(conn, lesson)
    assert sorted(c["char"] for c in content["characters"]) == ["啼", "月"] and content["words"] == {"银行", "乌鸦"} and content["extra_words"] == []
    assert [(n["note"], n["anchor"]) for n in content["notes"]] == [("a note", None)]


def test_files_of_both_shapes_round_trip_and_build(site, tmp_path):
    conn = connect(site)
    lesson = lessons.create(conn, None, "V")
    lessons.add_character(conn, lesson, "月")
    lessons.add_word(conn, lesson, "银行")
    lessons.add_note(conn, lesson, "n")
    conn.commit()
    lesson_files.write_file(conn, lesson, site.data)
    path = site.data / "lessons" / f"{lesson}.json"
    expected = {"lesson_id": lesson, "text_id": None, "name": "V", "characters": ["月"], "words": ["银行"], "extra_words": [], "notes": [{"anchor": None, "note": "n", "origin": "manual"}]}
    assert json.loads(path.read_text(encoding="utf-8")) == expected and lesson_files.export(conn, lesson) == expected
    counts = db.build(tmp_path / "again.sqlite", site.data)
    again = db.connect(tmp_path / "again.sqlite", readonly=True)
    assert counts["lesson"] == 1 and lesson_files.export(again, lesson) == expected and lessons.vocabulary(again)[0]["name"] == "V"
    for name, content, message in [(f"1-{lesson}.json", expected, f"the file name should be {lesson}.json"),
                                   ("1.json", {**expected, "text_id": 1}, "the file name should be 1-1.json"),
                                   ("1-1.json", {**expected, "lesson_id": 1, "text_id": 1, "words": []}, None)]:
        path.unlink(missing_ok=True)
        for stale in (site.data / "lessons").glob("*.json"):
            stale.unlink()
        (site.data / "lessons" / name).write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        if message:
            with pytest.raises(AnnotationError, match=re.escape(f"{name}: {message}")):
                db.build(tmp_path / "x.sqlite", site.data)
        else:
            assert db.build(tmp_path / "x.sqlite", site.data)["lesson"] == 1
    for stale in (site.data / "lessons").glob("*.json"):
        stale.unlink()
    conn = connect(site)
    lesson = lessons.create(conn, None, "W")
    conn.commit()
    lesson_files.write_file(conn, lesson, site.data)
    assert (site.data / "lessons" / f"{lesson}.json").is_file()
    lessons.delete(conn, lesson)  # empty: allowed
    conn.commit()
    lesson_files.write_file(conn, lesson, site.data)
    assert not (site.data / "lessons" / f"{lesson}.json").exists()


def test_removal_undoes_an_automatic_exposure_only_when_no_lesson_holds_it(site):
    conn = connect(site)
    progress.set_state(conn, "character", "乌", "exposed", "manual")
    progress.set_state(conn, "word", "银行", "exposed", "import")
    conn.commit()
    v = lessons.create(conn, None, "V")
    for ch in "月乌":
        lessons.add_character(conn, v, ch)
        progress.expose(conn, "character", ch)
    for w in ("银行", "乌鸦"):
        lessons.add_word(conn, v, w)
        progress.expose(conn, "word", w)
    t = lessons.create(conn, 1, "T")
    lessons.add_character(conn, t, "月")
    conn.commit()
    assert states(conn) == {"月": "exposed", "乌": "exposed", "银行": "exposed", "乌鸦": "exposed"}
    from chineselearning.admin.common import deselect

    deselect(conn, v, "characters", "月")  # the text lesson still holds 月
    deselect(conn, v, "characters", "乌")  # manual: stays
    deselect(conn, v, "words", "银行")  # import: stays
    deselect(conn, v, "words", "乌鸦")  # auto and alone: back to unconfirmed
    assert states(conn) == {"月": "exposed", "乌": "exposed", "银行": "exposed"} and lessons.held(conn, "character", "月") and not lessons.held(conn, "word", "乌鸦")
    deselect(conn, t, "characters", "月")
    assert states(conn) == {"乌": "exposed", "银行": "exposed"}


def items(html):
    return re.findall(r'<tr id="entry-(.*?)"', html)


def test_add_all_shown_to_a_new_and_an_existing_lesson(site):
    conn = connect(site)
    filters = {"q": "乌", "kind": "all", "source": "all", "min": "1", "max": "7", "state": "unconfirmed"}
    shown = items(get(site, "/dictionary/rows", **filters).text)
    assert shown == ["乌黑", "乌", "乌云", "乌鸦", "鸦"]
    r = post(site, "/dictionary/add-to-lesson", lesson="new", **filters)
    assert r.status_code == 200 and r.text.startswith('<div id="rows" class="card">') and items(r.text) == []  # now exposed: no longer unconfirmed
    lesson = lessons.vocabulary(conn)[0]
    assert lesson["name"] == f"Vocabulary {TODAY}" and f'Added 5 to Vocabulary {TODAY} · <a href="/lessons/{lesson["id"]}">Open →</a>' in r.text
    assert f'<option value="{lesson["id"]}" selected>Vocabulary {TODAY}</option>' in r.text and '<option value="new">New lesson…</option>' in r.text
    content = lessons.load(conn, lesson["id"])
    assert sorted(c["char"] for c in content["characters"]) == ["乌", "鸦"] and content["words"] == {"乌黑", "乌云", "乌鸦"}
    data = json.loads((site.data / "lessons" / f"{lesson['id']}.json").read_text(encoding="utf-8"))
    assert (data["text_id"], data["characters"], data["words"]) == (None, ["乌", "鸦"], ["乌云", "乌鸦", "乌黑"])
    assert states(conn) == {"乌": "exposed", "鸦": "exposed", "乌黑": "exposed", "乌云": "exposed", "乌鸦": "exposed"}
    r = post(site, "/dictionary/add-to-lesson", lesson=str(lesson["id"]), **{**filters, "state": "exposed"})
    assert r.status_code == 200 and f"Added 0 to Vocabulary {TODAY} · " in r.text and len(items(r.text)) == 5  # the same rows: nothing changes
    assert json.loads((site.data / "lessons" / f"{lesson['id']}.json").read_text(encoding="utf-8")) == data
    r = post(site, "/dictionary/add-to-lesson", lesson="new", q="月亮", kind="all", source="all", min="1", max="7", state="any")
    second = lessons.vocabulary(conn)[0]
    assert second["name"] == f"Vocabulary {TODAY} (2)" and f"Added 1 to Vocabulary {TODAY} (2)" in r.text and lessons.load(conn, second["id"])["words"] == {"月亮"}
    assert r.text.index(f'value="{second["id"]}"') < r.text.index(f'value="{lesson["id"]}"')  # newest first
    assert post(site, "/dictionary/add-to-lesson", lesson="999", q="月亮").status_code == 404
    lessons.create(conn, 1, "T")
    conn.commit()
    assert post(site, "/dictionary/add-to-lesson", lesson=str(lessons.for_text(conn, 1)[0]["id"]), q="月亮").status_code == 404  # a text lesson is not a target


def test_changed_filter_and_the_dates_endpoint(site):
    conn = connect(site)
    progress.set_state(conn, "character", "月", "mastered", "manual", changed_at="2026-09-01T10:00:00Z")
    progress.set_state(conn, "character", "落", "recognized", "manual", changed_at="2026-10-01T10:00:00Z")
    progress.set_state(conn, "word", "银行", "exposed", "import", changed_at="2026-10-01")
    progress.set_state(conn, "character", "乌", "exposed", "auto", changed_at="2026-10-15T23:59:59Z")
    conn.commit()
    rows = lambda changed, date="", q="": set(items(get(site, "/dictionary/rows", q=q, kind="all", changed=changed, date=date).text))  # noqa: E731
    assert rows("on", "2026-10-01") == {"落", "银行"} and rows("before", "2026-10-01") == {"月"} and rows("on_or_before", "2026-10-01") == {"月", "落", "银行"}
    assert rows("after", "2026-10-01") == {"乌"} and rows("on_or_after", "2026-10-01") == {"落", "银行", "乌"} and rows("on", "2026-10-02") == set()
    assert "天" in rows("any", q="天") and "天" in rows("any", "2026-10-01", q="天") and "天" in rows("on", q="天")  # unconfirmed rows match only any; no date means no constraint
    assert "天" not in rows("on", "2026-10-01", q="天") and items(get(site, "/dictionary/rows", changed="on", date="2026-10-01", state="unconfirmed").text) == []
    page = site.client.get("/dictionary", params={"changed": "on", "date": "2026-10-01"}).text
    assert '<select name="changed" aria-label="Changed" hx-get="/dictionary/changed-dates" hx-target="#date" hx-swap="outerHTML" hx-include="#date">' in page
    assert '<option value="on" selected>on</option>' in page and '<select id="date" name="date" aria-label="Date"><option value="2026-10-15">2026-10-15 (1)</option><option value="2026-10-01" selected>2026-10-01 (2)</option><option value="2026-09-01">2026-09-01 (1)</option></select>' in page
    r = get(site, "/dictionary/changed-dates", changed="after", date="2026-10-01")
    assert r.status_code == 200 and r.text == '<input id="date" type="date" name="date" aria-label="Date" value="2026-10-01">'
    assert get(site, "/dictionary/changed-dates", changed="any", date="2026-10-01").text == '<input id="date" type="hidden" name="date" value="2026-10-01">'
    assert get(site, "/dictionary/changed-dates", changed="on").text.startswith('<select id="date" name="date" aria-label="Date"><option value="2026-10-15">2026-10-15 (1)</option>')
