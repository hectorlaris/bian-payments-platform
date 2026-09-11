"""End-to-end handoff test across the shared event contract.

Demonstrates that a payment initiated by the Payment Initiation service produces a
``PaymentInitiated`` event whose payload can drive the downstream Payment Order flow
(rebuilding the pain.001, mapping to pacs.008 and pacs.002 via the shared library),
and that the resulting status flows back into the Initiation read model (CQRS).
"""

from __future__ import annotations

from iso20022.mapping import pacs008_to_pacs002, pain001_to_pacs008
from iso20022.messages import Pain001, TransactionStatus
from payment_initiation.events import InMemoryEventPublisher
from payment_initiation.projection import InMemoryStatusProjection
from payment_initiation.service import PaymentInitiationService


def _sample_pain(body: dict) -> Pain001:
    """Rebuild a pain.001 from an event payload using the shared DTOs.

    Args:
        body: The ``pain001`` payload emitted in the PaymentInitiated event.

    Returns:
        A validated pain.001 message.
    """
    return Pain001.model_validate(body)


def test_initiation_to_execution_status_flows_back() -> None:
    """A full happy-path handoff settles and updates the initiation projection."""
    publisher = InMemoryEventPublisher()
    projection = InMemoryStatusProjection()
    service = PaymentInitiationService(publisher, projection)

    # 1. Initiation captures intent and emits PaymentInitiated (status ACTC).
    from iso20022.messages import (
        Account,
        Amount,
        CreditTransferTransaction,
        GroupHeader,
        Party,
    )

    pain = Pain001(
        group_header=GroupHeader(
            message_id="MSG-0001", creation_date_time="2026-01-01T12:00:00Z"
        ),
        payment_information_id="PMTINF-0001",
        transactions=[
            CreditTransferTransaction(
                end_to_end_id="E2E-0001",
                amount=Amount(value="100.00", currency="EUR"),
                debtor=Party(name="Alice", agent_bic="DEUTDEFF"),
                debtor_account=Account(iban="DE89370400440532013000"),
                creditor=Party(name="Bob", agent_bic="NDEAFIHH"),
                creditor_account=Account(iban="FI2112345600000785"),
            )
        ],
    )
    result = service.initiate(pain)
    assert service.get_status(result.payment_id).status is TransactionStatus.ACTC

    # 2. The downstream Order consumes the event payload and drives the flow.
    _, event = publisher.published[0]
    rebuilt = _sample_pain(event.payload["pain001"])
    fitofi_id = "FI" + result.payment_id.replace("-", "")  # 34 chars, ISO-compliant
    pacs008 = pain001_to_pacs008(rebuilt, message_id=fitofi_id)
    pacs002 = pacs008_to_pacs002(pacs008, TransactionStatus.ACSC)

    # 3. The resulting status flows back into the initiation projection (CQRS).
    service.apply_status_update(result.payment_id, pacs002.transaction_status)
    assert service.get_status(result.payment_id).status is TransactionStatus.ACSC


def test_initiation_projection_reflects_failure() -> None:
    """A rejected downstream status is reflected with its reason code."""
    service = PaymentInitiationService(
        InMemoryEventPublisher(), InMemoryStatusProjection()
    )
    service.apply_status_update("p-fail", TransactionStatus.RJCT, reason_code="AM04")

    view = service.get_status("p-fail")
    assert view is not None
    assert view.status is TransactionStatus.RJCT
    assert view.reason_code == "AM04"
