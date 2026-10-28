"""The supplement: data/supplement.tsv loaded into the dictionary at build, its validation, and the write-through add and update."""

import re

import pytest

from chineselearning import db, supplement
from chineselearning.supplement import SupplementError


def build_with(site, tmp_path, extra):
    """Build a database from the site's data with `extra` appended to its supplement file."""
    path = site.data / "supplement.tsv"
    path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")
    db_path = tmp_path / "x.sqlite"
    return db.build(db_path, site.data), db.connect(db_path, readonly=True)


def test_supplement_loads_every_entry_with_derived_levels(built, baseline, probe):
    path, counts = built
    conn = db.connect(path, readonly=True)
    assert (counts["supplement"], counts["supplement_unglossed"]) == (baseline.entries, baseline.unglossed)
    assert (counts["character"], counts["word"]) == (baseline.hsk_characters + baseline.characters, baseline.hsk_words + baseline.words)
    assert conn.execute("SELECT count(*) FROM character WHERE source = 'supplement'").fetchone()[0] == baseline.characters
    assert conn.execute("SELECT count(*) FROM word WHERE source = 'supplement'").fetchone()[0] == baseline.words
    ti = db.lookup_character(conn, "啼")
    assert (ti["id"], ti["pinyin"], ti["readings"], ti["gloss"], ti["hsk_level"]) == (ord("啼"), "tí", ["tí"], "cry, crow (of birds), weep", 7)
    assert (ti["hsk_edition"], ti["source"], ti["traditional"], ti["meanings"], ti["word_level"], ti["pos"]) == ("none", "supplement", None, [], None, None)
    assert db.lookup_character(conn, "魏")["readings"] == ["wèi", "wéi", "wēi"]  # the file's reading first, then pypinyin's others
    assert db.lookup_character(conn, "刘")["readings"] == ["liú"]
    found = db.lookup_characters(conn, "银啼龘")
    assert (found[1]["found"], found[1]["source"]) == (True, "supplement") and found[2] == {"char": "龘", "found": False}
    assert db.lookup_word(conn, "银行")["source"] == "hsk" and db.lookup_word(conn, probe.word) is None and db.lookup_character(conn, "龘") is None


def test_word_lines_derive_level_pinyin_and_traditional(site, tmp_path, baseline, probe):
    lines = f"寒山\t\tcold mountain\t\n{probe.word}\t\t\t\n\n# a word may precede its character\n龘龘\t\t\t2\n龘\tdá\tdragons flying\t\n"
    counts, conn = build_with(site, tmp_path, lines)
    assert (counts["supplement"], counts["supplement_unglossed"], counts["word"]) == (baseline.entries + 4, baseline.unglossed + 2, baseline.hsk_words + baseline.words + 3)
    base = supplement.WORD_ID_BASE + baseline.lines  # the index of the first appended line
    hs = db.lookup_word(conn, "寒山")
    assert (hs["id"], hs["traditional"], hs["pinyin"], hs["meanings"], hs["hsk_level"]) == (base, "寒山", "hán shān", ["cold mountain"], 4)
    assert (hs["hsk_edition"], hs["source"], hs["alt_readings"], hs["pos"], hs["frequency_rank"]) == ("none", "supplement", [], None, None)
    word = db.lookup_word(conn, probe.word)
    assert (word["id"], word["traditional"], word["pinyin"], word["meanings"], word["hsk_level"]) == (base + 1, probe.traditional, probe.pinyin, [], probe.level)
    assert (db.lookup_word(conn, "龘龘")["hsk_level"], db.lookup_word(conn, "龘龘")["pinyin"], db.lookup_character(conn, "龘")["readings"]) == (2, "dá dá", ["dá"])
    assert [w["simplified"] for w in db.find_words(conn, "寒山寺")] == ["寒山"]  # intake finds a supplement word like an HSK one


@pytest.mark.parametrize(
    "lines, offset, message",
    [  # {w} is the probe word; offset counts appended lines up to the bad one
        ("月\tyuè\tmoon\t\n", 1, "“月” is in the HSK master"),
        ("银行\t\t\t\n", 1, "“银行” is in the HSK master"),
        ("啼\t\t\t\n", 1, "duplicate item “啼”"),
        ("{w}\t\t\t\n{w}\t\t\t\n", 2, "duplicate item “{w}”"),
        ("\t\tx\t\n", 1, "blank item"),
        ("{w}\t\t\t9\n", 1, "level must be 1 to 7, not “9”"),
        ("{w}\t\t\tx\n", 1, "level must be 1 to 7, not “x”"),
        ("龘鸦龘\t\t\t\n", 1, "“龘鸦龘” has characters not in the dictionary: 龘; add them to data/supplement.tsv"),
    ],
)
def test_build_rejects_bad_lines_naming_file_and_line(site, tmp_path, baseline, probe, lines, offset, message):
    with pytest.raises(SupplementError, match=re.escape(f"supplement.tsv:{baseline.lines + offset}: {message.format(w=probe.word)}")):
        build_with(site, tmp_path, lines.format(w=probe.word))


def test_add_round_trips_file_and_row(site, baseline, probe):
    conn, path = db.connect(site.db), site.data / "supplement.tsv"
    before = path.read_text(encoding="utf-8")
    for item, message in (("月", "“月” is in the HSK master"), ("啼", "duplicate item “啼”"), (" ", "blank item"), ("龘龘", "not in the dictionary: 龘"),
                          ("\U0002a6d6", "has no known reading; give its pinyin"), (probe.word, "level must be 1 to 7, not “0”")):
        with pytest.raises(SupplementError, match=re.escape(message)):
            supplement.add(conn, site.data, item, "", "x", "0" if item == probe.word else "")
    assert path.read_text(encoding="utf-8") == before
    assert supplement.add(conn, site.data, "寒山寺", "han2 shan1 si4", "Hanshan Temple", "") == 10_000_000 + before.count("\n")
    assert supplement.add(conn, site.data, "龘", "", "dragons flying", "3") == ord("龘")
    assert supplement.add(conn, site.data, "龘龘", "", "", "") == 10_000_000 + before.count("\n") + 2
    conn.commit()
    assert path.read_text(encoding="utf-8") == before + "寒山寺\thán shān sì\tHanshan Temple\t\n龘\t\tdragons flying\t3\n龘龘\t\t\t\n"
    row = db.lookup_word(conn, "寒山寺")
    assert (row["pinyin"], row["meanings"], row["hsk_level"], row["hsk_edition"], row["source"]) == ("hán shān sì", ["Hanshan Temple"], 7, "none", "supplement")
    assert (db.lookup_character(conn, "龘")["hsk_level"], db.lookup_word(conn, "龘龘")["hsk_level"]) == (3, 3)
    counts = db.build(site.db, site.data)
    assert (counts["supplement"], counts["supplement_unglossed"]) == (baseline.entries + 3, baseline.unglossed + 1)
    again = db.connect(site.db, readonly=True)
    assert db.lookup_word(again, "寒山寺") == row and db.lookup_character(again, "龘")["gloss"] == "dragons flying"


def test_update_rewrites_the_line_and_the_row(site, baseline, probe):
    conn, path = db.connect(site.db), site.data / "supplement.tsv"
    supplement.add(conn, site.data, "寒山寺", "", "temple", "")
    supplement.update(conn, site.data, "寒山寺", "Han2 Shan1 Si4", "Hanshan Temple", "5")
    supplement.update(conn, site.data, "啼", "ti2", "", "")
    conn.commit()
    lines = path.read_text(encoding="utf-8").split("\n")
    assert lines[-2] == "寒山寺\tHán Shān Sì\tHanshan Temple\t5" and "啼\ttí\t\t" in lines and lines[-1] == ""
    row = db.lookup_word(conn, "寒山寺")
    assert (row["pinyin"], row["meanings"], row["hsk_level"]) == ("Hán Shān Sì", ["Hanshan Temple"], 5)
    assert (db.lookup_character(conn, "啼")["gloss"], db.lookup_character(conn, "啼")["readings"]) == (None, ["tí"])
    assert db.build(site.db, site.data)["supplement_unglossed"] == baseline.unglossed + 1
    again = db.connect(site.db, readonly=True)
    assert db.lookup_word(again, "寒山寺") == row and db.lookup_character(again, "啼")["gloss"] is None
    for item, level, message in (("月", "", "“月” is not a supplement entry"), (probe.word, "", f"“{probe.word}” is not a supplement entry"), ("啼", "8", "level must be 1 to 7, not “8”")):
        with pytest.raises(SupplementError, match=re.escape(message)):
            supplement.update(again, site.data, item, "", "x", level)
