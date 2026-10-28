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
