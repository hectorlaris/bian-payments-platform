"""Payments integration package.

Bridges domain events (Kafka) to integration events (Amazon EventBridge), keeping the
two planes separate. Provides an EventBridge client abstraction (in-memory fake and a
boto3-backed runtime implementation), rule matching, and a sample notification consumer.
"""

from payments_integration.bridge import DomainToIntegrationBridge, IntegrationEvent
from payments_integration.eventbridge import (
    EventBridgeClient,
    InMemoryEventBridgeClient,
    PutEventsEntry,
)
from payments_integration.notifications import NotificationConsumer, Rule

__all__ = [
    "DomainToIntegrationBridge",
    "EventBridgeClient",
    "InMemoryEventBridgeClient",
    "IntegrationEvent",
    "NotificationConsumer",
    "PutEventsEntry",
    "Rule",
]
