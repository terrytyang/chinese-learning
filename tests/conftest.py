import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from opencc import OpenCC

from chineselearning import db, supplement
from chineselearning.web import create_app

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
HSK_CHARACTERS, HSK_WORDS = 3034, 9899  # from hsk.sql, which changes only by re-derivation
PROBE_WORDS = ("月霜", "山月", "江枫")  # candidates for `probe`: characters of text 1, so the first one anchors an expansion there


def copy_data(target):
    """A private copy of data/ without the owner's annotation, lesson and progress files, so tests never depend on curation state."""
    shutil.copytree(DATA_DIR, target)
    for folder in ("annotations", "lessons"):
        shutil.rmtree(target / folder, ignore_errors=True)
    for folder in ("progress", "import/progress"):
        for file in (target / folder).glob("*.tsv"):
            file.unlink()
    return target


@pytest.fixture(scope="session")
def baseline():
    """What data/supplement.tsv holds, so that tests never hardcode the size of a curated file that is meant to grow."""
    text = (DATA_DIR / "supplement.tsv").read_text(encoding="utf-8")
    entries = [e for e in map(supplement.parse_line, text.split("\n")) if e]
    characters = sum(len(e["item"]) == 1 for e in entries)
    return SimpleNamespace(
        hsk_characters=HSK_CHARACTERS,
        hsk_words=HSK_WORDS,
        entries=len(entries),
        characters=characters,
        words=len(entries) - characters,
        unglossed=sum(not e["gloss"] for e in entries),
        lines=text.count("\n"),  # the index of the next line appended, hence `supplement.WORD_ID_BASE + lines` is the next word id
    )


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    """(db_path, counts) for a real build of data/ (texts and master only) into a temporary file."""
    folder = tmp_path_factory.mktemp("content")
    path = folder / "content.sqlite"
    return path, db.build(path, copy_data(folder / "data"))


@pytest.fixture(scope="session")
def probe(built):
    """A two-character word the dictionary lacks, made of characters it has: the first of PROBE_WORDS that is in neither table.

    `anchor` is its first character; `pinyin`, `level` and `traditional` are what the supplement derives for it.
    """
    conn = db.connect(built[0], readonly=True)
    for word in PROBE_WORDS:
        chars = [db.lookup_character(conn, ch) for ch in word]
        if all(chars) and db.lookup_word(conn, word) is None:
            return SimpleNamespace(word=word, anchor=word[0], pinyin=" ".join(c["pinyin"] for c in chars),
                                   level=max(c["hsk_level"] for c in chars), traditional=OpenCC("s2t").convert(word))
    pytest.fail(f"no probe word is absent from the dictionary: {', '.join(PROBE_WORDS)}; add one to PROBE_WORDS in conftest.py")


@pytest.fixture(scope="session")
def client(built):
    return TestClient(create_app(built[0], progress_path=built[0].parent / "progress.sqlite"))


@pytest.fixture
def site(tmp_path):
    """A private copy of data/ (without annotations) and a database built from it; the app writes into the copy."""
    data = copy_data(tmp_path / "data")
    db_path = tmp_path / "content.sqlite"
    db.build(db_path, data)
    progress = tmp_path / "progress.sqlite"
    client = TestClient(create_app(db_path, data, progress), follow_redirects=False)
    return SimpleNamespace(data=data, db=db_path, progress=progress, client=client, file=data / "annotations" / "1.json")
