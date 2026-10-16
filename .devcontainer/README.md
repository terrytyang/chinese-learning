# Development environment

All development happens inside a container so that nothing is installed on the
Mac. VS Code owns the container; any Mac terminal can attach to it.

## Day to day

1. Start Docker Desktop, open this folder in VS Code, **Dev Containers: Reopen in
   Container**. Use VS Code for editing and its Ports panel for `localhost:8000`.
2. From iTerm2 (or any terminal) in the project folder:

   ```sh
   bin/dev                      # Claude Code, inside the container
   bin/dev bash                 # a shell inside the container
   bin/dev uv run pytest -q
   bin/dev uv run chineselearning serve
   ```

   `bin/dev` finds the running Dev Container for this checkout and `docker exec`s
   into it as the `node` user. First time, `bin/dev` will ask you to sign in; if
   the browser callback never reaches the container, paste the code it shows.

## Without VS Code

`compose.yaml` builds the same Dockerfile into a separate container with its own
`.venv`, sharing only the Claude Code login:

```sh
docker volume create chineselearning-claude-state   # once per Docker host
docker compose build dev
docker compose run --rm dev                          # shell; deps synced on entry
docker compose run --rm dev claude
docker compose run --rm --service-ports dev uv run chineselearning serve
```

`--service-ports` is needed for a one-off container to publish port 8000 (bound
to `127.0.0.1` on the host). Note that `docker compose build` and VS Code build
separate images from the same Dockerfile; the layer cache is shared.

## What persists

- The repository is bind-mounted; edits are edits to your checkout.
- The `chineselearning-claude-state` volume holds Claude Code's login, settings
  and session history, and survives **Rebuild Container**. `CLAUDE_CONFIG_DIR`
  points at it so the `.claude.json` account file lands there too. Deleting the
  volume signs you out.
- Compose keeps its own `.venv` and uv cache in named volumes.
- `hsk-original/` is mounted read-only under Compose.

## Updating tools

Claude Code auto-update is disabled inside the image. To update it, uv, or Python:
**Dev Containers: Rebuild Container** (or `docker compose build --no-cache dev`).
