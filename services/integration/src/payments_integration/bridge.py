"""Bridge domain events (Kafka) to integration events (EventBridge).

Only a curated subset of domain events is forwarded. Domain events remain the source
of truth for the Saga; integration events are for downstream systems (notifications,
analytics) and must not be required to advance the core flow.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from payments_integration.eventbridge import EventBridgeClient, PutEventsEntry

# Domain event types that are forwarded to the integration plane.
FORWARDED_EVENT_TYPES: frozenset[str] = frozenset(
    {"PaymentCompleted", "PaymentFailed"}
)

EVENT_SOURCE = "payments.order"


@dataclass(frozen=True)
class IntegrationEvent:
    """A normalized integration event derived from a domain event."""

    detail_type: str
    payment_id: str
    detail: dict[str, Any]


class DomainToIntegrationBridge:
    """Forward selected domain events to EventBridge as integration events."""

    def __init__(self, client: EventBridgeClient, event_bus_name: str = "default") -> None:
        """Create the bridge.

        Args:
            client: The EventBridge client.
            event_bus_name: The target event bus name.
        """
        self._client = client
        self._bus = event_bus_name

    def forward(self, domain_event: dict[str, Any]) -> IntegrationEvent | None:
        """Forward a domain event if it is in the curated subset.

        Args:
            domain_event: A domain event envelope (eventType, paymentId, payload...).

        Returns:
            The integration event that was published, or ``None`` if not forwarded.
        """
        event_type = domain_event.get("eventType", "")
        if event_type not in FORWARDED_EVENT_TYPES:
            return None

        integration = _to_integration_event(domain_event)
        self._client.put_events(
            [
                PutEventsEntry(
                    source=EVENT_SOURCE,
                    detail_type=integration.detail_type,
                    detail=integration.detail,
                    event_bus_name=self._bus,
                )
            ]
        )
        return integration


def _to_integration_event(domain_event: dict[str, Any]) -> IntegrationEvent:
    """Normalize a domain event into an integration event.

    Args:
        domain_event: The domain event envelope.

    Returns:
        The normalized integration event.
    """
    payment_id = domain_event.get("paymentId", "")
    payload = domain_event.get("payload", {})
    detail = {
        "paymentId": payment_id,
        "status": payload.get("status"),
        "reasonCode": payload.get("reasonCode"),
    }
    return IntegrationEvent(
        detail_type=domain_event["eventType"],
        payment_id=payment_id,
        detail=detail,
    )
