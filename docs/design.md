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

- `character` — every character occurring in any HSK item (3,034): `id` = code
  point, `char`, `traditional`, `pinyin` (most common reading), `readings` (JSON
  list, most common first), `gloss` (short, curated: `data/character-gloss.tsv`,
  baked in by the derivation and applied again at build so the dictionary page
  can edit it), `hsk_level` (lowest level of any item containing
  it), `hsk_edition`. When the syllabus lists the character itself as an item
  (1,571 do), the item's data is carried on the same row: `meanings` (CEDICT,
  primary reading), `alt_readings` (other dictionary forms), `pos`,
  `frequency_rank`, `word_level` (its level *as an item*; 银 is a level-3
  character but a level-6 item). Null otherwise.
- `word` — multi-character items only (9,899): `id` = source entry id,
  `simplified`, `traditional`, `pinyin`, `meanings` (primary form),
  `alt_readings` (JSON `[{pinyin, traditional, meanings}]` for other forms, null
  when there is one), `pos`, `frequency_rank`, `hsk_level`, `hsk_edition`.

Both tables carry `source`: `hsk` for the generated rows, `supplement` for rows
loaded at build from `data/supplement.tsv` — non-HSK vocabulary the admin
curates (`item  pinyin  gloss  level`). A supplement character's level is 7 and a
supplement word's is the highest level among its characters, unless the file
says otherwise; `hsk_edition` is `none`. The supplement is edited in that file,
by the admin page's add forms, and by `import-progress`; nowhere else. There is
no "local word": every word a text or lesson refers to is a dictionary row.

A single character is a character everywhere — progress, lesson selection,
display; there is no word row for it. `hsk_edition` is `latest` (2026 list) or
`old`. Level 7 is the combined 7–9 band. Readings are ordered by commonness
(pypinyin); nothing is stored twice. 啼 and 枫 are not in the master; classical
texts routinely contain non-HSK characters.

### Layer 3: texts, text facts, lessons

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
humans; identity is the `id`. The admin page rewrites only the `tags:` line of
the header; author and period are edited in the file; it never rewrites the body.

Tables: `text(id, title, author, period, body, notes)`, `tag(name)`,
`text_tag(text_id, tag_name)`. Tags are literary categories (诗词, 文言, 散文, 节选,
讲解); the set grows by using a new name.

**Text facts** are true of the text however it is taught, stored once per text
in `data/annotations/<text id>.json`:

| Table | Meaning | Row |
| --- | --- | --- |
| `text_reading` | the reading of each Han character position, where known | `position`, `char`, `pinyin` |
| `text_character` | a character this text uses unusually | `char`, `gloss` (contextual, shown beside the dictionary's) |
| `text_word` | a word present in the text | `surface`, `word_id` (→ `word`, never null), `pinyin` (contextual override), `gloss` (contextual) |

Every row carries `origin`: `auto` (intake), `suggested` (an outside tool), or
`manual` (admin entered or confirmed). A position with no reading row is
unknown (a character the dictionary lacks, not yet given one). Readings are stored,
not resolved at view time, so a reading never changes because a word was added later and a
sheet printed last month still matches the page. A reading's `char` must equal
the body at its `position`; a body edit therefore fails the build until the
text is re-intaken.

**Lessons** are additive layers over a text — a named selection plus teaching
additions — many per text, each in `data/lessons/<text id>-<lesson id>.json`:

| Table | Row |
| --- | --- |
| `lesson` | `id`, `text_id`, `name` (unique per text) |
| `lesson_character` | `lesson_id`, `char` — a character to study in this lesson |
| `lesson_word` | `lesson_id`, `surface` — a text word to study in this lesson |
| `lesson_extra_word` | `lesson_id`, `surface`, `anchor` (nullable: a passage of the text; one character makes the word an *expansion* of it, 月 → 月亮, and the surface must contain it), `word_id` (→ `word`, never null), `pinyin` (prefilled from the dictionary), `gloss` (contextual), `origin`. Key: (lesson, surface, anchor or ''), a unique expression index |
| `lesson_note` | `id`, `lesson_id`, `anchor`, `note`, `origin` |

A lesson with no selections, extra words or notes renders as the plain text
with its facts. Intake creates the first lesson, "Learn 〈title〉", selecting every
unique character and every text word whose state is unconfirmed or exposed; the
admin then customises per lesson (drop a level, re-include mastered items).
Adding a character or word to a lesson, by any route, sets `exposed` when its
state is `unconfirmed`; nothing else changes state implicitly. A single
character is never a word: `text_word`, `lesson_word` and `lesson_extra_word`
reject one-character surfaces. The assembled material derives each extra word's
`kind`, `expansion` or `related`, from its anchor.
Lesson ids are assigned at creation and fixed by the file. Print and exercises
are lesson-based.

The dictionary row (HSK or supplement) always supplies pinyin, level and the
general meaning; a text's or lesson's `gloss` is shown in addition, as the
contextual sense (走 as "run" in a classical text). Adding a word the dictionary
lacks, anywhere in the app, writes a supplement entry first and links it.

Annotation and lesson files are persisted write-through: every admin save
updates the database *and* rewrites the file. Files store surfaces, never
`word_id`; `build` re-resolves. There is no export step.

```json
{"text_id": 1,
 "readings":   [{"position": 0, "char": "月", "pinyin": "yuè", "origin": "auto"}, "…"],
 "characters": [{"char": "啼", "gloss": "chirp", "origin": "manual"}],
 "words":      [{"surface": "寒山寺", "pinyin": null, "gloss": "苏州城外的寺庙", "origin": "manual"}]}
```
```json
{"lesson_id": 1, "text_id": 1, "name": "Learn 枫桥夜泊",
 "characters":  ["月", "落", "乌", "啼"],
 "words":       ["寒山寺"],
 "extra_words": [{"anchor": null, "surface": "半夜", "pinyin": "bàn yè", "gloss": null, "origin": "manual"},
                 {"anchor": "乌", "surface": "乌鸦", "pinyin": "wū yā", "gloss": "crow", "origin": "suggested"},
                 {"anchor": "姑苏", "surface": "苏州", "pinyin": "sū zhōu", "gloss": "Suzhou", "origin": "manual"},
                 {"anchor": "月", "surface": "月亮", "pinyin": "yuè liang", "gloss": null, "origin": "manual"}],
 "notes":       [{"anchor": "月落乌啼", "note": "……", "origin": "manual"}]}
```

### Intake

`chineselearning intake <text id>` runs once per text, before curation. It
stores, as `origin = auto`: a reading for every Han position (resolution order:
override already present > the reading of a text word covering the position,
leftmost-longest > the character's primary reading);
a `text_word` for every 2–4
character window of the body (within runs of Han characters) that matches
`word.simplified` — brute force, a few thousand lookups at most; and the default
lesson. False positives (交通, 无论 in 桃花源记) are rows to delete or gloss, not
to re-ignore on every view. Intake refuses to run on a text that already has
facts or lessons unless forced, and forcing redoes only `auto` rows; `build`
never runs it. A character the dictionary lacks is an error naming it: it goes into
`data/supplement.tsv` first. `intake --new` runs intake for every text with no facts and
no lesson. `intake --reset <id>` deletes a text's facts and lessons, manual rows included, and
their files, after the id is typed to confirm, then runs intake again; progress is untouched.

Judgment — which matches are real words here, which single characters deserve
expansion, contextual glosses, non-default readings — comes from outside the
app. `docs/prompts/` holds prompt templates with the file schemas, the rules,
and hand-annotated gold examples; any AI tool given one and a text produces the
file with `origin = suggested`. The app never calls a model; it validates a
file, strictly and with messages that name the offending value.

### Layer 4: learner state and collections

`progress(learner_id, kind, key, state, changed_at, origin)` — one row per key,
no history. `origin` is `auto` (intake, adding to a lesson), `manual` (a page)
or `import` (a file). `kind` is `character` or `word`; `key` is the character itself or the
word string (never a single character). States:
`unconfirmed` (no row) → `exposed` (met in a lesson) → `recognized` (can read and
explain, can't write) → `mastered` (can also write). Setting `unconfirmed`
deletes the row; `changed_at` says when the current state was set.

Attempts at exercises (cloze and later games) are logged in the same file:
`attempt(learner_id, text_id, exercise, score, detail JSON, at)`.

State is also reproducible from files. `chineselearning export-progress` writes
`data/progress/<learner>.tsv` (`item  state  as_of`); `import-progress` reads
that snapshot and every batch in `data/import/progress/*.tsv` (raw documents
transformed once, by hand or an AI tool following `docs/prompts/progress-import.md`,
with the state and date declared in the file — never the import time). For each
item the candidates are its explicit rows, the rows of words containing it (a
character takes a word's state by implication), and the current database row;
`auto` candidates count only when no other kind exists; among the rest the
latest `as_of` wins, a tie goes to the lowest state. Unmatched items join the
supplement. The export carries `origin`, so a round trip preserves it. `--check` reports without writing; re-running is a no-op.

### Day-0

`chineselearning init [--fresh]` rebuilds everything from `data/` in the only
order that works: `build` (content), `import-progress` (state, which the next
step reads), `intake --new` (facts and a default lesson for any text lacking
them). Every layer is recoverable from git.

## Modes

**Admin**: `/texts` lists texts with tag/author/period filters. `/texts/{text}?lesson=`
is one page per text: a shell (title, lesson select, tags as chips, the text with
ruby and an Edit pinyin mode) over htmx fragments, with five tabs per lesson at
`/texts/{text}/lessons/{lesson}/<tab>` — Characters, Words in text, Expansions,
Related words, Notes. Each tab is a fragment with its own URL; its filters and the
active tab live in the URL, and a non-htmx request to a fragment URL gets the whole
shell. Every mutation POSTs and returns the fragment it changed; a validation
failure returns it with the message at its form, status 422. Every label is
English; only content is Chinese. Pinyin typed as `ti2` is stored as `tí`.

Every student-facing presentation renders one assembled structure, built by one
function from a text, its facts, and optionally one lesson: the body as characters, each with its
resolved reading, traditional form, level, progress state and study flag; word
spans with reading and gloss; expansions; notes. New presentations are templates
over that structure, never new queries.

**Student**: `/learn/{text}` is the text with its facts; `/learn/{text}/{lesson}`
adds the lesson's selections, extra words and notes. Both offer toggles for pinyin (`<ruby>`), traditional (OpenCC
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
- 2026-10-18 Lessons are a separate entity, many per text, additive over the text's facts; study selections, expansions and notes move from text to lesson.
- 2026-10-18 Readings are stored per position at intake, not resolved at view time.
- 2026-10-18 The admin page may rewrite a text file's header (tags etc.), never its body.
- 2026-10-25 Character glosses complete (3,034) and baked into `hsk.sql` by the derivation; the app no longer loads the TSV.
- 2026-10-25 Single-character items consolidated onto `character` (`meanings`, `alt_readings`, `pos`, `frequency_rank`, `word_level`); `word` holds multi-character items only. Primary form in columns, other forms in `alt_readings`; the old `readings` column on `word` is gone.
- 2026-10-25 Learner states are `unconfirmed` (no row) → `exposed` → `recognized` → `mastered`; one row per key with `changed_at`, no history; adding to a lesson sets `exposed` from `unconfirmed`.
- 2026-10-25 Default lesson is "Learn 〈title〉"; intake records every word, the default selection excludes recognized and mastered; UI labels are English, content Chinese.
- 2026-10-27 `data/supplement.tsv`: curated non-HSK vocabulary loaded into the same tables with `source = 'supplement'`; "local word" removed; `text_character` is a contextual gloss only.
- 2026-10-27 Progress import/export in one TSV format with declared timestamps; resolution latest-wins, tie to lowest, characters implied by words; `init` is the day-0 sequence.
- 2026-10-26 `lesson_expansion` becomes `lesson_extra_word` with a nullable `anchor` and stored `pinyin`; a one-character anchor is an expansion, anything else a related word. Its key is a unique expression index because SQLite forbids `coalesce` in a PRIMARY KEY.
- 2026-10-26 Only `tags` is editable from the app; author and period are edited in the text file.
- 2026-10-26 Intake gives a character the master lacks pypinyin's reading (`auto`); pypinyin is a main dependency. Numbered pinyin is converted to tone marks wherever a reading is accepted.
- 2026-10-27 The admin page is a shell plus htmx fragments (vendored htmx 2.0.4): every region has its own URL, a mutation returns the region it changed, a 422 swaps the form back with its message; no redirects, no page anchors.
- 2026-10-27 Words in text is the text's word list under filters (default: not yet reviewed); a checkbox per row includes it in the lesson, "Mark all shown as reviewed" sets origin manual; inline edit changes pinyin and gloss only, a word's level is set when it is created.
- 2026-10-27 The page follows the admin mockup: a gloss and level are edited inline only for characters the master lacks; notes are added and deleted, not edited; a lesson is created and renamed on the page and deleted through the data layer.
- 2026-10-28 An imported state's `changed_at` is the file's `as_of` date; the export writes dates only, so a state set on the page keeps its date but not its time across export and import.
- 2026-10-28 The admin page edits no character fact: a character the dictionary lacks is added to `data/supplement.tsv` (intake refuses the text until then) and a contextual character gloss is edited in the annotation file. The add forms' pinyin, gloss and level make the supplement entry; a word's `gloss` on a text or lesson is contextual only. `pinyin.guess` is gone: a supplement character's readings are the file's and pypinyin's.
- 2026-10-28 Progress rows carry `origin` (`auto` | `manual` | `import`); automatic rows yield to any other candidate at import, which is what lets intake's `exposed` coexist with an older imported `mastered`. The progress database gets the column in place — the one schema change not done by rebuilding.
- 2026-10-28 A reading typed on the page must be one of the character's listed readings; one that comes from a dictionary word or a file (origin `auto` or `suggested`) may also be the neutral-tone form of one (地上 gives 上 `shang`), which intake otherwise fails on.
- 2026-10-28 `character-gloss.tsv` is applied at build as well as baked by the derivation, so the dictionary page can edit an HSK character's gloss; HSK word meanings stay the master's and read-only. A blank `level` in the supplement means derived at load.
- 2026-10-16 No collection entity and no text status: a text with its annotations is the material and is always in flux; `lesson` groups texts later.
- 2026-10-16 Intake is deterministic and in-app; judgment comes from any outside AI tool via a prompt template producing the annotation file. No model calls in the app.
- 2026-10-16 Traditional for display via OpenCC `s2t` (pure-Python), overridable per text; the master's character column stays best-effort.
- 2026-10-16 Setting a character's reading replaces the existing override (the pull-down is the editor); every other duplicate add stays a no-op.
- 2026-10-18 清除 on a stored reading re-resolves that character's positions to the default (origin `auto`) rather than leaving them unread; a character the master lacks ends with no reading.
