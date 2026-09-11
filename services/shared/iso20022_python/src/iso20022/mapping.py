"""Mapping functions between ISO 20022 messages in the payment lifecycle.

The flow is pain.001 (initiation) -> pacs.008 (interbank order) -> pacs.002
(status report). Each function is pure: it derives a new message from its input
without mutating shared state.
"""

from __future__ import annotations

from datetime import UTC, datetime

from iso20022.messages import (
    GroupHeader,
    Pacs002,
    Pacs008,
    Pain001,
    TransactionStatus,
)

_MAX_MESSAGE_ID = 35


def _now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string.

    Returns:
        The current instant formatted with a trailing ``Z``.
    """
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _status_message_id(original_message_id: str) -> str:
    """Build an ISO-compliant status message id from the original id.

    The ISO 20022 ``MsgId`` is limited to 35 characters. A ``STS-`` prefix is added
    and the result is truncated to stay within the limit.

    Args:
        original_message_id: The originating pacs.008 message id.

    Returns:
        A message id of at most 35 characters.
    """
    return f"STS-{original_message_id}"[:_MAX_MESSAGE_ID]


def pain001_to_pacs008(pain: Pain001, message_id: str) -> Pacs008:
    """Translate a pain.001 initiation into a pacs.008 interbank transfer.

    Args:
        pain: The validated customer credit transfer initiation.
        message_id: The new FI-to-FI group message id to assign.

    Returns:
        A pacs.008 message carrying the same transactions.
    """
    header = GroupHeader(message_id=message_id, creation_date_time=_now_iso())
    return Pacs008(group_header=header, transactions=list(pain.transactions))


def pacs008_to_pacs002(
    pacs008: Pacs008,
    status: TransactionStatus,
    status_reason_code: str | None = None,
) -> Pacs002:
    """Produce a pacs.002 status report for a pacs.008 transfer.

    Args:
        pacs008: The interbank transfer whose status is being reported.
        status: The resulting transaction status.
        status_reason_code: Optional ISO reason code when rejected.

    Returns:
        A pacs.002 status report correlated to the original message.
    """
    header = GroupHeader(
        message_id=_status_message_id(pacs008.group_header.message_id),
        creation_date_time=_now_iso(),
    )
    first = pacs008.transactions[0]
    return Pacs002(
        group_header=header,
        original_message_id=pacs008.group_header.message_id,
        original_end_to_end_id=first.end_to_end_id,
        transaction_status=status,
        status_reason_code=status_reason_code,
    )
