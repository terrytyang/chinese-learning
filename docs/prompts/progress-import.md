# Prompt: raw progress document → standard import file

Use this with any AI tool, once per file in `data/import/progress/raw/`. The
output goes to `data/import/progress/<same stem>.tsv` and is reviewed before
`chineselearning import-progress` reads it (see the README there).

---

You are transcribing a document that lists Chinese characters or words a
student has studied, into a tab-separated file. Copy what the document says.
Look nothing up, infer nothing about the student, and invent no dates.

Output: one file, UTF-8, tab-separated, in exactly this shape:

```
# source: raw/<the document's file name>
# as_of: <a date the document states for the whole batch, else ?>
# state: <exposed | recognized | mastered | none — only if the document states it for the whole batch, else ?>
item	state	as_of	pinyin	gloss	level
<one line per character or word>
```

Rules:

1. `item` is the character or word in simplified Chinese. Convert traditional
   forms. Strip numbering, punctuation, spaces, pinyin and glosses that sit in
   the same cell. One item per line; do not split a word into characters or
   join characters into a word.
2. Fill `state` and `as_of` on a line only when the document gives that
   information for that line (a date column, a status column, a tick). Map the
   document's own terms to our three states only if the mapping is obvious
   (✓ in a "mastered" column → mastered); otherwise leave the line blank and
   put `?` in the header so the owner decides.
3. Carry `pinyin`, `gloss` and `level` when the document has them for that
   line; leave blank otherwise. Pinyin is lowercase with tone marks (`liú`,
   not `Liú` or `liu2`). Level is 1–7 (write 7 for 7–9); a dash or
   "not HSK" is blank.
4. Keep every item, including ones that look trivial or duplicated across the
   document; the importer deduplicates.
5. No other columns, no comments beyond the three header lines, no blank
   lines, a single trailing newline.

Example output for a plain list with a date at the top and no states:

```
# source: raw/2026-0830-single-characters.md
# as_of: 2026-08-30
# state: ?
item	state	as_of	pinyin	gloss	level
司
班
```
