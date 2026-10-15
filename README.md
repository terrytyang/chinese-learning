# Chinese learning and teaching

`chineselearning` is a Chinese learning system supporting character recognition,
vocabulary, reading, and broader cultural and literary competence. School credit by
examination is one milestone, not the definition of the curriculum.

The application extracts HSK vocabulary into self-contained JSON, builds
reproducible character and vocabulary databases, and serves a read-only
character inventory page with a JSON API, plus a text library and plain reader.
The trial stack is Python 3.13, FastAPI, SQLAlchemy, Jinja2, and htmx, with SQLite
initially. The inventory uses FastAPI, Jinja2, plain CSS, and a small JavaScript
module; htmx and other frontend tooling are deferred.

## Development

Open the project in VS Code and select **Dev Containers: Reopen in Container**.
See [.devcontainer/README.md](.devcontainer/README.md) for setup and Codex login.

Alternatively, use Docker Compose from a host terminal:

```sh
docker compose build dev
docker compose run --rm dev
```

The shell opens with locked dependencies installed. To run Codex or tests
directly:

```sh
docker compose run --rm dev codex
docker compose run --rm -T dev uv run --locked pytest -q
```

See [.devcontainer/README.md](.devcontainer/README.md) for persistent containers,
shared Codex state, and hosted-machine setup.

The application name is `chineselearning`; the checkout directory, container
workspace paths, Docker resource names, and Codex state volume intentionally
keep their existing names. See the naming exceptions in the environment guide.

From the project root inside the container:

```sh
uv sync --locked
uv run --locked pytest -q
uv run --locked chineselearning-init --output build/trial.sqlite --sql-output build/trial.sql
```

The initialization command requires fresh output paths and refuses to overwrite
existing files. See [database initialization](docs/database-bootstrap.md) for
the model, importable SQL, and deliberate limitations.

## Character inventory trial

Build a fresh 140-character inventory using the saved selection, then start the
server inside the development container:

```sh
uv sync --locked
uv run --locked chineselearning-init --seed data/inventory.json --output build/inventory.sqlite --sql-output build/inventory.sql
CHINESELEARNING_DATABASE=build/inventory.sqlite uv run --locked uvicorn chineselearning.web:create_app --factory --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` through VS Code port forwarding. The database must
already exist; startup never builds or resets it. For repeat builds, choose
fresh output paths. See [inventory documentation](docs/character-inventory.md)
for Compose commands, the manifest, API contract, and verification limits.

## HSK vocabulary extraction trial

The separate extractor selects all vocabulary and constituent characters for
`newest`, exact level 1: 294 entries and 248 characters. It retains source
readings, their traditional forms and ordered meanings, and ordered constituents.
The existing eight- and 140-character fixtures remain separate.

```sh
uv run --locked chineselearning-extract --source hsk-original/hsk_vocab.sqlite --settings data/hsk-newest-level1.selection.json --output build/hsk-extraction.json
uv run --locked chineselearning-init --extracted build/hsk-extraction.json --output build/hsk-application.sqlite --sql-output build/hsk-application.sql
```

Use fresh output paths. The second command needs only the JSON. No extraction
runs during startup or requests. See [HSK extraction](docs/hsk-extraction.md) for
exact/cumulative selection semantics, artifacts, counts, and limitations. The
existing inventory page continues to describe its 140-character fixture.

## Text library and reader

The library contains 《枫桥夜泊》、《春晓》、《赠汪伦》、
《绝句（迟日江山丽）》 and 《桃花源记》. It supports multiple literary categories
and exact category/author/period filtering. Build it alongside the existing
HSK-1 data using only the saved JSON inputs:

```sh
uv run --locked chineselearning-init --extracted data/hsk-newest-level1.json --texts data/text-library.json --output build/library-filters-rebuilt.sqlite --sql-output build/library-filters-rebuilt.sql
CHINESELEARNING_DATABASE=build/library-filters-rebuilt.sqlite uv run --locked uvicorn chineselearning.web:create_app --factory --host 0.0.0.0 --port 8000
```

Use fresh output paths. Rebuild older text databases and restart the server;
curated format version 2 replaces `category_id` with `category_ids`. Open
`http://localhost:8000/texts` or `/texts/1` through VS Code port forwarding.
Readers `/texts/1` through `/texts/5` follow the works listed above. `/health`
returns `{"status":"ok"}` for application liveness without querying the database;
it does not establish ongoing database readiness. The existing `/` inventory page
still describes the 140-character fixture; use its database for that page. The character API works
against both datasets. See [text library documentation](docs/text-library.md)
for explicit IDs, import validation, SQL restoration, and verification limits.

## Layout

| Directory | Contents |
| --- | --- |
| `hsk-original/` | Original HSK database, loader, schema, and README, preserved unchanged |
| `src/chineselearning/` | Application schema and database initialization tools |
| `data/` | Selected seed data and generated, importable SQL snapshot |
| `tests/` | Initialization and SQL restoration tests |
| `docs/` | Project context and implementation documentation |
| `.devcontainer/` | Container environment definition |
| `compose.yaml` | Standalone development shell and Codex runtime |
| `build/` | Ignored, disposable application database outputs |

The original dataset documentation is [hsk-original/README.md](hsk-original/README.md).
Its relative commands assume you are in `hsk-original/`. The extractor and original character-fixture builder use
`hsk-original/hsk_vocab.sqlite` by default, read-only. Builds with `--extracted`
use only the self-contained JSON; the web application uses only a built database.

## Working agreement

Design, explanations, and independent review take place in the discussion chat.
Application implementation takes place in Codex CLI inside the development
container. Process and environment changes can be requested in the discussion
chat. Read [project context](docs/project-context.md) and [AGENTS.md](AGENTS.md)
for the established decisions and repository guidance.

## Version control

Local Git uses `main`. Track source, seed data, SQL snapshots, documentation,
the dependency lockfile, and the historical HSK artifacts. Virtual environments,
caches, local credentials, and disposable build outputs are ignored. No remote
repository is configured yet.
