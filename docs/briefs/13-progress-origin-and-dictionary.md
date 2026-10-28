# Brief 13 — Progress origin and the dictionary page

Read `CLAUDE.md`, `docs/design.md` (layer 2's gloss paragraph and layer 4 as
rewritten), `docs/mockups/dictionary-page.dc.html` (the page: match it) and
`docs/mockups/README.md`. Brief 12 is done and the Copilot fix to lesson 1-1 is
committed. Nothing in this brief touches the text admin page except its nav line.

## 1. Origin on progress rows

Brief 12's dry run showed the flaw: intake's automatic `exposed` (dated today)
outranks an imported `mastered` (dated September) under latest-wins. Fix:

- `progress.sql`: `origin TEXT NOT NULL CHECK (origin IN ('auto', 'manual',
  'import'))`. Because this is the one database that is never rebuilt,
  `db.connect` adds the column to an older file after applying the schema:
  `ALTER TABLE progress.progress ADD COLUMN origin TEXT NOT NULL DEFAULT
  'import'`. Say so in the SQL file's comment; it is the project's only in-place
  schema change.
- `progress.set_state(..., origin)` — required argument. The pages pass
  `manual`; `progress.expose` (intake, adding to a lesson) passes `auto`; the
  importer passes the entry's origin.
- Resolution (`progress_import.resolve`): candidates are built as before, each
  carrying an origin — a file entry's `origin` column (blank = `import`), an
  implied-by-word candidate takes the word entry's origin, the database row its
  own. If any candidate is not `auto`, the `auto` ones are dropped; then latest
  `as_of`, tie → lowest. `why` names the origin.
- File format (`data/import/progress/README.md`): an optional seventh column
  `origin` (`auto` | `manual` | `import`; blank or absent = `import`); any other
  value is an error naming the line. `export-progress` writes columns `item
  state as_of origin`, so a round trip preserves origin. Add to the README,
  while there, that a blank `level` in `supplement.tsv` and in an import line
  means *derived at load* (a character 7, a word the highest of its characters).

## 2. The gloss file applied at build

So the dictionary page can edit a character's gloss without regenerating
`hsk.sql`: `db.build` applies `data/character-gloss.tsv` after `hsk.sql` and
before the supplement — `UPDATE character SET gloss = ? WHERE char = ?` per
line; a line for a character the master lacks is an error naming the line.
Today's result is unchanged because the derivation bakes the same file.
`tools/derive_hsk.py` is not touched. A small module `gloss_file.py`: `read`,
`apply(conn, data_dir)`, `update(conn, data_dir, char, gloss)` — rewrites that
one line in place, order and the rest of the file byte-identical, and the row.
A gloss is non-empty with no tab or newline; the prompt's style rules are not
enforced. `CLAUDE.md`'s layout line becomes "`character-gloss.tsv` (curated,
applied at build)".

## 3. The dictionary page

`GET /dictionary`: a shell plus fragments, the mockup's layout.

- Nav. The admin shells (`/texts`, `/texts/{id}`, `/dictionary`) get the
  mockup's top line — `Texts · Learn · Dictionary`, current page bold; `Learn`
  is `/learn`. The text page keeps the rest of its header. Student pages get
  nothing.
- Header counts: characters (all sources), HSK words, supplement entries,
  "without a gloss" (characters with a null gloss plus supplement words with no
  gloss).
- Filters live in the URL query: `q`, `kind` (all | character | word), `source`
  (all | hsk | supplement), `min`, `max` (1–7), `state` (any | unconfirmed |
  exposed | recognized | mastered), `nogloss` (1). Defaults as the mockup: all,
  all, 1–7, any, off. The filter form is `hx-get /dictionary/rows` with
  `hx-push-url`, triggered on change, and for `q` on keyup after 300 ms.
- `GET /dictionary/rows`: one query over the union of `character` and `word`
  (item, pinyin, level, source, gloss, kind) under the filters; `q` is a
  case-insensitive substring of the item, the stored pinyin or the gloss;
  `state` joins progress (`unconfirmed` = no row). Order: level, then item.
  Cap at 200 rows; the count reads "37 shown" or "200 of 1,234 shown — narrow
  the filters".
- A row, as the mockup: item, primary pinyin, level (7 shown as 7–9), source
  pill, gloss, the four state buttons, Edit. Gloss column: a character's
  `gloss`; an HSK word's `meanings` joined with `; `; a supplement word's
  gloss. Empty → italic "no gloss yet". Reuse the text page's state-control
  markup so the two pages match.
- `POST /dictionary/state` (`item`, `state`) → `set_state` with origin
  `manual` (`unconfirmed` deletes) → the row fragment.
- Edit. `GET /dictionary/row/{item}?edit=1` returns the row as a form: an HSK
  character edits gloss only (pinyin and level shown fixed); a supplement
  character edits pinyin, gloss, level (1–7); a supplement word edits pinyin,
  gloss, level (1–7 or "derived" = blank). An HSK word has no Edit button —
  its meanings are the master's (the mockup shows Edit on every row; that is
  the one place it is wrong). `POST /dictionary/row/{item}` saves through
  `gloss_file.update` or `supplement.update` — file and row — and returns the
  row; invalid → 422 with the form and the message, the existing convention.
  Cancel is `GET /dictionary/row/{item}`.
- Add. `POST /dictionary/lookup` (`item`) returns the add card: in the
  dictionary → "Already in the dictionary" with a link to `/dictionary?q=item`;
  absent → the details form with pinyin prefilled from pypinyin (the text
  page's add forms do this already), gloss blank, level "derived".
  `POST /dictionary/add` (`item`, `pinyin`, `gloss`, `level`) → `supplement.add`
  → the add card reset with "Added to the supplement" and, out of band, the rows
  region for `q=item`. A word with a character the dictionary lacks → 422 with
  `supplement.add`'s message.

## 4. Tests

- Origin: an `auto` database row dated today loses to an `import` entry dated
  earlier; a `manual` row dated later than an import entry wins; implied-by-word
  candidates carry the word's origin; a file with an invalid origin errors
  naming the line; export → import round-trips origin; opening a progress file
  without the column adds it with `import` and keeps every row.
- Gloss file: `build` gives 月 the same gloss as before; `update` rewrites one
  line and leaves the file otherwise byte-identical; an unknown character
  errors.
- Dictionary: rows under each filter; the cap; `q` by item, pinyin and gloss;
  state POST writes `manual` and returns the row; editing an HSK character's
  gloss writes the TSV; editing a supplement word's pinyin and level writes
  `supplement.tsv`; an HSK word's edit route → 422 "not editable"; lookup for
  a known and an unknown item; add → supplement row and file; add with a
  missing character → 422 naming it.

## Acceptance

- `uv run chineselearning init --fresh`, then on `/dictionary`: `q=乌` shows
  乌, 乌云, 乌鸦; mark 乌鸦 recognized — the row updates and the progress row
  has origin `manual`; edit 乌鸦's gloss — `data/supplement.tsv` changes that
  line only; edit 月's gloss and put it back — `git diff
  data/character-gloss.tsv` is empty; `export-progress` writes the origin
  column; `import-progress --check` with the HSK 1 files reports no changes.
- The existing `build/progress.sqlite` opened by the new code gains the column
  and loses nothing.
- `uv run pytest -q` passes; no server is left on port 8000.

## Not in this brief

The text-import form and `intake --reset` (brief 14); a styling pass;
pagination beyond the cap; anything on the student pages.
