# Extending the Agent Image — Multi-Language Example

`devloop-agent-base` deliberately ships **no language runtimes** — project
repos are cloned at Job runtime, and the base stays language-agnostic so every
consumer pays only for what their project needs (see the Dockerfile comment in
`devloop-agent-base`: *"Project repos are cloned at Job runtime; do NOT add
project source here"*). A project that spans multiple ecosystems layers those
runtimes — and whatever else its agent needs to work effectively — on top.

This example is a **faithful near-copy of the image that runs Dev Loop against
[omneval/omneval](https://github.com/omneval/omneval)** in production (a
Go + TypeScript codebase), taken from `home-server`'s
`agents/images/omneval/Dockerfile.agent`. Unlike `../extend-prompts/`, which
is intentionally synthetic, this one is meant to read as "here's what a real,
heavily-customized consumer image looks like" — which means **it can and will
drift** from the real image over time (Go/Node version bumps, new skills,
revised prompts). Treat `home-server`'s copy as the source of truth; treat
this as the illustrative shape of the pattern.

## What it layers on top of the base image

| Layer | Why |
|-------|-----|
| Go toolchain (hand-installed tarball) | `apt`'s Go package lags upstream releases by months |
| Node.js LTS (NodeSource apt repo) | Debian-slim's default Node is too old for frontend tooling |
| `CODING_STANDARDS.md` | Referenced by `prompts/implement.md`; gives the agent per-ecosystem conventions (Go *and* TypeScript) it can't infer from the diff alone |
| `prompts/implement.md` override | Tells the agent about the Go↔TypeScript split, points it at `CODING_STANDARDS.md`, and names the project's `make verify` / `npm run check` entry points — see [`../extend-prompts/`](../extend-prompts/) for the override mechanism in isolation |
| `skills/tdd/` | Bakes a vendored Agent Skill into the [Skills convergence directory](../../../CONTEXT.md#skills-convergence-directory) so `invoke_skill('tdd')` in the prompt resolves to something |

## File layout

```
multi-language-agent/
├── Dockerfile                  # FROM devloop-agent-base + Go/Node + the layers above
├── CODING_STANDARDS.md         # per-ecosystem conventions (Go services, TS frontend)
├── prompts/
│   └── implement.md            # overrides only the "implement" template
└── skills/
    └── tdd/
        └── SKILL.md            # stub — see note inside; vendor the real skill the same way
```

The real `omneval` image overrides four templates (`plan`, `implement`,
`review`, `merge`); this example ships only `implement.md` to stay readable —
every other phase falls through to the agent-base default, exactly as if this
project had only ever needed to customize one.

## Adapting this for your project

1. Replace the Go/Node install steps with whatever runtimes your project
   needs (Python via `uv`, Rust via `rustup`, JVM via the distro's `apt`
   package, ...) — same pattern: a versioned, pinned, retried download.
2. Replace `CODING_STANDARDS.md` and `prompts/*.md` with your project's real
   conventions and entry points.
3. Vendor any Agent Skills your prompts invoke into `skills/<name>/` — remember
   multi-file skills must be baked (a ConfigMap can't express subdirectories),
   and add a `triggers:` block if the upstream skill ships without one.
4. Build: `docker build -t ghcr.io/your-org/your-project-agent:latest .`

## Building the image

```bash
docker build -t ghcr.io/your-org/your-project-agent:latest .
```
