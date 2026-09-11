"""API request/response models aligned to the OpenAPI contract.

The public contract (apis/payment-initiation.openapi.yaml) uses camelCase field
names. These models accept camelCase input and convert to the internal snake_case
ISO 20022 DTOs from the shared ``iso20022`` library.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from iso20022.messages import (
    Account,
    Amount,
    CreditTransferTransaction,
    GroupHeader,
    Pain001,
    Party,
    TransactionStatus,
)


class _CamelModel(BaseModel):
    """Base model that accepts camelCase input and populates by name."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class AmountIn(_CamelModel):
    """Inbound amount value object."""

    value: str
    currency: str


class AccountIn(_CamelModel):
    """Inbound account value object."""

    iban: str
    name: str | None = None


class PartyIn(_CamelModel):
    """Inbound party value object."""

    name: str
    agent_bic: str | None = None


class GroupHeaderIn(_CamelModel):
    """Inbound group header."""

    message_id: str
    creation_date_time: str


class TransactionIn(_CamelModel):
    """Inbound credit transfer transaction."""

    end_to_end_id: str
    amount: AmountIn
    debtor: PartyIn
    debtor_account: AccountIn
    creditor: PartyIn
    creditor_account: AccountIn
    instruction_id: str | None = None
    remittance_information: str | None = None


class Pain001In(_CamelModel):
    """Inbound pain.001 request body."""

    group_header: GroupHeaderIn
    payment_information_id: str
    transactions: list[TransactionIn] = Field(min_length=1)

    def to_domain(self) -> Pain001:
        """Convert this API model into the internal ISO 20022 DTO.

        Returns:
            A validated ``Pain001`` domain message.
        """
        return Pain001(
            group_header=GroupHeader(
                message_id=self.group_header.message_id,
                creation_date_time=self.group_header.creation_date_time,
            ),
            payment_information_id=self.payment_information_id,
            transactions=[_to_transaction(item) for item in self.transactions],
        )


def _to_transaction(item: TransactionIn) -> CreditTransferTransaction:
    """Map an inbound transaction to the domain DTO.

    Args:
        item: The inbound transaction model.

    Returns:
        The domain credit transfer transaction.
    """
    return CreditTransferTransaction(
        end_to_end_id=item.end_to_end_id,
        amount=Amount(value=item.amount.value, currency=item.amount.currency),
        debtor=Party(name=item.debtor.name, agent_bic=item.debtor.agent_bic),
        debtor_account=Account(
            iban=item.debtor_account.iban, name=item.debtor_account.name
        ),
        creditor=Party(name=item.creditor.name, agent_bic=item.creditor.agent_bic),
        creditor_account=Account(
            iban=item.creditor_account.iban, name=item.creditor_account.name
        ),
        instruction_id=item.instruction_id,
        remittance_information=item.remittance_information,
    )


class PaymentInitiationState(_CamelModel):
    """Response body for the Payment Initiation control record."""

    initiation_id: str
    payment_id: str
    status: TransactionStatus
    end_to_end_id: str


class PaymentStatusResponse(_CamelModel):
    """Response body for the status projection view."""

    payment_id: str
    status: TransactionStatus
    updated_at: str
    reason_code: str | None = None
