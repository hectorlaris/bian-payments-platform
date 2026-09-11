"""Fixtures for the Payment Initiation tests."""

from __future__ import annotations

import time
from typing import Any

import jwt
import pytest
from fastapi.testclient import TestClient

from payment_initiation.app import create_app
from payment_initiation.security import LocalTokenVerifier

# At least 32 bytes to satisfy HS256 key-length recommendations (RFC 7518).
TEST_SECRET = "test-secret-0123456789abcdef0123456789"


def make_token(scopes: str) -> str:
    """Mint an HS256 test token with the given space-delimited scopes.

    Args:
        scopes: Space-delimited OAuth2 scopes to embed.

    Returns:
        A signed JWT string.
    """
    claims = {
        "sub": "test-client",
        "scope": scopes,
        "exp": int(time.time()) + 300,
    }
    return jwt.encode(claims, TEST_SECRET, algorithm="HS256")


def auth_headers(scopes: str) -> dict[str, str]:
    """Build an Authorization header carrying a token with the given scopes.

    Args:
        scopes: Space-delimited OAuth2 scopes.

    Returns:
        A headers dict with a bearer token.
    """
    return {"Authorization": f"Bearer {make_token(scopes)}"}


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client using the local HS256 verifier.

    Returns:
        A configured ``TestClient``.
    """
    app = create_app(token_verifier=LocalTokenVerifier(secret=TEST_SECRET))
    return TestClient(app)


@pytest.fixture
def valid_pain001_body() -> dict[str, Any]:
    """Return a valid pain.001 request body in the contract's camelCase form.

    Returns:
        A JSON-serializable request body dictionary.
    """
    return {
        "groupHeader": {
            "messageId": "MSG-0001",
            "creationDateTime": "2026-01-01T12:00:00Z",
        },
        "paymentInformationId": "PMTINF-0001",
        "transactions": [
            {
                "endToEndId": "E2E-0001",
                "amount": {"value": "100.00", "currency": "EUR"},
                "debtor": {"name": "Alice Debtor", "agentBic": "DEUTDEFF"},
                "debtorAccount": {"iban": "DE89370400440532013000", "name": "Alice"},
                "creditor": {"name": "Bob Creditor", "agentBic": "NDEAFIHH"},
                "creditorAccount": {"iban": "FI2112345600000785", "name": "Bob"},
                "remittanceInformation": "Invoice 42",
            }
        ],
    }
