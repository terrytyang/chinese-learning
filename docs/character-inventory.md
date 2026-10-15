# Character inventory trial

The page at `/` and `GET /api/characters` run in the same FastAPI application.
The page uses Jinja2, plain CSS, and a JavaScript module with `fetch()`; there
is no frontend service or build step. The server opens only an existing
application database in SQLite read-only mode. It never imports from the
historical database during HTTP requests, initializes tables, or resets data.

## Data selection and rebuilds

`data/inventory.json` is the committed-ready selection manifest. It records
scheme `newest`, label **HSK 3.0 (2026 syllabus)**, random seed **20261014**, the
sampling method, and 140 distinct selected characters with their exact bands.
Candidate lists are sorted by Unicode character order before sampling 20 from
each band 1–6 and the combined 7–9 band (stored as integer 7).

The historical view derives first appearance from vocabulary, rather than an
independent character syllabus. That distinction is visible on the page. The
builder validates the manifest's band assignments against the historical
source during preparation. Ordinary rebuilds reuse the selected characters;
they do not invoke sampling. IDs follow saved manifest order.

The existing five character tables are unchanged. Fresh builds also include
five empty vocabulary tables from the [HSK extraction increment](hsk-extraction.md)
and three empty text tables from the [text library increment](text-library.md),
unless text input is supplied. The builder retains
all available scheme memberships, optional single best-effort traditional
forms, NULL English glosses and usage notes, and separate recognition and
production statuses. Initial `not_encountered` codes are placeholder trial
state, not actual student assessments. Status editing, accounts, enrichment,
character pronunciation and character-type classification remain absent. The
separate HSK-1 extraction has 294 vocabulary entries and 248 characters; it does
not replace this sample or change its page labels.

Run from the repository root in the development container:

```sh
uv sync --locked
uv run --locked chineselearning-init --seed data/inventory.json --output build/inventory.sqlite --sql-output build/inventory.sql
```

Both output paths must be fresh. Subsequent builds need different paths; there
is no implicit overwrite. `data/inventory.sqlite.sql` is the generated snapshot
for this manifest. The eight-character `data/bootstrap.json` fixture and
`data/bootstrap.sqlite.sql` snapshot still work with the builder's default seed.

Restore the inventory snapshot independently of the historical source:

```sh
sqlite3 build/inventory-restored.sqlite < data/inventory.sqlite.sql
sqlite3 build/inventory-restored.sqlite 'PRAGMA integrity_check; PRAGMA foreign_key_check;'
```

Use a fresh destination. To audit the selection algorithm without replacing the
saved manifest, generate a new scratch file explicitly:

```sh
uv run --locked python -m chineselearning.inventory_selection --output /tmp/inventory-selection-check.json
cmp /tmp/inventory-selection-check.json data/inventory.json
```

This generator refuses an existing destination. It is not part of the rebuild
or server startup path; do not casually replace the saved manifest.

## Run the server

Inside the development container, after the explicit build:

```sh
CHINESELEARNING_DATABASE=build/inventory.sqlite uv run --locked uvicorn chineselearning.web:create_app --factory --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` through VS Code's forwarded port. Forwarding uses
localhost; use the Ports panel to forward 8000 manually in an existing container
if the configuration has not been reread. `CHINESELEARNING_DATABASE` accepts a
SQLite file path; relative paths are relative to the server's working directory.
The default is `build/inventory.sqlite`. Missing or incompatible files fail
startup with an error, without creating a database. For a server directly on
the host, use `--host 127.0.0.1` instead.

Compose commands from the Docker host:

```sh
docker compose run --rm dev uv run --locked chineselearning-init --seed data/inventory.json --output build/inventory.sqlite --sql-output build/inventory.sql
docker compose run --rm --service-ports dev env CHINESELEARNING_DATABASE=build/inventory.sqlite uv run --locked uvicorn chineselearning.web:create_app --factory --host 0.0.0.0 --port 8000
```

Compose binds host exposure to `127.0.0.1:8000`. `--service-ports` is required
for a one-off server. Run the build only if its outputs do not already exist.
No server is started automatically with the development shell.

## JSON API contract

`GET /api/characters` accepts these query parameters:

| Parameter | Default | Allowed values / meaning |
| --- | --- | --- |
| `hsk_scheme` | `newest` | `old`, `new`, `newest`; must exist in the application database |
| `hsk_level` | omitted | Exact first-appearance band; 1–6 for `old`, 1–7 for `new`/`newest` |
| `page` | `1` | Positive integer, one-based |
| `page_size` | `20` | `10`, `20`, `50`, `100` |
| `sort` | `simplified` | Explicit allowlist: `simplified`, `hsk_level` |
| `order` | `asc` | `asc`, `desc` |

Filtering and sorting occur before pagination. Simplified sorting uses SQLite
`BINARY` collation (Unicode character order for these single-code-point strings),
not pinyin/linguistic order, followed by ID. HSK-level sorting orders by band,
then simplified character, then ID. Direction applies to every ordering key.
The ID is a final tie-breaker; simplified characters are unique in this schema.

The response has `items`, filtered `total`, requested `page`, `page_size`,
`total_pages`, and `hsk_scheme: {code, label}`. Each item has `id`, `simplified`,
nullable `traditional`, `english_gloss`, `usage_note`, selected-scheme `hsk_level`,
`hsk_level_label`, and separate `recognition_status`/`production_status` codes.
The display label for stored level 7 is “7–9.” Characters with no membership
in the selected scheme are excluded. Missing learning relations produce null
status codes rather than fabricated assessments.

Invalid parameters return HTTP 422. Empty filters return HTTP 200, `items: []`,
`total: 0`, and `total_pages: 0`; the requested page is retained. Pages beyond
the last page likewise return HTTP 200 with empty items and accurate totals;
they are not clamped or redirected. The page's controls prevent ordinary
navigation beyond the available pages. Changing the filter, sort, or page size
resets to page 1. An abort signal plus a request sequence check prevents stale
successes or failures from replacing a newer selection.

Example:

```sh
curl 'http://localhost:8000/api/characters?hsk_scheme=newest&hsk_level=7&page=1&page_size=20&sort=hsk_level&order=asc'
```

## Verification and environment refresh

```sh
uv run --locked pytest -q
node tests/inventory_controller.test.mjs
docker compose config --quiet
```

Python tests cover both fixtures, manifest validation, repeated builds, SQL
restoration, API behavior using targeted data, startup safety, and page/assets
delivery. Node tests exercise the shipped fetch controller's requests, page
resets, cancellation/races, error states, and retry. They do not verify browser
layout, rendering, focus behavior, or installed Chinese fonts.

During implementation, Docker and browser tooling were unavailable. Container
configuration can be checked structurally here, but Docker's own Compose
validation must run on the host. Browser verification and screenshots remain
manual: open the page, choose each page size, navigate pages, toggle both sort
headers, choose exact bands (including 7–9), and confirm counts/reset behavior.
Use keyboard Tab/Enter/Space to check controls and horizontal table scrolling;
check narrow screens, missing values, loading, and offline/retry states.

A native Google Sheets copy of `HSK1_Character_Inventory` was accessible as a
presentation reference; only its header row was read. No curriculum data was
copied. The seven required columns take precedence over its type/status layout.

After dependency changes, run `uv sync --locked` in the Dev Container and
`docker compose exec dev uv sync --locked` for an existing Compose environment;
restart Python servers. Existing containers do not gain new port mappings
automatically. The one-off `--service-ports` command above can serve the page
without recreating an existing persistent container. Do not synchronize the
same Compose Python volume concurrently. Workspace paths, Docker resource names,
and `chineselearn-codex-state` storage remain unchanged.
