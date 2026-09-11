using Iso20022;

namespace PaymentExecution;

/// <summary>The Payment Execution control record.</summary>
public sealed record ExecutionState
{
    /// <summary>The payment aggregate id (idempotency key).</summary>
    public required string PaymentId { get; init; }

    /// <summary>The resulting transaction status.</summary>
    public required TransactionStatus Status { get; init; }

    /// <summary>The pacs.002 status report produced by execution.</summary>
    public required Pacs002 Pacs002 { get; init; }

    /// <summary>The rail used (mock or sandbox).</summary>
    public required string Rail { get; init; }
}

/// <summary>Persistence for execution records, keyed by payment id (idempotency).</summary>
public interface IExecutionStore
{
    /// <summary>Return an existing execution for a payment id, or null.</summary>
    /// <param name="paymentId">The payment aggregate id.</param>
    /// <returns>The stored execution or null.</returns>
    ExecutionState? Get(string paymentId);

    /// <summary>Store an execution record.</summary>
    /// <param name="state">The execution state to store.</param>
    void Save(ExecutionState state);
}

/// <summary>In-memory execution store used by unit tests and local runs.</summary>
public sealed class InMemoryExecutionStore : IExecutionStore
{
    private readonly Dictionary<string, ExecutionState> _store = new();

    /// <inheritdoc />
    public ExecutionState? Get(string paymentId)
        => _store.TryGetValue(paymentId, out var state) ? state : null;

    /// <inheritdoc />
    public void Save(ExecutionState state) => _store[state.PaymentId] = state;
}
