"""Tests for the rail adapter mock/sandbox strategy."""

from __future__ import annotations

import pytest

from iso20022.mapping import pain001_to_pacs008
from iso20022.messages import (
    Account,
    Amount,
    CreditTransferTransaction,
    GroupHeader,
    Pacs008,
    Pain001,
    Party,
    TransactionStatus,
)
from rail_adapter import MockRail, SandboxRail, build_rail


def _pacs008(amount: str = "100.00") -> Pacs008:
    """Build a pacs.008 with a configurable amount.

    Args:
        amount: The transaction amount as a decimal string.

    Returns:
        A pacs.008 interbank transfer.
    """
    transaction = CreditTransferTransaction(
        end_to_end_id="E2E-0001",
        amount=Amount(value=amount, currency="EUR"),
        debtor=Party(name="Alice", agent_bic="DEUTDEFF"),
        debtor_account=Account(iban="DE89370400440532013000"),
        creditor=Party(name="Bob", agent_bic="NDEAFIHH"),
        creditor_account=Account(iban="FI2112345600000785"),
    )
    pain = Pain001(
        group_header=GroupHeader(
            message_id="MSG-0001", creation_date_time="2026-01-01T12:00:00Z"
        ),
        payment_information_id="PMTINF-0001",
        transactions=[transaction],
    )
    return pain001_to_pacs008(pain, message_id="FITOFI-0001")


def test_mock_rail_settles_positive_amount() -> None:
    """The mock rail settles a positive-amount transfer (ACSC)."""
    outcome = MockRail().send(_pacs008("100.00"))
    assert outcome.status is TransactionStatus.ACSC
    assert outcome.rail == "mock"
    assert outcome.reason_code is None


def test_mock_rail_rejects_zero_amount() -> None:
    """The mock rail rejects a zero-amount transfer (RJCT with reason)."""
    outcome = MockRail().send(_pacs008("0"))
    assert outcome.status is TransactionStatus.RJCT
    assert outcome.reason_code == "AM04"


def test_build_rail_defaults_to_mock() -> None:
    """The factory returns the mock rail by default."""
    assert isinstance(build_rail(), MockRail)


def test_build_rail_sandbox_selected() -> None:
    """The factory returns the sandbox rail when requested."""
    assert isinstance(build_rail("sandbox"), SandboxRail)


def test_build_rail_unknown_raises() -> None:
    """An unknown rail selector raises ValueError."""
    with pytest.raises(ValueError):
        build_rail("unknown")


def test_sandbox_rail_not_configured_raises() -> None:
    """The sandbox rail raises until an integration is configured."""
    with pytest.raises(NotImplementedError):
        SandboxRail().send(_pacs008("100.00"))
