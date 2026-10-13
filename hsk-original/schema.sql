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
