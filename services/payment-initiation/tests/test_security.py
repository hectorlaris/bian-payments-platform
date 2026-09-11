"""Security tests: OAuth2 bearer token and per-operation scope enforcement."""

from __future__ import annotations

import time
from typing import Any

import jwt
from fastapi.testclient import TestClient

from tests.conftest import TEST_SECRET, auth_headers


def test_missing_token_returns_401(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """A request without a bearer token is rejected with 401."""
    response = client.post("/payment-initiations", json=valid_pain001_body)
    assert response.status_code == 401


def test_wrong_scope_returns_403(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """A token lacking the initiate scope is rejected with 403."""
    headers = auth_headers("payments.read")  # missing payments.initiate
    response = client.post(
        "/payment-initiations", json=valid_pain001_body, headers=headers
    )
    assert response.status_code == 403


def test_valid_scope_allows_initiate(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """A token with the initiate scope is authorized (201)."""
    headers = auth_headers("payments.initiate")
    response = client.post(
        "/payment-initiations", json=valid_pain001_body, headers=headers
    )
    assert response.status_code == 201


def test_invalid_signature_returns_401(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """A token signed with the wrong secret is rejected with 401."""
    claims = {
        "sub": "attacker",
        "scope": "payments.initiate",
        "exp": int(time.time()) + 300,
    }
    forged = jwt.encode(claims, "wrong-secret-0123456789abcdef0123456789", algorithm="HS256")
    response = client.post(
        "/payment-initiations",
        json=valid_pain001_body,
        headers={"Authorization": f"Bearer {forged}"},
    )
    assert response.status_code == 401


def test_expired_token_returns_401(
    client: TestClient, valid_pain001_body: dict[str, Any]
) -> None:
    """An expired token is rejected with 401."""
    claims = {
        "sub": "test-client",
        "scope": "payments.initiate",
        "exp": int(time.time()) - 10,
    }
    expired = jwt.encode(claims, TEST_SECRET, algorithm="HS256")
    response = client.post(
        "/payment-initiations",
        json=valid_pain001_body,
        headers={"Authorization": f"Bearer {expired}"},
    )
    assert response.status_code == 401
