FROM mcr.microsoft.com/devcontainers/javascript-node:1-22-bookworm

# uv 0.13.0, pinned to the inspected upstream image digest.
COPY --from=ghcr.io/astral-sh/uv@sha256:cdc6093146eb3ff6a40107b38f008b789e050e77ad87865e381d9917da55a168 /uv /uvx /usr/local/bin/

ARG CODEX_VERSION=0.162.1

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv sqlite3 ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global @openai/codex@${CODEX_VERSION} \
    && mkdir -p /home/node/.codex \
    && printf 'cli_auth_credentials_store = "file"\n' > /home/node/.codex/config.toml \
    && chown -R node:node /home/node/.codex \
    && chmod 700 /home/node/.codex

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

COPY --chmod=0755 compose-entrypoint.sh /usr/local/bin/chinese_learning-entrypoint
# Seed ownership for Compose's separate Python environment volume.
RUN mkdir -p /workspaces/chinese_learning/.venv \
    && chown -R node:node /workspaces/chinese_learning

USER node
RUN uv python install 3.13
