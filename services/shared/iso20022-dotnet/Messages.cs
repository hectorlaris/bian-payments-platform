using System.ComponentModel.DataAnnotations;

namespace Iso20022;

/// <summary>ISO 20022 transaction status vocabulary (MVP subset).</summary>
public enum TransactionStatus
{
    /// <summary>AcceptedTechnicalValidation.</summary>
    ACTC,

    /// <summary>AcceptedSettlementInProcess.</summary>
    ACSP,

    /// <summary>AcceptedSettlementCompleted.</summary>
    ACSC,

    /// <summary>Rejected.</summary>
    RJCT
}

/// <summary>An amount of money with an ISO 4217 currency.</summary>
public sealed record Amount(
    [property: RegularExpression(@"^\d{1,15}(\.\d{1,5})?$")] string Value,
    [property: RegularExpression("^[A-Z]{3}$")] string Currency);

/// <summary>A cash account identified by IBAN.</summary>
public sealed record Account(
    [property: RegularExpression(@"^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$")] string Iban,
    [property: MaxLength(140)] string? Name = null);

/// <summary>A debtor or creditor party.</summary>
public sealed record Party(
    [property: Required, MaxLength(140)] string Name,
    [property: RegularExpression("^[A-Z0-9]{8}([A-Z0-9]{3})?$")] string? AgentBic = null);

/// <summary>ISO 20022 group header (GrpHdr).</summary>
public sealed record GroupHeader(
    [property: Required, MaxLength(35)] string MessageId,
    [property: Required] string CreationDateTime);

/// <summary>A single credit transfer instruction.</summary>
public sealed record CreditTransferTransaction(
    [property: Required, MaxLength(35)] string EndToEndId,
    [property: Required] Amount Amount,
    [property: Required] Party Debtor,
    [property: Required] Account DebtorAccount,
    [property: Required] Party Creditor,
    [property: Required] Account CreditorAccount,
    [property: MaxLength(35)] string? InstructionId = null,
    [property: MaxLength(140)] string? RemittanceInformation = null);

/// <summary>ISO 20022 pain.001 CustomerCreditTransferInitiation (MVP subset).</summary>
public sealed record Pain001(
    [property: Required] GroupHeader GroupHeader,
    [property: Required, MaxLength(35)] string PaymentInformationId,
    [property: Required, MinLength(1)] IReadOnlyList<CreditTransferTransaction> Transactions);

/// <summary>ISO 20022 pacs.008 FIToFICustomerCreditTransfer (MVP subset).</summary>
public sealed record Pacs008(
    [property: Required] GroupHeader GroupHeader,
    [property: Required, MinLength(1)] IReadOnlyList<CreditTransferTransaction> Transactions);

/// <summary>ISO 20022 pacs.002 FIToFIPaymentStatusReport (MVP subset).</summary>
public sealed record Pacs002(
    [property: Required] GroupHeader GroupHeader,
    [property: Required, MaxLength(35)] string OriginalMessageId,
    TransactionStatus TransactionStatus,
    [property: MaxLength(35)] string? OriginalEndToEndId = null,
    [property: MaxLength(35)] string? StatusReasonCode = null);
