using Iso20022;

namespace PaymentOrder.Application;

/// <summary>Read-model row for a payment order (CQRS query side).</summary>
public sealed record PaymentOrderView
{
    /// <summary>The payment aggregate id.</summary>
    public required string PaymentId { get; init; }

    /// <summary>The current lifecycle status.</summary>
    public required TransactionStatus Status { get; init; }

    /// <summary>The number of events applied to the aggregate.</summary>
    public required int Version { get; init; }

    /// <summary>ISO 20022 status reason code when rejected.</summary>
    public string? ReasonCode { get; init; }
}

/// <summary>Query-side projection store for payment orders.</summary>
public interface IPaymentOrderReadModel
{
    /// <summary>Insert or update a projected view.</summary>
    /// <param name="view">The view to store.</param>
    void Upsert(PaymentOrderView view);

    /// <summary>Return the projected view for a payment id, or null.</summary>
    /// <param name="paymentId">The payment aggregate id.</param>
    /// <returns>The stored view or null.</returns>
    PaymentOrderView? Get(string paymentId);
}

/// <summary>In-memory read model backing status queries in the MVP.</summary>
public sealed class InMemoryPaymentOrderReadModel : IPaymentOrderReadModel
{
    private readonly Dictionary<string, PaymentOrderView> _store = new();

    /// <inheritdoc />
    public void Upsert(PaymentOrderView view) => _store[view.PaymentId] = view;

    /// <inheritdoc />
    public PaymentOrderView? Get(string paymentId)
        => _store.TryGetValue(paymentId, out var view) ? view : null;
}
