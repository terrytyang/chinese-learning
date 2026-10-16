# Brief 03 — Intake: pre-populated annotations, origin, readings, status

Read `CLAUDE.md` and `docs/design.md` ("Intake", the annotation table, the
reading resolution order). Briefs 01–02 are done. This brief moves discovery
from view time to a one-time `intake` step, adds provenance to every annotation,
lets the admin fix a character's reading in a text, and gates texts by status.

Still plain HTML forms, no JavaScript.

## 1. Schema and files

- `origin TEXT NOT NULL CHECK (origin IN ('auto','suggested','manual'))` on
  `text_character`, `text_word`, `text_expansion`, `text_note`.
- `text_word.pinyin TEXT` nullable: a local word's reading, or a contextual
  correction of a linked word's.
- New `text_reading (text_id, char, pinyin, position INTEGER, origin, PRIMARY KEY
  (text_id, char, coalesce(position, -1)))` — use a generated column or a
  unique index expression, whichever is cleaner in SQLite. `position` is the
  0-based index into the body when the override applies to one occurrence only;
  null means every occurrence. This brief's UI sets only the null form.
- `text.status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','ready'))`,
  from an optional `status` header key in the text file.
- Annotation file: every row gains `"origin"`; words gain `"pinyin"`; a new
  `"readings"` list of `{char, pinyin, position, origin}` sorted by `(char,
  position)`. Key order: `text_id, characters, words, expansions, readings,
  notes`. On import, a missing `origin` defaults to `manual`.

## 2. Validation additions

- `text_reading.pinyin` must be one of that character's `character.readings`
  (exact string); if the character is not in the master, any non-blank value.
  Message names the character and lists the allowed readings.
- `text_word.pinyin`, when given, must be non-blank. For a local word, if absent,
  prefill from the characters' primary readings joined by spaces (resolution
  order applies per character) and store it, so every word has a reading.
- `position`, when given, must index a `char` in the body.

## 3. `chineselearning intake <text id> [--force]`

One-time. Refuses with a message if the text already has any annotation rows,
unless `--force`, which first deletes rows with `origin = 'auto'` only.
Inserts, as `auto`: a `text_word` for every brute-force match (the existing
`find_words` logic; `pinyin` null since the master supplies it) and a
`text_character` for every character absent from the master (gloss null).
Writes the annotation file. Prints counts. Accept `--db` and `--data` for tests.

## 4. Reading resolution (one function, used by the page and later by every
presentation)

`readings_for(conn, text_id) -> list[dict]`: for each character position in the
body, `{char, pinyin, source}` where `source` is `override`, `word:<surface>`,
`primary`, or `none` (not in master, no override). Order: `text_reading` with
matching position > `text_reading` with null position > a `text_word` whose
surface covers this position (leftmost-longest when several do; take the
reading's syllable for this character's offset within the word, from the
word's `pinyin` split on spaces when the syllable count equals the surface
length, else fall back) > `character.pinyin` > none.

## 5. Admin page changes

- 词表 (computed candidates) is removed. The 标注 → 词 table is the list,
  each row showing an `origin` badge (自动 / 建议 / 手动) and, for `auto` and
  `suggested`, a 确认 button that sets `manual`. Same badge and button on 学习字,
  扩展, 注.
- 字表: the 拼音 column shows the resolved reading and its source in small text
  (默认 / 由「银行」确定 / 指定). When `character.readings` has more than one
  entry, the cell is a form: a `<select>` of the readings, current one selected,
  and a 设定 button posting to `POST …/readings` with `char`, `pinyin`. A 清除
  button appears when an override exists (`POST …/readings/{char}/delete`).
- 添加词 gains a `pinyin` field (optional).
- The header shows 状态 (草稿 / 可用).
- `/texts`: a 状态 column and filter.

## 6. Routes added

`POST …/readings` (`char`, `pinyin`), `POST …/readings/{char}/delete`,
`POST …/{kind}/…/confirm` for the four annotation kinds, mirroring the delete
routes' paths.

## 7. Tests

Intake on a copy of `data/` under `tmp_path`: text 1 yields 2 auto characters
(啼, 枫) and 0 words; text 5 yields the same words `find_words` found, all
`auto`; the file has `origin` on every row; rerun refuses; `--force` removes
only auto rows and keeps a manual one. Reading resolution on text 5 for 舍 in
便舍船: primary gives shě; after an override to shè, `source == "override"`;
for 银 in a text containing the linked word 银行 (use a fixture body), the
source is `word:银行` and the reading háng for 行. Confirm flips origin.
Invalid reading rejected with the allowed list in the message. `status` header
parsed; `/texts?status=ready` filters. Round trip through build still
byte-identical.

## Acceptance

- `chineselearning intake 5` then `/texts/5`: 词 list populated with 自动
  badges; 字表 shows readings with sources; 舍 has a pull-down; setting it to
  shè updates the body-order reading and `data/annotations/5.json`.
- `uv run pytest -q` passes.

## Not in this brief

Per-position overrides in the UI, student mode, OpenCC, the prompt template,
htmx, editing a row in place, lessons, progress.
