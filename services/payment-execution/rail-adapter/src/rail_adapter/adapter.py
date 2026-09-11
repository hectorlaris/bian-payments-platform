"""Rail adapter abstraction and implementations.

The adapter pattern isolates the Payment Execution domain from the concrete payment
rail. ``MockRail`` is the default for the MVP; ``SandboxRail`` is a placeholder for an
external sandbox selected via configuration/feature flag.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from iso20022.messages import Pacs008, TransactionStatus


@dataclass(frozen=True)
class RailOutcome:
    """The outcome of submitting a transfer to a rail."""

    status: TransactionStatus
    reason_code: str | None = None
    rail: str = "mock"


class RailAdapter(ABC):
    """Abstraction over a payment rail."""

    name: str = "abstract"

    @abstractmethod
    def send(self, pacs008: Pacs008) -> RailOutcome:
        """Submit a pacs.008 transfer to the rail and return the outcome.

        Args:
            pacs008: The interbank transfer to submit.

        Returns:
            The settlement outcome.
        """
        raise NotImplementedError


class MockRail(RailAdapter):
    """Deterministic in-process rail used for local runs and tests.

    Business rule for the mock: transfers with a zero amount are rejected; all
    other well-formed transfers settle successfully. This gives a predictable
    happy path and an easy failure path for demos and tests.
    """

    name = "mock"

    def send(self, pacs008: Pacs008) -> RailOutcome:
        """Settle any positive-amount transfer; reject zero amounts.

        Args:
            pacs008: The interbank transfer to submit.

        Returns:
            ``ACSC`` on success, or ``RJCT`` with reason ``AM04`` for zero amounts.
        """
        amount = pacs008.transactions[0].amount.value
        if _is_zero(amount):
            return RailOutcome(
                status=TransactionStatus.RJCT,
                reason_code="AM04",
                rail=self.name,
            )
        return RailOutcome(status=TransactionStatus.ACSC, rail=self.name)


class SandboxRail(RailAdapter):
    """Placeholder for an external sandbox rail.

    Wiring to a concrete sandbox (endpoint, credentials, message translation) is an
    integration task beyond the MVP. Until configured it raises, so misconfiguration
    fails fast rather than silently using the wrong rail.
    """

    name = "sandbox"

    def __init__(self, endpoint: str | None = None) -> None:
        """Store the sandbox endpoint.

        Args:
            endpoint: The external sandbox endpoint URL, if any.
        """
        self.endpoint = endpoint

    def send(self, pacs008: Pacs008) -> RailOutcome:
        """Raise until the external sandbox integration is configured.

        Args:
            pacs008: The interbank transfer to submit.

        Raises:
            NotImplementedError: Always, until wired to a real sandbox.
        """
        raise NotImplementedError(
            "SandboxRail is not configured; set RAIL=mock or provide an integration."
        )


def _is_zero(amount: str) -> bool:
    """Return whether a decimal-string amount is zero.

    Args:
        amount: The amount as a decimal string.

    Returns:
        ``True`` when the amount parses to zero.
    """
    try:
        return float(amount) == 0.0
    except ValueError:
        return False


def build_rail(rail: str = "mock", endpoint: str | None = None) -> RailAdapter:
    """Build a rail adapter from configuration.

    Args:
        rail: The rail selector (``mock`` or ``sandbox``).
        endpoint: Optional endpoint for the sandbox rail.

    Returns:
        The configured rail adapter.

    Raises:
        ValueError: When the selector is unknown.
    """
    normalized = rail.strip().lower()
    if normalized == "mock":
        return MockRail()
    if normalized == "sandbox":
        return SandboxRail(endpoint=endpoint)
    raise ValueError(f"Unknown rail '{rail}'; expected 'mock' or 'sandbox'.")
