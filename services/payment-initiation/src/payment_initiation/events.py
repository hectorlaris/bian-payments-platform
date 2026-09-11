"""Domain event envelope and the event publisher abstraction.

The envelope mirrors the platform-wide event contract (see docs/architecture/
eda-flow.md). The publisher is an interface so the domain layer stays independent
of transport; the MVP provides an in-memory implementation, and a Kafka-backed
implementation is added in a later task.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def _new_id() -> str:
    """Return a new random UUID string.

    Returns:
        A UUID4 formatted as a string.
    """
    return str(uuid.uuid4())


def _now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string.

    Returns:
        The current instant formatted with a trailing ``Z``.
    """
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class DomainEvent:
    """A domain event using the shared platform envelope."""

    event_type: str
    payment_id: str
    payload: dict[str, Any]
    correlation_id: str
    event_id: str = field(default_factory=_new_id)
    occurred_at: str = field(default_factory=_now_iso)
    schema_version: int = 1


class EventPublisher(ABC):
    """Abstraction for publishing domain events to the backbone."""

    @abstractmethod
    def publish(self, topic: str, event: DomainEvent) -> None:
        """Publish an event to a topic.

        Args:
            topic: The logical topic name.
            event: The domain event to publish.
        """
        raise NotImplementedError


class InMemoryEventPublisher(EventPublisher):
    """In-memory publisher that records events for tests and local demos."""

    def __init__(self) -> None:
        """Initialize the publisher with an empty event log."""
        self.published: list[tuple[str, DomainEvent]] = []

    def publish(self, topic: str, event: DomainEvent) -> None:
        """Record the event in the in-memory log.

        Args:
            topic: The logical topic name.
            event: The domain event to publish.
        """
        self.published.append((topic, event))
