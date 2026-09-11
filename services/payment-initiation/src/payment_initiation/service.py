"""Payment Initiation domain service.

Coordinates the Initiate use case: validate the pain.001, register the initial
status in the projection, and publish the ``PaymentInitiated`` domain event.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from iso20022.messages import Pain001, TransactionStatus
from payment_initiation.events import DomainEvent, EventPublisher
from payment_initiation.projection import (
    PaymentStatusView,
    StatusProjection,
)

INITIATION_TOPIC = "payments.initiation.v1"


@dataclass(frozen=True)
class InitiationResult:
    """The outcome of initiating a payment."""

    initiation_id: str
    payment_id: str
    status: TransactionStatus
    end_to_end_id: str


class PaymentInitiationService:
    """Application service for the Payment Initiation control record."""

    def __init__(
        self,
        publisher: EventPublisher,
        projection: StatusProjection,
    ) -> None:
        """Initialize the service with its collaborators.

        Args:
            publisher: The domain event publisher.
            projection: The status read-model projection.
        """
        self._publisher = publisher
        self._projection = projection

    def initiate(self, pain: Pain001) -> InitiationResult:
        """Initiate a payment from a validated pain.001 message.

        Args:
            pain: The validated customer credit transfer initiation.

        Returns:
            The initiation result including the assigned payment id and status.
        """
        payment_id = str(uuid.uuid4())
        initiation_id = str(uuid.uuid4())
        end_to_end_id = pain.transactions[0].end_to_end_id
        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        self._projection.upsert(
            PaymentStatusView(
                payment_id=payment_id,
                status=TransactionStatus.ACTC,
                updated_at=now,
            )
        )
        self._publisher.publish(
            INITIATION_TOPIC,
            DomainEvent(
                event_type="PaymentInitiated",
                payment_id=payment_id,
                correlation_id=payment_id,
                payload={
                    "initiationId": initiation_id,
                    "pain001": pain.model_dump(mode="json"),
                },
            ),
        )
        return InitiationResult(
            initiation_id=initiation_id,
            payment_id=payment_id,
            status=TransactionStatus.ACTC,
            end_to_end_id=end_to_end_id,
        )

    def get_status(self, payment_id: str) -> PaymentStatusView | None:
        """Return the current status view for a payment.

        Args:
            payment_id: The payment aggregate id.

        Returns:
            The status view, or ``None`` if unknown.
        """
        return self._projection.get(payment_id)

    def apply_status_update(
        self,
        payment_id: str,
        status: TransactionStatus,
        reason_code: str | None = None,
    ) -> None:
        """Update the status projection from a downstream domain event.

        This is invoked when Payment Order publishes lifecycle events (order created,
        completed, failed), keeping the Initiation read model in sync (CQRS).

        Args:
            payment_id: The payment aggregate id.
            status: The new lifecycle status.
            reason_code: Optional ISO reason code when rejected.
        """
        now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._projection.upsert(
            PaymentStatusView(
                payment_id=payment_id,
                status=status,
                updated_at=now,
                reason_code=reason_code,
            )
        )
