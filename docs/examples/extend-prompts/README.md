# Extending the Agent Image — Minimal Example

This is the cheapest way to specialize devloop for your project: extend
`devloop-agent-base` with a couple of plain Docker layers, no custom Temporal
workflow required. It shows the two most common reasons a project needs its
own agent image:

1. **Extra Python libraries** the agent needs at runtime (`pyproject.toml`).
2. **A project-specific Phase prompt template** that overrides one of the
   language-agnostic defaults baked into `devloop-agent-base`.

## How the prompt override works

Every Dev Loop phase (plan, execute, review, merge, ...) renders one bundled
markdown template — see `_PROMPT_FILES` in `devloop-agent-base`'s
`entrypoint.py`. The base image bakes language-agnostic defaults at
`/usr/local/share/agent-prompts/<phase>.md`.

A per-project image overrides individual templates by `COPY`-ing its own
`prompts/<phase>.md` to that same path **and filename** — a build-time Docker
layer overwrite (see `Dockerfile`). Any template you don't ship falls through
to the agent-base default; you only need to provide the files you want to
change.

Resolution order at runtime (`_prompts_dir` in `entrypoint.py`):

1. `AGENT_PROMPTS_DIR` env var, if set
2. `/usr/local/share/agent-prompts` (the image install path)
3. the bundled `prompts/` next to `entrypoint.py` (test/dev fallback)

This is a simpler mechanism than the [Skills convergence
directory](../../../CONTEXT.md#skills-convergence-directory) — there is no
runtime stage-and-install merge. Whatever file occupies
`/usr/local/share/agent-prompts/<phase>.md` when the image is built wins.

## File layout

```
extend-prompts/
├── Dockerfile           # FROM devloop-agent-base + the two overrides
├── pyproject.toml       # extra Python deps installed on top of the base image
└── prompts/
    └── implement.md     # overrides the bundled "implement" template only
```

`prompts/implement.md` is the bundled template plus one new "PROJECT
CONVENTIONS" section (telling the agent to run `make verify` / `make generate`
instead of guessing at language-specific commands) — everything else is
unchanged, and every other phase (`plan.md`, `review.md`, `merge.md`, ...)
still uses the agent-base default because this project doesn't ship them.

## Adapting this for your project

1. Add whatever runtime dependencies your project's tooling needs to
   `pyproject.toml` (replace `httpx`/`pydantic` with your real list).
2. Copy the bundled template for the phase you want to change from
   `devloop-agent-base`'s `prompts/` directory, edit it, and place it at
   `prompts/<phase>.md` here — keep the `{{VAR}}` placeholders the entrypoint
   substitutes (`{{TASK_ID}}`, `{{ISSUE_TITLE}}`, `{{BRANCH}}`, ...).
3. Build: `docker build -t ghcr.io/your-org/your-project-agent:latest .`
4. Point your Project Registry entry's `agent_image` at the built image.

## Building the image

```bash
docker build -t ghcr.io/your-org/your-project-agent:latest .
```
