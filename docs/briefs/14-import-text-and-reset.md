# Brief 14 — Importing a text from the page, `intake --reset`, and the docs

Read `CLAUDE.md`, `docs/design.md` (layer 3, "Intake"),
`docs/mockups/import-text.dc.html` (match it) and `docs/mockups/README.md`.
Brief 13 is merged. Three small pieces; the first is the one that matters.

## 1. Import a text

`GET /texts/import`: a page in the admin shell (nav line, `Texts` current) with
the mockup's form — title, author, period, tags (default `诗词`), body — and
the "Will be written as" preview. A link "Import a text" on `/texts` leads to it.

- Preview. The pre block is a fragment, `POST /texts/import/preview`, refreshed
  by htmx on `input` (300 ms delay) from the form's fields; it renders the exact
  file content, or the parse error `texts.parse_text` would raise, so the
  server's rules are the only rules. The next id is `max(text.id) + 1` (1 when
  there are no texts).
- `POST /texts/import`: validate before writing anything —
  `texts.parse_text` on the composed content; the title must not contain `/`;
  every Han character of the body must be in the dictionary, else 422 naming
  the missing ones with a link to `/dictionary` ("add them there, then import
  again"). Then write `data/texts/<id, three digits>-<title>.md` (header lines
  in the order id, title, author, period, tags, omitting empty optionals; a
  blank line; the body as typed, trailing whitespace stripped per line, one
  trailing newline), insert the text and its tags through the same function
  `db.build` uses for one text (extract it if it is inline), run `intake` for
  it, commit. The response is the form's fragment replaced by a confirmation
  card: "Written `data/texts/006-….md` · intake: N characters, M words" and a
  link "Open 〈title〉 →" to `/texts/<id>`, with an empty form below it for the
  next one. No redirect, no rebuild: a later `build` must produce the same rows
  (test it). An error after the file is written (intake failing for a reason
  the checks above missed) is reported with the file name, since the file is
  the source and `build` + `intake` will pick it up.
- The mockup's status line says "rebuilds" and "opening"; both are superseded
  by the above. Note that in `docs/mockups/README.md`.

## 2. `intake --reset <text id>`

Redo a text from scratch: `chineselearning intake --reset <id>` (not with
`--new` or `--force`). It prints what it will delete — the counts of facts by
table and of lessons, and the files: `data/annotations/<id>.json` and every
`data/lessons/<id>-*.json` — and asks for confirmation by typing the text id;
anything else aborts with nothing changed. Then it deletes those rows and files
(manual and suggested rows too; that is the point), runs `intake`, and prints
its summary. Progress rows are not touched: states stay, and the fresh default
lesson selects by them as usual. `CLAUDE.md`'s command line for intake gains
`--reset <id>`.

## 3. Docs

The project now runs in three places: the VS Code dev container (`bin/dev`), a
plain checkout, and Claude Code cloud sessions. Fix `README.md`,
`.devcontainer/README.md` and `CLAUDE.md` so they describe the container as how
the owner runs it locally, not as a requirement; keep the commands as `uv run
…`. In `CLAUDE.md`'s standing rules add two lines: `hsk-original/` is never
written (the read-only mount no longer guards it everywhere); and tests derive
expected counts from the data files — nothing asserts the size of a curated
file, and a test that needs an absent word takes one from the probe fixture.
Short, in the existing voice.

## 4. Tests

- Preview renders the composed file and, for a bad header, the parse error.
- Import on a copy of `data/`: the file is written with the expected name and
  content; the text, its tags and its intake rows exist; `build` on that copy
  afterwards yields the same `text`, `text_tag`, `text_reading`, `text_word`
  and `lesson*` rows; a body with a character the dictionary lacks → 422
  naming it and no file written; a title with `/` → 422; a second import gets
  the next id.
- `--reset`: with the id typed, the rows and files are gone and recreated with
  only `auto` origins while a manual progress row survives; with anything else
  typed, nothing changes.

## Acceptance

- On the page, import 静夜思 (李白, 唐朝, 诗词, the four lines); the confirmation
  names `data/texts/006-静夜思.md`; its admin page opens from the link with
  readings and the default lesson; `git status` shows the new text file and its
  annotation and lesson files, nothing else.
- `uv run chineselearning intake --reset 6`, typing `6` at the prompt, redoes
  it; typing nothing aborts.
- `uv run pytest -q` passes; no server is left on port 8000.

## Not in this brief

Editing a text's header or body from the page (the file is edited by hand);
vocabulary lessons and the dictionary-page additions (brief 15); the export
(brief 16).
