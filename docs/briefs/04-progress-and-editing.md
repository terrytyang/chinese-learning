# Brief 04 — Learner progress, edit-in-place, levels for local words

Read `CLAUDE.md` and `docs/design.md` (layer 4 "Learner", the annotation table).
Briefs 01–03 are done. This brief adds the student's state per character and
word in its own database file, lets the admin edit annotations instead of
deleting and re-adding, and closes three gaps on the admin page.

Still plain HTML forms, no JavaScript.

## 1. Progress database

`src/chineselearning/progress.sql`, applied with `CREATE TABLE IF NOT EXISTS`
on open — this file is never repaved, so "create if missing" is the whole
schema story. Path from `CHINESELEARNING_PROGRESS`, default
`build/progress.sqlite`; `build` never touches it.

```sql
learner  (id INTEGER PRIMARY KEY, name TEXT NOT NULL)
progress (id INTEGER PRIMARY KEY, learner_id REFERENCES learner(id),
          kind TEXT CHECK (kind IN ('character','word')), key TEXT NOT NULL,
          state TEXT CHECK (state IN ('unrecognized','recognized','mastered')),
          changed_at TEXT NOT NULL)   -- ISO 8601 UTC, append-only
```
`key` is the character itself or the word string (works for local words).
Current state = the latest row per `(learner_id, kind, key)`; absent = `unrecognized`.
On first open, create learner 1 named `学生` if the table is empty. The app
serves learner 1; `learner_id` is carried everywhere so a second learner is a
row, not a redesign.

Open it by `ATTACH DATABASE ? AS progress` on the content connection in
`db.connect` (parameter `progress_path`), so one connection serves a request
and queries can join across. Tests pass a `tmp_path` progress file.

## 2. State on the admin page

- 字表: a 状态 column showing the current state (未识 / 认识 / 掌握) and three
  small buttons to set it (`POST …/progress` with `kind`, `key`, `state`;
  303 back). Same column and buttons on the 标注 → 词 and 扩展 tables (key =
  surface).
- A `?hide_mastered=1` toggle: a one-checkbox GET form at the top of the page;
  when set, 字表 rows and 词/扩展 rows whose key is `mastered` are omitted and
  the counts line reads `N 字（已掌握 M 个已隐藏）`. Links on the page preserve
  the parameter.
- A `kind`/`key` whose state is set to its current state is a no-op (no row).

## 3. Edit in place

Each row in 学习字, 词, 扩展, 注 gets a 编辑 button that re-renders the page with
that one row as an inline form (`GET …?edit=<kind>:<key>`; the key encoded as
the delete routes encode it), prefilled, with 保存 and 取消. Save is
`POST …/<kind>/<key>/update` with the editable fields:
- character: `gloss`
- word: `pinyin`, `gloss`, `hsk_level` (only for a local word)
- expansion: `surface`, `gloss`, `hsk_level` (only when unlinked). Changing
  `surface` re-resolves `word_id`; the natural key changes, so delete+insert
  inside one transaction.
- note: `anchor`, `note`
Editing a row sets its `origin` to `manual`. Validation as for add; failure is
422 with the form still open and the message.

## 4. Levels for local words

`hsk_level INTEGER CHECK (1 <= hsk_level <= 7)` on `text_word` and
`text_expansion`, null when `word_id` is set (the master's level applies).
添加词 and the 扩展 inline form get a 级 pull-down, 1–7, default 7, shown only
for the local case where the UI can know it (添加词 always shows it; ignore the
value when the surface resolves to a master word). In the annotation file,
`hsk_level` is present only for unlinked rows. The page shows the level from
whichever applies.

## 5. Pinyin for characters absent from the master

In 字表, a character with no master entry gets a free-text pinyin input in the
reading cell (instead of the pull-down), posting to the existing
`…/readings` route; validation already accepts any non-blank reading for such
a character. After setting, the cell shows it with source 指定 and a 清除 button.

## 6. Housekeeping

- Replace the `httpx` dev dependency with `httpx2` (Starlette's test client now
  wants it) and run `uv lock`.
- Rebuild the design doc's file example only if a field name here differs from it.

## 7. Tests

Progress: default state is `unrecognized`; setting writes a row with a UTC
timestamp; setting the same state again writes nothing; latest row wins;
`build` leaves the progress file untouched; `hide_mastered` omits exactly the
mastered rows and adjusts the counts. Edit: each kind round-trips through the
form and the annotation file, origin becomes `manual`, invalid edit keeps the
form open with 422, expansion surface change re-resolves. Local word level
stored, exported, shown, absent for linked rows. Missing-character pinyin set
and cleared.

## Acceptance

- On `/texts/1`: mark 月 掌握, tick 隐藏已掌握, 月 disappears from 字表 and
  the counts say so; `build/progress.sqlite` has one row; `chineselearning
  build` and the page still shows 月 as 掌握.
- Edit 寒山寺's gloss in place; `data/annotations/1.json` reflects it.
- Give 枫 a reading; it shows with 指定.
- `uv run pytest -q` passes.

## Not in this brief

Student mode, OpenCC, the prompt template, attempts/exercises, htmx, lessons,
per-position reading overrides in the UI, styling.
