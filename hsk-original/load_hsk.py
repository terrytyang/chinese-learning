#!/usr/bin/env python3
"""
load_hsk.py — load drkameleon/complete-hsk-vocabulary into SQLite, losslessly.

Usage:
    python3 load_hsk.py REPO_DIR OUT.sqlite [--force]
    python3 load_hsk.py --print-schema

REPO_DIR is a clone of https://github.com/drkameleon/complete-hsk-vocabulary.
The loader:
  * reads complete.json (the repo's single source of truth),
  * maps every field into normalized tables, keeping original order and quirks
    (duplicate level tags, undocumented POS codes) exactly as they are,
  * fails loudly on any key it does not know, so an upstream format change
    can never be silently dropped,
  * records the repo commit and file checksum in import_run,
  * verifies the load by rebuilding complete.json from the database and
    comparing it to the original, and by regenerating every file under
    wordlists/ from the database and comparing those too.

Standard library only (Python 3.8+).
"""
import argparse
import datetime
import hashlib
import json
import os
import sqlite3
import subprocess
import sys

LOADER_VERSION = "1.0"
REPO_URL = "https://github.com/drkameleon/complete-hsk-vocabulary"

ENTRY_KEYS = {"simplified", "radical", "level", "frequency", "pos", "forms"}
FORM_KEYS = {"traditional", "transcriptions", "meanings", "classifiers"}
TRANSCRIPTION_KEYS = ("pinyin", "numeric", "wadegiles", "bopomofo", "romatzyh")

# Level schemes as described in the repo README / scripts/process.rb.
# 'newest' is not documented in the README; it was added on 2026-02-10 in the
# commit "Add new HSK3.0 levels, matching 2026 syllabus".
LEVEL_SCHEMES = [
    ("old", "HSK 2.0", 6, "Six-level HSK in use 2010–2021."),
    ("new", "HSK 3.0 (2021 standard)", 7, "Nine-band standard; level 7 covers bands 7–9."),
    ("newest", "HSK 3.0 (2026 syllabus)", 7,
     "Undocumented in README; added upstream 2026-02-10 'matching 2026 syllabus'."),
]

# Part-of-speech codes from the repo README.
POS_CODES = {
    "a": "adjective", "ad": "adjective as adverbial", "ag": "adjective morpheme",
    "an": "adjective with nominal function", "b": "non-predicate adjective",
    "c": "conjunction", "d": "adverb", "dg": "adverb morpheme", "e": "interjection",
    "f": "directional locality", "g": "morpheme", "h": "prefix", "i": "idiom",
    "j": "abbreviation", "k": "suffix", "l": "fixed expressions", "m": "numeral",
    "mg": "numeric morpheme", "n": "common noun", "ng": "noun morpheme",
    "nr": "personal name", "ns": "place name", "nt": "organization name",
    "nx": "nominal character string", "nz": "other proper noun", "o": "onomatopoeia",
    "p": "preposition", "q": "classifier", "r": "pronoun", "rg": "pronoun morpheme",
    "s": "space word", "t": "time word", "tg": "time word morpheme", "u": "auxiliary",
    "v": "verb", "vd": "verb as adverbial", "vg": "verb morpheme",
    "vn": "verb with nominal function", "w": "symbol and non-sentential punctuation",
    "x": "unclassified items", "y": "modal particle", "z": "descriptive",
}

SCHEMA = r"""
PRAGMA foreign_keys = ON;

-- ───────────── provenance ─────────────
CREATE TABLE import_run (
  run_id          INTEGER PRIMARY KEY,
  imported_at     TEXT NOT NULL,          -- UTC ISO-8601
  loader_version  TEXT NOT NULL,
  repo_url        TEXT NOT NULL,
  repo_commit     TEXT,                   -- git HEAD of REPO_DIR, if available
  repo_commit_date TEXT,
  source_file     TEXT NOT NULL,          -- 'complete.json'
  source_sha256   TEXT NOT NULL,
  entry_count     INTEGER NOT NULL,
  verified        INTEGER NOT NULL DEFAULT 0   -- 1 once round-trip checks pass
);

-- ───────────── lookups ─────────────
CREATE TABLE hsk_level_scheme (
  scheme       TEXT PRIMARY KEY,          -- 'old' | 'new' | 'newest'
  label        TEXT NOT NULL,
  max_level    INTEGER NOT NULL,
  note         TEXT
);

CREATE TABLE hsk_pos_code (
  code         TEXT PRIMARY KEY,
  meaning      TEXT,                      -- NULL where the README does not define the code
  documented   INTEGER NOT NULL           -- 1 = listed in README, 0 = seen in data only
);

-- ───────────── entries (one per object in complete.json) ─────────────
CREATE TABLE hsk_entry (
  entry_id     INTEGER PRIMARY KEY,       -- = position in complete.json, 1-based
  simplified   TEXT NOT NULL UNIQUE,
  radical      TEXT NOT NULL,
  frequency    INTEGER NOT NULL           -- lower = more common
);

CREATE TABLE hsk_entry_level (            -- the "level" array, order and duplicates kept
  entry_id     INTEGER NOT NULL REFERENCES hsk_entry(entry_id),
  tag_seq      INTEGER NOT NULL,          -- 1-based position in the array
  tag          TEXT NOT NULL,             -- raw tag, e.g. 'old-2'
  scheme       TEXT NOT NULL REFERENCES hsk_level_scheme(scheme),
  level        INTEGER NOT NULL,
  PRIMARY KEY (entry_id, tag_seq)
);

CREATE TABLE hsk_entry_pos (              -- the "pos" array, order kept
  entry_id     INTEGER NOT NULL REFERENCES hsk_entry(entry_id),
  pos_seq      INTEGER NOT NULL,
  pos          TEXT NOT NULL REFERENCES hsk_pos_code(code),
  PRIMARY KEY (entry_id, pos_seq)
);

-- ───────────── forms (one per reading / traditional variant) ─────────────
CREATE TABLE hsk_form (
  form_id      INTEGER PRIMARY KEY,
  entry_id     INTEGER NOT NULL REFERENCES hsk_entry(entry_id),
  form_seq     INTEGER NOT NULL,          -- 1-based position in "forms"
  traditional  TEXT NOT NULL,
  pinyin       TEXT NOT NULL,             -- tone marks
  numeric      TEXT NOT NULL,             -- tone numbers
  wadegiles    TEXT NOT NULL,
  bopomofo     TEXT NOT NULL,
  romatzyh     TEXT NOT NULL,
  UNIQUE (entry_id, form_seq)
);

CREATE TABLE hsk_meaning (
  form_id      INTEGER NOT NULL REFERENCES hsk_form(form_id),
  meaning_seq  INTEGER NOT NULL,
  meaning      TEXT NOT NULL,
  PRIMARY KEY (form_id, meaning_seq)
);

CREATE TABLE hsk_classifier (
  form_id        INTEGER NOT NULL REFERENCES hsk_form(form_id),
  classifier_seq INTEGER NOT NULL,
  classifier     TEXT NOT NULL,
  PRIMARY KEY (form_id, classifier_seq)
);

-- ───────────── derived: characters of each entry ─────────────
-- Not in the source; computed deterministically from hsk_entry.simplified
-- so that character-level queries are joins rather than string splitting.
CREATE TABLE hsk_entry_char (
  entry_id     INTEGER NOT NULL REFERENCES hsk_entry(entry_id),
  position     INTEGER NOT NULL,          -- 1-based
  char         TEXT NOT NULL,
  PRIMARY KEY (entry_id, position)
);

CREATE INDEX ix_entry_level_scheme ON hsk_entry_level(scheme, level, entry_id);
CREATE INDEX ix_entry_char_char    ON hsk_entry_char(char, entry_id);
CREATE INDEX ix_form_entry         ON hsk_form(entry_id);
CREATE INDEX ix_form_pinyin        ON hsk_form(numeric);

-- ───────────── views ─────────────

-- Reproduces wordlists/{exclusive|inclusive}/{scheme}/{level}.json exactly:
--   exclusive N = entries tagged with level N (NOT disjoint: an entry tagged
--                 old-1 and old-2 is in both exclusive lists)
--   inclusive N = entries tagged with any level 1..N
-- Ordered by entry_id, which is the order of complete.json.
CREATE VIEW hsk_wordlist AS
SELECT DISTINCT 'exclusive' AS kind, l.scheme, l.level, l.entry_id
  FROM hsk_entry_level l
UNION
SELECT DISTINCT 'inclusive' AS kind, s.scheme, n.level, l.entry_id
  FROM hsk_level_scheme s
  JOIN (WITH RECURSIVE k(level) AS (SELECT 1 UNION ALL SELECT level + 1 FROM k WHERE level < 7)
        SELECT level FROM k) n ON n.level <= s.max_level
  JOIN hsk_entry_level l ON l.scheme = s.scheme AND l.level <= n.level;

-- Lowest level per scheme for each entry.
CREATE VIEW hsk_entry_min_level AS
SELECT entry_id, scheme, MIN(level) AS level
  FROM hsk_entry_level GROUP BY entry_id, scheme;

-- Lowest level per scheme at which each character first appears in any entry.
CREATE VIEW hsk_char_min_level AS
SELECT c.char, m.scheme, MIN(m.level) AS level
  FROM hsk_entry_char c JOIN hsk_entry_min_level m USING (entry_id)
 GROUP BY c.char, m.scheme;

-- Flat browsing view: one row per entry, arrays joined for reading.
CREATE VIEW hsk_entry_flat AS
SELECT e.entry_id, e.simplified, e.radical, e.frequency,
       (SELECT group_concat(tag, ' ')  FROM (SELECT tag FROM hsk_entry_level WHERE entry_id = e.entry_id ORDER BY tag_seq)) AS levels,
       (SELECT group_concat(pos, ' ')  FROM (SELECT pos FROM hsk_entry_pos   WHERE entry_id = e.entry_id ORDER BY pos_seq))  AS pos,
       (SELECT group_concat(traditional, ' / ') FROM (SELECT traditional FROM hsk_form WHERE entry_id = e.entry_id ORDER BY form_seq)) AS traditional,
       (SELECT group_concat(pinyin, ' / ')      FROM (SELECT pinyin      FROM hsk_form WHERE entry_id = e.entry_id ORDER BY form_seq)) AS pinyin,
       (SELECT group_concat(m.meaning, ' | ')
          FROM (SELECT m.meaning FROM hsk_form f JOIN hsk_meaning m USING (form_id)
                 WHERE f.entry_id = e.entry_id ORDER BY f.form_seq, m.meaning_seq) m) AS meanings
  FROM hsk_entry e;
"""


def fail(msg):
    sys.exit(f"ERROR: {msg}")


def is_hanzi(c):
    o = ord(c)
    return 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF or 0x20000 <= o <= 0x2FA1F


def git_info(repo):
    try:
        commit = subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"],
                                         stderr=subprocess.DEVNULL, text=True).strip()
        date = subprocess.check_output(["git", "-C", repo, "log", "-1", "--format=%cI"],
                                       stderr=subprocess.DEVNULL, text=True).strip()
        return commit, date
    except (OSError, subprocess.CalledProcessError):
        return None, None


def parse_tag(tag):
    scheme, _, lvl = tag.rpartition("-")
    if scheme not in {s for s, *_ in LEVEL_SCHEMES} or not lvl.isdigit():
        fail(f"unknown level tag {tag!r}")
    return scheme, int(lvl)


def load(repo, out):
    src = os.path.join(repo, "complete.json")
    raw = open(src, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, list):
        fail("complete.json is not a JSON array")

    db = sqlite3.connect(out)
    db.executescript(SCHEMA)
    cur = db.cursor()

    commit, commit_date = git_info(repo)
    cur.execute("""INSERT INTO import_run (imported_at, loader_version, repo_url, repo_commit,
                   repo_commit_date, source_file, source_sha256, entry_count)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                 LOADER_VERSION, REPO_URL, commit, commit_date, "complete.json", sha, len(data)))
    run_id = cur.lastrowid

    cur.executemany("INSERT INTO hsk_level_scheme VALUES (?,?,?,?)", LEVEL_SCHEMES)
    seen_pos = sorted({p for e in data for p in e.get("pos", [])})
    for code in sorted(set(POS_CODES) | set(seen_pos)):
        cur.execute("INSERT INTO hsk_pos_code VALUES (?,?,?)",
                    (code, POS_CODES.get(code), 1 if code in POS_CODES else 0))

    form_id = 0
    for entry_id, e in enumerate(data, start=1):
        extra = set(e) - ENTRY_KEYS
        missing = ENTRY_KEYS - set(e)
        if extra or missing:
            fail(f"entry {entry_id} ({e.get('simplified')}): unexpected keys {extra}, missing {missing}")
        cur.execute("INSERT INTO hsk_entry VALUES (?,?,?,?)",
                    (entry_id, e["simplified"], e["radical"], e["frequency"]))
        for i, tag in enumerate(e["level"], start=1):
            scheme, lvl = parse_tag(tag)
            cur.execute("INSERT INTO hsk_entry_level VALUES (?,?,?,?,?)",
                        (entry_id, i, tag, scheme, lvl))
        for i, p in enumerate(e["pos"], start=1):
            cur.execute("INSERT INTO hsk_entry_pos VALUES (?,?,?)", (entry_id, i, p))
        for i, ch in enumerate(e["simplified"], start=1):
            if not is_hanzi(ch):
                fail(f"entry {entry_id}: non-hanzi character {ch!r} in {e['simplified']!r}")
            cur.execute("INSERT INTO hsk_entry_char VALUES (?,?,?)", (entry_id, i, ch))
        for fseq, f in enumerate(e["forms"], start=1):
            extra = set(f) - FORM_KEYS
            missing = FORM_KEYS - set(f)
            if extra or missing:
                fail(f"entry {entry_id} form {fseq}: unexpected keys {extra}, missing {missing}")
            t = f["transcriptions"]
            if set(t) != set(TRANSCRIPTION_KEYS):
                fail(f"entry {entry_id} form {fseq}: transcription keys {sorted(t)}")
            form_id += 1
            cur.execute("INSERT INTO hsk_form VALUES (?,?,?,?,?,?,?,?,?)",
                        (form_id, entry_id, fseq, f["traditional"],
                         *(t[k] for k in TRANSCRIPTION_KEYS)))
            for i, m in enumerate(f["meanings"], start=1):
                cur.execute("INSERT INTO hsk_meaning VALUES (?,?,?)", (form_id, i, m))
            for i, c in enumerate(f["classifiers"], start=1):
                cur.execute("INSERT INTO hsk_classifier VALUES (?,?,?)", (form_id, i, c))
    db.commit()
    return db, data, run_id


def rebuild_entry(db, entry_id, with_level=True):
    """Rebuild one entry as a dict with the same key order as complete.json."""
    simp, rad, freq = db.execute(
        "SELECT simplified, radical, frequency FROM hsk_entry WHERE entry_id=?", (entry_id,)).fetchone()
    e = {"simplified": simp, "radical": rad}
    if with_level:
        e["level"] = [r[0] for r in db.execute(
            "SELECT tag FROM hsk_entry_level WHERE entry_id=? ORDER BY tag_seq", (entry_id,))]
    e["frequency"] = freq
    e["pos"] = [r[0] for r in db.execute(
        "SELECT pos FROM hsk_entry_pos WHERE entry_id=? ORDER BY pos_seq", (entry_id,))]
    forms = []
    for row in db.execute(
            "SELECT form_id, traditional, pinyin, numeric, wadegiles, bopomofo, romatzyh "
            "FROM hsk_form WHERE entry_id=? ORDER BY form_seq", (entry_id,)).fetchall():
        fid, trad, *tr = row
        forms.append({
            "traditional": trad,
            "transcriptions": dict(zip(TRANSCRIPTION_KEYS, tr)),
            "meanings": [r[0] for r in db.execute(
                "SELECT meaning FROM hsk_meaning WHERE form_id=? ORDER BY meaning_seq", (fid,))],
            "classifiers": [r[0] for r in db.execute(
                "SELECT classifier FROM hsk_classifier WHERE form_id=? ORDER BY classifier_seq", (fid,))],
        })
    e["forms"] = forms
    return e


def verify(db, data, repo, run_id):
    ids = [r[0] for r in db.execute("SELECT entry_id FROM hsk_entry ORDER BY entry_id")]
    rebuilt = [rebuild_entry(db, i) for i in ids]
    if rebuilt != data:
        bad = next(i for i, (a, b) in enumerate(zip(rebuilt, data)) if a != b) if len(rebuilt) == len(data) else None
        fail(f"round-trip mismatch for complete.json (first differing index: {bad})")
    if json.dumps(rebuilt, ensure_ascii=False, sort_keys=False) != json.dumps(data, ensure_ascii=False, sort_keys=False):
        fail("round-trip key order mismatch")
    print(f"  complete.json: {len(data)} entries rebuilt from the database — identical")

    # Wordlist files: regenerate each from the hsk_wordlist view and compare.
    checked = 0
    wl_root = os.path.join(repo, "wordlists")
    if os.path.isdir(wl_root):
        no_level = {i: rebuild_entry(db, i, with_level=False) for i in ids}
        for kind in ("exclusive", "inclusive"):
            for scheme, _, max_level, _ in LEVEL_SCHEMES:
                for lvl in range(1, max_level + 1):
                    path = os.path.join(wl_root, kind, scheme, f"{lvl}.json")
                    if not os.path.exists(path):
                        continue
                    expected = json.load(open(path, encoding="utf-8"))
                    got = [no_level[r[0]] for r in db.execute(
                        "SELECT entry_id FROM hsk_wordlist WHERE kind=? AND scheme=? AND level=? "
                        "ORDER BY entry_id", (kind, scheme, lvl))]
                    if got != expected:
                        fail(f"wordlist mismatch: {kind}/{scheme}/{lvl}.json "
                             f"(file {len(expected)} entries, view {len(got)})")
                    checked += 1
        print(f"  wordlists/: {checked} files regenerated from the hsk_wordlist view — identical")
    db.execute("UPDATE import_run SET verified = 1 WHERE run_id = ?", (run_id,))
    db.commit()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--force", action="store_true", help="overwrite OUT if it exists")
    ap.add_argument("--print-schema", action="store_true")
    a = ap.parse_args()
    if a.print_schema:
        print(SCHEMA.strip())
        return
    if not a.repo or not a.out:
        ap.error("REPO_DIR and OUT.sqlite are required")
    if os.path.exists(a.out):
        if not a.force:
            fail(f"{a.out} exists (use --force to overwrite)")
        os.remove(a.out)
    db, data, run_id = load(a.repo, a.out)
    print(f"Loaded {len(data)} entries into {a.out}")
    verify(db, data, a.repo, run_id)
    db.execute("VACUUM")
    db.close()
    print("OK")


if __name__ == "__main__":
    main()
