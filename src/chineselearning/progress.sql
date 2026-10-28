-- Learner progress (build/progress.sqlite), attached to the content connection as `progress`.
-- Never repaved: applied with IF NOT EXISTS on every open. One row per (learner, kind, key)
-- holding the current state and when it changed; no row means 'unconfirmed'. No history.
-- The one in-place schema change in the project: a file made before `origin` existed gets the
-- column on open (db.connect: ALTER TABLE ... ADD COLUMN origin TEXT NOT NULL DEFAULT 'import').
CREATE TABLE IF NOT EXISTS progress.learner (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS progress.progress (
  learner_id INTEGER NOT NULL REFERENCES learner(id),
  kind TEXT NOT NULL CHECK (kind IN ('character', 'word')),
  key TEXT NOT NULL,                -- the character itself, or the word string (never a single character)
  state TEXT NOT NULL CHECK (state IN ('exposed', 'recognized', 'mastered')),
  changed_at TEXT NOT NULL,         -- ISO 8601 UTC
  origin TEXT NOT NULL CHECK (origin IN ('auto', 'manual', 'import')),  -- auto: intake or adding to a lesson; manual: a page; import: a file
  PRIMARY KEY (learner_id, kind, key)
);
