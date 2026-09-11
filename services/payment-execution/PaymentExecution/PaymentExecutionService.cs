using Iso20022;

namespace PaymentExecution;

/// <summary>Result of an execution attempt, including whether it was a replay.</summary>
public sealed record ExecutionResult(ExecutionState State, bool WasReplay);

/// <summary>
/// Application service for the Payment Execution Service Domain. Executes a payment
/// order against the rail and emits a pacs.002. Idempotent by payment id: repeating
/// an execution returns the existing result rather than contacting the rail again.
/// </summary>
public sealed class PaymentExecutionService
{
    private readonly IRailClient _rail;
    private readonly IExecutionStore _store;

    /// <summary>Create the service with its collaborators.</summary>
    /// <param name="rail">The rail client.</param>
    /// <param name="store">The execution store (idempotency).</param>
    public PaymentExecutionService(IRailClient rail, IExecutionStore store)
    {
        _rail = rail;
        _store = store;
    }

    /// <summary>Execute a payment order idempotently and produce a pacs.002.</summary>
    /// <param name="paymentId">The payment aggregate id / idempotency key.</param>
    /// <param name="pacs008">The interbank transfer to execute.</param>
    /// <returns>The execution result, flagged as a replay when already executed.</returns>
    public async Task<ExecutionResult> ExecuteAsync(string paymentId, Pacs008 pacs008)
    {
        var existing = _store.Get(paymentId);
        if (existing is not null)
        {
            return new ExecutionResult(existing, WasReplay: true);
        }

        var outcome = await _rail.SendAsync(pacs008);
        var pacs002 = MessageMapper.Pacs008ToPacs002(
            pacs008,
            outcome.Status,
            outcome.ReasonCode);

        var state = new ExecutionState
        {
            PaymentId = paymentId,
            Status = outcome.Status,
            Pacs002 = pacs002,
            Rail = outcome.Rail,
        };
        _store.Save(state);
        return new ExecutionResult(state, WasReplay: false);
    }

    /// <summary>Return the stored execution for a payment id, or null.</summary>
    /// <param name="paymentId">The payment aggregate id.</param>
    /// <returns>The execution state or null.</returns>
    public ExecutionState? Get(string paymentId) => _store.Get(paymentId);
}
