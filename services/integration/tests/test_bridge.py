"""Tests for the Kafka -> EventBridge bridge and notification routing."""

from __future__ import annotations

from payments_integration.bridge import (
    EVENT_SOURCE,
    DomainToIntegrationBridge,
)
from payments_integration.eventbridge import InMemoryEventBridgeClient
from payments_integration.notifications import NotificationConsumer, Rule


def _domain_event(event_type: str, status: str, reason: str | None = None) -> dict:
    """Build a domain event envelope for tests.

    Args:
        event_type: The domain event type.
        status: The payment status in the payload.
        reason: Optional reason code.

    Returns:
        A domain event envelope dictionary.
    """
    return {
        "eventType": event_type,
        "paymentId": "p1",
        "payload": {"status": status, "reasonCode": reason},
    }


def test_completed_event_is_forwarded_to_eventbridge() -> None:
    """A PaymentCompleted domain event is forwarded as an integration event."""
    client = InMemoryEventBridgeClient()
    bridge = DomainToIntegrationBridge(client)

    result = bridge.forward(_domain_event("PaymentCompleted", "ACSC"))

    assert result is not None
    assert len(client.entries) == 1
    assert client.entries[0].source == EVENT_SOURCE
    assert client.entries[0].detail_type == "PaymentCompleted"
    assert client.entries[0].detail["paymentId"] == "p1"


def test_non_curated_event_is_not_forwarded() -> None:
    """A domain event outside the curated subset is not forwarded."""
    client = InMemoryEventBridgeClient()
    bridge = DomainToIntegrationBridge(client)

    result = bridge.forward(_domain_event("PaymentOrderCreated", "ACSP"))

    assert result is None
    assert client.entries == []


def test_rule_routes_event_to_notification_consumer() -> None:
    """An integration event matching a rule reaches the notification consumer."""
    client = InMemoryEventBridgeClient()
    bridge = DomainToIntegrationBridge(client)
    consumer = NotificationConsumer(
        rule=Rule(
            source=EVENT_SOURCE,
            detail_types=frozenset({"PaymentCompleted", "PaymentFailed"}),
        )
    )

    bridge.forward(_domain_event("PaymentCompleted", "ACSC"))
    # Simulate EventBridge delivering the matched entry to the target.
    handled = [consumer.handle(entry) for entry in client.entries]

    assert handled == [True]
    assert consumer.notifications[0]["paymentId"] == "p1"
    assert consumer.notifications[0]["type"] == "PaymentCompleted"


def test_rule_ignores_non_matching_source() -> None:
    """The consumer ignores entries whose source does not match its rule."""
    consumer = NotificationConsumer(
        rule=Rule(source="other.source", detail_types=frozenset({"PaymentCompleted"}))
    )
    client = InMemoryEventBridgeClient()
    DomainToIntegrationBridge(client).forward(_domain_event("PaymentCompleted", "ACSC"))

    handled = [consumer.handle(entry) for entry in client.entries]

    assert handled == [False]
    assert consumer.notifications == []


def test_failed_event_carries_reason_code() -> None:
    """A PaymentFailed event forwards the reason code in the detail."""
    client = InMemoryEventBridgeClient()
    bridge = DomainToIntegrationBridge(client)

    bridge.forward(_domain_event("PaymentFailed", "RJCT", reason="AM04"))

    assert client.entries[0].detail["reasonCode"] == "AM04"
