# Development environment

## Start locally

1. Start Docker Desktop.
2. Open this project folder in VS Code.
3. Run **Dev Containers: Reopen in Container** from the command palette.
4. Open a terminal in the container and sign in:

   ```sh
   codex login --device-auth
   codex login status
   ```

   Complete the browser step yourself. Device code login may need enabling in
   your ChatGPT account's security settings or workspace permissions.
5. Start a session from the project root:

   ```sh
   codex
   ```

   Suggested first prompt:

   > Read docs/project-context.md and README.md. Summarize the current project
   > and discuss the next data-modeling step with me before changing files.

The container includes Node.js for installing Codex, Python 3.13 managed by uv
for application tools, system Python for the historical loader, SQLite tools,
Git, and ripgrep. Codex CLI is pinned to 0.162.1 and uv to an image digest in
the Dockerfile. The base image and operating-system packages are not fully pinned.

Container creation runs `uv sync --locked` to install the project's locked
dependencies in `.venv`. After pulling dependency changes, run that command
again. Use `uv run` for application commands and tests. See
[database initialization](../docs/database-bootstrap.md) for the first milestone.

If you already have the original container running, use **Dev Containers:
Rebuild Container** to obtain uv and Python 3.13. Your Codex state volume survives.

## Persistent state

VS Code mounts the project folder into the container. Edits there are edits to
your checkout. The Docker volume `chineselearn-codex-state` holds Codex's login,
configuration, and session history separately from the repository and survives
container recreation. It is shared by containers using this definition on the
same Docker host. Deleting that volume removes that state.

The container uses its own login; it does not mount your Mac's Codex directory.
Credentials are never baked into the image. Keep Codex's normal permission and
sandbox controls enabled. If a tool fails inside the container, inspect the
specific failure before changing permissions.

The configuration disables Docker's default seccomp filter because it blocks
namespace creation required by Codex's Linux sandbox on the tested Docker
Desktop host. Codex's sandbox remains enabled. The container still runs as the
non-root `node` user, without privileged mode or access to the Docker socket.
Recheck sandbox compatibility when moving to a hosted Docker machine; host
security policy may differ.

## Move to a hosted development machine

Provision a Linux machine with Docker and SSH access. Once this project is in
Git, clone it on that machine, connect using VS Code Remote SSH, and reopen the
folder in its Dev Container. The same Dockerfile and configuration apply; no
Mac-specific workspace path is embedded here.

The Docker volume is local to each Docker host, so sign in again on the new
host. Commit or otherwise preserve project changes before moving. Session
history does not automatically move with the repository.

## Update tools

Change `CODEX_VERSION` in the Dockerfile and run **Dev Containers: Rebuild
Container**. A container rebuild preserves the Codex state volume.

## Official references

- [Codex CLI](https://learn.chatgpt.com/docs/codex/cli)
- [Authentication, including device code login](https://learn.chatgpt.com/docs/auth)
