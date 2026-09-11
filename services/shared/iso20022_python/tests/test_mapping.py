"""Mapping tests for the ISO 20022 lifecycle transformations."""

from __future__ import annotations

from iso20022.mapping import pacs008_to_pacs002, pain001_to_pacs008
from iso20022.messages import Pain001, TransactionStatus


def test_pain001_to_pacs008_preserves_transactions(valid_pain001: Pain001) -> None:
    """Mapping to pacs.008 carries the transactions and assigns the new id."""
    pacs008 = pain001_to_pacs008(valid_pain001, message_id="FITOFI-0001")
    assert pacs008.group_header.message_id == "FITOFI-0001"
    assert pacs008.transactions == valid_pain001.transactions


def test_pacs008_to_pacs002_settled(valid_pain001: Pain001) -> None:
    """A settled status maps to ACSC and correlates the end-to-end id."""
    pacs008 = pain001_to_pacs008(valid_pain001, message_id="FITOFI-0001")
    pacs002 = pacs008_to_pacs002(pacs008, TransactionStatus.ACSC)
    assert pacs002.transaction_status is TransactionStatus.ACSC
    assert pacs002.original_message_id == "FITOFI-0001"
    assert pacs002.original_end_to_end_id == "E2E-0001"
    assert pacs002.status_reason_code is None


def test_pacs008_to_pacs002_rejected_carries_reason(valid_pain001: Pain001) -> None:
    """A rejected status carries the ISO reason code."""
    pacs008 = pain001_to_pacs008(valid_pain001, message_id="FITOFI-0001")
    pacs002 = pacs008_to_pacs002(
        pacs008, TransactionStatus.RJCT, status_reason_code="AM04"
    )
    assert pacs002.transaction_status is TransactionStatus.RJCT
    assert pacs002.status_reason_code == "AM04"


def test_full_lifecycle_roundtrip(valid_pain001: Pain001) -> None:
    """The full pain.001 -> pacs.008 -> pacs.002 chain preserves correlation."""
    pacs008 = pain001_to_pacs008(valid_pain001, message_id="FITOFI-0001")
    pacs002 = pacs008_to_pacs002(pacs008, TransactionStatus.ACSC)
    original_e2e = valid_pain001.transactions[0].end_to_end_id
    assert pacs002.original_end_to_end_id == original_e2e
