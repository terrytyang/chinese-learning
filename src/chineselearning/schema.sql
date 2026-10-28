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

-- Text facts: true of the text however it is taught (data/annotations/<text id>.json).
-- Every row has an origin: auto (intake), suggested (an outside tool), manual (admin entered or confirmed).
CREATE TABLE text_reading (       -- the reading of every Han position; char must equal the body there
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,       -- 0-based index into the body
  char TEXT NOT NULL,
  pinyin TEXT NOT NULL,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (text_id, position)
);
CREATE TABLE text_character (     -- a character this text uses unusually: a contextual gloss beside the dictionary's
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  char TEXT NOT NULL,                -- its reading is its text_reading rows
  gloss TEXT,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (text_id, char)
);
CREATE TABLE text_word (          -- a word present in the text; always a dictionary row (HSK or supplement)
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  surface TEXT NOT NULL,
  word_id INTEGER NOT NULL REFERENCES word(id),
  pinyin TEXT,                     -- a contextual correction of the dictionary's reading
  gloss TEXT,                      -- a contextual gloss beside the dictionary's
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (text_id, surface)
);

-- Lessons: additive layers over a text (data/lessons/<text id>-<lesson id>.json), or vocabulary lessons with no text
-- (text_id null, data/lessons/<lesson id>.json). Ids are fixed by the file. Names are unique per text and unique among
-- vocabulary lessons; the constraint covers the first (NULLs are distinct), lessons._check_name both.
CREATE TABLE lesson (
  id INTEGER PRIMARY KEY,
  text_id INTEGER REFERENCES text(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  UNIQUE (text_id, name)
);
CREATE TABLE lesson_character (   -- a character to study in this lesson
  lesson_id INTEGER NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
  char TEXT NOT NULL,
  PRIMARY KEY (lesson_id, char)
);
CREATE TABLE lesson_word (        -- a text word to study in this lesson
  lesson_id INTEGER NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
  surface TEXT NOT NULL,
  PRIMARY KEY (lesson_id, surface)
);
CREATE TABLE lesson_extra_word (  -- a word the lesson teaches that the text does not contain as written
  lesson_id INTEGER NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
  surface TEXT NOT NULL,
  anchor TEXT,                     -- a passage of the text it relates to; one character = an expansion (月 -> 月亮)
  word_id INTEGER NOT NULL REFERENCES word(id),
  pinyin TEXT,                     -- prefilled from the dictionary
  gloss TEXT,                      -- a contextual gloss beside the dictionary's
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual'))
);
-- The key is (lesson, surface, anchor or ''); SQLite forbids expressions in a PRIMARY KEY, so it is a unique index.
CREATE UNIQUE INDEX lesson_extra_word_key ON lesson_extra_word (lesson_id, surface, coalesce(anchor, ''));
CREATE TABLE lesson_note (        -- free commentary, optionally anchored on a substring of the text
  id INTEGER PRIMARY KEY,
  lesson_id INTEGER NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
  anchor TEXT,
  note TEXT NOT NULL,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual'))
);
