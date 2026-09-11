"""ISO 20022 message DTOs (MVP subset) with validation.

These Pydantic models mirror the OpenAPI component schemas in
``apis/components/iso20022.yaml``. They validate the fields required for a
credit-transfer happy path plus status reporting. JSON is the internal
serialization format; XML is produced at the edges by dedicated adapters.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

# Shared regular expressions aligned with the OpenAPI schemas.
_AMOUNT_PATTERN = r"^\d{1,15}(\.\d{1,5})?$"
_CURRENCY_PATTERN = r"^[A-Z]{3}$"
_IBAN_PATTERN = r"^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$"
_BIC_PATTERN = r"^[A-Z0-9]{8}([A-Z0-9]{3})?$"


class TransactionStatus(StrEnum):
    """ISO 20022 transaction status vocabulary (MVP subset)."""

    ACTC = "ACTC"  # AcceptedTechnicalValidation
    ACSP = "ACSP"  # AcceptedSettlementInProcess
    ACSC = "ACSC"  # AcceptedSettlementCompleted
    RJCT = "RJCT"  # Rejected


class _Frozen(BaseModel):
    """Base model: immutable and rejecting unknown fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Amount(_Frozen):
    """An amount of money with an ISO 4217 currency."""

    value: str = Field(pattern=_AMOUNT_PATTERN)
    currency: str = Field(pattern=_CURRENCY_PATTERN)


class Account(_Frozen):
    """A cash account identified by IBAN."""

    iban: str = Field(pattern=_IBAN_PATTERN)
    name: str | None = Field(default=None, max_length=140)


class Party(_Frozen):
    """A debtor or creditor party."""

    name: str = Field(max_length=140)
    agent_bic: str | None = Field(default=None, pattern=_BIC_PATTERN)


class GroupHeader(_Frozen):
    """ISO 20022 group header (GrpHdr)."""

    message_id: str = Field(max_length=35)
    creation_date_time: str


class CreditTransferTransaction(_Frozen):
    """A single credit transfer instruction."""

    end_to_end_id: str = Field(max_length=35)
    amount: Amount
    debtor: Party
    debtor_account: Account
    creditor: Party
    creditor_account: Account
    instruction_id: str | None = Field(default=None, max_length=35)
    remittance_information: str | None = Field(default=None, max_length=140)


class Pain001(_Frozen):
    """ISO 20022 pain.001 CustomerCreditTransferInitiation (MVP subset)."""

    group_header: GroupHeader
    payment_information_id: str = Field(max_length=35)
    transactions: list[CreditTransferTransaction] = Field(min_length=1)


class Pacs008(_Frozen):
    """ISO 20022 pacs.008 FIToFICustomerCreditTransfer (MVP subset)."""

    group_header: GroupHeader
    transactions: list[CreditTransferTransaction] = Field(min_length=1)


class Pacs002(_Frozen):
    """ISO 20022 pacs.002 FIToFIPaymentStatusReport (MVP subset)."""

    group_header: GroupHeader
    original_message_id: str = Field(max_length=35)
    transaction_status: TransactionStatus
    original_end_to_end_id: str | None = Field(default=None, max_length=35)
    status_reason_code: str | None = Field(default=None, max_length=35)
