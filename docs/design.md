# Design

## Purpose

A parent who is a native Chinese speaker teaches a seventh-grader, using curated
texts — poems, classical prose, excerpts, explanatory articles — as the material.
The app holds the texts, relates them to characters and words, records what the
student knows, and supports exercises built from a text. Credit by examination is
one milestone; literary and cultural competence is the aim. HSK is a reference
scale for difficulty and coverage, not a syllabus.

Scale: hundreds of texts, not thousands. One admin, one student (designed so a
second student costs a column, not a redesign). Private, local, never hosted.

## Four layers, four lifetimes

| Layer | What | Lifetime | Source of truth |
| --- | --- | --- | --- |
| 1. Reference | `hsk-original/` | permanent, read-only | upstream dataset |
| 2. Master HSK | `character`, `word` | regenerated rarely | `data/hsk.sql`, produced by `tools/derive_hsk.py` |
| 3. Texts & annotations | `text`, `tag`, `text_*` | repaved on every build | `data/texts/*.md`, `data/annotations/*.json` (exported by the app) |
| 4. Learner & collections | `progress`, `collection` | accumulates; never repaved | `build/progress.sqlite`, backed up by hand |

Layers 2–3 live in `build/content.sqlite`; `chineselearning build` recreates it from
`data/` every time. Layer 4 lives in `build/progress.sqlite` and refers to content
only by natural keys (the character, the word string, the text id), so a content
rebuild cannot orphan it.

### Layer 2: master HSK

Two flat tables, deliberately lossy. Rules are documented in `tools/derive_hsk.py`.

- `character(id = code point, char, traditional, pinyin, readings JSON, hsk_level 1–7, hsk_edition)`
- `word(id = source entry id, simplified UNIQUE, traditional, pinyin, meanings JSON, readings JSON, pos, frequency_rank, hsk_level, hsk_edition)`

`hsk_edition` is `latest` (2026 list) or `old` (survives only from an earlier list;
班主任 is `5/old`). Level 7 is the combined 7–9 band. Readings are ordered by
commonness (pypinyin), and the first one is denormalized into `pinyin`/`meanings`.
3,034 characters, 11,470 words. 啼 and 枫 are not in it; classical texts routinely
contain non-HSK characters.

### Layer 3: texts and annotations

A text is one file in `data/texts/`, hand-written:

```
id: 1
title: 枫桥夜泊
author: 张继
period: 唐朝
tags: 诗词

月落乌啼霜满天，江枫渔火对愁眠。
姑苏城外寒山寺，夜半钟声到客船。
```

Header: `key: value` lines up to the first blank line; `id`, `title`, `tags`
required; `tags` comma-separated, at least one; `author`, `period`, `notes`
optional. Body: everything after the blank line, verbatim. The file name is for
humans; identity is the `id`.

Tables: `text(id, title, author, period, body, notes)`, `tag(name)`,
`text_tag(text_id, tag_name)`. Tags are literary categories (诗词, 文言, 散文, 节选,
讲解); the set grows by using a new name in a file.

Annotations belong to the text, never to the master tables. The master is a
dictionary; the text owns how its material is taught. Four kinds, all keyed by
`text_id`, all created in admin mode and exported back to
`data/annotations/<id>.json` so a rebuild restores them:

| Table | Meaning | Row |
| --- | --- | --- |
| `text_character` | a character singled out for study in this text | `char`, `gloss` |
| `text_word` | a word present in the text | `surface`, `word_id` (nullable → `word`), `gloss` |
| `text_expansion` | a single character taught through a modern word (月→月亮, 乌→乌鸦) | `char`, `surface`, `word_id` (nullable), `gloss` |
| `text_note` | free commentary | `note`, optional `anchor` (substring it refers to) |

Rule for anything with `word_id` + `gloss`: the master entry, when linked,
always supplies pinyin, level and dictionary meanings; the text's `gloss` is shown
in addition, as the contextual explanation. `word_id` null with a `gloss` is a
local word (寒山寺, 姑苏城). Both null is invalid.

Annotations are persisted write-through: every admin save updates the database
*and* rewrites `data/annotations/<text id>.json`. That file is the source of
truth and stores surfaces, never `word_id`; `build` re-resolves each surface
against `word.simplified`. There is no separate export step to forget.

```json
{"text_id": 1,
 "characters": [{"char": "愁", "gloss": "忧愁"}],
 "words":      [{"surface": "寒山寺", "gloss": "苏州城外的寺庙"}],
 "expansions": [{"char": "月", "surface": "月亮", "gloss": null},
                {"char": "乌", "surface": "乌鸦", "gloss": null}],
 "notes":      [{"anchor": "月落乌啼", "note": "……"}]}
```

Finding candidates is brute force: every 2–4 character substring of the body
looked up in `word.simplified` — a few hundred to a few thousand lookups per text.
Expansions are chosen by the admin, one click per character. Inference-assisted
suggestions are an admin-mode convenience to add later, never part of the data
path.

### Layer 4: learner state and collections

`progress(learner_id, kind, key, state, changed_at)` — append-only. `kind` is
`character` or `word`; `key` is the character itself or the word string (works
for local words too). States: `unrecognized`, `recognized` (can read and explain,
can't write), `mastered` (can also write). Current state = latest row; history
answers "what became recognized last week".

A collection is a named set of characters and words, usually built from one text
and named after it: `collection(id, name, text_id)`, `collection_item(collection_id,
kind, key)`. Collections are curated content and are exported like annotations.

## Modes

**Admin (plain)**: list texts with tag/author/period filters; open a text and see
every unique character with pinyin, level and whether it is in the master; the
word candidates found; the annotations so far. Click a character to add it to
study, to create an expansion, or to add a local word. Save a collection.

**Student**: the text with toggles for pinyin above characters and for
hover/tap explanations (character or word granularity); characters tinted by
HSK level or by progress state. Exercises built from the text: expansion fill-in
(月落乌啼 → 月__ 落__ …), cloze memorization (poem with characters blanked).

## Stack

Python 3.13, `sqlite3` directly, FastAPI, Jinja2, htmx for admin interactions and
student toggles (vendored `static/htmx.min.js`; no build step, no framework).
Server-rendered HTML; JSON endpoints only where a page needs them. Tests build a
real database from `data/` and query it.

## Decision log

- 2026-10-16 Drop SQLAlchemy; plain `sqlite3`. Portability to PostgreSQL is not a goal before learner state exists, and JSON columns are SQLite-specific anyway.
- 2026-10-16 One level per word, newest edition wins; editions collapse to `latest`/`old`. Per-edition membership, Wade–Giles, Bopomofo, Romatzyh, radicals, classifiers dropped.
- 2026-10-16 Readings ordered by pypinyin commonness, not source (alphabetical) order.
- 2026-10-16 Character traditional form by majority vote over all words; known weak spot: 苏→甦 (source never sees 蘇).
- 2026-10-16 Annotations are owned by texts; local words are not inserted into the master.
- 2026-10-16 Progress keyed by natural keys in its own database file.
- 2026-10-16 Texts are one Markdown-ish file each with a `key: value` header; no JSON for hand-written content.
- 2026-10-16 Annotation files store surfaces, not word ids, and are written on every save; no export command.
