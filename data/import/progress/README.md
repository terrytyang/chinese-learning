# Progress import

`raw/` holds the original documents as they were — spreadsheets, Word files,
plain lists. Each is transformed **once**, by hand or by any AI tool following
`docs/prompts/progress-import.md`, into one standard file here, named after it:
`raw/HSK1_Derived_Words.xlsx` → `HSK1_Derived_Words.tsv`. Both are committed.
The transform copies what the document says and looks nothing up.

A standard file:

```
# source: raw/2026-0830-single-characters.md
# as_of: 2026-08-30
# state: recognized
item	state	as_of	pinyin	gloss	level
司
班	mastered	2026-09-14
```

- Header `# as_of` and `# state` apply to every line that leaves those columns
  blank. A file with neither a header `as_of` nor one on every line is refused;
  the import run time is never used as a timestamp.
- `state`: exposed / recognized / mastered. `# state: none` (or no state at
  all) means the file carries dictionary entries only and says nothing about
  the student.
- `pinyin`, `gloss`, `level` are optional and matter only for items the
  dictionary does not have: they become the supplement entry.
- Anything missing that only the owner knows is written as `?` by the
  transform and filled in before import; the importer refuses `?`.

`chineselearning import-progress` reads every `.tsv` here and in
`data/progress/` (the exported snapshot), resolves each item's state by
timestamp (latest wins; on a tie the lowest state), implies a character's
state from the words containing it, adds unmatched items to
`data/supplement.tsv`, and prints a report. `--check` prints the report and
writes nothing. Re-running is a no-op.
