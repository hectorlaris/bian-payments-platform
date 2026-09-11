"""Read-model projection for payment status (CQRS query side).

For the MVP this is an in-memory stub. In later tasks it is replaced by a
projection fed from the Payment Order event stream.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from iso20022.messages import TransactionStatus


@dataclass(frozen=True)
class PaymentStatusView:
    """The read-model view of a payment's current status."""

    payment_id: str
    status: TransactionStatus
    updated_at: str
    reason_code: str | None = None


class StatusProjection(ABC):
    """Abstraction over the payment status read model."""

    @abstractmethod
    def get(self, payment_id: str) -> PaymentStatusView | None:
        """Return the status view for a payment, or ``None`` if unknown.

        Args:
            payment_id: The payment aggregate id.

        Returns:
            The current status view or ``None``.
        """
        raise NotImplementedError

    @abstractmethod
    def upsert(self, view: PaymentStatusView) -> None:
        """Insert or update the status view for a payment.

        Args:
            view: The status view to store.
        """
        raise NotImplementedError


class InMemoryStatusProjection(StatusProjection):
    """In-memory projection backing status queries in the MVP."""

    def __init__(self) -> None:
        """Initialize the projection with an empty store."""
        self._store: dict[str, PaymentStatusView] = {}

    def get(self, payment_id: str) -> PaymentStatusView | None:
        """Return the stored status view for a payment id.

        Args:
            payment_id: The payment aggregate id.

        Returns:
            The stored view or ``None`` when not present.
        """
        return self._store.get(payment_id)

    def upsert(self, view: PaymentStatusView) -> None:
        """Store the status view keyed by payment id.

        Args:
            view: The status view to store.
        """
        self._store[view.payment_id] = view
