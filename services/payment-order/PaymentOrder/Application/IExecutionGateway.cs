using Iso20022;

namespace PaymentOrder.Application;

/// <summary>The outcome of asking the execution domain to execute a transfer.</summary>
public sealed record ExecutionGatewayResult(TransactionStatus Status, string? ReasonCode);

/// <summary>
/// Boundary the Saga uses to invoke the Payment Execution Service Domain. At runtime
/// this publishes an ExecutePayment command over Kafka and awaits the resulting
/// pacs.002 event; tests provide an in-process fake.
/// </summary>
public interface IExecutionGateway
{
    /// <summary>Execute the transfer and return its settlement outcome.</summary>
    /// <param name="paymentId">The payment aggregate id (idempotency key).</param>
    /// <param name="pacs008">The interbank transfer to execute.</param>
    /// <returns>The execution outcome.</returns>
    Task<ExecutionGatewayResult> ExecuteAsync(string paymentId, Pacs008 pacs008);
}
