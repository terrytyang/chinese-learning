# Chinese learning and teaching

`chineselearning` is a Chinese learning system supporting character recognition,
vocabulary, reading, and broader cultural and literary competence. School credit by
examination is one milestone, not the definition of the curriculum.

The first implementation builds a small, reproducible character database.
The trial stack is Python 3.13, FastAPI, SQLAlchemy, Jinja2, and htmx, with SQLite
initially. Only the database tools and tests are implemented so far.

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
Its relative commands assume you are in `hsk-original/`. Application tools use
`hsk-original/hsk_vocab.sqlite` by default and read it without modifying it.

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
