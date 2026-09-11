using Iso20022;
using PaymentExecution;
using Xunit;

namespace PaymentExecution.Tests;

/// <summary>Tests for the Payment Execution service and idempotency.</summary>
public class ExecutionTests
{
    private static Pacs008 Pacs008(string amount = "100.00")
    {
        var transaction = new CreditTransferTransaction(
            EndToEndId: "E2E-0001",
            Amount: new Amount(amount, "EUR"),
            Debtor: new Party("Alice", "DEUTDEFF"),
            DebtorAccount: new Account("DE89370400440532013000"),
            Creditor: new Party("Bob", "NDEAFIHH"),
            CreditorAccount: new Account("FI2112345600000785"));
        return new Pacs008(new GroupHeader("FITOFI-0001", "2026-01-01T12:00:00Z"),
            new[] { transaction });
    }

    private static PaymentExecutionService NewService()
        => new(new MockRailClient(), new InMemoryExecutionStore());

    [Fact]
    public async Task Execute_Success_EmitsAcscPacs002()
    {
        var service = NewService();

        var result = await service.ExecuteAsync("p1", Pacs008("100.00"));

        Assert.False(result.WasReplay);
        Assert.Equal(TransactionStatus.ACSC, result.State.Status);
        Assert.Equal(TransactionStatus.ACSC, result.State.Pacs002.TransactionStatus);
        Assert.Equal("E2E-0001", result.State.Pacs002.OriginalEndToEndId);
        Assert.Equal("mock", result.State.Rail);
    }

    [Fact]
    public async Task Execute_ZeroAmount_EmitsRjctPacs002WithReason()
    {
        var service = NewService();

        var result = await service.ExecuteAsync("p1", Pacs008("0"));

        Assert.Equal(TransactionStatus.RJCT, result.State.Status);
        Assert.Equal("AM04", result.State.Pacs002.StatusReasonCode);
    }

    [Fact]
    public async Task Execute_IsIdempotent_ByPaymentId()
    {
        var service = NewService();

        var first = await service.ExecuteAsync("p1", Pacs008("100.00"));
        var second = await service.ExecuteAsync("p1", Pacs008("100.00"));

        Assert.False(first.WasReplay);
        Assert.True(second.WasReplay);
        Assert.Equal(first.State.Pacs002.OriginalMessageId,
            second.State.Pacs002.OriginalMessageId);
    }

    [Fact]
    public async Task Execute_IdempotentReplay_DoesNotRecontactRail()
    {
        var rail = new CountingRailClient();
        var service = new PaymentExecutionService(rail, new InMemoryExecutionStore());

        await service.ExecuteAsync("p1", Pacs008("100.00"));
        await service.ExecuteAsync("p1", Pacs008("100.00"));

        Assert.Equal(1, rail.CallCount);
    }

    private sealed class CountingRailClient : IRailClient
    {
        public int CallCount { get; private set; }

        public Task<RailOutcome> SendAsync(Pacs008 pacs008)
        {
            CallCount++;
            return Task.FromResult(new RailOutcome(TransactionStatus.ACSC, "mock"));
        }
    }
}
