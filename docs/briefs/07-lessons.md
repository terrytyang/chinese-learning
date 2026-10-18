# Brief 07 — Lessons: the model, the files, intake, the lists

Read `CLAUDE.md` and `docs/design.md` — layer 3 was rewritten: text facts vs
lessons, stored readings. Briefs 01–06 are done. This brief changes the data
model and files and shows lessons in both lists. The admin page's rework
(pinyin edit mode, bulk selection, tag editing) is brief 08; here the admin page
only gains lesson create/rename/delete and keeps working on the default lesson.

## 1. Schema

Text facts (`data/annotations/<text>.json`):
- `text_reading (text_id, position, char, pinyin, origin, PRIMARY KEY (text_id, position))`
  — one row per Han position. The old nullable-position form is gone.
- `text_character (text_id, char, hsk_level, gloss, origin, PK (text_id, char))`
  — facts only; no longer means "selected for study".
- `text_word` unchanged.

Lessons (`data/lessons/<text>-<lesson>.json`):
- `lesson (id, text_id, name, UNIQUE (text_id, name))`
- `lesson_character (lesson_id, char, PK)`, `lesson_word (lesson_id, surface, PK)`
- `lesson_expansion` = the old `text_expansion` keyed by `lesson_id`
- `lesson_note` = the old `text_note` keyed by `lesson_id`
All with `ON DELETE CASCADE` from `lesson`, which cascades from `text`.
Drop `text_expansion` and `text_note`.

## 2. Files

Formats exactly as the two examples in `docs/design.md`. Readings sorted by
position; characters by char; words by surface; lesson characters and words
as sorted plain lists; expansions by `(char, surface)`; notes by `(anchor,
note)`. Write-through on every save, as now. A lesson file for a text id or
lesson id with no text is a build error; two lesson files claiming the same
lesson id, likewise. On import, a reading whose `char` differs from the body
at `position` is an error naming the file and position ("re-run intake").

Convert the two existing files (`data/annotations/1.json`, `3.json`) with a
one-off script run once and not committed: study characters → the default
lesson's characters; expansions and notes → the default lesson; per-character
glosses stay as text facts; readings become per-position rows. Create the
default lesson for every text (id order, named after the title) with the
intake default selection, as if intake had made it. Commit the resulting files.

## 3. Intake

`intake` now also stores a reading for every Han position (using the current
`readings_for` logic as the resolver, then persisting) and creates the default
lesson: `name` = title, characters = every unique Han character whose state is
not `mastered`, words = every `text_word`. `--force` redoes `auto` rows and
leaves lessons alone. `readings_for` is no longer called at view time.

## 4. Material

`assemble(conn, text_id, lesson_id=None, learner_id=1)`. Readings come from
`text_reading`. With `lesson_id`: `study` is the lesson's characters, `words`
and `highlight` are the lesson's words, `expansions` and `notes` the lesson's.
Without: `study`, `expansions`, `notes` are empty and `words`/`highlight` are
every text word (facts). Character glosses: `text_character.gloss` over
master. Add `lesson` (id, name) or null to the structure.

## 5. Pages

- `/learn`: under each text, its lessons as links (`/learn/{text}/{lesson}`),
  plus a 原文 link to `/learn/{text}`. Progress bar per lesson (over the
  lesson's characters), and per text (over all unique characters).
- `/learn/{text}` and `/learn/{text}/{lesson}`: the reader, same toggles.
- `/texts`: lesson names under each title, linking to `/texts/{text}?lesson=`.
- `/texts/{text}`: a 课程 block at the top: the lessons as links, the current
  one marked, 新建 (name field), 重命名, 删除 (only when the lesson is empty).
  `?lesson=<id>` selects which lesson the 学习字 / 词 / 扩展 / 注 sections edit;
  default is the lowest id. Existing forms keep working, now writing to the
  selected lesson; "加入学习" adds to the lesson's characters, 词's 加入 to the
  lesson's words. The reading pull-down stays as is for now (brief 08 replaces
  it) but writes per-position rows: setting a reading from the 字表 applies to
  every position of that character.

## 6. Tests

Build from the converted files; both lesson files load; a reading mismatch
fails naming position; intake on a fresh copy creates the default lesson with
the expected characters (text 1: 28 unique, minus any mastered in the fixture
progress file) and all words; `assemble` with and without a lesson; both lists
show lessons; create/rename/delete lesson; delete refused when non-empty;
round trips byte-identical.

## Acceptance

- `/learn` shows 枫桥夜泊 with lesson 枫桥夜泊 and 原文; both open.
- `/texts/1`: create lesson "一级字", open it, add 月 to it; `data/lessons/1-2.json`
  exists with `["月"]`; `/learn/1/2` highlights only that.
- `uv run pytest -q` passes.

## Not in this brief

Pinyin edit mode, bulk selection, tag editing, print, exercises, JavaScript.
