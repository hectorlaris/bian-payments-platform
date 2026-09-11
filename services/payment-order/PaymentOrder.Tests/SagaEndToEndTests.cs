using Iso20022;
using PaymentExecution;
using PaymentOrder.Application;
using Xunit;

namespace PaymentOrder.Tests;

/// <summary>
/// End-to-end Saga tests wiring the Payment Order Saga to the real Payment Execution
/// service through a gateway adapter. Proves the happy path and the failure path with
/// compensation across both bounded contexts.
/// </summary>
public class SagaEndToEndTests
{
    /// <summary>Adapter bridging the Order Saga to the real Execution service.</summary>
    private sealed class ExecutionServiceGateway : IExecutionGateway
    {
        private readonly PaymentExecutionService _execution;

        public ExecutionServiceGateway(PaymentExecutionService execution)
            => _execution = execution;

        public async Task<ExecutionGatewayResult> ExecuteAsync(string paymentId, Pacs008 pacs008)
        {
            var result = await _execution.ExecuteAsync(paymentId, pacs008);
            return new ExecutionGatewayResult(result.State.Status, result.State.Pacs002.StatusReasonCode);
        }
    }

    private static (PaymentSaga saga, PaymentOrderService orders) Build()
    {
        var orders = new PaymentOrderService(
            new InMemoryEventStore(), new InMemoryPaymentOrderReadModel());
        var execution = new PaymentExecutionService(
            new MockRailClient(), new InMemoryExecutionStore());
        var saga = new PaymentSaga(orders, new ExecutionServiceGateway(execution));
        return (saga, orders);
    }

    [Fact]
    public async Task HappyPath_SettlesEndToEnd()
    {
        var (saga, orders) = Build();

        var result = await saga.RunAsync("p1", TestData.ValidPain001());

        Assert.Equal(SagaState.Completed, result.State);
        Assert.Equal(TransactionStatus.ACSC, result.Status);

        var view = orders.GetView("p1");
        Assert.Equal(TransactionStatus.ACSC, view!.Status);
    }

    [Fact]
    public async Task FailurePath_CompensatesToRjct()
    {
        var (saga, orders) = Build();

        // A zero-amount transfer is rejected by the mock rail, triggering compensation.
        var pain = ZeroAmountPain();
        var result = await saga.RunAsync("p2", pain);

        Assert.Equal(SagaState.Failed, result.State);
        Assert.Equal(TransactionStatus.RJCT, result.Status);
        Assert.Equal("AM04", result.ReasonCode);

        var view = orders.GetView("p2");
        Assert.Equal(TransactionStatus.RJCT, view!.Status);
        Assert.Equal("AM04", view.ReasonCode);
    }

    private static Pain001 ZeroAmountPain()
    {
        var transaction = new CreditTransferTransaction(
            EndToEndId: "E2E-ZERO",
            Amount: new Amount("0", "EUR"),
            Debtor: new Party("Alice", "DEUTDEFF"),
            DebtorAccount: new Account("DE89370400440532013000"),
            Creditor: new Party("Bob", "NDEAFIHH"),
            CreditorAccount: new Account("FI2112345600000785"));
        return new Pain001(
            new GroupHeader("MSG-ZERO", "2026-01-01T12:00:00Z"),
            "PMTINF-ZERO",
            new[] { transaction });
    }
}
