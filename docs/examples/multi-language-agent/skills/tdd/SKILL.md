---
name: tdd
description: Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development.
# triggers: required for this image. Some vendored skills ship no `triggers:`
# field; under the default skillsSelectionMode "triggers" a triggerless skill
# never surfaces, so a phase prompt that calls invoke_skill('tdd') would find
# nothing. Add the field yourself when vendoring such a skill.
triggers:
  - tdd
  - test
  - tests
  - red-green-refactor
  - implement
  - feature
  - bug
  - fix
  - refactor
---

# Test-Driven Development

NOTE — this file is a stub for the example. The real omneval image vendors the
full multi-file `tdd` skill from https://github.com/mattpocock/skills (this
SKILL.md plus reference files: deep-modules.md, interface-design.md,
mocking.md, refactoring.md, tests.md — multi-file skills like this one must be
baked, since a Helm-managed ConfigMap can't express subdirectories per
CONTEXT.md's "Skills convergence directory"). It isn't reproduced verbatim
here to avoid redistributing third-party content; vendor the real thing the
same way — drop its directory under `skills/` and add a `triggers:` block if
it ships without one.

The mechanism this demonstrates is what matters: any directory under
`skills/` here lands in `/usr/local/share/agent-skills/installed/` at build
time, additive to whatever `devloop-agent-base` already baked.
