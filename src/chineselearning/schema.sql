-- Text layer (design.md layer 3). Repaved on every build; annotations are
-- re-imported from data/annotations/<id>.json.
CREATE TABLE text (
  id INTEGER PRIMARY KEY,          -- from the file header
  title TEXT NOT NULL,
  author TEXT,
  period TEXT,
  body TEXT NOT NULL,              -- verbatim file body
  notes TEXT
);
CREATE TABLE tag (
  name TEXT PRIMARY KEY            -- literary category: 诗词, 文言, ...
);
CREATE TABLE text_tag (
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  tag_name TEXT NOT NULL REFERENCES tag(name),
  PRIMARY KEY (text_id, tag_name)
);

-- Annotations: owned by the text, never by the master tables. Every row has an
-- origin: auto (intake), suggested (an outside tool), manual (admin entered or confirmed).
CREATE TABLE text_character (     -- a character singled out for study
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  char TEXT NOT NULL,
  gloss TEXT,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (text_id, char)
);
CREATE TABLE text_word (          -- a word present in the text; word_id null = local word
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  surface TEXT NOT NULL,
  word_id INTEGER REFERENCES word(id),
  pinyin TEXT,                     -- a local word's reading, or a contextual correction of a linked word's
  gloss TEXT,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (text_id, surface),
  CHECK (word_id IS NOT NULL OR gloss IS NOT NULL)
);
CREATE TABLE text_expansion (     -- a character taught through a modern word (月 -> 月亮)
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  char TEXT NOT NULL,
  surface TEXT NOT NULL,
  word_id INTEGER REFERENCES word(id),
  gloss TEXT,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (text_id, char, surface),
  CHECK (word_id IS NOT NULL OR gloss IS NOT NULL)
);
CREATE TABLE text_reading (       -- a character's reading in this text when not the default
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  char TEXT NOT NULL,
  pinyin TEXT NOT NULL,
  position INTEGER,                -- 0-based index into the body; null = every occurrence
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual'))
);
CREATE UNIQUE INDEX text_reading_key ON text_reading (text_id, char, coalesce(position, -1));
CREATE TABLE text_note (          -- free commentary, optionally anchored on a substring
  id INTEGER PRIMARY KEY,
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  anchor TEXT,
  note TEXT NOT NULL,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual'))
);
