-- Learner progress (build/progress.sqlite), attached to the content connection as `progress`.
-- Never repaved: applied with IF NOT EXISTS on every open. Append-only; the latest row per
-- (learner, kind, key) is the current state, and no row means 'unrecognized'.
CREATE TABLE IF NOT EXISTS progress.learner (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS progress.progress (
  id INTEGER PRIMARY KEY,
  learner_id INTEGER NOT NULL REFERENCES learner(id),
  kind TEXT NOT NULL CHECK (kind IN ('character', 'word')),
  key TEXT NOT NULL,                -- the character itself, or the word string (local words too)
  state TEXT NOT NULL CHECK (state IN ('unrecognized', 'recognized', 'mastered')),
  changed_at TEXT NOT NULL          -- ISO 8601 UTC
);
CREATE INDEX IF NOT EXISTS progress.progress_key ON progress (learner_id, kind, key, id);
