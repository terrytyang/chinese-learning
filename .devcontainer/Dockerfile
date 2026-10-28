# Development container: Python 3.13 via uv, Node for Claude Code, SQLite tools, Chromium for the UI check.
# Used by both VS Code (.devcontainer/devcontainer.json) and plain Compose (compose.yaml).
FROM mcr.microsoft.com/devcontainers/javascript-node:1-22-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /uvx /usr/local/bin/

# The Playwright version uv.lock pins (`name = "playwright"`); the lock is outside this build context, so keep them equal by hand.
# A bump in the lock means rebuilding the image: the browsers below belong to this version.
ARG PLAYWRIGHT_VERSION=1.64.1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends sqlite3 ripgrep python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global @anthropic-ai/claude-code@latest
# Chromium and its system libraries, in a path the project's .venv finds through PLAYWRIGHT_BROWSERS_PATH (the cloud sessions carry their own).
RUN python3 -m pip install --break-system-packages --no-cache-dir "playwright==${PLAYWRIGHT_VERSION}" \
    && playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/* \
    && chmod -R a+rX /ms-playwright

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
# Claude Code: keep login/config/history in a mounted volume; rebuild the image to update the CLI.
ENV CLAUDE_CONFIG_DIR=/home/node/.claude DISABLE_AUTOUPDATER=1

COPY --chmod=0755 compose-entrypoint.sh /usr/local/bin/chineselearning-entrypoint
RUN mkdir -p /home/node/.claude /workspaces/chineselearning/.venv \
    && chown -R node:node /home/node/.claude /workspaces/chineselearning

USER node
RUN uv python install 3.13
