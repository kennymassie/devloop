# Architecture remediation plan

Deepening work for `omneval-devloop`, derived from the 2026-06-01 architecture
review. Five candidates, sequenced so deletions clear noise first, the shared
foundation lands next, and the protocol/interface work builds on it.

Vocabulary follows `CONTEXT.md` (domain) and the review's architecture glossary:
**module / interface / implementation / deep / shallow / seam / adapter /
leverage / locality**.

Tooling: this repo uses **uv**. Run tests with `uv run pytest` and lint with
`uv run ruff check .` after every phase. Do not introduce `requirements.txt`.

## Sequencing

| Phase | Candidate | Why this order |
|-------|-----------|----------------|
| 0 | **C2** Delete unreached Planner | Pure deletion; removes the most misleading path before touching anything else. |
| 0 | **C5** Prune batch-merge vestiges | Pure deletion; independent of all others. |
| 1 | **C1** Cluster ConfigMap/Secret store | Foundation; C3 builds on it. |
| 2 | **C3** Agent Job ConfigMap protocol | Needs `shared.py` changes; pairs with C1's ConfigMap ownership. |
| 3 | **C4** Slim `AwaitInput` / narrow poll | Independent; smallest blast radius, do last. |

Each phase is a self-contained branch + PR. Green tests gate the next phase.

Note: C2 (Phase 0) and C3 (Phase 2) both touch
`images/agent-base/entrypoint.py`. C2 lands first and adds `_extract_review`;
C3's protocol refactor then sits on top of it (it changes how payloads are
(de)serialized, not the review-extraction logic). Expect to rebase C3 onto C2.

---

## C2 — Collapse the second, unreached Planner *(Strong · deletion test)*

**Verified:** no workflow calls `plan_issues`; `ExecutionPlan.render()` has zero
callers anywhere (not even a test). The live **Planner** is the Agent Execution
Job `plan` phase (`dev_loop.py::_plan_phase`), matching `CONTEXT.md`'s definition
(the Planner is an OpenHands agent, not an HTTP issue-sorter).

### Delete
- `src/devloop/github_ops.py`: `plan_issues`, `build_plan`, `_extract_deps`,
  `PlanInput`, the `_ISSUE_REF` / `_DEP_HINT` regexes, and the
  `from .shared import ExecutionPlan, ... PlannedIssue` parts no longer used.
  Keep `agent_pr_issue_numbers`, `open_agent_pr_issue_numbers`, `_AGENT_BRANCH`,
  and the HTTP client helpers.
- `src/devloop/shared.py`: `ExecutionPlan`, `PlannedIssue`.
- `src/devloop/worker.py`: drop `plan_issues` from the import block and from
  `ACTIVITIES`.
- `tests/test_github_ops.py`: `test_plan_issues_orders_and_fetches` and any
  `build_plan` tests.

### The three currently-unreached GitHub activities — decided
`post_pr_comments`, `file_issues`, `close_issues` are registered in
`worker.ACTIVITIES` but no workflow calls them yet. Decisions:

- **`post_pr_comments` → keep and wire in.** Once the reviewer Agent Execution
  Job finishes, the workflow posts a summary of its findings on the PR.
  - **Dependency — the reviewer must first emit findings.** Verified: today
    `handle_review` (`images/agent-base/entrypoint.py:833`) returns only
    `{status, issue_number, branch, commits, summary}`; there is **no `review`
    key**, so `AgentJobResult.review` always arrives `None`. The reviewer prompt
    only tells the agent to fix-in-place and commit. Plumbing that already
    exists: the `AgentJobResult.review` field, `post_pr_comments`,
    `PostCommentsInput`, `InlineComment`. Missing piece: the agent producing the
    findings. Required agent-side changes (same C2 PR):
    - `images/agent-base/prompts/review.md`: instruct the agent to also emit a
      `<review>{...}</review>` block — `{"summary": str, "inline_comments":
      [{"file": str, "line": int, "body": str}]}` — alongside its in-place fixes.
    - `images/agent-base/entrypoint.py`: add `_REVIEW_RE` + `_extract_review()`
      mirroring `_extract_diagnosis` (tolerant of a ```` ```json ```` fence and
      missing tags); have `handle_review` set `"review": _extract_review(
      outcome.summary)` in its payload. Add a test in
      `images/agent-base/test_entrypoint.py`.
  - **Workflow side.** `dev_loop.py::_review_phase` reads `result.review`; when
    present, calls the `post_pr_comments` activity with
    `PostCommentsInput(project_id, pr_number, summary, inline_comments)`. No-op
    cleanly when `review` is `None` (e.g. the reviewer found nothing).
  - PR number: derive from `exec_result["pr_url"]` (parse trailing `/pull/<N>`)
    via a small pure helper + test rather than parsing inline. The review payload
    does not carry `pr_url`, so the workflow must supply it from `exec_result`.
  - Add a `_review_phase` test in `test_dev_loop.py` asserting `post_pr_comments`
    is dispatched with the review summary, and one asserting it's skipped when
    `review` is `None`.
- **`close_issues` → delete.** Not needed under the PR-review merge model (a human
  merging the PR closes the issue). Remove the activity, `CloseIssuesInput`, the
  `worker.py` import + `ACTIVITIES` entry, and its tests.
- **`file_issues` → keep, leave unwired for now.** Reserved for a forthcoming
  **QA Validator** agent (see Future work) that files issues for problems it
  finds. Keep `file_issues`, `FileIssuesInput`, `NewIssue`, and their tests; add a
  comment marking it as the QA Validator's seam.

### Risk
- `plan_issues` / `ExecutionPlan` are not advertised public API (absent from
  `__init__.__all__`), so removal just narrows a private surface. Nothing is
  published yet (no PyPI release), so breaking changes here carry no consumer
  cost — see C4.

### Verify
- `uv run pytest` green; `grep -rn "plan_issues\|ExecutionPlan\|PlannedIssue\|build_plan\|close_issues" src/ tests/` returns nothing.
- Review phase posts findings: `post_pr_comments` appears in `M.dispatched_phases`
  (or its own recorder) in the new `_review_phase` test.

---

## C5 — Prune the batch-merge vestiges *(Worth exploring · deletion test)*

**Verified:** `parse_merge_reply` is reachable only from `tests/test_pure_logic.py`;
the live merge gate uses `is_approval`. `Verdict` is used only by
`parse_merge_reply` (src side).

### Delete
- `src/devloop/dev_loop_logic.py`: `parse_merge_reply` and the
  `from .shared import Verdict` line.
- `src/devloop/shared.py`: `Verdict` enum.
- `tests/test_pure_logic.py`: `test_parse_merge_reply_all_passed_excludes_fail`,
  `test_parse_merge_reply_explicit_subset`, `test_parse_merge_reply_none`.

### If a multi-branch merge is genuinely planned
Do **not** delete — instead record an ADR (`docs/adr/`) stating the batch-merge
model is intentionally retained, so the next architecture review doesn't re-flag
it. (Offer this only if the user says the multi-branch path is coming back.)

### Verify
- `grep -rn "parse_merge_reply\|Verdict" src/ tests/` returns nothing;
  `uv run pytest` green.

---

## C1 — Deepen cluster access into one ConfigMap/Secret store *(Strong · top pick)*

**Verified shallowness:** the incluster→kubeconfig fallback is copied into
`k8s_jobs._load_config`, `github_ops._read_token`, and `summarize_activities._core`.
The `cm.data`-vs-`dict` duck-type appears three times (`k8s_jobs.py:270`,
`summarize_activities.py:73`, `:84`).

### New module: `src/devloop/cluster.py`
Non-deterministic (imports `kubernetes`), so it must **never** be imported by a
workflow module (`dev_loop.py`, `summarization.py`, `workflows.py`, `shared.py`).
Imported only by activity modules.

```python
# accessors (patchable seam for tests)
def core() -> CoreV1Api: ...      # incluster→kubeconfig fallback, once
def batch() -> BatchV1Api: ...

# deep helpers (hide data parsing + 404 + base64)
def read_configmap_data(name: str, namespace: str = NAMESPACE) -> dict | None: ...   # None on 404
def patch_configmap_data(name: str, data: dict, namespace: str = NAMESPACE) -> None: ...
def read_secret_value(name: str, key: str, namespace: str = NAMESPACE) -> str: ...   # base64-decoded
```

`NAMESPACE` (`AGENTS_NAMESPACE`, default `"agents"`) moves here; the three modules
import it from `cluster` instead of each redefining it.

### Migrate call sites
- `k8s_jobs.py`: drop `_load_config` / `_core` / `_batch`; use `cluster.core()`,
  `cluster.batch()`. Replace `_read_output`'s manual read+parse with
  `cluster.read_configmap_data(job_name)` (still extracts the `result` key — that
  parsing belongs to C3). `answer_agent_job` → `cluster.patch_configmap_data`.
  `cleanup_agent_job` keeps `batch.delete_*` via `cluster.batch()`.
- `github_ops.py`: delete `_read_token`; `_client` calls
  `cluster.read_secret_value(cfg.github_token_secret, "GITHUB_TOKEN")`.
- `summarize_activities.py`: delete `_core`; `get_last_sha`/`set_last_sha` use
  `cluster.read_configmap_data` / `patch_configmap_data`. The `cm.data`/`dict`
  duck-type disappears (absorbed into the helper).

### The two adapters that justify the seam
- prod: real `CoreV1Api` / `BatchV1Api` behind `cluster.core()` / `cluster.batch()`.
- test: existing `FakeCore` / `FakeBatch`, now mounted at the single
  `cluster.core` / `cluster.batch` seam.

### Test migration
- `tests/test_k8s_jobs.py`, `tests/test_summarization.py`: patch
  `devloop.cluster.core` / `devloop.cluster.batch` instead of the per-module
  `_core` / `_batch`. Keep `FakeCore`/`FakeBatch` as-is.
- `tests/test_github_ops.py`: patch `cluster.read_secret_value` (or
  `cluster.core`) for token resolution.
- Add `tests/test_cluster.py`: 404 → `None`, base64 decode, data-shape parsing.

### Wins
- locality: the cluster fallback + ConfigMap parsing live in one module.
- leverage: one interface, three call sites.
- tests mock one seam, not three.

### Verify
- `grep -rn "load_incluster_config" src/` returns only `cluster.py`;
  `grep -rn "isinstance(cm, dict)" src/` returns nothing; `uv run pytest` green.

---

## C3 — Give the Agent Execution Job ConfigMap protocol one owner *(Strong)*

**Verified:** the payload shape is the seam between two **devloop images**. The
worker side hand-codes it in `k8s_jobs._read_output`, `_result_from_payload`
(17 fields, manual int/bool coercion), `render_job` (`TASK_SPEC = asdict(spec)`),
and `answer_agent_job`. The agent side (`images/agent-base/entrypoint.py`)
**re-derives the same keys independently** — its own `TaskSpec`-like dataclass
(line 126), `json.loads(TASK_SPEC)` (132), `{"result": json.dumps(payload)}`
(151), `human_answer` read (186), `{"status":"awaiting_human","question":…}` (210).
No shared definition; a key rename on one side silently breaks the other.

### Decided: agent-base installs `omneval-devloop`
Image weight is no longer a constraint, so the **Agent Base Image** installs the
package and both images `import devloop.shared`. The protocol lives on the
existing sandbox-safe dataclasses in `shared.py` (stdlib-only). No vendored copy.

Agent-base Dockerfile / image changes (`images/agent-base/`):
- Add `omneval-devloop` to the image's installed deps (per `CONTEXT.md` uv
  convention: `uv pip install --system --no-cache` the package).
- **Install the argocd CLI**, mirroring how the fluxcd CLI is installed in the
  same Dockerfile (same download-pinned-binary pattern, kept next to the `flux`
  install step).
- Update `CONTEXT.md`'s **Agent Base Image** definition: its toolchain list gains
  `argocd CLI` and `omneval-devloop` alongside the existing
  OpenHands/Temporal/git/gh/kubectl/flux entries.

These two image changes (package install, argocd CLI) are independent of the
protocol refactor below but ship in the same PR since they touch one Dockerfile.

### Add to `shared.py`
```python
@dataclass
class AgentJobResult:
    ...
    @classmethod
    def from_payload(cls, payload: dict, job_name: str) -> "AgentJobResult": ...  # moves _result_from_payload
    def to_payload(self) -> dict: ...                                             # agent side / round-trip tests

@dataclass
class TaskSpec:
    ...
    def to_env_value(self) -> str: ...     # json.dumps(asdict(self))
    @classmethod
    def from_env(cls, raw: str) -> "TaskSpec": ...
```
Optionally centralise the ConfigMap key constants (`KEY_RESULT = "result"`,
`KEY_HUMAN_ANSWER = "human_answer"`) in `shared.py` so both sides reference them.

### Migrate
- `k8s_jobs.py`: delete `_result_from_payload`; call `AgentJobResult.from_payload`.
  `render_job` uses `spec.to_env_value()`. `_read_output` extracts `KEY_RESULT`.
- `images/agent-base/entrypoint.py`: replace its local dataclass + ad-hoc dict
  with `TaskSpec.from_env` / `AgentJobResult.to_payload` (and the key constants).
- Update `CONTEXT.md`: add a term for the **Agent Job output ConfigMap** contract
  (the message-bus seam between the worker and the Job) — it's a real domain seam
  worth naming.

### Tests
- `tests/test_stub_roundtrip.py` already exercises round-trip — point it at the
  new methods. Add direct `from_payload` / `to_payload` symmetry tests.
- Add a test in `images/agent-base/` confirming the entrypoint uses the shared
  definition (guards against the two copies drifting again).

### Wins
- locality: the cross-image contract lives in one module.
- leverage: rename a field once, both images follow.
- interface shrinks; coercion absorbed into the type.

### Verify
- `grep -n "_result_from_payload" src/` returns nothing; both images' test
  suites green; `uv run pytest` green.

---

## C4 — Slim `AwaitInput`; narrow the poll interface *(Worth exploring)*

**Verified:** `AwaitInput` carries `project_id`, `issue_number`, `task_spec`,
`poll_interval_seconds`, but `await_agent_job` uses them only to rebuild a
`DispatchInput` that `_poll_to_terminal` then reads for `poll_interval` alone.
A strict-subset dataclass plus a rebuild step — shallow doubling.

### Keep the phase split (real constraint)
The dispatch → answer → await split stays: the human reply arrives as a Temporal
**signal** that only the workflow can receive, so the workflow must mediate. This
candidate narrows *input types*, not the phase split.

### Change
- `k8s_jobs.py`: change `_poll_to_terminal(core, batch, job_name, d)` to
  `_poll_to_terminal(core, batch, job_name, poll_interval)`; `dispatch_agent_job`
  passes `d.poll_interval_seconds`.
- `shared.py`: slim `AwaitInput` to the two fields it actually needs —
  `job_name: str`, `poll_interval_seconds: float = 5.0`. Remove `project_id`,
  `issue_number`, `task_spec`.
- `k8s_jobs.await_agent_job`: stop rebuilding `DispatchInput`; call
  `_poll_to_terminal(core(), batch(), inp.job_name, inp.poll_interval_seconds)`.
- `dev_loop.py::_answer_questions`: construct `AwaitInput(result.job_name,
  poll_interval_seconds=inp.poll_interval_seconds)` — drop the now-unused args.

### Public API — fine to break now
`AwaitInput` is in `__init__.__all__`, so slimming it changes the public shape.
This is acceptable: nothing is published yet (no PyPI release, not public-facing),
so now is the time to make interface changes. Do the clean slim — no compatibility
shim.

### Verify
- `uv run pytest` green (esp. `test_execute_mid_run_question_*` in
  `test_dev_loop.py`, which drive the resume path).

---

## Future work (out of scope for these phases)

- **QA Validator agent.** A new agent/phase that validates completed work and, on
  finding problems, files follow-up issues via the retained `file_issues`
  activity. Building it is its own effort; C2 only preserves the seam.

## Definition of done (all phases)

- `uv run pytest` green after each phase (plus `images/agent-base/` tests for C3).
- `uv run ruff check .` clean.
- `CONTEXT.md` updated: C3 adds the **Agent Job output ConfigMap** term and
  extends the **Agent Base Image** toolchain (argocd CLI, omneval-devloop).
- `uv.lock` committed if deps change; no new `requirements.txt`.
