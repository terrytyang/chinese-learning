# Repository Guidelines

## Pair-Programming Workflow

Before each logical component, explain the proposed plan and tradeoffs so the owner can discuss them. Distinguish established decisions, observations, and proposals. Read `docs/project-context.md`, `.devcontainer/README.md`, and `README.md` when establishing project context. Introduce relevant OpenAI/Codex workflows when useful. Respect the current request's file-edit boundaries.

## Project Structure & Module Organization

This project is an early-stage Chinese learning and teaching system. Read `docs/project-context.md` for agreed direction before proposing architecture.

- `hsk-original/load_hsk.py`: Python 3.8+ standard-library loader and embedded SQLite schema.
- `hsk-original/schema.sql`: reference copy of the loader schema.
- `hsk-original/hsk_vocab.sqlite`: historical HSK vocabulary dataset.
- `hsk-original/README.md`: original dataset documentation, rebuild instructions, and example queries; relative commands run from that directory.
- `README.md`: application overview and development commands.
- `.devcontainer/`: VS Code container configuration and setup documentation.
- `compose.yaml`: standalone development runtime using the same Dockerfile.

The trial stack is Python 3.13, FastAPI, SQLAlchemy, Jinja2, and htmx, with SQLite initially. The first milestone uses only SQLAlchemy and pytest; web dependencies and frontend assets are deferred. `src/chineselearning/` contains the preliminary schema and builder, `data/` contains seed inputs and a generated SQL snapshot, and `tests/` verifies initialization. See `docs/database-bootstrap.md` for scope and limitations.

## Build, Test, and Development Commands

Open the workspace in the VS Code Dev Container for the configured development environment. There is no web server command yet.

Alternatively, run `docker compose build dev` and `docker compose run --rm dev`
from the Docker host. Compose synchronizes locked dependencies at startup,
keeps its Python environment separate from VS Code's, and mounts the historical
directory read-only. `docker compose run --rm -T dev uv run --locked pytest -q`
runs tests directly. See `.devcontainer/README.md` for state-volume setup.

For the application data milestone, run from the repository root:

- `uv sync --locked`: install locked application and test dependencies.
- `uv run chineselearning-init --output build/trial.sqlite --sql-output build/trial.sql`: build fresh outputs; existing files are refused.
- `uv run pytest`: test initialization, SQL restoration, constraints, and safety boundaries.
- `uv run chineselearning-init --print-schema postgresql`: compile DDL only, not a tested PostgreSQL build.

These commands apply only to the historical dataset:

- `python3 hsk-original/load_hsk.py --help`: inspect loader usage.
- `python3 hsk-original/load_hsk.py --print-schema`: display the embedded schema.
- `python3 hsk-original/load_hsk.py /path/to/complete-hsk-vocabulary /tmp/hsk-check.sqlite`: import an upstream clone into a fresh scratch database and run built-in verification.
- `sqlite3 /tmp/hsk-check.sqlite "PRAGMA integrity_check; PRAGMA foreign_key_check;"`: check database integrity and references.

Use a new output path for verification; `--force` deletes an existing output file.

## Coding Style & Naming Conventions

Use four-space Python indentation, snake_case functions and SQL identifiers, and uppercase constants. No formatter or linter is configured. When working with the historical reference files, follow their existing conventions. Preserve Unicode text, source ordering, duplicate tags, and contextual readings.

## Testing Guidelines

Application tests use pytest with descriptive `test_*.py` modules. No coverage threshold is set. Test real construction and SQL import behavior rather than implementation mirrors. Keep the generated `data/bootstrap.sqlite.sql` consistent with schema and seed changes. The existing dataset loader's verification reconstructs JSON content and key order and compares available upstream wordlist files; use a complete upstream checkout and inspect the reported comparisons.

## Commit & Pull Request Guidelines

The project uses local Git on `main`; remote hosting remains undecided. Use concise, imperative commit subjects. Pull requests should explain the change, link relevant issues when available, and report validation commands and results. Include screenshots for future interface changes.

## Data & Configuration Boundaries

Preserve the historical dataset, loader, schema, and original README under `hsk-original/`. Develop independent learning models in new tables and maintain curated data in importable source files. Keep credentials and local settings out of tracked files; follow `.gitignore` for environment files and local agent state.
