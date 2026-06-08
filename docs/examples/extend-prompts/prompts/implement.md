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

# PROJECT CONVENTIONS

This project's single entry point for build, lint, and test is `make verify` —
always run it (not `go test` / `npm test` / etc. directly) so the agent
exercises the same checks CI does. Generated code under `gen/` is never
hand-edited; regenerate it with `make generate` instead.

# EXPLORATION

Explore the repo and fill your context window with relevant information that
will allow you to complete the task. Pay extra attention to test files that
touch the relevant parts of the code.

# EXECUTION

Use a red-green-refactor (TDD) loop to complete the task:

1. RED: write one failing test and confirm it fails with `make verify`
2. GREEN: write the minimum implementation to make that test pass
3. REPEAT until all acceptance criteria are covered
4. REFACTOR: clean up without breaking tests

If you genuinely cannot proceed without a human decision, emit a single line
starting with `QUESTION:` followed by the question, then stop and wait.

# FEEDBACK LOOPS

Before committing, run `make verify`. It must pass with no errors before you commit.
