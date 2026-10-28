"""The data/ drift guard: the fingerprint build records, the banner on admin pages, the supplement writers' refusal, and the
app's own writes keeping the record current."""

import os

import pytest

from chineselearning import db, drift, gloss_file, lesson_files, lessons, progress, progress_files, supplement
from chineselearning.intake import intake
from chineselearning.supplement import SupplementError

HX = {"HX-Request": "true"}


def bump(path):
    """A hand edit: the content changes and the mtime moves on (older, so a same-second write still differs)."""
    path.write_text(path.read_text(encoding="utf-8") + "# edited by hand\n", encoding="utf-8")
    os.utime(path, (path.stat().st_atime, path.stat().st_mtime - 100))


def test_build_records_every_file_and_changed_names_differences(site):
    conn = db.connect(site.db)
    record = drift.stored(conn)
    assert record == drift.fingerprint(site.data) and "supplement.tsv" in record and "texts/001-枫桥夜泊.md" in record and "hsk.sql" in record
    assert all(isinstance(v, list) and len(v) == 2 for v in record.values()) and drift.changed(conn, site.data) == []
    bump(site.data / "supplement.tsv")
    (site.data / "texts" / "099-x.md").write_text("id: 99\ntitle: x\ntags: 诗词\n\n月\n", encoding="utf-8")
    (site.data / "character-gloss.tsv").unlink()
    assert drift.changed(conn, site.data) == ["character-gloss.tsv", "supplement.tsv", "texts/099-x.md"]
    assert drift.message(["supplement.tsv"]) == "data/ has changed since the last build (supplement.tsv): run `chineselearning build`"


def test_banner_on_admin_pages_only_and_build_clears_it(site):
    pages = ("/texts", "/texts/1", "/texts/import", "/dictionary")
    assert all('class="banner"' not in site.client.get(p).text for p in pages)
    bump(site.data / "supplement.tsv")
    for p in pages:
        assert '<div class="banner">data/ has changed since the last build (supplement.tsv): run `chineselearning build`</div>' in site.client.get(p).text, p
    conn = db.connect(site.db)
    lesson = lessons.create(conn, None, "V")
    conn.commit()
    assert '<div class="banner">data/ has changed' in site.client.get(f"/lessons/{lesson}").text
    assert "banner" not in site.client.get("/learn").text and "banner" not in site.client.get("/learn/1").text  # student pages: nothing
    db.build(site.db, site.data)
    assert all('class="banner"' not in site.client.get(p).text for p in pages)


def test_supplement_writers_refuse_while_the_file_has_changed(site, probe):
    conn = db.connect(site.db, progress_path=site.progress)
    intake(conn, 1, site.data)
    bump(site.data / "texts" / "002-春晓.md")  # another file: the banner names it, nothing refuses
    r = site.client.post("/texts/1/lessons/1/expansions/add", data={"anchor": probe.anchor, "surface": probe.word, "step": "2", "pinyin": probe.pinyin, "gloss": "t"}, headers=HX)
    assert r.status_code == 200 and db.lookup_word(conn, probe.word) is not None
    bump(site.data / "supplement.tsv")
    message = "data/ has changed since the last build (supplement.tsv, texts/002-春晓.md): run `chineselearning build`"
    r = site.client.post("/texts/1/lessons/1/related/add", data={"anchor": "", "surface": "月霜月", "step": "2", "gloss": "t"}, headers=HX)
    assert r.status_code == 422 and f'class="error">{message}</p>' in r.text and db.lookup_word(conn, "月霜月") is None
    r = site.client.post("/dictionary/row/乌鸦", data={"pinyin": "wū yā", "gloss": "x", "level": "7"}, headers=HX)
    assert r.status_code == 422 and message in r.text
    with pytest.raises(SupplementError, match="supplement.tsv"):
        supplement.add(conn, site.data, "龘", "da2", "d", "")
    assert site.client.post("/dictionary/state", data={"item": "乌鸦", "state": "exposed"}, headers=HX).status_code == 200  # nothing else refuses
    assert site.client.post("/dictionary/row/月", data={"gloss": "moon"}, headers=HX).status_code == 200
    db.build(site.db, site.data)
    assert site.client.post("/dictionary/row/乌鸦", data={"pinyin": "wū yā", "gloss": "x", "level": "7"}, headers=HX).status_code == 200


def test_the_apps_own_writes_keep_the_record_current(site, probe):
    conn = db.connect(site.db, progress_path=site.progress)
    intake(conn, 1, site.data)  # annotations/1.json and lessons/1-1.json
    assert drift.changed(conn, site.data) == []
    assert site.client.post("/texts/1/tags/add", data={"tag": "七绝"}, headers=HX).status_code == 200  # the text file's header
    assert site.client.post("/texts/1/lessons/1/expansions/add", data={"anchor": probe.anchor, "surface": probe.word, "step": "2", "pinyin": probe.pinyin}, headers=HX).status_code == 200  # supplement + lesson file
    assert site.client.post("/dictionary/row/月", data={"gloss": "moon"}, headers=HX).status_code == 200  # the gloss file
    assert site.client.post("/dictionary/add-to-lesson", data={"lesson": "new", "q": "乌鸦", "kind": "word", "source": "supplement"}, headers=HX).status_code == 200  # a vocabulary lesson file
    assert site.client.post("/texts/import", data={"title": "x", "tags": "诗词", "body": "月"}, headers=HX).status_code == 200  # a text file and its facts
    progress_files.export(conn, site.data)  # data/progress/student.tsv
    assert site.client.post("/texts/1/lessons/1/characters/add", data={"chars": ["月"]}, headers=HX).status_code == 200
    v = lessons.vocabulary(conn)[0]["id"]
    assert site.client.post(f"/lessons/{v}/remove", data={"item": "乌鸦"}, headers=HX).status_code == 200
    conn2 = db.connect(site.db)
    lessons.delete(conn2, v)  # deleted through the data layer: its file goes and the record follows
    conn2.commit()
    lesson_files.write_file(conn2, v, site.data)
    assert not (site.data / "lessons" / f"{v}.json").exists() and drift.changed(conn2, site.data) == []
    assert '<div class="banner">' not in site.client.get("/texts").text
    gloss_file.update(conn2, site.data, "月", "moon, month")  # inside the caller's transaction: recorded with its commit
    conn2.commit()
    progress.set_state(conn, "character", "月", "mastered", "manual")
    conn.commit()
    assert drift.changed(db.connect(site.db), site.data) == []
