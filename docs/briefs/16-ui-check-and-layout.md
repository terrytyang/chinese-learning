# Brief 16 — The UI check, layout fixes, and the data/ drift guard

Read `CLAUDE.md` and `docs/design.md` ("Modes", and the 2026-10-28 decision-log
lines about the UI check and the build fingerprint). Brief 15 is merged. This
brief adds the harness that later UI briefs are accepted with, fixes the layout
defects found so far, and makes a stale database say so instead of failing
oddly. The owner approves one dev dependency: `playwright` (with Chromium).

## 1. The UI check

`tests/test_ui.py`, marked `ui`, skipped with a clear message when Playwright's
Chromium is not installed; `uv run chineselearning ui-check` runs the same
harness outside pytest and keeps its output. Both read one manifest.

- Manifest `tests/ui_manifest.py`: a list of pages, each a URL and an ordered
  list of steps — `click(selector)`, `fill(selector, text)`,
  `select(selector, value)`, `expect(selector, text)`, `expect_422(selector)`
  for a step whose response is a deliberate 422. Cover every admin page and
  every htmx interaction that exists today: texts list and import (preview,
  a 422 for a missing title, a successful import), the text page's tabs and
  one mutation per tab, the dictionary (filters, state, edit, lookup, add,
  add-all-shown, the Changed control), the lesson page (rename and its 422,
  remove, mark all), and the student pages.
- Harness: builds a copy of `data/` with a fresh progress database (the tests'
  copy helper), serves it in-process on a free port, opens Chromium at
  1366 × 768, runs each page's steps, and fails the page on any of: a console
  message at warning or error level; a response with status ≥ 400 that no
  `expect_422` step claimed; a server log record at WARNING or above; a
  document wider than the viewport; an element whose box extends outside its
  nearest scrolling ancestor; two `rt` (pinyin) boxes that overlap; a `.zh`
  table cell taller than two lines. Each page's screenshot after its last step
  goes to `build/ui/<page>.png`; `build/ui/report.txt` lists every page, pass
  or fail, with the reasons. The test fails if any page fails and prints the
  report.
- Logging: the app logs through `logging` (`chineselearning.*`): every 422 at
  INFO with its message, every file write at INFO with the path, anything
  unexpected at WARNING or above; `serve` turns on uvicorn's access log. The
  harness captures the app's records.

## 2. The drift guard

`build` records a fingerprint of `data/` — every file's path, size and mtime —
in a `meta` table of the content database. The admin shell compares the
current tree with it on each render (a few dozen stats) and, when they differ,
shows a banner across the top: "data/ has changed since the last build
(supplement.tsv, annotations/6.json): run `chineselearning build`". Writes the
app makes itself update the fingerprint for the files they wrote, so the
banner appears only for changes made outside the app — a git checkout, a hand
edit. `supplement.add` and `update` refuse with the same message when
`supplement.tsv` is among the changed files, as a 422; nothing else refuses.

## 3. Layout

Pages are designed for a window at least 1024 px wide; the check runs at 1366.

- Tables with Chinese item cells (dictionary, lesson page, every text-page
  tab): `table-layout: fixed`; item and pinyin cells never wrap; the gloss
  column takes the remaining width and wraps; the state control and the
  action buttons never wrap. A long gloss makes the row taller, never the item
  narrower.
- The text block: each character's box is at least as wide as its pinyin, so
  adjacent pinyin never touch and character spacing is uniform; punctuation
  keeps its own width. Same in the student reader and in Edit pinyin mode.
- The four state buttons are one segmented control, one line, on every page
  that shows them.
- The import page's preview shows a placeholder until title and body are both
  present, not a parse error.
- The dictionary's header counts refresh after an add (out of band with the
  rows).
- A vocabulary lesson's default name uses the local date, not UTC.

## 4. Rules

`CLAUDE.md` gains, under Standing rules: a brief that touches a page adds its
pages and interactions to `tests/ui_manifest.py` and passes the UI check, and
the report quotes the result; and, under Commands, a line that any git
operation touching `data/` is followed by `build` (the banner says so too).
`README.md` mentions installing Chromium for Playwright once in the container.

## Acceptance

- `uv run chineselearning ui-check` on the current data is clean; its report
  and screenshots are in `build/ui/`; opening the screenshots shows no stacked
  Chinese, no touching pinyin, no wrapped state controls.
- Edit `data/supplement.tsv` by hand with the server running: the next admin
  page shows the banner naming the file; adding a word from the expansions
  tab returns the 422 with the same message; `build` clears it.
- `uv run pytest -q` passes, with `test_ui` running (Chromium installed) or
  skipping with its message (not installed); no server is left on port 8000.

## Not in this brief

The paper export (brief 17); any new page; styling beyond the defects listed.
