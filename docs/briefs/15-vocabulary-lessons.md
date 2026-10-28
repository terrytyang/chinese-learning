# Brief 15 — Vocabulary lessons

Read `CLAUDE.md` and `docs/design.md` (layer 3 "Lessons" and layer 4 as
rewritten for vocabulary lessons; the decision log's 2026-10-28 lines). Brief 14
is merged. There is no mockup for the lesson page: it follows the dictionary
page's row style, and the owner will react to it once it exists.

## 1. A lesson without a text

- `schema.sql`: `lesson.text_id` nullable. Names are unique per text and
  unique among lessons with no text; `UNIQUE (text_id, name)` does not do the
  second (NULLs are distinct), so `_check_name` enforces it.
- `lessons.create(conn, None, name)` makes a vocabulary lesson. The default
  name is `Vocabulary <today, YYYY-MM-DD>`, then `Vocabulary <date> (2)`, `(3)`
  … when taken; `lessons.default_name(conn)` returns the next free one.
- Members: for a lesson with no text, `add_character` requires the character
  to be in the dictionary and `add_word` requires the surface to be a
  dictionary word (HSK or supplement) — the text checks apply only when there
  is a text. `add_extra_word` refuses on a vocabulary lesson ("a vocabulary
  lesson's words are members; add it as a word"); notes are allowed, anchor
  null.
- Files: `data/lessons/<lesson id>.json` when `text_id` is null (`"text_id":
  null` in the content). `write_files` for a vocabulary lesson writes that one
  file; `import_all` accepts both name shapes and checks each against the
  content. Deleting an empty vocabulary lesson removes its file.
- State: adding sets `exposed` from `unconfirmed` as before. Removing an item
  from any lesson, when its row is `exposed` with origin `auto` and no other
  lesson (text or vocabulary) holds it, sets it to `unconfirmed`.
- `progress.set_state` with the current state again: when the origin differs,
  update `origin` and `changed_at`; when both match, no-op as now. So a page
  click on the lit button turns an `auto` row `manual`.

## 2. Dictionary page additions

- **Add all shown to ▾.** In the results card's header line, next to "N
  shown": a select listing the vocabulary lessons (newest first) plus "New
  lesson…", and a button "Add all N shown". `POST /dictionary/add-to-lesson`
  with the filter fields and `lesson` (an id, or `new`): adds every row the
  filters produce, up to the cap — the same rows the page shows — creating the
  lesson with the default name when `new`; duplicates are no-ops. The response
  is the results card again with a line "Added 37 to Vocabulary 2026-10-28 ·
  Open →" (the link to `/lessons/{id}`), and the select now showing that
  lesson. Characters go through `add_character`, words through `add_word`;
  the lesson file is written once at the end.
- **Changed.** A new filter: operator select `any | on | before | on or before
  | after | on or after` and a date. For the four comparisons the date is an
  `<input type="date">`; for `on` it is a select of the distinct dates in the
  learner's progress table, newest first, each with its count — swapped in by
  htmx when the operator changes (`GET /dictionary/changed-dates`). Applies
  to the date part of `changed_at`; `unconfirmed` rows match only `any`.
  Parameters `changed` and `date` in the URL like the other filters.
- The search box triggers on `input` rather than `keyup`. The pushed URL is
  `/dictionary?…` (set `HX-Push-Url` on the rows response) rather than
  `/dictionary/rows?…`.

## 3. The lesson page

`GET /lessons/{id}`, admin shell (nav: `Texts` current), for a lesson with no
text. For a text lesson it renders one line, "This lesson belongs to 〈title〉",
linking to `/texts/{text}?lesson={id}`; no redirect.

- Header: the name, editable inline (`POST /lessons/{id}/name`, returns the
  header fragment, 422 on a duplicate); the count of characters and words.
- Members: two tables, Characters and Words, rows in the dictionary page's
  style — item, pinyin, level, source pill, gloss, current state — and a
  Remove button per row (`POST /lessons/{id}/remove`, returns the members
  fragment). Order: level, then item.
- **Mark all as ▾ ‹state›** with a button, under the members: `POST
  /lessons/{id}/mark` raises every member whose state is below the chosen one
  to it (origin `manual`, now) and leaves the rest; the response is the members
  fragment with a line "12 raised to recognized, 3 already there". Help text
  beside it: "raises items below this state; higher states are kept".
- Notes: the text page's Notes fragment reused, without anchors.
- `/texts` lists vocabulary lessons in a section under the texts table, newest
  first, each linking to its page, with a "New lesson" button that creates one
  with the default name and returns the section (the page then links to it).

## 4. Tests

- Create: default names on a day with none, one, two lessons; a duplicate name
  → error; file written as `<id>.json`; `build` on a copy of `data/` with such
  a file loads it; `import_all` rejects a text-prefixed name on a text-less
  file and vice versa.
- Members: a dictionary word adds; a non-word → error; `add_extra_word` →
  error; removal undoes an `auto` exposure only when no other lesson holds the
  item, never a `manual` or `import` row.
- `set_state` same state, different origin → origin and date change; same
  origin → nothing.
- Add all shown: with a filter yielding N rows, the lesson has N members and
  the file lists them; `new` creates and names; a second add of the same rows
  changes nothing.
- Changed filter: each operator against rows with known dates; the distinct
  dates endpoint lists dates with counts.
- Lesson page: members fragment, remove, rename (and a 422 on duplicate), mark
  all (raised vs. kept counts; a `mastered` member untouched when marking
  `recognized`), a text lesson's id renders the link line.

## Acceptance

- On `/dictionary`, filter words, HSK 2, unconfirmed; "Add all N shown" to a
  new lesson; the line names `Vocabulary 2026-…`; open it; remove two; "Mark
  all as recognized" raises the rest; `export-progress` shows them with
  today's date and origin `manual`; the two removed are `unconfirmed` again;
  `data/lessons/<id>.json` lists exactly the remaining members; `build` from
  `data/` reproduces the lesson.
- The Changed filter with `on` lists today's date with the right count.
- `uv run pytest -q` passes; no server is left on port 8000.

## Not in this brief

The Excel export (brief 16); vocabulary lessons on the student pages;
gamification; per-row membership markers on the dictionary page.
