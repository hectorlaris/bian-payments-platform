"""End-to-end smoke test of the payment flow across the shared contracts.

This harness exercises the full lifecycle using the installed packages, without
requiring live infrastructure: initiate a payment, map it through the ISO 20022
messages, execute it against the mock rail, and forward the completion to the
integration plane where a notification consumer receives it.

It is intended to run in CI after unit tests, and locally as a demo. Exit code is
non-zero if any step does not produce the expected result.
"""

from __future__ import annotations

import sys

from iso20022.mapping import pacs008_to_pacs002, pain001_to_pacs008
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
from payment_initiation.service import PaymentInitiationService
from payments_integration.bridge import DomainToIntegrationBridge
from payments_integration.eventbridge import InMemoryEventBridgeClient
from payments_integration.notifications import NotificationConsumer, Rule
from rail_adapter import build_rail


def _sample_pain(amount: str) -> Pain001:
    """Build a valid pain.001 for the smoke test.

    Args:
        amount: The transaction amount as a decimal string.

    Returns:
        A validated pain.001 message.
    """
    transaction = CreditTransferTransaction(
        end_to_end_id="E2E-SMOKE",
        amount=Amount(value=amount, currency="EUR"),
        debtor=Party(name="Alice", agent_bic="DEUTDEFF"),
        debtor_account=Account(iban="DE89370400440532013000"),
        creditor=Party(name="Bob", agent_bic="NDEAFIHH"),
        creditor_account=Account(iban="FI2112345600000785"),
    )
    return Pain001(
        group_header=GroupHeader(
            message_id="MSG-SMOKE", creation_date_time="2026-01-01T12:00:00Z"
        ),
        payment_information_id="PMTINF-SMOKE",
        transactions=[transaction],
    )


def run_flow(amount: str) -> TransactionStatus:
    """Run the full payment flow for a given amount and return the final status.

    Args:
        amount: The transaction amount as a decimal string.

    Returns:
        The final ISO 20022 transaction status.
    """
    publisher = InMemoryEventPublisher()
    projection = InMemoryStatusProjection()
    initiation = PaymentInitiationService(publisher, projection)

    result = initiation.initiate(_sample_pain(amount))
    fitofi_id = "FI" + result.payment_id.replace("-", "")
    pacs008 = pain001_to_pacs008(_sample_pain(amount), message_id=fitofi_id)

    outcome = build_rail("mock").send(pacs008)
    pacs002 = pacs008_to_pacs002(pacs008, outcome.status, outcome.reason_code)

    initiation.apply_status_update(
        result.payment_id, pacs002.transaction_status, pacs002.status_reason_code
    )

    integration_client = InMemoryEventBridgeClient()
    bridge = DomainToIntegrationBridge(integration_client)
    consumer = NotificationConsumer(
        rule=Rule(
            source="payments.order",
            detail_types=frozenset({"PaymentCompleted", "PaymentFailed"}),
        )
    )
    event_type = (
        "PaymentCompleted"
        if pacs002.transaction_status is TransactionStatus.ACSC
        else "PaymentFailed"
    )
    bridge.forward(
        {
            "eventType": event_type,
            "paymentId": result.payment_id,
            "payload": {
                "status": str(pacs002.transaction_status),
                "reasonCode": pacs002.status_reason_code,
            },
        }
    )
    for entry in integration_client.entries:
        consumer.handle(entry)

    assert consumer.notifications, "notification consumer received no events"
    return pacs002.transaction_status


def main() -> int:
    """Run happy-path and failure-path smoke flows and report the result.

    Returns:
        Process exit code: ``0`` when both flows behave as expected.
    """
    happy = run_flow("100.00")
    failed = run_flow("0")
    print(f"happy-path status: {happy}")
    print(f"failure-path status: {failed}")
    if happy is not TransactionStatus.ACSC:
        print("FAIL: happy path did not settle (ACSC).")
        return 1
    if failed is not TransactionStatus.RJCT:
        print("FAIL: failure path did not reject (RJCT).")
        return 1
    print("E2E smoke OK: happy path settled, failure path rejected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
