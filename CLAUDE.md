# chineselearning

Private Chinese learning/teaching app: one parent (admin, native speaker) teaching one
student. Runs only inside the dev container, never on the internet. Read
`docs/design.md` before touching the data model or routes; work from the brief in
`docs/briefs/` that the owner points you at, and nothing beyond it.

## Commands

- `uv sync --locked` — install (runs automatically on container create)
- `uv run pytest -q` — tests
- `uv run chineselearning build` — rebuild `build/content.sqlite` from `data/`; always overwrites
- `uv run chineselearning serve` — dev server on 0.0.0.0:8000
- `python3 tools/derive_hsk.py` — regenerate `data/hsk.sql` from `hsk-original/` (rare)

## Layout

- `hsk-original/` — reference dataset. Read-only. The app never opens it.
- `tools/` — one-off derivation scripts (may use pypinyin)
- `data/` — source-controlled content: `hsk.sql` (generated), `texts/*.md` (hand-written)
- `src/chineselearning/` — the app: `sqlite3` + FastAPI + Jinja2 (+ htmx later)
- `tests/` — pytest; tests build a real SQLite file from `data/` and query it
- `build/` — disposable outputs, git-ignored

## Standing rules

- Column and code identifiers in English. Everything the user sees is Chinese
  (标题, 作者, 年代, 类别 …), including admin pages.
- The content database is repaved, never migrated. Schema change → change the
  build → rebuild. No migration tooling, no compatibility adapters.
- Learner progress lives in a separate database file (`build/progress.sqlite`)
  keyed by natural keys (the character, the word string). A content rebuild never
  touches it.
- IDs are natural or fixed by the source files: `character.id` is the code point,
  `word.id` comes from `data/hsk.sql`, `text.id` from the file header. Anything
  that must survive a rebuild is exported to `data/`, never kept only in the DB.
- No machinery against a hostile operator: no refuse-to-overwrite, exclusive
  publication, symlink checks, or input-path protection. `build` overwrites.
- Plain `sqlite3` with SQL strings; no ORM. JSON columns are fine. Schema lives in
  `.sql` files, not Python objects.
- Don't add options, abstractions, or features the brief didn't ask for. Ask
  before adding a dependency.
- Docs are short and state decisions, not deferrals. Record a changed decision as
  one line in `docs/design.md`'s decision log; don't write changelogs elsewhere.
- Classical texts rarely contain modern HSK words (枫桥夜泊 contains none); don't
  design as if word matching will do most of the work.
