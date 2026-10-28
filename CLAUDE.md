# chineselearning

Private Chinese learning/teaching app: one parent (admin, native speaker) teaching one
student. Runs locally, never on the internet: the owner's dev container (`bin/dev`), a
plain checkout, or a Claude Code cloud session, all with the same `uv run …` commands. Read
`docs/design.md` before touching the data model or routes; work from the brief in
`docs/briefs/` that the owner points you at, and nothing beyond it.

## Commands

- `uv sync --locked` — install (runs automatically on container create)
- `uv run pytest -q` — tests
- `uv run chineselearning build` — rebuild `build/content.sqlite` from `data/`; always overwrites
- `uv run chineselearning intake --new | <text id> [--force] | --reset <id>` — facts and default lesson for texts
- `uv run chineselearning import-progress [--check]` / `export-progress` — learner state ↔ `data/`
- `uv run chineselearning init [--fresh]` — day-0: build, import-progress, intake --new
- `uv run chineselearning serve` — dev server on 0.0.0.0:8000
- `uv run chineselearning ui-check` — every admin page in headless Chromium (`tests/ui_manifest.py`); report and screenshots in `build/ui/`
- Any git operation that touches `data/` (checkout, pull, merge) is followed by `build`; the admin pages show a banner until it runs
- `python3 tools/derive_hsk.py` — regenerate `data/hsk.sql` from `hsk-original/` (rare)

## Layout

- `hsk-original/` — reference dataset. Never written; the app never opens it.
- `tools/` — one-off derivation scripts (may use pypinyin)
- `data/` — source-controlled content: `hsk.sql` (generated), `supplement.tsv`, `character-gloss.tsv`
  (curated, applied at build), `texts/*.md` (hand-written), `annotations/`, `lessons/` (written by the app),
  `progress/` (exported state), `import/progress/` (raw documents and their standard files)
- `src/chineselearning/` — the app: `sqlite3` + FastAPI + Jinja2 + htmx (vendored in `static/`)
- `docs/mockups/` — agreed page designs; a brief that says "match the mockup" means this
- `tests/` — pytest; tests build a real SQLite file from `data/` and query it
- `build/` — disposable outputs, git-ignored

## Standing rules

- Identifiers, labels, buttons, headings and messages are English. Content is
  Chinese: titles, text bodies, tags (诗词), glosses are English.
- The content database is repaved, never migrated. Schema change → change the
  build → rebuild. No migration tooling, no compatibility adapters.
- Learner progress lives in a separate database file (`build/progress.sqlite`)
  keyed by natural keys (the character, the word string), one row per key with
  `changed_at`, no history. States: unconfirmed (no row) → exposed → recognized
  → mastered. A content rebuild never touches it.
- A single character is a character everywhere: never a `word` key, never a
  one-character surface in a word table. Its dictionary data is on `character`.
- Every word a text or lesson refers to is a dictionary row (HSK or supplement);
  adding one the dictionary lacks writes `data/supplement.tsv` first. Every UI
  edit writes the file it belongs to as well as the database.
- IDs are natural or fixed by the source files: `character.id` is the code point,
  `word.id` comes from `data/hsk.sql`, `text.id` from the file header. Anything
  that must survive a rebuild is exported to `data/`, never kept only in the DB.
- No machinery against a hostile operator: no refuse-to-overwrite, exclusive
  publication, symlink checks, or input-path protection. `build` overwrites.
- Plain `sqlite3` with SQL strings; no ORM. JSON columns are fine. Schema lives in
  `.sql` files, not Python objects.
- Don't add options, abstractions, or features the brief didn't ask for. Ask
  before adding a dependency.
- A dev server started to verify a change is stopped before the work is
  reported done; never leave a process holding port 8000.
- Docs are short and state decisions, not deferrals. Record a changed decision as
  one line in `docs/design.md`'s decision log; don't write changelogs elsewhere.
- Classical texts rarely contain modern HSK words (枫桥夜泊 contains none); don't
  design as if word matching will do most of the work.
- Pages are a shell plus htmx fragments: a mutation returns the fragment it
  changed, never a redirect; state that selects a view lives in the URL.
- `hsk-original/` is never written. The read-only mount guards it only under
  Compose; everywhere else this rule does.
- Tests derive expected counts from the data files (the `baseline` fixture):
  nothing asserts the size of a curated file, and a test that needs a word the
  dictionary lacks takes one from the `probe` fixture.
- A brief that touches a page adds its pages and interactions to
  `tests/ui_manifest.py` and passes the UI check (`ui-check`, `tests/test_ui.py`);
  the report quotes the result.
