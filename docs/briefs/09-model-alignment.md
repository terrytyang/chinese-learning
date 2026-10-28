# Brief 09 — Align the app with the consolidated master and the settled model

Read `CLAUDE.md` and `docs/design.md` (layer 2 as rewritten; the decision log
entries dated 2026-10-25). Brief 08 is done. `data/hsk.sql` has changed shape
under the app; this brief brings the app back in step and lands the model
decisions that don't need the new page. No UI rework here beyond what the
model forces; brief 10 rebuilds the admin page.

Everything in `data/lessons/`, `data/annotations/` and `build/progress.sqlite`
is throwaway test data: delete and regenerate rather than migrate.

## 1. Master schema

- `word.readings` no longer exists; `alt_readings` (nullable JSON) holds the
  non-primary forms. Fix every reader (`db.find_words`, `material`,
  `annotations.load`, templates). Where the full list is wanted, it is
  `[primary] + alt_readings`.
- `character` gained `meanings`, `alt_readings`, `pos`, `frequency_rank`,
  `word_level`; expose them in `lookup_characters`, `/api/characters`, and the
  material structure.
- Remove the brief-05 TSV gloss loader from `build` and its tests; `gloss` now
  arrives in `hsk.sql`. `build` must not read `data/character-gloss.tsv`.

## 2. Single character = character

- Validation rejects a one-character surface in `text_word` and in lesson
  word tables with the message "a single character is a character; add it in
  Characters". `find_words` already scans 2–4.
- `progress.set_state` rejects `kind='word'` with a one-character key.

## 3. Learner states, no history

`progress.sql`: `progress (learner_id, kind, key, state, changed_at, PRIMARY
KEY (learner_id, kind, key))`, `state IN ('exposed','recognized','mastered')`.
No row = `unconfirmed`. `set_state` upserts; setting `unconfirmed` deletes the
row. `current()` and `state_of()` keep their signatures. Delete the existing
`build/progress.sqlite`; the schema is new.

Adding a character or word to a lesson (any route that does) sets `exposed`
when the current state is `unconfirmed`; nothing else changes state
implicitly.

## 4. Lesson-owned words with an anchor

Replace `lesson_expansion` with:

```sql
lesson_extra_word (lesson_id, surface, anchor, word_id, pinyin, hsk_level, gloss, origin,
                   PRIMARY KEY (lesson_id, surface, coalesce(anchor, '')))
```
`anchor` nullable; when given it must occur in the body. When `anchor` is a
single character, `surface` must contain it (that is an expansion). `word_id`
resolved from `surface`; `pinyin` prefilled from the master or from the
characters' readings; `hsk_level` only when unlinked (default 7); `gloss`
required when unlinked. Lesson file key `extra_words` replaces `expansions`,
sorted by `(anchor or "", surface)`. `material.assemble` returns `extra_words`
with a derived `kind`: `expansion` (one-character anchor) or `related`.
Existing admin routes and templates for expansions are adapted minimally to
the new table (brief 10 replaces them).

## 5. Intake and lessons

- Default lesson name: `Learn <title>`.
- Intake stores every brute-force word as a text fact (unchanged); the default
  lesson selects characters and words whose state is `unconfirmed` or
  `exposed`, not `recognized`/`mastered`.
- Intake prefills a reading for characters absent from the master with
  pypinyin (`origin = auto`); move `pypinyin` from the `tools` group to the
  main dependencies and run `uv lock`.
- A `pinyin.py` helper converts numbered pinyin (`ti2`, `lv4`) to tone marks;
  every place a reading or a word pinyin is accepted runs the input through it.
- Delete `data/lessons/*`, `data/annotations/*`, run `intake` on all five
  texts, commit the regenerated files.

## 6. Text header edits

Only `tags` is editable from the app. Remove author/period editing if brief 08
added it. The header rewrite touches the `tags:` line only.

## 7. English labels

Every label, heading, button, placeholder, badge and message in every template
and every Chinese-language exception message becomes English. Content stays
Chinese. State labels: unconfirmed / exposed / recognized / mastered; origin
badges: auto / suggested / manual; tabs and sections as in
`docs/mockups/admin-page.dc.html`. The student reader and `/learn` included.

## 8. Tests

Fix the two currently failing tests (gloss count; default lesson name). Add:
one-character surfaces rejected; state upsert and `unconfirmed` deletion;
exposed-on-add; `lesson_extra_word` validation (anchor in body, expansion
contains anchor, unlinked requires gloss); numbered pinyin conversion; intake
default selection excludes recognized/mastered; file round trips.

## Acceptance

- `chineselearning build` from the regenerated `data/`; `uv run pytest -q` passes.
- `/learn` and `/texts/1` render in English with content in Chinese.
- `data/lessons/1-1.json` is named "Learn 枫桥夜泊" and has an `extra_words` key.

## Not in this brief

htmx, the tabbed page, tag chips, pinyin edit mode, bulk selection, print,
exercises, styling.
