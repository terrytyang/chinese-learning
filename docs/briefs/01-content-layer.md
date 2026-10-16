# Brief 01 — Content layer: build, texts, plain reader

Read `CLAUDE.md` and `docs/design.md` first. This brief delivers layers 2 and 3
without annotations, plus the admin-mode plain view of a text. No learner state,
no annotations, no htmx yet.

## Deliverables

1. **Package skeleton** under `src/chineselearning/`: `cli.py` (`build`, `serve`),
   `db.py` (open content DB, foreign keys on), `schema.sql` (text layer tables),
   `texts.py` (parse `data/texts/*.md`), `web.py` (FastAPI app factory `create_app`
   and module-level `app`), `templates/`, `static/`.

2. **`chineselearning build`**: delete and recreate `build/content.sqlite`:
   execute `data/hsk.sql`, then `schema.sql`, then import every `data/texts/*.md`.
   Fail loudly on a bad text file (missing id/title/tags, duplicate id, empty
   body). Print row counts. Accept `--db PATH` for tests.

3. **Text file parser** exactly as `docs/design.md` specifies. Body is verbatim
   after the first blank line; strip only the final trailing newline.

4. **`chineselearning serve`**: uvicorn on 0.0.0.0:8000, DB path from
   `CHINESELEARNING_DB` (default `build/content.sqlite`), opened read-only.

5. **Routes** (all Chinese UI, English identifiers):
   - `GET /texts` — list, with 类别/作者/年代 dropdown filters (AND), result count.
   - `GET /texts/{id}` — the plain admin view:
     - header (标题/作者/年代/类别), body with line breaks preserved;
     - **字表**: every unique character in body order, with 拼音, HSK 级, 版本
       (`latest`/`old`), and a visible marker for characters absent from the master;
     - **词表**: every 2–4 character substring of the body that matches
       `word.simplified`, each once, in order of first appearance, with 拼音, 级,
       first three meanings;
     - counts: N 字, M 个不在字库, K 个词.
   - `GET /api/characters?chars=月落乌` — JSON lookup used later by admin UI.
   - `GET /health`.
   - 404 for unknown text id.

6. **Tests** (`tests/`): parser (header/body/edge cases), build from `data/` into a
   temp path (counts: 3034 characters, 11470 words, 5 texts), `/texts` filters,
   `/texts/1` shows 啼 and 枫 as missing and finds zero words, `/texts/5` finds
   some words, 404.

## Acceptance

- `uv run chineselearning build && uv run chineselearning serve`, open
  `/texts/1`, see the 字表 with 啼 and 枫 flagged.
- `uv run pytest -q` passes.
- No file in `src/` longer than ~200 lines. No module named after a trial.

## Not in this brief

Annotations, expansions, local words, progress, collections, student mode,
exports, pagination, authentication, PostgreSQL,
migrations, refuse-to-overwrite logic, any JavaScript, docs beyond docstrings and one README
paragraph if needed.
