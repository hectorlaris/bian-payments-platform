using Iso20022;

namespace PaymentOrder.Domain;

/// <summary>
/// Event-sourced Payment Order aggregate. State is derived by replaying events;
/// command methods validate lifecycle rules and return the new events to append.
/// </summary>
public sealed class PaymentOrderAggregate
{
    private readonly List<PaymentOrderEvent> _changes = new();

    private PaymentOrderAggregate(string paymentId)
    {
        PaymentId = paymentId;
    }

    /// <summary>The aggregate id (payment id / idempotency key).</summary>
    public string PaymentId { get; private set; }

    /// <summary>The current lifecycle status.</summary>
    public TransactionStatus Status { get; private set; }

    /// <summary>The number of events applied to the aggregate.</summary>
    public int Version { get; private set; }

    /// <summary>The interbank transfer message once the order is created.</summary>
    public Pacs008? Pacs008 { get; private set; }

    /// <summary>Uncommitted events produced by command methods.</summary>
    public IReadOnlyList<PaymentOrderEvent> UncommittedChanges => _changes;

    /// <summary>Rehydrate an aggregate by replaying its persisted events.</summary>
    /// <param name="paymentId">The aggregate id.</param>
    /// <param name="history">The ordered event history.</param>
    /// <returns>The reconstructed aggregate.</returns>
    public static PaymentOrderAggregate Rehydrate(
        string paymentId,
        IEnumerable<PaymentOrderEvent> history)
    {
        var aggregate = new PaymentOrderAggregate(paymentId);
        foreach (var change in history)
        {
            aggregate.Apply(change);
            aggregate.Version++;
        }
        return aggregate;
    }

    /// <summary>Create a new payment order from an accepted initiation.</summary>
    /// <param name="paymentId">The aggregate id.</param>
    /// <param name="pacs008">The interbank transfer built from the initiation.</param>
    /// <returns>A new aggregate carrying the creation event.</returns>
    public static PaymentOrderAggregate Create(string paymentId, Pacs008 pacs008)
    {
        var aggregate = new PaymentOrderAggregate(paymentId);
        aggregate.Raise(new PaymentOrderCreated { PaymentId = paymentId, Pacs008 = pacs008 });
        return aggregate;
    }

    /// <summary>Submit the order for execution (ACSP -> submitted).</summary>
    /// <exception cref="InvalidOperationException">When not in a submittable state.</exception>
    public void Submit()
    {
        EnsureStatus(TransactionStatus.ACSP, nameof(Submit));
        Raise(new PaymentOrderSubmitted { PaymentId = PaymentId });
    }

    /// <summary>Mark the order completed after successful execution.</summary>
    /// <exception cref="InvalidOperationException">When not awaiting settlement.</exception>
    public void Complete()
    {
        EnsureStatus(TransactionStatus.ACSP, nameof(Complete));
        Raise(new PaymentCompleted { PaymentId = PaymentId });
    }

    /// <summary>Mark the order failed with an ISO reason code (compensation).</summary>
    /// <param name="reasonCode">The ISO 20022 status reason code.</param>
    public void Fail(string? reasonCode)
    {
        EnsureStatus(TransactionStatus.ACSP, nameof(Fail));
        Raise(new PaymentFailed { PaymentId = PaymentId, ReasonCode = reasonCode });
    }

    /// <summary>Cancel the order before settlement completes (compensation).</summary>
    /// <param name="reason">The cancellation reason.</param>
    public void Cancel(string? reason)
    {
        if (Status is TransactionStatus.ACSC or TransactionStatus.RJCT)
        {
            throw new InvalidOperationException(
                $"Cannot cancel a payment in status {Status}.");
        }
        Raise(new PaymentCancelled { PaymentId = PaymentId, Reason = reason });
    }

    /// <summary>Clear uncommitted changes after they are persisted.</summary>
    public void MarkChangesCommitted() => _changes.Clear();

    private void Raise(PaymentOrderEvent change)
    {
        Apply(change);
        Version++;
        _changes.Add(change);
    }

    private void Apply(PaymentOrderEvent change)
    {
        switch (change)
        {
            case PaymentOrderCreated created:
                Pacs008 = created.Pacs008;
                Status = TransactionStatus.ACSP;
                break;
            case PaymentOrderSubmitted:
                Status = TransactionStatus.ACSP;
                break;
            case PaymentCompleted:
                Status = TransactionStatus.ACSC;
                break;
            case PaymentFailed:
                Status = TransactionStatus.RJCT;
                break;
            case PaymentCancelled:
                Status = TransactionStatus.RJCT;
                break;
        }
    }

    private void EnsureStatus(TransactionStatus expected, string action)
    {
        if (Status != expected)
        {
            throw new InvalidOperationException(
                $"{action} not allowed in status {Status}; expected {expected}.");
        }
    }
}
