"""Contract-level tests for the Payment Initiation API (with auth)."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from tests.conftest import auth_headers

INITIATE = auth_headers("payments.initiate payments.read")
READ = auth_headers("payments.read")


def test_initiate_returns_201_with_id_and_status(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """POST /payment-initiations returns 201 with a payment id and ACTC status."""
    response = client.post(
        "/payment-initiations", json=valid_pain001_body, headers=INITIATE
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ACTC"
    assert body["paymentId"]
    assert body["initiationId"]
    assert body["endToEndId"] == "E2E-0001"


def test_status_roundtrip_from_projection(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """After initiation, the status endpoint returns the projected status."""
    created = client.post(
        "/payment-initiations", json=valid_pain001_body, headers=INITIATE
    ).json()
    payment_id = created["paymentId"]

    response = client.get(
        f"/payment-initiations/{payment_id}/status", headers=READ
    )
    assert response.status_code == 200
    body = response.json()
    assert body["paymentId"] == payment_id
    assert body["status"] == "ACTC"


def test_status_unknown_payment_returns_404(client: TestClient) -> None:
    """Querying an unknown payment id returns 404 (with a valid read token)."""
    response = client.get(
        "/payment-initiations/does-not-exist/status", headers=READ
    )
    assert response.status_code == 404


def test_initiate_rejects_bad_currency(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """A malformed currency is rejected as a 400 domain validation error.

    Structural/type problems yield 422; ISO 20022 domain-rule violations (like a
    bad currency pattern) are caught at the domain boundary and returned as 400.
    """
    valid_pain001_body["transactions"][0]["amount"]["currency"] = "euro"
    response = client.post(
        "/payment-initiations", json=valid_pain001_body, headers=INITIATE
    )
    assert response.status_code == 400


def test_initiate_rejects_empty_transactions(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """A pain.001 with no transactions is rejected."""
    valid_pain001_body["transactions"] = []
    response = client.post(
        "/payment-initiations", json=valid_pain001_body, headers=INITIATE
    )
    assert response.status_code == 422
