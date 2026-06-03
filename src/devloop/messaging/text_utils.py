"""Shared text clamping utilities for messaging platforms (issue #29).

Provides ``clamp`` to prevent messages from exceeding platform limits.
Each platform imports this and uses its own constants.
"""

from __future__ import annotations

# Default constants — platforms override with their own limits.
DEFAULT_MAX_MESSAGE = 3000
DEFAULT_MAX_THREAD_NAME = 100
TRUNC_MARKER = "\u2026"  # …


def clamp(text: str | None, max_len: int, marker: str = TRUNC_MARKER) -> str:
    """Truncate *text* to *max_len* characters, appending *marker* when needed.

    If the marker itself exceeds *max_len*, falls back to a hard cut (no marker).
    Returns ``""`` for ``None`` input.
    """
    if text is None:
        return ""
    if len(text) <= max_len:
        return text

    # If marker is longer than the limit, just hard-cut
    if len(marker) > max_len:
        return text[:max_len]

    return text[: max_len - len(marker)] + marker
