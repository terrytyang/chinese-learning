# Brief 08 — Admin page rework: one place for each thing

Read `CLAUDE.md` and `docs/design.md`. Brief 07 is done. The admin text page
is rebuilt around the lesson: readings are edited over the text, characters and
words each have one section holding state, selection and facts, expansions are
entered per character with a lookup, and the page stops jumping to the top.
Still no JavaScript.

## 1. Page layout, `/texts/{text}?lesson=<id>`

Top to bottom:

1. **课文信息**: title; a one-line form to edit 作者, 年代, 类别 (comma-separated
   tags, multiple allowed). Saving rewrites the text file's header only,
   preserving the body byte-for-byte and the other header keys, then updates
   the database. New tag names are created.
2. **课程**: as brief 07 left it.
3. **原文**: the body with pinyin over every character, always (ruby). A 编辑拼音
   button opens edit mode (`?edit=pinyin`): the same body, where each 多音字
   position's `<rt>` is a `<select>` of the character's master readings and
   each non-master character's `<rt>` is a text input; single-reading
   characters stay static. One form, 保存 / 取消. Save writes the changed
   positions as `manual` readings and redirects back. A text input must be
   non-blank.
4. **学习字**: the lesson's characters, one row each: 字, 拼音 (from the readings
   at its first position; read-only here), 级, 释义, 状态 with the three state
   buttons, 移出. For a character absent from the master, 级 and 释义 are
   editable inline (写入 `text_character`); for a master character they are
   shown and the master gloss is read-only, but a text-level 释义 override can
   still be added. Below the rows, **候选字**: every unique character of the
   text not in the lesson, with filters 级 (range) and 状态, a checkbox per row,
   全选, and 加入本课. Filtering is a GET form that keeps `lesson`.
5. **词**: same shape as 学习字: the lesson's words (surface, 拼音, 级, 释义,
   词典释义, 状态 buttons, 编辑, 移出), then **候选词**: text words not in the
   lesson with the same filters, checkboxes, 加入本课. Then 添加词 (surface,
   pinyin, gloss, level) which creates the text fact and adds it to the lesson
   in one step. Word facts edit here; the 候选词 list is also where auto
   false-positives get 删除 (removes the text fact).
6. **扩展**: one block per lesson character, in lesson order: the character,
   its existing expansions as rows (word, 拼音, 级, 释义, 状态 buttons, 编辑,
   删除), and an input + 扩展 button to add one more. Submitting looks the word
   up: if it is a master word, the expansion is created linked, no further
   input; if not, the page returns with that character's block showing a second
   form asking for 释义 (required), 级 (pull-down, default 7) and 状态 (default
   未识), with the word prefilled. A character may have any number of
   expansions.
7. **注**: as now, keyed to the lesson.

Remove the old 字表 and its pull-downs; readings are edited only in 原文.
Remove `text_character.pinyin` if brief 07 left it; a non-master character's
reading is its `text_reading` rows.

## 2. No more jumping

Every POST redirects to the page with a fragment naming the element touched:
`#info`, `#lesson`, `#reading`, `#char-月`, `#word-寒山寺`, `#expansion-月-月亮`,
`#note-3`. Every section and row carries the matching `id`, so the browser
scrolls there. On a 422 re-render, the error message is placed inside the form
that failed, at its row, with the form rendered open and the submitted values
kept, so the message is where the user is looking.

## 3. Routes

Replace the brief 02–04 routes with: `POST …/info`, `POST …/readings` (the
edit-mode form), `POST …/characters/add` (bulk, `chars[]`),
`POST …/characters/{char}/remove`, `POST …/characters/{char}/facts`,
`POST …/words/add` (bulk), `POST …/words/{surface}/remove`,
`POST …/words/{surface}/facts`, `POST …/words/{surface}/delete` (text fact),
`POST …/words/new`, `POST …/expansions` (two-step), the existing expansion
edit/delete, note add/edit/delete, `POST …/progress`. All carry `lesson`.

## 4. Tests

Header rewrite preserves body and unrelated keys byte-for-byte; edit-mode save
writes only changed positions as manual; bulk add/remove characters and words;
filters; 添加词 creates fact and selection; expansion two-step (master word →
linked at once; local → second form → created with gloss/level); multiple
expansions per character; every POST's redirect carries the right fragment;
a 422 renders the error at the row. Existing round-trip tests adapted.

## 5. Finish

Re-run `intake --force` on all five texts so every text has stored readings,
auto words and a default lesson, review nothing, commit the files.

## Acceptance

- `/texts/5?lesson=…`: open 编辑拼音, set 舍 at its first position to shè, save;
  the page returns at `#reading` with the ruby updated; the JSON shows one
  manual reading.
- In 候选字 filter 级 1–2, 全选, 加入本课; they appear in 学习字.
- In 扩展 under 月, enter 月亮 → appears linked; enter 月影 → second form →
  gloss → appears local.
- `uv run pytest -q` passes.

## Not in this brief

JavaScript or htmx, print, exercises, styling, lessons spanning texts.
