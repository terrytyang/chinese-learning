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
CREATE TABLE text_character (     -- facts about a character the master lacks or this text uses unusually
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  char TEXT NOT NULL,
  pinyin TEXT,
  hsk_level INTEGER CHECK (1 <= hsk_level AND hsk_level <= 7),
  gloss TEXT,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (text_id, char)
);
CREATE TABLE text_word (          -- a word present in the text; word_id null = local word
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
  surface TEXT NOT NULL,
  word_id INTEGER REFERENCES word(id),
  pinyin TEXT,                     -- a local word's reading, or a contextual correction of a linked word's
  hsk_level INTEGER CHECK (1 <= hsk_level AND hsk_level <= 7),  -- local words only; null when linked
  gloss TEXT,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (text_id, surface),
  CHECK (word_id IS NOT NULL OR gloss IS NOT NULL)
);

-- Lessons: additive layers over a text (data/lessons/<text id>-<lesson id>.json). Ids are fixed by the file.
CREATE TABLE lesson (
  id INTEGER PRIMARY KEY,
  text_id INTEGER NOT NULL REFERENCES text(id) ON DELETE CASCADE,
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
CREATE TABLE lesson_expansion (   -- a character taught through a modern word (月 -> 月亮)
  lesson_id INTEGER NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
  char TEXT NOT NULL,
  surface TEXT NOT NULL,
  word_id INTEGER REFERENCES word(id),
  hsk_level INTEGER CHECK (1 <= hsk_level AND hsk_level <= 7),  -- unlinked expansions only
  gloss TEXT,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual')),
  PRIMARY KEY (lesson_id, char, surface),
  CHECK (word_id IS NOT NULL OR gloss IS NOT NULL)
);
CREATE TABLE lesson_note (        -- free commentary, optionally anchored on a substring of the text
  id INTEGER PRIMARY KEY,
  lesson_id INTEGER NOT NULL REFERENCES lesson(id) ON DELETE CASCADE,
  anchor TEXT,
  note TEXT NOT NULL,
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'suggested', 'manual'))
);
