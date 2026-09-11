"""Validation tests for the ISO 20022 DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from iso20022.messages import Account, Amount, Pain001, Party


def test_valid_pain001_builds(valid_pain001: Pain001) -> None:
    """A well-formed pain.001 validates and preserves its end-to-end id."""
    assert valid_pain001.transactions[0].end_to_end_id == "E2E-0001"


def test_amount_rejects_non_numeric() -> None:
    """An amount with non-numeric text is rejected."""
    with pytest.raises(ValidationError):
        Amount(value="abc", currency="EUR")


def test_amount_rejects_bad_currency() -> None:
    """A currency that is not a 3-letter ISO code is rejected."""
    with pytest.raises(ValidationError):
        Amount(value="10.00", currency="euro")


def test_account_rejects_bad_iban() -> None:
    """An IBAN that fails the structural pattern is rejected."""
    with pytest.raises(ValidationError):
        Account(iban="12345")


def test_party_rejects_bad_bic() -> None:
    """A malformed BIC is rejected."""
    with pytest.raises(ValidationError):
        Party(name="X", agent_bic="lowercase")


def test_pain001_requires_at_least_one_transaction() -> None:
    """A pain.001 with no transactions is rejected."""
    with pytest.raises(ValidationError):
        Pain001(
            group_header={
                "message_id": "M",
                "creation_date_time": "2026-01-01T12:00:00Z",
            },
            payment_information_id="P",
            transactions=[],
        )


def test_models_reject_unknown_fields() -> None:
    """Unknown fields are rejected (extra=forbid)."""
    with pytest.raises(ValidationError):
        Amount(value="10.00", currency="EUR", unexpected="x")


def test_models_are_immutable(valid_pain001: Pain001) -> None:
    """DTOs are frozen; attribute assignment raises."""
    with pytest.raises(ValidationError):
        valid_pain001.payment_information_id = "changed"
