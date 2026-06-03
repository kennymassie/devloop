"""devloop.messaging — messaging platform abstraction and bridge implementations.

Public API:

Protocol & wrapper
    MessagingPlatform       — protocol any messaging bridge must implement
    StubPlatform            — test double / in-memory implementation
    MessagingActivities     — generic Temporal activity wrapper

Data contracts
    SendMessageInput
    SendMessageOutput
    SendNotificationInput
    ArchiveThreadInput

Platform-specific bridges
    discord_bot             — Discord bridge (devloop.messaging.discord_bot)
    slack_bot               — Slack bridge (devloop.messaging.slack_bot)

Shared utilities
    text_utils              — platform-agnostic text clamping helpers
    thread_store            — ConfigMap-backed thread ↔ workflow mapping
"""

from devloop.messaging.core import (
    ArchiveThreadInput,
    MessagingActivities,
    MessagingPlatform,
    SendMessageInput,
    SendMessageOutput,
    SendNotificationInput,
    StubPlatform,
)

__all__ = [
    "ArchiveThreadInput",
    "MessagingActivities",
    "MessagingPlatform",
    "SendMessageInput",
    "SendMessageOutput",
    "SendNotificationInput",
    "StubPlatform",
]
