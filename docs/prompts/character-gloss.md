# Prompt: English glosses for characters

Use this with any AI tool to produce lines for `data/character-gloss.tsv`.
Generate the input with `python3 tools/gloss_context.py --min-level N --max-level N`
(or `--missing` for whatever has no gloss yet), paste the prompt below followed
by the TSV, and append the tool's output to the gloss file. Review before
committing: `chineselearning build` validates every line and names any problem.

---

You are writing one-line English glosses for Chinese characters, for a
seventh-grade heritage learner whose parent is a native speaker. Each gloss is
a quick reminder of what the character means when it appears in a text, not a
dictionary entry.

Input: a TSV with columns `char`, `readings` (most common first), `level`,
`edition`, `cedict` (meanings of the standalone dictionary entry per reading,
when one exists), `kdefinition` (Unihan's one-line definition). The last two are
context only; condense them, don't copy them.

Output: TSV, two columns, `char` then `gloss`, one line per input character, in
input order, no header, nothing else.

Rules for the gloss:

1. Short. At most about eight English words per reading; fewer is better.
   Separate senses with commas: `moon, month`.
2. Lead with the sense a student meets in common words and in classical texts.
   Drop surnames, place-name abbreviations, slang, dialect, radical numbers,
   "variant of", and chemistry/physics senses unless nothing else exists.
3. Split by reading only when the readings carry different meanings, and name
   the reading: `xíng: walk, go, OK · háng: row, line, firm`. One gloss with no
   reading label when the meanings are the same or the other readings are rare.
   Separator between readings is ` · ` (space, middle dot, space).
4. Grammar words get their function, briefly: `completed-action particle`,
   `question particle`, `measure word for people, things`. Write "measure
   word", never "classifier" or "numerary adjunct".
5. A character that mostly lives inside words gets the word in parentheses
   first: `(什么) what`, `(时候) time, moment`.
6. Plain words. No pinyin except as a reading label, no Chinese except a
   parenthesised word as in rule 5, no quotation marks, no trailing period.

Example output:

```
月	moon, month
行	xíng: walk, go, OK, all right · háng: row, line, firm
了	le: completed-action particle, change of state · liǎo: finish, understand
什	(什么) what
个	measure word (general), individual
```
