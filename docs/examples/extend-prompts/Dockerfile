# syntax=docker/dockerfile:1
# Per-project agent image — minimal extension example.
#
# Shows the two cheapest ways to specialize the Agent Base Image for a project:
#   1. add Python libraries the agent needs at runtime (pyproject.toml)
#   2. override one Phase prompt template with project-specific instructions
#
# Neither requires touching the agent runtime itself — both are plain Docker
# layers on top of devloop-agent-base. See README.md for how the override
# resolves at runtime.

FROM ghcr.io/omneval/devloop-agent-base:0.0.12

COPY --from=ghcr.io/astral-sh/uv:0.11.18 /uv /uvx /bin/

WORKDIR /app

# Extra libraries this project's agent needs (e.g. to call its own internal
# tooling or APIs during Plan/Execute/Review). Installed on top of the base
# image's pinned OpenHands + omneval-devloop stack.
COPY pyproject.toml .
RUN UV_HTTP_TIMEOUT=300 uv pip install --system --no-cache .

# Overrides the bundled "implement" template at the same path/filename — a
# build-time Docker layer overwrite. Every other phase (plan, review, merge,
# ...) keeps the agent-base default because this project ships only one file.
COPY prompts/ /usr/local/share/agent-prompts/

WORKDIR /workspace
