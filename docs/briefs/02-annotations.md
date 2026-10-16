# Brief 02 — Annotations: admin curation of a text, persisted to data/

Read `CLAUDE.md` and `docs/design.md` (layer 3, "Annotations"). Brief 01 is done.
This brief makes the text page an admin tool: the owner marks characters for
study, links or declares words, creates expansions, and writes notes, and all
of it survives a rebuild through `data/annotations/<id>.json`.

Plain HTML forms with POST → redirect → GET. No JavaScript, no htmx yet.

## 0. Fix first

`db.find_words` must only form candidates inside maximal runs of Han characters,
so a window never spans punctuation or a line break (天\n江 must not become 天江).
Add a test with a two-line body and no end-of-line punctuation.

## 1. Schema (`schema.sql`)

```sql
text_character (text_id, char, gloss,            PRIMARY KEY (text_id, char))
text_word      (text_id, surface, word_id, gloss, PRIMARY KEY (text_id, surface))
text_expansion (text_id, char, surface, word_id, gloss, PRIMARY KEY (text_id, char, surface))
text_note      (id INTEGER PRIMARY KEY, text_id, anchor, note)
```
`word_id` references `word(id)`, nullable. CHECK on `text_word` and
`text_expansion`: `word_id IS NOT NULL OR gloss IS NOT NULL`. Foreign keys to
`text(id)` with ON DELETE CASCADE.

## 2. Annotation files

`data/annotations/<text id>.json`, format exactly as in `docs/design.md`. Keys in
that order, `ensure_ascii=False`, indent 2, trailing newline, lists sorted by
their natural key so a rewrite of unchanged content is byte-identical.

- `build` imports every file present; a file for an unknown text id is an error;
  `word_id` is resolved from `surface` (and from `surface` of an expansion). A
  surface that is neither in the master nor glossed is an error naming the file.
- Every successful admin save rewrites the file for that text from the database.
  A text with no annotations has no file (delete it if it exists).

## 3. Validation (in `db`, raised as one exception type with a Chinese message)

- `char` must be a single Han character present in the text body.
- `text_word.surface` must occur in the body. `text_expansion.surface` need not.
- Local word or expansion (no master match) requires a non-blank `gloss`.
- Duplicate of an existing row is a no-op, not an error.

## 4. Routes (all under `/texts/{id}`)

| Method, path | Form fields | Effect |
| --- | --- | --- |
| `POST …/characters` | `char`, `gloss?` | add to 学习字 |
| `POST …/characters/{char}/delete` | | remove |
| `POST …/words` | `surface`, `gloss?` | add word; links master if found |
| `POST …/words/{surface}/delete` | | remove |
| `POST …/expansions` | `char`, `surface`, `gloss?` | add expansion |
| `POST …/expansions/{char}/{surface}/delete` | | remove |
| `POST …/notes` | `anchor?`, `note` | add note |
| `POST …/notes/{note_id}/delete` | | remove |

Validation failure: HTTP 422, re-render the text page with the message at the
top and the submitted values kept. Success: 303 to `/texts/{id}`.

The server now opens the database read-write (it writes annotations). Keep the
connection-per-request pattern.

## 5. Text page (`text.html`) additions

- Above 字表: a **标注** section listing current 学习字 (with gloss), 词 (with
  拼音/级 when linked, gloss when present, dictionary meanings when linked), 扩展
  (char → word, same display), 注 (anchor, note). Each row has a 删除 button.
- 字表 rows gain two inline forms: 加入学习 (with optional gloss field) and 扩展
  (surface field + optional gloss, submit). Characters not in the master are
  still eligible for both.
- 词表 rows gain a 加入 button.
- Below 词表: an **添加词** form (surface, gloss) for words brute force didn't
  find, and an **添加注** form (anchor, note).

Keep the page legible: forms are small, one line each; this is an admin page,
not a student page.

## 6. Tests

Round trip: through the test client, add one of each annotation kind to text 1
(use 愁 as a study character with a gloss, 寒山寺 as a local word, 月→月亮 and
乌→乌鸦 as expansions, a note anchored on 月落乌啼); assert the JSON file matches
the documented format byte-for-byte for a fixed example; rebuild into a new
database with that `data/` directory; assert the annotations are present with
`word_id` resolved for 月亮 and 乌鸦 and null for 寒山寺. Validation cases: char
not in body, surface not in body, local word without gloss, duplicate add is a
no-op, delete removes the row and rewrites the file. The fix in §0.

Tests must not write into the real `data/annotations/`; build and save take the
data directory as a parameter already — use a copy under `tmp_path`.

## Acceptance

- On `/texts/1`: mark 愁, expand 月 to 月亮, add 寒山寺 with a gloss, add a note;
  reload; `cat data/annotations/1.json` shows all four; `chineselearning build`
  then reload shows the same page.
- `uv run pytest -q` passes.

## Not in this brief

Progress, collections, student mode, htmx or any JavaScript, inference-assisted
suggestions, editing an existing annotation in place (delete and re-add is fine),
pagination, authentication.
