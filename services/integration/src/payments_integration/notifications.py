"""Sample notification consumer with EventBridge-style rule matching.

A ``Rule`` matches integration events by source and detail-type (a simplified subset of
an EventBridge event pattern). The ``NotificationConsumer`` records notifications for
events that match its rule, standing in for a downstream target such as SNS or a queue.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from payments_integration.eventbridge import PutEventsEntry


@dataclass(frozen=True)
class Rule:
    """A simplified EventBridge rule matching by source and detail types."""

    source: str
    detail_types: frozenset[str]

    def matches(self, entry: PutEventsEntry) -> bool:
        """Return whether an entry matches this rule.

        Args:
            entry: The EventBridge entry to test.

        Returns:
            ``True`` when the source and detail-type match.
        """
        return entry.source == self.source and entry.detail_type in self.detail_types


@dataclass
class NotificationConsumer:
    """Consumes matching integration events and records notifications."""

    rule: Rule
    notifications: list[dict] = field(default_factory=list)

    def handle(self, entry: PutEventsEntry) -> bool:
        """Handle an entry, recording a notification if the rule matches.

        Args:
            entry: The EventBridge entry delivered to the consumer.

        Returns:
            ``True`` when a notification was recorded.
        """
        if not self.rule.matches(entry):
            return False
        self.notifications.append(
            {
                "paymentId": entry.detail.get("paymentId"),
                "type": entry.detail_type,
                "status": entry.detail.get("status"),
            }
        )
        return True
