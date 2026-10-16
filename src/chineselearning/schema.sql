-- Text layer (design.md layer 3, without annotations). Repaved on every build.
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
