"""Pure-logic unit tests for planner ordering, gate parsing, alert
classification, and summary dedup (issues #20, #22, #23, #24, #26)."""

import pytest

from devloop import dev_loop_logic as dl
from devloop.summarize_activities import build_prompt, should_summarize


# ---- approval / merge parsing (#20, #23) --------------------------------- #
@pytest.mark.parametrize(
    "reply,expected",
    [
        ("approve", True),
        ("Approved!", True),
        ("yes please", True),
        ("✅", True),
        ("lgtm", True),
        ("no", False),
        ("redo the plan", False),
        ("", False),
    ],
)
def test_is_approval(reply, expected):
    assert dl.is_approval(reply) is expected


# ---- PR number extraction (#22) ------------------------------------------ #
@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://github.com/omneval/omneval/pull/42", 42),
        ("https://github.com/o/r/pull/7/files", 7),
        ("branch pushed (no PR link)", 0),
        ("", 0),
    ],
)
def test_pr_number_from_url(url, expected):
    assert dl.pr_number_from_url(url) == expected


# ---- summary dedup (#24) ------------------------------------------------- #
def test_should_summarize():
    assert should_summarize("abc", "def", []) is True  # new head
    assert should_summarize("abc", "abc", []) is False  # nothing new
    assert should_summarize("abc", "abc", [1]) is True  # closed issues present
    assert should_summarize("", "", []) is False


def test_build_prompt_mentions_commits_and_issues():
    p = build_prompt(["fix bug", "add feature"], [{"number": 7, "title": "Crash"}])
    assert "fix bug" in p and "#7 Crash" in p
    assert "plain-english" in p.lower()
