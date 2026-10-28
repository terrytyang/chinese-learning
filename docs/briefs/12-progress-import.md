# Brief 12 — Progress import and export, and the day-0 sequence

Read `CLAUDE.md`, `docs/design.md` (layer 4 as rewritten, "Day-0"),
`data/import/progress/README.md` (the file format — authoritative) and
`docs/prompts/progress-import.md`. Brief 11 is done. The three raw documents
in `data/import/progress/raw/` are NOT to be transformed by this brief; the
owner does that. Build the machinery and test it on fixtures.

## 1. Parsing

`progress_files.read(path) -> list[Entry]` for a standard file: header keys
`source`, `as_of`, `state` (optional `none`); columns `item state as_of pinyin
gloss level`. Rules from the README: per-line values override the header; a
line with no `as_of` from either source is an error naming the line; `?`
anywhere is an error; state ∉ {exposed, recognized, mastered} is an error
(`none` only in the header, meaning the file carries no state); items are
converted to simplified with OpenCC `t2s` and the conversion reported;
duplicates within a file are allowed (the resolution handles them).

## 2. Resolution

`progress_import.resolve(conn, entries) -> dict[(kind, key) -> (state, as_of,
why)]`:
- `kind` by length (single character = character).
- Candidates for an item: its explicit entries; for a character, every entry
  of a word containing it (state and `as_of` of that word); and the current
  row in `progress.progress` (state, `changed_at`).
- Winner: latest `as_of`; on a tie, the lowest state (unconfirmed < exposed
  < recognized < mastered). `why` records which candidate won and from which
  file, for the report.
- Entries with no state (header `none`) contribute nothing to resolution but
  still go through matching (§3).

## 3. Matching and the supplement

Every item is looked up in the dictionary (`db.lookup_character` /
`db.lookup_word`). Unmatched items are added to the supplement via
`supplement.add` with the entry's `pinyin`/`gloss`/`level` when present
(pinyin otherwise from pypinyin, gloss blank, level derived), and listed in
the report under "added to supplement" with a count of those still without a
gloss. In `--check` mode nothing is added; they are listed as "would add".

## 4. Commands

- `chineselearning import-progress [--check] [--learner 1] [FILE...]`: with no
  files, reads `data/progress/*.tsv` then `data/import/progress/*.tsv`. Writes
  the resolved states with `changed_at = as_of` (upsert; a resolved
  `unconfirmed` deletes). Prints the report: files read, entries, conversions,
  changes grouped by transition (unconfirmed→exposed …), unchanged, downgrades
  (with the winning file), supplement additions. Exit non-zero on any file
  error, having written nothing.
- `chineselearning export-progress [--learner 1]`: writes
  `data/progress/<learner slug>.tsv` with header `# source: export`, columns
  `item state as_of` from `progress` ordered by key; `as_of` = `changed_at`'s
  date. Byte-identical when nothing changed.
- `chineselearning init [--fresh]`: `--fresh` deletes `build/`; then `build`,
  `import-progress`, `intake --new`. Prints each step's summary.

## 5. Tests

Fixtures under `tests/fixtures/progress/`: a plain list with header
`as_of`/`state`; a sheet-like file with per-line states and dates; a
`state: none` dictionary-only file; a traditional-script file; a file with
`?`; a file with a line lacking any date. Assert: parsing and each error;
resolution — explicit vs implied by timestamp, tie → lowest, DB row as a
candidate, a character implied by two words; idempotence (second run changes
nothing); `--check` writes nothing; unmatched → supplement with the file's
gloss; export then import round-trips to the same states; `init --fresh` on a
copy of `data/` produces a working content database, a progress database and
lessons for all texts.

## Acceptance

- Create a two-line standard file by hand for 月 (mastered, 2026-09-01) and
  银行 (recognized, 2026-10-01); `import-progress --check` reports 月, 银, 行
  and 银行 with the states the rules give; without `--check` the admin page
  shows them; `export-progress` writes the snapshot; `init --fresh` rebuilds
  everything and the states are still there.
- `uv run pytest -q` passes.

## Not in this brief

Transforming the raw documents; the dictionary page; marking state from a
dictionary page; a UI for import.
