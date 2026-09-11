"""Shared pytest fixtures for the iso20022 library tests."""

from __future__ import annotations

import pytest

from iso20022.messages import (
    Account,
    Amount,
    CreditTransferTransaction,
    GroupHeader,
    Pain001,
    Party,
)


@pytest.fixture
def valid_pain001() -> Pain001:
    """Return a minimal valid pain.001 message for use across tests.

    Returns:
        A validated pain.001 with a single credit transfer transaction.
    """
    transaction = CreditTransferTransaction(
        end_to_end_id="E2E-0001",
        amount=Amount(value="100.00", currency="EUR"),
        debtor=Party(name="Alice Debtor", agent_bic="DEUTDEFF"),
        debtor_account=Account(iban="DE89370400440532013000", name="Alice"),
        creditor=Party(name="Bob Creditor", agent_bic="NDEAFIHH"),
        creditor_account=Account(iban="FI2112345600000785", name="Bob"),
        remittance_information="Invoice 42",
    )
    return Pain001(
        group_header=GroupHeader(
            message_id="MSG-0001",
            creation_date_time="2026-01-01T12:00:00Z",
        ),
        payment_information_id="PMTINF-0001",
        transactions=[transaction],
    )
