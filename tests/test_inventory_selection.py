from collections import Counter
import json
from pathlib import Path
import sqlite3

import pytest

from chineselearning.bootstrap import build_database
from chineselearning.inventory_selection import generate_selection, RANDOM_SEED
from test_bootstrap import logical_snapshot

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "hsk-original/hsk_vocab.sqlite"
MANIFEST = ROOT / "data/inventory.json"


def test_manifest_matches_seed_and_exact_first_appearance_bands():
    spec = json.loads(MANIFEST.read_text())
    assert spec["inventory"]["random_seed"] == RANDOM_SEED
    assert spec["inventory"]["scheme"] == "newest"
    assert spec == generate_selection(SOURCE)
    records = spec["characters"]
    assert len({r["simplified"] for r in records}) == 140
    assert Counter(r["hsk_level"] for r in records) == dict.fromkeys(range(1, 8), 20)
    with sqlite3.connect(SOURCE.as_uri() + "?mode=ro", uri=True) as source:
        bands = dict(source.execute("SELECT char, level FROM hsk_char_min_level WHERE scheme='newest'"))
    assert all(bands[r["simplified"]] == r["hsk_level"] for r in records)


def test_inventory_rebuild_and_sql_restore_are_equivalent(tmp_path, monkeypatch):
    # Ordinary builds must not call the sampler.
    def forbidden(*args):
        raise AssertionError("Rebuild must use the manifest")
    monkeypatch.setattr("chineselearning.inventory_selection.generate_selection", forbidden)
    outputs = []
    for number in range(2):
        database = tmp_path / f"inventory{number}.sqlite"
        sql = tmp_path / f"inventory{number}.sql"
        counts = build_database(SOURCE, MANIFEST, database, sql)
        assert counts["hanzi_character"] == 140
        outputs.append((database, sql))
    assert outputs[0][1].read_bytes() == outputs[1][1].read_bytes()
    assert outputs[0][1].read_bytes() == (ROOT / "data/inventory.sqlite.sql").read_bytes()
    restored = tmp_path / "restored.sqlite"
    with sqlite3.connect(restored) as connection:
        connection.executescript(outputs[0][1].read_text())
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    assert logical_snapshot(restored) == logical_snapshot(outputs[0][0]) == logical_snapshot(outputs[1][0])
    snapshot = logical_snapshot(restored)
    assert all(row[3:] == (None, None) for row in snapshot["hanzi_character"])
    assert all(row[1:] == (1, 1) for row in snapshot["character_learning"])


@pytest.mark.parametrize("problem", ["duplicate", "band", "null", "metadata", "count"])
def test_invalid_manifest_publishes_no_outputs(tmp_path, problem):
    spec = json.loads(MANIFEST.read_text())
    if problem == "duplicate":
        spec["characters"][1]["simplified"] = spec["characters"][0]["simplified"]
    elif problem == "band":
        # Keep counts balanced while assigning incorrect source bands.
        spec["characters"][0]["hsk_level"], spec["characters"][20]["hsk_level"] = 2, 1
    elif problem == "null":
        spec["characters"][0]["english_gloss"] = "invented"
    elif problem == "metadata":
        spec["inventory"]["scheme"] = "new"
    else:
        spec["characters"].pop()
    selection = tmp_path / "bad.json"
    selection.write_text(json.dumps(spec))
    output, sql = tmp_path / "bad.sqlite", tmp_path / "bad.sql"
    with pytest.raises(ValueError):
        build_database(SOURCE, selection, output, sql)
    assert not output.exists() and not sql.exists()
