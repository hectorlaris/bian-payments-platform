"""Test the boto3-backed EventBridge client payload construction."""

from __future__ import annotations

import json
from typing import Any

from payments_integration.eventbridge import Boto3EventBridgeClient, PutEventsEntry


class _FakeBotoEvents:
    """Minimal stand-in for a boto3 EventBridge client."""

    def __init__(self, failed: int = 0) -> None:
        """Store the simulated failed-entry count and capture calls.

        Args:
            failed: The FailedEntryCount to report.
        """
        self.failed = failed
        self.calls: list[list[dict[str, Any]]] = []

    def put_events(self, Entries: list[dict[str, Any]]) -> dict[str, Any]:  # noqa: N803
        """Capture the entries and return a PutEvents-shaped response.

        Args:
            Entries: The PutEvents entries (boto3 uses this exact casing).

        Returns:
            A response dict with the configured FailedEntryCount.
        """
        self.calls.append(Entries)
        return {"FailedEntryCount": self.failed, "Entries": []}


def test_boto3_client_builds_putevents_payload() -> None:
    """The client serializes detail to JSON and reports accepted count."""
    fake = _FakeBotoEvents()
    client = Boto3EventBridgeClient(fake)

    accepted = client.put_events(
        [
            PutEventsEntry(
                source="payments.order",
                detail_type="PaymentCompleted",
                detail={"paymentId": "p1", "status": "ACSC"},
            )
        ]
    )

    assert accepted == 1
    sent = fake.calls[0][0]
    assert sent["Source"] == "payments.order"
    assert sent["DetailType"] == "PaymentCompleted"
    assert json.loads(sent["Detail"]) == {"paymentId": "p1", "status": "ACSC"}


def test_boto3_client_subtracts_failed_entries() -> None:
    """The accepted count excludes failed entries."""
    client = Boto3EventBridgeClient(_FakeBotoEvents(failed=1))

    accepted = client.put_events(
        [
            PutEventsEntry("payments.order", "PaymentFailed", {"paymentId": "p1"}),
        ]
    )

    assert accepted == 0
