"""Unit tests for the Payment Initiation domain service."""

from __future__ import annotations

from iso20022.messages import (
    Account,
    Amount,
    CreditTransferTransaction,
    GroupHeader,
    Pain001,
    Party,
    TransactionStatus,
)
from payment_initiation.events import InMemoryEventPublisher
from payment_initiation.projection import InMemoryStatusProjection
from payment_initiation.service import (
    INITIATION_TOPIC,
    PaymentInitiationService,
)


def _sample_pain() -> Pain001:
    """Build a valid pain.001 for service-level tests.

    Returns:
        A validated pain.001 message.
    """
    transaction = CreditTransferTransaction(
        end_to_end_id="E2E-0001",
        amount=Amount(value="100.00", currency="EUR"),
        debtor=Party(name="Alice", agent_bic="DEUTDEFF"),
        debtor_account=Account(iban="DE89370400440532013000"),
        creditor=Party(name="Bob", agent_bic="NDEAFIHH"),
        creditor_account=Account(iban="FI2112345600000785"),
    )
    return Pain001(
        group_header=GroupHeader(
            message_id="MSG-0001", creation_date_time="2026-01-01T12:00:00Z"
        ),
        payment_information_id="PMTINF-0001",
        transactions=[transaction],
    )


def test_initiate_publishes_event_and_sets_status() -> None:
    """Initiating publishes a PaymentInitiated event and projects ACTC status."""
    publisher = InMemoryEventPublisher()
    projection = InMemoryStatusProjection()
    service = PaymentInitiationService(publisher, projection)

    result = service.initiate(_sample_pain())

    assert result.status is TransactionStatus.ACTC
    assert len(publisher.published) == 1
    topic, event = publisher.published[0]
    assert topic == INITIATION_TOPIC
    assert event.event_type == "PaymentInitiated"
    assert event.payment_id == result.payment_id
    assert event.correlation_id == result.payment_id

    view = projection.get(result.payment_id)
    assert view is not None
    assert view.status is TransactionStatus.ACTC


def test_get_status_unknown_returns_none() -> None:
    """Requesting status for an unknown payment returns None."""
    service = PaymentInitiationService(
        InMemoryEventPublisher(), InMemoryStatusProjection()
    )
    assert service.get_status("unknown") is None
