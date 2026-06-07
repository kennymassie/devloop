# syntax=docker/dockerfile:1
# Per-project agent image — heavy multi-language extension example.
#
# devloop-agent-base ships no language runtimes (project repos are cloned at
# Job runtime, and the base stays language-agnostic on purpose). A project
# that works across multiple ecosystems layers them on here. This is a
# faithful near-copy of the image that runs Dev Loop against omneval/omneval
# (a Go + TypeScript codebase) in production — see
# https://github.com/omneval/omneval and home-server's
# agents/images/omneval/Dockerfile.agent. It may drift from that real image
# over time (Go/Node version bumps, new skills); treat the real image as the
# source of truth and this as the illustrative shape of the pattern.

FROM ghcr.io/omneval/devloop-agent-base:0.0.12

ARG GO_VERSION=1.23.8
ARG NODE_MAJOR=22

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Go toolchain — installed by hand because the Debian/apt Go package lags
# upstream releases by months.
RUN curl -fsSL --retry 5 --retry-delay 5 --max-time 300 \
    -o /tmp/go.tar.gz \
    "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" \
    && tar -C /usr/local -xzf /tmp/go.tar.gz \
    && rm /tmp/go.tar.gz

ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPATH="/go"
ENV PATH="${GOPATH}/bin:${PATH}"

# Node.js LTS — via the NodeSource apt repo, which tracks current LTS lines
# (the Debian-slim default is too old for most frontend tooling).
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
    | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" \
    > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY CODING_STANDARDS.md ./

# Project-specific phase prompts (Go workspace conventions, TDD-skill
# invocation, commit format). These OVERRIDE the language-agnostic defaults
# baked into agent-base at the same path — a project that ships none falls
# back to the agent-base default per-phase. See ../extend-prompts/ for the
# override mechanism in isolation.
COPY prompts/ /usr/local/share/agent-prompts/

# Agent Skills baked into the convergence directory (CONTEXT.md: "Skills
# convergence directory"). COPY adds to the directory without removing the
# base image's baked skills — ConfigMap-delivered skills win on name
# collision at pod start, baked skills are the floor every project gets.
COPY skills/ /usr/local/share/agent-skills/installed/

WORKDIR /workspace
