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
| 4. Learner | `progress` | accumulates; never repaved | `build/progress.sqlite`, backed up by hand |

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
讲解); the set grows by using a new name in a file. A text with its annotations
*is* the teaching material, and it is always in flux: there is no draft/ready
state and nothing to promote. There is no separate "collection"; a `lesson`
(later) orders several texts.

Annotations belong to the text, never to the master tables. The master is a
dictionary; the text owns how its material is taught. Five kinds, all keyed by
`text_id`, all persisted in `data/annotations/<id>.json` so a rebuild restores
them:

| Table | Meaning | Row |
| --- | --- | --- |
| `text_character` | a character singled out for study in this text | `char`, `gloss` |
| `text_word` | a word present in the text | `surface`, `word_id` (nullable → `word`), `pinyin` (nullable), `gloss` |
| `text_expansion` | a single character taught through a modern word (月→月亮, 乌→乌鸦) | `char`, `surface`, `word_id` (nullable), `gloss` |
| `text_reading` | the reading of a character in this text when it is not the default | `char`, `pinyin`, optional `position` |
| `text_note` | free commentary | `note`, optional `anchor` (substring it refers to) |

Every row carries `origin`: `auto` (deterministic intake), `suggested` (an
outside tool's proposal), or `manual` (entered or confirmed by the admin).
Confirming a row sets it to `manual`.

A character's reading in a text resolves in this order: `text_reading` override
> the reading of a linked `text_word` covering it > the character's primary
reading. The admin page shows which one applied ("háng 由「银行」确定"), and
offers a pull-down of `character.readings` only when there is more than one.

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
 "characters": [{"char": "啼", "gloss": "chirp", "origin": "auto"},
                {"char": "愁", "gloss": "忧愁", "origin": "manual"}],
 "words":      [{"surface": "寒山寺", "pinyin": "hán shān sì", "hsk_level": 7,
                 "gloss": "苏州城外的寺庙", "origin": "manual"}],
 "expansions": [{"char": "月", "surface": "月亮", "gloss": null, "origin": "manual"},
                {"char": "乌", "surface": "乌鸦", "hsk_level": 7, "gloss": "crow", "origin": "suggested"}],
 "readings":   [{"char": "舍", "pinyin": "shè", "position": null, "origin": "manual"}],
 "notes":      [{"anchor": "月落乌啼", "note": "……", "origin": "manual"}]}
```

### Intake

`chineselearning intake <text id>` runs once per text, before curation, and
stores its results as `origin = auto` rows in the annotation file: every 2–4
character window of the body (within runs of Han characters) that matches
`word.simplified` becomes a `text_word` — brute force, a few thousand lookups at
most — and every character absent from the master becomes a `text_character`,
since it needs the admin's attention. False positives (交通, 无论 in 桃花源记) are
rows to delete or gloss, not to re-ignore on every view. Intake refuses to run
on a text that already has annotations unless forced; `build` never runs it.
Readings are not stored per character: they resolve at view time by the order
above, and only overrides are rows.

Judgment — which matches are real words here, which single characters deserve
expansion, contextual glosses, non-default readings — comes from outside the
app. `docs/prompts/intake.md` is a prompt template with the file schema, the
rules, and one hand-annotated gold example; any AI tool given it and a text
produces `data/annotations/<id>.json` with `origin = suggested`. The app never
calls a model; it validates a file, strictly and with messages that name the
offending value, because an outside tool is a less trustworthy author than the
admin.

### Layer 4: learner state and collections

`progress(learner_id, kind, key, state, changed_at)` — append-only. `kind` is
`character` or `word`; `key` is the character itself or the word string (works
for local words too). States: `unrecognized`, `recognized` (can read and explain,
can't write), `mastered` (can also write). Current state = latest row; history
answers "what became recognized last week".

Attempts at exercises (cloze and later games) are logged in the same file:
`attempt(learner_id, text_id, exercise, score, detail JSON, at)`.

## Modes

**Admin (plain)**: list texts with tag/author/period filters; open a text and see
every unique character with pinyin, level and whether it is in the master; the
word candidates found; the annotations so far. Click a character to add it to
study, to create an expansion, or to add a local word. Save a collection.

Every student-facing presentation renders one assembled structure, built by one
function from a text and its annotations: the body as characters, each with its
resolved reading, traditional form, level, progress state and study flag; word
spans with reading and gloss; expansions; notes. New presentations are templates
over that structure, never new queries.

**Student**: the text with toggles for pinyin (`<ruby>`), traditional (OpenCC
`s2t`, pure-Python package, overridable per text), hover/tap glosses, and word
highlighting with the highlighted words listed beneath; characters tinted by
HSK level or progress state. **Print**: the same structure through `@media print`
templates — poem with ruby, vocabulary list, 田字格 sheet, cloze sheet. **Games**:
cloze with a tunable blank ratio (seeded, reproducible), pinyin hints, server-side
grading, attempts logged to progress.

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
- 2026-10-16 No collection entity and no text status: a text with its annotations is the material and is always in flux; `lesson` groups texts later.
- 2026-10-16 Intake is deterministic and in-app; judgment comes from any outside AI tool via a prompt template producing the annotation file. No model calls in the app.
- 2026-10-16 Traditional for display via OpenCC `s2t` (pure-Python), overridable per text; the master's character column stays best-effort.
- 2026-10-16 Setting a character's reading replaces the existing override (the pull-down is the editor); every other duplicate add stays a no-op.
