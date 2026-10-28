"""Progress import and export: the standard file, resolution by timestamp, unmatched items into the supplement, the report, and day-0 (`init`)."""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from chineselearning import db, progress, progress_files
from chineselearning.cli import main
from chineselearning.progress_files import ProgressFileError, read
from chineselearning.progress_import import resolve, run
from chineselearning.web import create_app

FIXTURES = Path(__file__).parent / "fixtures" / "progress"


def connect(site):
    return db.connect(site.db, progress_path=site.progress)


def brief(entries):
    return [(e.item, e.state, e.as_of) for e in entries]


def states(conn):
    return {key: state for (_, key), state in progress.current(conn).items()}


def origins(conn):
    return {r[0]: r[1] for r in conn.execute("SELECT key, origin FROM progress.progress")}


def supplement_text(site):
    return (site.data / "supplement.tsv").read_text(encoding="utf-8")


@pytest.fixture
def dictionary_only(tmp_path, probe):
    """A file that says nothing about the student (`state: none`) but carries a word the dictionary lacks, and one it has."""
    path = tmp_path / "dictionary-only.tsv"
    path.write_text(f"# source: raw/dictionary.md\n# as_of: 2026-08-01\n# state: none\nitem\tstate\tas_of\tpinyin\tgloss\tlevel\n{probe.word}\t\t\t{probe.pinyin}\ttest\t\n月\n", encoding="utf-8")
    return path


def test_read_header_values_fill_blank_columns():
    entries = read(FIXTURES / "plain-list.tsv")
    assert brief(entries) == [("司", "recognized", "2026-08-30"), ("班", "mastered", "2026-09-14")]
    assert (entries[0].file, entries[0].line, entries[0].where, entries[0].kind, entries[0].original) == ("plain-list.tsv", 5, "plain-list.tsv:5", "character", None)


def test_read_per_line_values_and_optional_columns():
    entries = read(FIXTURES / "sheet.tsv")
    assert brief(entries) == [("银行", "recognized", "2026-10-01"), ("月", "mastered", "2026-09-01"), ("行走", "exposed", "2026-10-01"),
                              ("寒山寺", "recognized", "2026-10-01"), ("龘", "exposed", "2026-10-02")]
    assert [(e.pinyin, e.gloss, e.level) for e in entries] == [("", "", ""), ("", "", ""), ("", "", "5"), ("hán shān sì", "Hanshan Temple", "7"), ("", "dragons flying", "")]
    assert [e.kind for e in entries] == ["word", "character", "word", "word", "character"]


def test_read_state_none_and_traditional_conversion(dictionary_only, probe):
    entries = read(dictionary_only)
    assert brief(entries) == [(probe.word, None, "2026-08-01"), ("月", None, "2026-08-01")] and entries[0].pinyin == probe.pinyin
    entries = read(FIXTURES / "traditional.tsv")
    assert brief(entries) == [("银行", "exposed", "2026-09-10"), ("学习", "exposed", "2026-09-10"), ("马", "exposed", "2026-09-10")]
    assert [e.original for e in entries] == ["銀行", "學習", "馬"]


@pytest.mark.parametrize(
    "name, content, message",
    [
        ("question.tsv", None, "question.tsv:2: “?” must be replaced by the owner before import"),
        ("no-date.tsv", None, "no-date.tsv:5: no as_of on the line or in the header"),
        ("x.tsv", "# as_of: 2026-09-01\nitem\tstate\tas_of\n月\tlearned\t\n", "x.tsv:3: state must be exposed, recognized or mastered, not “learned”"),
        ("x.tsv", "# as_of: 2026-09-01\nitem\tstate\tas_of\n月\tnone\t\n", "x.tsv:3: state must be exposed, recognized or mastered, not “none”"),
        ("x.tsv", "# state: learned\nitem\tstate\tas_of\n", "x.tsv:1: state must be exposed, recognized, mastered or none, not “learned”"),
        ("x.tsv", "# as_of: 2026-9-1\nitem\tstate\tas_of\n", "x.tsv:1: as_of must be a date (YYYY-MM-DD), not “2026-9-1”"),
        ("x.tsv", "item\tstate\tas_of\n月\texposed\tSeptember\n", "x.tsv:2: as_of must be a date (YYYY-MM-DD), not “September”"),
        ("x.tsv", "# as_of: 2026-09-01\nitem\tstate\tas_of\n\texposed\n", "x.tsv:3: blank item"),
        ("x.tsv", "# as_of: 2026-09-01\nitem\tstate\tas_of\tpinyin\tgloss\tlevel\n月\t\t\t\t\t9\n", "x.tsv:3: level must be 1 to 7, not “9”"),
        ("x.tsv", "# date: 2026-09-01\nitem\tstate\tas_of\n", "x.tsv:1: unknown header line"),
        ("x.tsv", "# as_of: 2026-09-01\nitem\tstate\n", "x.tsv:2: expected the column header: item state as_of, then any of pinyin gloss level origin in that order"),
        ("x.tsv", "# as_of: 2026-09-01\nitem\tstate\tas_of\tlevel\tgloss\n", "x.tsv:2: expected the column header: item state as_of, then any of pinyin gloss level origin in that order"),
        ("x.tsv", "# as_of: 2026-09-01\nitem\tstate\tas_of\torigin\n月\texposed\t\tpage\n", "x.tsv:3: origin must be auto, manual or import, not “page”"),
        ("x.tsv", "# as_of: 2026-09-01\n", "x.tsv: no column header"),
    ],
)
def test_read_errors_name_the_file_and_line(tmp_path, name, content, message):
    path = FIXTURES / name if content is None else tmp_path / name
    if content is not None:
        path.write_text(content, encoding="utf-8")
    with pytest.raises(ProgressFileError, match=re.escape(message)):
        read(path)


def test_resolve_explicit_implied_tie_and_current_row(site, dictionary_only, probe):
    conn = connect(site)
    entries = read(FIXTURES / "sheet.tsv") + read(FIXTURES / "traditional.tsv") + read(dictionary_only)
    resolved = resolve(conn, entries)
    assert resolved[("word", "银行")] == ("recognized", "2026-10-01", "import", "recognized 2026-10-01 in sheet.tsv:3, origin import")  # later than traditional.tsv's exposed
    assert resolved[("character", "银")] == ("recognized", "2026-10-01", "import", "recognized 2026-10-01 implied by 银行 in sheet.tsv:3, origin import")
    assert resolved[("character", "行")] == ("exposed", "2026-10-01", "import", "exposed 2026-10-01 implied by 行走 in sheet.tsv:5, origin import")  # a tie goes to the lowest state
    assert resolved[("character", "月")] == ("mastered", "2026-09-01", "import", "mastered 2026-09-01 in sheet.tsv:4, origin import")  # dictionary-only.tsv says nothing
    assert resolved[("character", "马")] == ("exposed", "2026-09-10", "import", "exposed 2026-09-10 in traditional.tsv:7, origin import")
    assert resolved[("character", "学")] == ("exposed", "2026-09-10", "import", "exposed 2026-09-10 implied by 学习 in traditional.tsv:6, origin import")
    assert resolved[("character", "龘")][:2] == ("exposed", "2026-10-02") and ("word", probe.word) not in resolved and len(resolved) == 15
    progress.set_state(conn, "character", "月", "recognized", "manual", changed_at="2026-09-15T10:00:00Z")  # the current row is a candidate too
    progress.set_state(conn, "word", "银行", "mastered", "manual", changed_at="2026-09-20T10:00:00Z")
    progress.set_state(conn, "character", "走", "mastered", "manual", changed_at="2026-10-01T23:00:00Z")
    resolved = resolve(conn, entries)
    assert resolved[("character", "月")] == ("recognized", "2026-09-15", "manual", "recognized 2026-09-15 current, origin manual")
    assert resolved[("word", "银行")] == ("recognized", "2026-10-01", "import", "recognized 2026-10-01 in sheet.tsv:3, origin import")  # the file is later: a downgrade
    assert resolved[("character", "走")][:2] == ("exposed", "2026-10-01")  # same date: the lowest state, whatever the time of day


def test_run_writes_states_adds_to_supplement_reports_and_is_idempotent(site, dictionary_only, probe):
    conn = connect(site)
    files = [FIXTURES / "sheet.tsv", FIXTURES / "traditional.tsv", dictionary_only]
    report = run(conn, site.data, files)
    assert report.files == [str(p) for p in files] and report.entries == 10 and report.conversions == [("銀行", "银行"), ("學習", "学习"), ("馬", "马")]
    assert report.changes == {"unconfirmed→recognized": ["银行", "银", "寒山寺", "寒", "山", "寺"], "unconfirmed→mastered": ["月"],
                              "unconfirmed→exposed": ["行", "行走", "走", "龘", "学习", "学", "习", "马"]}
    assert (report.unchanged, report.downgrades) == (0, [])
    assert [(r["item"], r["pinyin"], r["gloss"], r["level"]) for r in report.added] == [("龘", "", "dragons flying", ""), ("寒山寺", "hán shān sì", "Hanshan Temple", "7"), (probe.word, probe.pinyin, "test", "")]
    assert supplement_text(site).endswith(f"龘\t\tdragons flying\t\n寒山寺\thán shān sì\tHanshan Temple\t7\n{probe.word}\t{probe.pinyin}\ttest\t\n")
    assert db.lookup_word(conn, probe.word)["meanings"] == ["test"] and db.lookup_character(conn, "龘")["pinyin"] == "dá"
    assert states(conn) == {"银行": "recognized", "银": "recognized", "行": "exposed", "寒山寺": "recognized", "寒": "recognized", "山": "recognized", "寺": "recognized",
                            "月": "mastered", "行走": "exposed", "走": "exposed", "龘": "exposed", "学习": "exposed", "学": "exposed", "习": "exposed", "马": "exposed"}
    assert conn.execute("SELECT changed_at FROM progress.progress WHERE key = '银行'").fetchone()[0] == "2026-10-01"
    text = report.text()
    assert text.startswith("files read: ") and "\nentries: 10, converted from traditional: 銀行→银行, 學習→学习, 馬→马\n" in text
    assert "\nunconfirmed→mastered: 月\n" in text and "\nunchanged: 0\n" in text and text.endswith(f"\nadded to supplement: 龘, 寒山寺, {probe.word} (0 without a gloss)")
    again = run(connect(site), site.data, files)
    assert (again.changes, again.unchanged, again.downgrades, again.added) == ({}, 15, [], []) and "would add" not in again.text() and "supplement" not in again.text()
    assert states(connect(site)) == states(conn) and supplement_text(site).count(f"\n{probe.word}\t") == 1


def test_check_reports_and_writes_nothing(site):
    conn = connect(site)
    before = supplement_text(site)
    report = run(conn, site.data, [FIXTURES / "sheet.tsv"], check=True)
    assert report.check and report.changes["unconfirmed→mastered"] == ["月"] and [r["item"] for r in report.added] == ["龘", "寒山寺"]
    assert report.text().startswith("check: nothing written; files read: ") and report.text().endswith("would add to supplement: 龘, 寒山寺 (0 without a gloss)")
    assert states(connect(site)) == {} and supplement_text(site) == before and db.lookup_word(conn, "寒山寺") is None


def test_downgrade_names_the_winning_file(site):
    conn = connect(site)
    progress.set_state(conn, "word", "银行", "mastered", "manual", changed_at="2026-09-20T10:00:00Z")
    progress.set_state(conn, "character", "月", "mastered", "manual", changed_at="2026-09-01T10:00:00Z")
    conn.commit()
    report = run(conn, site.data, [FIXTURES / "sheet.tsv"])
    assert report.downgrades == ["银行 mastered→recognized (recognized 2026-10-01 in sheet.tsv:3, origin import)"] and report.changes["mastered→recognized"] == ["银行"]
    assert report.unchanged == 1 and "downgrades: 银行 mastered→recognized (recognized 2026-10-01 in sheet.tsv:3, origin import)" in report.text()
    assert (progress.state_of(conn, "word", "银行"), progress.state_of(conn, "character", "月")) == ("recognized", "mastered")


def test_unmatched_word_with_unknown_characters_is_refused_before_anything_is_written(site, tmp_path):
    conn = connect(site)
    path = tmp_path / "bad.tsv"
    path.write_text("# as_of: 2026-09-01\n# state: exposed\nitem\tstate\tas_of\n月\n龘龖\n", encoding="utf-8")
    before = supplement_text(site)
    with pytest.raises(ProgressFileError, match="bad.tsv:5: “龘龖” has characters not in the dictionary: 龘, 龖; add them to the file or data/supplement.tsv"):
        run(conn, site.data, [path])
    assert states(connect(site)) == {} and supplement_text(site) == before
    with pytest.raises(ProgressFileError, match="no such file"):
        run(conn, site.data, [tmp_path / "missing.tsv"])
    path.write_text("# as_of: 2026-09-01\n# state: exposed\nitem\tstate\tas_of\n龘\n龖\n龘龖\n", encoding="utf-8")  # the characters come with the word
    assert [r["item"] for r in run(conn, site.data, [path]).added] == ["龘", "龖", "龘龖"] and db.lookup_word(conn, "龘龖")["pinyin"] == "dá dá"


def test_export_then_import_round_trips(site):
    conn = connect(site)
    assert not list((site.data / "progress").glob("*.tsv"))  # no snapshot yet
    progress.set_state(conn, "character", "月", "mastered", "import", changed_at="2026-09-01T10:00:00Z")
    progress.set_state(conn, "word", "银行", "recognized", "manual", changed_at="2026-10-01T23:59:59Z")
    progress.set_state(conn, "character", "行", "exposed", "manual", changed_at="2026-10-01T23:59:59Z")
    conn.commit()
    path = progress_files.export(conn, site.data)
    assert path == site.data / "progress" / "student.tsv"
    assert path.read_text(encoding="utf-8") == "# source: export\nitem\tstate\tas_of\torigin\n月\tmastered\t2026-09-01\timport\n行\texposed\t2026-10-01\tmanual\n银行\trecognized\t2026-10-01\tmanual\n"
    conn.execute("DELETE FROM progress.progress")
    conn.commit()
    report = run(conn, site.data)  # no files given: the snapshot, then data/import/progress/*.tsv (none yet)
    assert report.files == [str(path)] and states(conn) == {"月": "mastered", "行": "exposed", "银行": "recognized", "银": "recognized"}
    assert conn.execute("SELECT changed_at FROM progress.progress WHERE key = '月'").fetchone()[0] == "2026-09-01"
    assert origins(conn) == {"月": "import", "行": "manual", "银行": "manual", "银": "manual"}  # a round trip preserves origin; 银 is implied by 银行
    conn.execute("DELETE FROM progress.progress WHERE key = '银'")
    conn.commit()
    before = path.read_bytes()
    assert progress_files.export(conn, site.data).read_bytes() == before  # byte-identical when nothing changed
    with pytest.raises(ProgressFileError, match="no learner with id 2"):
        progress_files.export(conn, site.data, 2)


def test_cli_init_import_check_export_and_fresh_rebuild(site, monkeypatch, capsys, baseline):
    """Day-0 with a hand-written batch in place: init imports it before intake, so the default lessons leave out what the student knows."""
    monkeypatch.chdir(site.data.parent)
    hand = Path("data/import/progress/hand.tsv")
    hand.write_text("# source: by hand\nitem\tstate\tas_of\n月\tmastered\t2026-09-01\n银行\trecognized\t2026-10-01\n", encoding="utf-8")
    main(["init", "--fresh"])
    out = capsys.readouterr().out
    assert f"build/content.sqlite: character {baseline.hsk_characters + baseline.characters}" in out and f"{baseline.entries} supplement entries" in out
    assert "files read: data/import/progress/hand.tsv\nentries: 2\nunconfirmed→mastered: 月\nunconfirmed→recognized: 银行, 银, 行\nunchanged: 0\n" in out
    assert [line.split(":")[0] for line in out.splitlines() if line.startswith("text ")] == [f"text {i}" for i in baseline.text_ids]
    assert Path("build/content.sqlite").is_file() and Path("build/progress.sqlite").is_file() and len(list(Path("data/lessons").glob("*.json"))) == len(baseline.texts)
    conn = db.connect("build/content.sqlite", progress_path="build/progress.sqlite")
    assert conn.execute("SELECT count(*) FROM lesson").fetchone()[0] == len(baseline.texts)
    lesson = json.loads(Path("data/lessons/1-1.json").read_text(encoding="utf-8"))["characters"]
    assert len(lesson) == 27 and "月" not in lesson and "落" in lesson  # a mastered character stays out of the default lesson (行 is not in text 1)
    assert (progress.state_of(conn, "character", "月"), progress.state_of(conn, "character", "落"), progress.state_of(conn, "word", "银行")) == ("mastered", "exposed", "recognized")
    page = TestClient(create_app("build/content.sqlite", "data", "build/progress.sqlite")).get("/texts/1/lessons/1/characters", params={"state": "any", "min": 1, "max": 7}).text
    assert re.search(r'name="chars" value="月"[^>]*>.*?<td class="st">mastered</td>', page, re.S) and re.search(r'<tr id="char-落">.*?value="exposed" class="on"', page, re.S)
    Path("data/import/progress/later.tsv").write_text("# source: by hand\n# as_of: 2026-10-15\n# state: mastered\nitem\tstate\tas_of\n银行\n", encoding="utf-8")
    main(["import-progress", "--check"])
    out = capsys.readouterr().out
    assert out == "check: nothing written; files read: data/import/progress/hand.tsv, data/import/progress/later.tsv\nentries: 3\nrecognized→mastered: 银行, 银, 行\nunchanged: 1\n"
    assert progress.state_of(conn, "word", "银行") == "recognized"  # 行 was recognized, so intake left it alone; the later file promotes it
    main(["import-progress"])
    assert "recognized→mastered: 银行, 银, 行\n" in capsys.readouterr().out
    assert (progress.state_of(conn, "word", "银行"), progress.state_of(conn, "character", "银"), progress.state_of(conn, "character", "行")) == ("mastered", "mastered", "mastered")
    main(["export-progress"])
    assert capsys.readouterr().out == "wrote data/progress/student.tsv\n"
    snapshot = Path("data/progress/student.tsv").read_text(encoding="utf-8")
    assert snapshot.startswith("# source: export\nitem\tstate\tas_of\torigin\n") and "月\tmastered\t2026-09-01\timport\n" in snapshot and "银行\tmastered\t2026-10-15\timport\n" in snapshot
    assert "落\texposed\t" in snapshot and snapshot.count("\tauto\n") > 0  # intake's rows carry auto
    main(["init", "--fresh"])
    out = capsys.readouterr().out
    assert "files read: data/progress/student.tsv, data/import/progress/hand.tsv, data/import/progress/later.tsv\n" in out and "nothing to intake" in out
    conn = db.connect("build/content.sqlite", progress_path="build/progress.sqlite")
    assert (progress.state_of(conn, "character", "月"), progress.state_of(conn, "word", "银行"), progress.state_of(conn, "character", "落")) == ("mastered", "mastered", "exposed")
    assert json.loads(Path("data/lessons/1-1.json").read_text(encoding="utf-8"))["characters"] == lesson  # lessons already existed: untouched
    with pytest.raises(SystemExit, match="import-progress failed: nope.tsv: no such file"):
        main(["import-progress", "nope.tsv"])


def test_auto_rows_yield_to_any_other_candidate(site):
    """Intake's `exposed` (today) loses to an imported `mastered` dated earlier; a `manual` row dated later than the import wins."""
    conn = connect(site)
    assert progress.expose(conn, "character", "月") and progress.expose(conn, "word", "银行") and origins(conn) == {"月": "auto", "银行": "auto"}
    progress.set_state(conn, "character", "行", "recognized", "manual", changed_at="2026-10-20T10:00:00Z")
    conn.commit()
    entries = read(FIXTURES / "sheet.tsv")  # 月 mastered 2026-09-01; 银行 recognized 2026-10-01; 行 exposed 2026-10-01 (implied by 行走)
    resolved = resolve(conn, entries)
    assert resolved[("character", "月")] == ("mastered", "2026-09-01", "import", "mastered 2026-09-01 in sheet.tsv:4, origin import")
    assert resolved[("word", "银行")][:3] == ("recognized", "2026-10-01", "import")
    assert resolved[("character", "行")] == ("recognized", "2026-10-20", "manual", "recognized 2026-10-20 current, origin manual")
    report = run(conn, site.data, [FIXTURES / "sheet.tsv"])
    assert report.changes["exposed→mastered"] == ["月"] and report.changes["exposed→recognized"] == ["银行"] and report.downgrades == []
    assert origins(conn)["月"] == "import" and origins(conn)["银行"] == "import" and origins(conn)["行"] == "manual"
    assert conn.execute("SELECT changed_at FROM progress.progress WHERE key = '月'").fetchone()[0] == "2026-09-01"
    again = run(connect(site), site.data, [FIXTURES / "sheet.tsv"])
    assert again.changes == {} and again.downgrades == []


def test_file_origin_column_and_implied_candidates_carry_the_words_origin(site, tmp_path):
    conn = connect(site)
    path = tmp_path / "origins.tsv"
    path.write_text("# as_of: 2026-09-01\nitem\tstate\tas_of\torigin\n银行\texposed\t\tauto\n月亮\trecognized\t2026-08-01\tmanual\n月\tmastered\t2026-08-15\t\n", encoding="utf-8")
    entries = read(path)
    assert [(e.item, e.origin) for e in entries] == [("银行", "auto"), ("月亮", "manual"), ("月", "import")]
    resolved = resolve(conn, entries)
    assert resolved[("word", "银行")] == ("exposed", "2026-09-01", "auto", "exposed 2026-09-01 in origins.tsv:3, origin auto")  # nothing else: auto counts
    assert resolved[("character", "银")][2:] == ("auto", "exposed 2026-09-01 implied by 银行 in origins.tsv:3, origin auto")
    assert resolved[("character", "亮")] == ("recognized", "2026-08-01", "manual", "recognized 2026-08-01 implied by 月亮 in origins.tsv:4, origin manual")
    assert resolved[("character", "月")] == ("mastered", "2026-08-15", "import", "mastered 2026-08-15 in origins.tsv:5, origin import")  # later than the implied manual
    run(conn, site.data, [path])
    assert origins(conn) == {"银行": "auto", "银": "auto", "行": "auto", "月亮": "manual", "亮": "manual", "月": "import"}


def test_opening_an_older_progress_file_adds_the_origin_column(site):
    """The one in-place schema change: a progress.sqlite made before `origin` gains the column as `import` and keeps every row."""
    import sqlite3

    old = sqlite3.connect(site.progress)
    old.executescript("""
        CREATE TABLE learner (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE progress (learner_id INTEGER NOT NULL REFERENCES learner(id), kind TEXT NOT NULL, key TEXT NOT NULL,
                               state TEXT NOT NULL, changed_at TEXT NOT NULL, PRIMARY KEY (learner_id, kind, key));
        INSERT INTO learner VALUES (1, 'Student');
        INSERT INTO progress VALUES (1, 'character', '月', 'mastered', '2026-09-10'), (1, 'word', '银行', 'recognized', '2026-10-01T10:00:00Z');
    """)
    old.commit()
    old.close()
    conn = connect(site)
    assert "origin" in [r[1] for r in conn.execute("PRAGMA progress.table_info(progress)")]
    assert origins(conn) == {"月": "import", "银行": "import"} and states(conn) == {"月": "mastered", "银行": "recognized"}
    assert progress.set_state(conn, "character", "月", "recognized", "manual") and origins(conn)["月"] == "manual"
    conn.rollback()
    assert origins(connect(site)) == {"月": "import", "银行": "import"}  # a second open changes nothing
