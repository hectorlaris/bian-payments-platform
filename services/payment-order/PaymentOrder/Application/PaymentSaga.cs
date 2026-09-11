using Iso20022;
using PaymentOrder.Domain;

namespace PaymentOrder.Application;

/// <summary>The lifecycle state of the payment Saga.</summary>
public enum SagaState
{
    /// <summary>No order exists yet.</summary>
    NotStarted,

    /// <summary>Order created; awaiting execution.</summary>
    OrderCreated,

    /// <summary>Submitted to execution; awaiting outcome.</summary>
    AwaitingExecution,

    /// <summary>Settled successfully.</summary>
    Completed,

    /// <summary>Failed and compensated.</summary>
    Failed,
}

/// <summary>The result of running the Saga for a payment.</summary>
public sealed record SagaResult(SagaState State, TransactionStatus Status, string? ReasonCode);

/// <summary>
/// Orchestrated Saga for the payment lifecycle: Initiation -> Order -> Execution.
/// It creates the order, submits it for execution, and applies the execution outcome,
/// compensating (marking the order failed) when execution is rejected.
/// </summary>
public sealed class PaymentSaga
{
    private readonly PaymentOrderService _orders;
    private readonly IExecutionGateway _execution;

    /// <summary>Create the Saga with its collaborators.</summary>
    /// <param name="orders">The Payment Order application service.</param>
    /// <param name="execution">The gateway to the execution domain.</param>
    public PaymentSaga(PaymentOrderService orders, IExecutionGateway execution)
    {
        _orders = orders;
        _execution = execution;
    }

    /// <summary>
    /// Run the Saga for an initiated payment: create the order, execute it, and record
    /// the final outcome with compensation on failure.
    /// </summary>
    /// <param name="paymentId">The payment aggregate id.</param>
    /// <param name="pain">The originating pain.001 initiation.</param>
    /// <returns>The Saga result including the final status.</returns>
    public async Task<SagaResult> RunAsync(string paymentId, Pain001 pain)
    {
        var aggregate = await _orders.HandlePaymentInitiatedAsync(paymentId, pain);
        aggregate.Submit();
        await _orders.SaveAsync(aggregate);

        var outcome = await _execution.ExecuteAsync(paymentId, aggregate.Pacs008!);
        return await ApplyOutcomeAsync(paymentId, outcome);
    }

    private async Task<SagaResult> ApplyOutcomeAsync(
        string paymentId,
        ExecutionGatewayResult outcome)
    {
        var aggregate = await _orders.LoadAsync(paymentId)
            ?? throw new InvalidOperationException($"Unknown payment {paymentId}.");

        if (outcome.Status == TransactionStatus.ACSC)
        {
            aggregate.Complete();
            await _orders.SaveAsync(aggregate);
            return new SagaResult(SagaState.Completed, TransactionStatus.ACSC, null);
        }

        // Compensation: execution failed, mark the order failed.
        aggregate.Fail(outcome.ReasonCode);
        await _orders.SaveAsync(aggregate);
        return new SagaResult(SagaState.Failed, TransactionStatus.RJCT, outcome.ReasonCode);
    }
}
