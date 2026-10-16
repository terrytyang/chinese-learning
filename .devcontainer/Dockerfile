# Development container: Python 3.13 via uv, Node for Claude Code, SQLite tools.
# Used by both VS Code (.devcontainer/devcontainer.json) and plain Compose (compose.yaml).
FROM mcr.microsoft.com/devcontainers/javascript-node:1-22-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /uvx /usr/local/bin/

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends sqlite3 ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global @anthropic-ai/claude-code@latest

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
# Claude Code: keep login/config/history in a mounted volume; rebuild the image to update the CLI.
ENV CLAUDE_CONFIG_DIR=/home/node/.claude DISABLE_AUTOUPDATER=1

COPY --chmod=0755 compose-entrypoint.sh /usr/local/bin/chineselearning-entrypoint
RUN mkdir -p /home/node/.claude /workspaces/chineselearning/.venv \
    && chown -R node:node /home/node/.claude /workspaces/chineselearning

USER node
RUN uv python install 3.13
