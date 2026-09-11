"""EventBridge client abstraction with in-memory and boto3 implementations.

The abstraction lets the bridge and tests run without AWS, while the boto3-backed
client is used at runtime. Entries follow the EventBridge PutEvents shape.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PutEventsEntry:
    """A single EventBridge PutEvents entry."""

    source: str
    detail_type: str
    detail: dict[str, Any]
    event_bus_name: str = "default"


class EventBridgeClient(ABC):
    """Abstraction over Amazon EventBridge PutEvents."""

    @abstractmethod
    def put_events(self, entries: list[PutEventsEntry]) -> int:
        """Publish integration events to the bus.

        Args:
            entries: The entries to publish.

        Returns:
            The number of entries accepted.
        """
        raise NotImplementedError


class InMemoryEventBridgeClient(EventBridgeClient):
    """In-memory EventBridge used by the bridge tests and local demos."""

    def __init__(self) -> None:
        """Initialize the client with an empty capture buffer."""
        self.entries: list[PutEventsEntry] = []

    def put_events(self, entries: list[PutEventsEntry]) -> int:
        """Record the entries and report the count accepted.

        Args:
            entries: The entries to publish.

        Returns:
            The number of entries recorded.
        """
        self.entries.extend(entries)
        return len(entries)


class Boto3EventBridgeClient(EventBridgeClient):
    """EventBridge client backed by boto3 for runtime use on AWS."""

    def __init__(self, client: Any) -> None:
        """Store the underlying boto3 ``events`` client.

        Args:
            client: A boto3 EventBridge client instance.
        """
        self._client = client

    def put_events(self, entries: list[PutEventsEntry]) -> int:
        """Publish entries via the boto3 PutEvents API.

        Args:
            entries: The entries to publish.

        Returns:
            The number of entries accepted (total minus failed).
        """
        payload = [
            {
                "Source": entry.source,
                "DetailType": entry.detail_type,
                "Detail": json.dumps(entry.detail),
                "EventBusName": entry.event_bus_name,
            }
            for entry in entries
        ]
        response = self._client.put_events(Entries=payload)
        failed = int(response.get("FailedEntryCount", 0))
        return len(entries) - failed
