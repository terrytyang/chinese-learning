"""data/character-gloss.tsv applied at build, and the dictionary page's in-place update of one line."""

import pytest

from chineselearning import db, gloss_file
from chineselearning.gloss_file import GlossFileError


def test_build_applies_the_file_and_leaves_glosses_as_baked(built):
    conn = db.connect(built[0], readonly=True)
    assert conn.execute("SELECT gloss FROM character WHERE char = '月'").fetchone()[0] == "moon, month"
    assert conn.execute("SELECT count(*) FROM character WHERE source = 'hsk' AND gloss IS NULL").fetchone()[0] == 0


def test_read_and_apply_name_a_bad_line(site, tmp_path):
    path = site.data / "character-gloss.tsv"
    lines = gloss_file.read(site.data)
    assert (2, "一", "one, a, whole, as soon as") == lines[0] and all(len(ch) == 1 and g for _, ch, g in lines)
    before = path.read_text(encoding="utf-8")
    path.write_text(before + "龘\tdragons flying\n", encoding="utf-8")
    with pytest.raises(GlossFileError, match=r"character-gloss\.tsv:3036: “龘” is not in the HSK master"):
        db.build(tmp_path / "x.sqlite", site.data)
    path.write_text(before + "月\t\n", encoding="utf-8")
    with pytest.raises(GlossFileError, match=r"character-gloss\.tsv:3036: a gloss is required"):
        gloss_file.read(site.data)
    path.write_text(before + "月亮\tmoon\n", encoding="utf-8")
    with pytest.raises(GlossFileError, match=r"character-gloss\.tsv:3036: expected one character, a tab and its gloss"):
        gloss_file.read(site.data)


def test_update_rewrites_one_line_and_the_row(site):
    conn = db.connect(site.db)
    path = site.data / "character-gloss.tsv"
    before = path.read_text(encoding="utf-8")
    gloss_file.update(conn, site.data, "月", " moon; month ")
    after = path.read_text(encoding="utf-8")
    assert after.replace("月\tmoon; month\n", "月\tmoon, month\n") == before and after.count("\n") == before.count("\n")
    assert conn.execute("SELECT gloss FROM character WHERE char = '月'").fetchone()[0] == "moon; month"
    gloss_file.update(conn, site.data, "月", "moon, month")
    assert path.read_bytes() == before.encode("utf-8")
    for char, gloss, message in [("月", "", "a gloss is required"), ("月", "moon\tmonth", "a gloss is one line without tabs"),
                                 ("啼", "cry", "“啼” is not an HSK character"), ("龘", "x", "“龘” is not an HSK character")]:
        with pytest.raises(GlossFileError, match=message):
            gloss_file.update(conn, site.data, char, gloss)
    assert path.read_bytes() == before.encode("utf-8")
