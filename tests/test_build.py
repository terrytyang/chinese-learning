import sqlite3

from chineselearning import db


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
