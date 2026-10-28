import json
import sqlite3
from pathlib import Path

from chineselearning import annotation_files, db, lesson_files, lessons


def test_build_counts(built, baseline):
    path, counts = built
    expected = {"character": baseline.hsk_characters + baseline.characters, "word": baseline.hsk_words + baseline.words, "text": 5, "tag": 2}
    assert {k: counts[k] for k in expected} == expected


def test_build_imports_texts_with_tags(built):
    conn = db.connect(built[0], readonly=True)
    assert db.get_text(conn, 1)["tags"] == ["诗词"]
    assert db.get_text(conn, 5)["period"] == "东晋"
    assert db.get_text(conn, 1)["body"].startswith("月落乌啼")
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_build_overwrites(tmp_path):
    path = tmp_path / "content.sqlite"
    path.write_bytes(b"garbage")
    db.build(path, "data")
    assert sqlite3.connect(path).execute("SELECT count(*) FROM text").fetchone()[0] == 5


def test_cli_build_prints_counts(tmp_path, capsys, baseline):
    from chineselearning.cli import main

    main(["build", "--db", str(tmp_path / "c.sqlite")])
    out = capsys.readouterr().out
    assert f"character {baseline.hsk_characters + baseline.characters}, word {baseline.hsk_words + baseline.words}, text 5, tag 2" in out
    assert f"{baseline.entries} supplement entries, {baseline.unglossed} without a gloss" in out


def test_find_words_never_spans_a_line_break_or_punctuation(built):
    conn = db.connect(built[0], readonly=True)
    assert [w["simplified"] for w in db.find_words(conn, "山中\n国家")] == ["国家"]
    assert [w["simplified"] for w in db.find_words(conn, "山中，国家")] == ["国家"]
    assert [w["simplified"] for w in db.find_words(conn, "山中国家")] == ["中国", "国家"]


def test_master_shape(built, baseline):
    """Glosses arrive baked into hsk.sql; `word` holds multi-character items only; forms beyond the primary are in alt_readings."""
    conn = db.connect(built[0], readonly=True)
    assert conn.execute("SELECT count(*) FROM character WHERE source = 'hsk' AND gloss IS NULL").fetchone()[0] == 0
    assert conn.execute("SELECT count(*) FROM character WHERE source = 'hsk'").fetchone()[0] == baseline.hsk_characters
    assert conn.execute("SELECT gloss FROM character WHERE char = '月'").fetchone()[0] == "moon, month"
    assert conn.execute("SELECT count(*) FROM word WHERE length(simplified) = 1").fetchone()[0] == 0
    assert "readings" not in [r[1] for r in conn.execute("PRAGMA table_info(word)")]
    word = db.find_words(conn, "银行")[0]
    assert word["pinyin"] == "yín háng" and word["meanings"][0] == "bank" and word["alt_readings"] == []
    yin = db.lookup_characters(conn, "银啼")
    assert (yin[0]["hsk_level"], yin[0]["word_level"], yin[0]["readings"][0]) == (3, 6, "yín") and "n" in yin[0]["pos"].split(",")
    assert isinstance(yin[0]["meanings"], list) and isinstance(yin[0]["frequency_rank"], int) and yin[0]["alt_readings"] == []
    assert (yin[1]["found"], yin[1]["source"], yin[1]["hsk_level"], yin[1]["readings"]) == (True, "supplement", 7, ["tí"])
    assert db.lookup_characters(conn, "龘") == [{"char": "龘", "found": False}]


def test_committed_facts_and_lessons_load(tmp_path):
    """The regenerated files in data/ build: a reading for every Han position of every text, the default lesson each, no character
    facts (the supplement covers 啼, 枫, 鸯, …), and every file exports byte-identical."""
    from chineselearning.texts import HAN

    path = tmp_path / "live.sqlite"
    counts = db.build(path, "data")
    assert counts["lesson"] == 5 and counts["lesson_extra_word"] == 0 and counts["lesson_note"] == 0 and counts["text_character"] == 0
    conn = db.connect(path, readonly=True)
    as_file = lambda data: json.dumps(data, ensure_ascii=False, indent=2) + "\n"  # noqa: E731
    for text in db.list_texts(conn):
        body = db.get_text(conn, text["id"])["body"]
        stored = {r[0] for r in conn.execute("SELECT position FROM text_reading WHERE text_id = ?", (text["id"],))}
        assert stored == {i for i, ch in enumerate(body) if HAN.fullmatch(ch)}, text["title"]
        assert conn.execute("SELECT count(*) FROM lesson WHERE text_id = ? AND name = ?", (text["id"], f"Learn {text['title']}")).fetchone()[0] == 1
        assert as_file(annotation_files.export(conn, text["id"])) == Path("data", "annotations", f"{text['id']}.json").read_text(encoding="utf-8")
        for lesson in lessons.for_text(conn, text["id"]):
            assert as_file(lesson_files.export(conn, lesson["id"])) == Path("data", "lessons", f"{text['id']}-{lesson['id']}.json").read_text(encoding="utf-8")
    assert conn.execute("SELECT count(*) FROM lesson_character c JOIN lesson l ON l.id = c.lesson_id WHERE l.text_id = 1").fetchone()[0] == 28
    assert conn.execute("SELECT pinyin, origin FROM text_reading WHERE text_id = 1 AND char = '啼'").fetchone()[:] == ("tí", "auto")
