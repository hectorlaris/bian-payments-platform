using Iso20022;

namespace PaymentOrder.Tests;

/// <summary>Factory helpers producing valid sample messages for tests.</summary>
internal static class TestData
{
    /// <summary>Build a minimal valid pain.001 with one credit transfer.</summary>
    /// <returns>A validated pain.001 sample.</returns>
    public static Pain001 ValidPain001()
    {
        var transaction = new CreditTransferTransaction(
            EndToEndId: "E2E-0001",
            Amount: new Amount("100.00", "EUR"),
            Debtor: new Party("Alice Debtor", "DEUTDEFF"),
            DebtorAccount: new Account("DE89370400440532013000", "Alice"),
            Creditor: new Party("Bob Creditor", "NDEAFIHH"),
            CreditorAccount: new Account("FI2112345600000785", "Bob"),
            RemittanceInformation: "Invoice 42");

        return new Pain001(
            new GroupHeader("MSG-0001", "2026-01-01T12:00:00Z"),
            "PMTINF-0001",
            new[] { transaction });
    }

    /// <summary>Build a pacs.008 from the sample pain.001.</summary>
    /// <returns>A pacs.008 interbank transfer.</returns>
    public static Pacs008 ValidPacs008()
        => MessageMapper.Pain001ToPacs008(ValidPain001(), "FITOFI-0001");
}
