# Brief 06 — Student view: the assembled material and the plain reader

Read `CLAUDE.md` and `docs/design.md` ("Modes": the one assembled structure).
Briefs 01–05 are done. This brief builds the structure every student-facing
presentation renders from, and the first two pages on it. No JavaScript: every
toggle is a GET parameter, hover glosses are CSS.

## 1. Split `web.py`

It is at the line limit. `web.py` keeps `create_app`, the connection
dependency, templates, `/health`; `admin.py` gets the existing `/texts…`
routes as an `APIRouter`; `learn.py` gets the new `/learn…` routes. No
behaviour change; existing tests pass unchanged.

## 2. `material.py` — `assemble(conn, text_id, learner_id=1) -> dict`

One function, one structure. Reuse `readings.readings_for`, `annotations`,
`progress.current`.

```
text:        {id, title, author, period, tags, notes}
chars:       one per character of the body, in order, including non-Han
             characters (punctuation, newlines) with han=False and nothing else:
             {position, char, han, pinyin, source, traditional, hsk_level,
              hsk_edition, gloss, in_master, study (bool), state}
words:       text_word rows with their occurrences:
             {surface, pinyin, hsk_level, gloss, meanings (first 3), linked (bool),
              state, spans: [[start, end), …]}  — all occurrences, in order
highlight:   non-overlapping spans chosen leftmost-longest from `words`, for
             rendering; each {start, end, surface}
study:       text_character rows joined to the master: {char, pinyin, gloss
             (text gloss, else master gloss), hsk_level, state}
expansions:  {char, surface, pinyin, hsk_level, gloss, meanings, linked, state}
notes:       {anchor, note}
counts:      {chars: total Han, unique, unrecognized, recognized, mastered}
```

Traditional: convert the whole body with OpenCC `s2t`
(`opencc-python-reimplemented`; add to dependencies, run `uv lock`); when the
converted string has the same length, take it per position, otherwise convert
each character alone. Keep the converter as a module-level singleton.

Per-text traditional overrides are not in this brief.

## 3. `GET /learn` — the list (for the admin's eyes)

A table: 标题, 作者, 类别, 字数 (unique Han), and a progress bar: a `<div>` with
three inner spans whose widths are the unrecognized/recognized/mastered shares,
plus the three numbers. Order by text id. Each title links to `/learn/{id}`.

## 4. `GET /learn/{id}` — the reader

Query parameters, each `0`/`1`, default shown: `pinyin=0`, `traditional=0`,
`gloss=0`, `words=0`, `tint=none` (`none` | `level` | `state`),
`show_mastered=0`. A one-line form at the top with four checkboxes (拼音, 繁体,
释义, 词语), a radio group (着色: 无 / 按等级 / 按掌握), a checkbox (显示已掌握),
and an 应用 button. The form is `method="get"` so the URL is the state.

Rendering the body: each Han character is `<span class="c">`, with classes
`lvl-N` (1–7, or `lvl-0` when absent from the master) and `state-<state>`
always present and `study` when flagged; CSS applies colour only under
`.tint-level` / `.tint-state` on the container. `pinyin=1` wraps each in
`<ruby>字<rt>pinyin</rt></ruby>` (empty `<rt>` when none). `traditional=1`
shows the traditional character instead. `gloss=1` sets `data-gloss` to the
character's gloss (text gloss over master gloss) and CSS shows it on hover.
`words=1` wraps each `highlight` span in `<span class="w" data-gloss="…">`
with the word's gloss or meanings, and lists the words beneath the text
(词语: surface, pinyin, level, gloss / meanings). Newlines in the body become
line breaks; blank lines become paragraph breaks.

Beneath the text, always: 学习字 (char, pinyin, gloss), 扩展 (char → word,
pinyin, gloss), 注 (anchor, note). Mastered characters and words are omitted
from every list beneath the text unless `show_mastered=1`; they still appear in
the body.

No state-setting on this page: the student reads, the admin marks.

## 5. CSS

Minimal additions to `style.css`: ruby sizing, level tints (7 steps of one hue),
state tints (three colours), a `.study` underline, `.w` highlight, and a pure-CSS
hover tooltip from `data-gloss` (`position: relative` + `::after`). Still a
plain page; the styling pass is a later brief.

## 6. Tests

`assemble` on text 1: 28 unique Han, 啼 has `in_master=False` and no pinyin
until a reading is set, 寒山寺 appears in `words` with one span after adding it,
`highlight` is non-overlapping when two words overlap (fixture body with 银行
and 行走 adjacent). Traditional: 乌→烏, 后 in a fixture containing 后面→後面
(the phrase dictionary), length preserved. Reader: each toggle changes the HTML
in the expected way (`<ruby>`, 烏, `data-gloss`, `.w`), tint classes present,
mastered word omitted from the list unless `show_mastered=1`. `/learn` lists
five texts with counts that match `assemble`.

## Acceptance

- `/learn/1?pinyin=1&words=1&tint=level` shows 枫桥夜泊 with pinyin over each
  character, 寒山寺 highlighted with its gloss on hover, characters coloured by
  level, and the lists beneath.
- `/learn` shows the five texts with bars.
- `uv run pytest -q` passes.

## Not in this brief

JavaScript, exercises, print templates, per-text traditional overrides,
per-position readings in the UI, lessons, styling beyond §5, setting state
from the student page.
