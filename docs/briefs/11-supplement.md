# Brief 11 — The supplement: one dictionary, two sources; no local words

Read `CLAUDE.md` and `docs/design.md` (layer 2 "source", layer 3 facts table,
decision log 2026-10-27). Brief 10 is done. `data/hsk.sql` now carries a
`source` column on both tables, and `data/supplement.tsv` exists with 15
characters. This brief loads the supplement, removes the "local word" concept,
and adds `intake --new`.

## 1. Load the supplement at build

After `hsk.sql`, `build` reads `data/supplement.tsv` (`item  pinyin  gloss
level`, `#` comments) and inserts rows with `source = 'supplement'`,
`hsk_edition = 'none'`:

- one character → `character`: `id` = code point, `readings` = pypinyin list
  (the file's `pinyin` first if given), `pinyin` = first reading, `gloss`,
  `hsk_level` = `level` or 7, everything else null.
- longer → `word`: `id` = 10,000,000 + line index, `simplified`, `traditional`
  via OpenCC, `pinyin` = the file's or the characters' primary readings joined,
  `meanings` = `[gloss]` or `[]`, `hsk_level` = `level` or the highest
  `hsk_level` among its characters (a character not in the dictionary counts
  7), `pos`/`frequency_rank`/`alt_readings` null.

Validate, failing with file and line: item already in the HSK master; duplicate
item; blank item; level outside 1–7; a word whose characters are not all in
the dictionary after the supplement is loaded (list them). A blank gloss is
allowed and counted; `build` prints "N supplement entries, M without a gloss".

A write-through helper `supplement.add(conn, data_dir, item, pinyin, gloss,
level)` appends a line to the file (sorted by nothing; append) and inserts the
row, returning its id; `supplement.update(...)` for pinyin/gloss/level on an
existing supplement row rewrites the line. These are the only writers.

## 2. No local words

- `text_word.word_id` and `lesson_extra_word.word_id` become `NOT NULL`; drop
  `hsk_level` from both and the `word_id OR gloss` CHECKs. `text_word.pinyin`
  stays as a contextual override. `text_character` keeps only `char`, `gloss`,
  `origin` (drop `hsk_level`).
- Every add path (admin words tab, expansions, related words, intake's
  unmatched characters) that used to create an unlinked row now calls
  `supplement.add` first when the dictionary lacks the item, then links. The
  two-step forms stay as they are from the user's side; the second form's
  fields (pinyin, gloss, level) feed `supplement.add`.
- Intake no longer creates `text_character` rows for missing characters; a
  character the dictionary lacks after the supplement is loaded is an intake
  error naming it ("add it to data/supplement.tsv"). Readings for supplement
  characters come from their `readings`.
- Annotation files: `characters` entries lose `hsk_level`; `words` lose
  `hsk_level`; lesson `extra_words` lose `hsk_level`. Regenerate the five
  texts' files (`intake --force` for all) and commit them; the existing
  `auto` character rows (啼, 枫, 鸯, …) disappear since the supplement covers
  them.

## 3. Lookup

`db.lookup_word(conn, surface)` and `db.lookup_character(conn, char)` return
the row from either source; the admin "Look up" uses them. `material` and the
reader treat supplement rows exactly like HSK rows; the reader's level tint
uses `hsk_level` as always, so supplement words tint by their derived level.

## 4. `intake --new`

`chineselearning intake --new` runs intake for every text with no facts and
no lesson; prints which. `intake <id>` unchanged.

## 5. Tests

Supplement loads (15 characters, 0 words) with derived levels; a word line
derives its level from its characters; validation cases; `supplement.add`
round-trips file and row; adding a non-dictionary word from the admin forms
creates the supplement entry and the link; intake refuses an unknown
character; `--new` picks only texts without files; the regenerated files
round-trip byte-identical.

## Acceptance

- `chineselearning build` reports 15 supplement entries; `/learn/1` shows 啼
  with pinyin tí and gloss "cry, crow (of birds), weep" on hover.
- In the admin page add 寒山寺 as a word in text 1 with a gloss: a line appears
  in `data/supplement.tsv`, `text_word.word_id` is set, the word shows level 7.
- `uv run pytest -q` passes.

## Not in this brief

Progress import/export, `init`, the dictionary page, editing supplement
entries from the UI beyond the add forms.
