# Brief 05 — Character gloss overlay

Small. `data/character-gloss.tsv` is a curated overlay on the generated master:
`char<TAB>gloss`, `#` comment lines, rules in `docs/prompts/character-gloss.md`.
The master's `character` table now has a null `gloss` column for it.

1. `build` loads the file after `hsk.sql`: `UPDATE character SET gloss = ?
   WHERE char = ?`. Validate and fail naming the line: exactly two columns, the
   character exists in the master, gloss non-blank, no duplicate character,
   gloss at most 120 characters. Print how many characters have a gloss.
2. Show the gloss: a 释义 column in 字表 (after 拼音), and in `/api/characters`.
3. Tests: the committed file loads with 248 glosses; a bad line (unknown
   character, duplicate, blank) fails with the line named; 字表 for text 1 shows
   `moon, month` on 月.

Not in this brief: anything else.
