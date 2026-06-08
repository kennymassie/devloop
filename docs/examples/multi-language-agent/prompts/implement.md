# TASK

Fix issue {{TASK_ID}}: {{ISSUE_TITLE}}

Pull in the issue using `gh issue view {{TASK_ID}}`. If it has a parent PRD, pull that in too.

Only work on the issue specified.

Work on branch {{BRANCH}}. Make commits and run tests.

# CONTEXT

Review recent history to understand current conventions:

```
git log -n 10 --format="%H%n%ad%n%B---" --date=short
```

This is a Go + TypeScript codebase: Go services live under `services/*/` (one
`go.mod` each, inside the `go.work` workspace, shared types in `internal/`),
the frontend lives in `web/` (TypeScript/React), and `api/openapi.yaml` is the
source of truth for the contract between them. Follow the standards in
`CODING_STANDARDS.md` — note that Go and the frontend each have their own
build/lint/test entry point (`make verify`, `npm run check`); a change
touching both sides must satisfy both.

# EXPLORATION

Explore the repo and fill your context window with relevant information that
will allow you to complete the task. Identify whether this issue touches Go,
TypeScript, or the OpenAPI contract between them — that determines which
toolchain commands below apply.

Pay extra attention to test files that touch the relevant parts of the code.

# EXECUTION

This issue involves writing code, so drive it test-first. Invoke the `tdd`
skill (`invoke_skill('tdd')`) and follow its red-green-refactor loop — one
failing test, then the minimum code to pass it, repeat; never write all the
tests up front.

1. RED: write one failing test (`go test ./...` for Go, `npm test` for `web/`) and confirm it fails
2. GREEN: write the minimum implementation to pass that test
3. REPEAT until all acceptance criteria are covered
4. REFACTOR: clean up without breaking tests

If a change crosses the Go↔TypeScript boundary, update `api/openapi.yaml`
first and regenerate both the server stubs and the TS client — never hand-edit
generated code.

If you genuinely cannot proceed without a human decision, emit a single line
starting with `QUESTION:` followed by the question, then stop and wait.

# FEEDBACK LOOPS

Before committing, run whichever of these apply to your change — both if it
crosses languages:

```
make verify       # Go services: build, vet, test
npm run check     # web/: prettier, eslint, test
```

All applicable checks must pass with no errors before you commit.

# COMMIT

Make a git commit. The commit message must:

1. Start with `RALPH:` prefix
2. Include task completed + issue reference (e.g. `fixes #{{TASK_ID}}`)
3. Key decisions made
4. Files changed
5. Blockers or notes for next iteration

Keep it concise.

# THE ISSUE

If the task is not complete, leave a comment on the issue with what was done and what remains.

Do not close the issue — this will be done by the merge agent.

Once complete, YOU MUST output exactly <promise>COMPLETE</promise>.

# FINAL RULES

ONLY WORK ON A SINGLE TASK.
