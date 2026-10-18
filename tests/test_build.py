import sqlite3

import pytest

from chineselearning import db
from chineselearning.db import GlossFileError


def test_build_counts(built):
    path, counts = built
    assert {k: counts[k] for k in ("character", "word", "text", "tag")} == {"character": 3034, "word": 11470, "text": 5, "tag": 2}


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


def test_cli_build_prints_counts(tmp_path, capsys):
    from chineselearning.cli import main

    main(["build", "--db", str(tmp_path / "c.sqlite")])
    assert "character 3034, word 11470, text 5, tag 2" in capsys.readouterr().out


def test_find_words_never_spans_a_line_break_or_punctuation(built):
    conn = db.connect(built[0], readonly=True)
    assert [w["simplified"] for w in db.find_words(conn, "山中\n国家")] == ["国家"]
    assert [w["simplified"] for w in db.find_words(conn, "山中，国家")] == ["国家"]
    assert [w["simplified"] for w in db.find_words(conn, "山中国家")] == ["中国", "国家"]


def test_character_glosses_loaded(built):
    path, counts = built
    assert counts["character_gloss"] == 248
    conn = db.connect(path, readonly=True)
    assert conn.execute("SELECT gloss FROM character WHERE char = '月'").fetchone()[0] == "moon, month"
    assert conn.execute("SELECT count(*) FROM character WHERE gloss IS NOT NULL").fetchone()[0] == 248


@pytest.mark.parametrize(
    "lines, message",
    [
        (["月\tmoon", "鿿\tnothing"], "gloss.tsv:2: character '鿿' is not in the master"),
        (["月\tmoon", "# comment", "", "月\tmonth"], "gloss.tsv:4: duplicate character '月' (also on line 1)"),
        (["月\t  "], "gloss.tsv:1: blank gloss for '月'"),
        (["月\tmoon\tmonth"], "gloss.tsv:1: expected two tab-separated columns, got 3"),
        (["月"], "gloss.tsv:1: expected two tab-separated columns, got 1"),
        (["月\t" + "x" * 121], "gloss.tsv:1: gloss for '月' is 121 characters, over 120"),
    ],
)
def test_bad_gloss_line_fails_naming_the_line(built, tmp_path, lines, message):
    path = tmp_path / "gloss.tsv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    conn = db.connect(built[0])
    try:
        with pytest.raises(GlossFileError) as info:
            db.load_character_glosses(conn, path)
        assert str(info.value).endswith(message)
    finally:
        conn.rollback()


def test_committed_facts_and_lessons_load(tmp_path):
    """The converted files in data/ build: a reading for every Han position of every text, and a default lesson each."""
    from chineselearning.texts import HAN

    path = tmp_path / "live.sqlite"
    counts = db.build(path, "data")
    assert counts["lesson"] >= 5 and counts["lesson_expansion"] >= 7 and counts["lesson_note"] >= 1
    conn = db.connect(path, readonly=True)
    for text in db.list_texts(conn):
        body = db.get_text(conn, text["id"])["body"]
        stored = {r[0] for r in conn.execute("SELECT position FROM text_reading WHERE text_id = ?", (text["id"],))}
        readable = {i for i, ch in enumerate(body) if HAN.fullmatch(ch) and conn.execute("SELECT 1 FROM character WHERE char = ?", (ch,)).fetchone()}
        assert readable <= stored, text["title"]
        assert conn.execute("SELECT count(*) FROM lesson WHERE text_id = ? AND name = ?", (text["id"], text["title"])).fetchone()[0] == 1
    assert conn.execute("SELECT count(*) FROM lesson_expansion e JOIN lesson l ON l.id = e.lesson_id WHERE l.text_id = 3").fetchone()[0] == 5
    assert conn.execute("SELECT count(*) FROM lesson_character c JOIN lesson l ON l.id = c.lesson_id WHERE l.text_id = 1").fetchone()[0] == 28
