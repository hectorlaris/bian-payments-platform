using Iso20022;
using PaymentOrder.Domain;

namespace PaymentOrder.Application;

/// <summary>
/// Application service for the Payment Order aggregate. Coordinates loading and saving
/// through the event store and keeps the read model projection up to date.
/// </summary>
public sealed class PaymentOrderService
{
    private readonly IEventStore _store;
    private readonly IPaymentOrderReadModel _readModel;

    /// <summary>Create the service with its collaborators.</summary>
    /// <param name="store">The event store.</param>
    /// <param name="readModel">The read-model projection.</param>
    public PaymentOrderService(IEventStore store, IPaymentOrderReadModel readModel)
    {
        _store = store;
        _readModel = readModel;
    }

    /// <summary>
    /// Handle a PaymentInitiated event: build the pacs.008 from the pain.001 and create
    /// the order. Idempotent: if the order already exists, it is returned unchanged.
    /// </summary>
    /// <param name="paymentId">The payment aggregate id.</param>
    /// <param name="pain">The originating pain.001 initiation.</param>
    /// <returns>The current aggregate state.</returns>
    public async Task<PaymentOrderAggregate> HandlePaymentInitiatedAsync(
        string paymentId,
        Pain001 pain)
    {
        var history = await _store.LoadAsync(paymentId);
        if (history.Count > 0)
        {
            return PaymentOrderAggregate.Rehydrate(paymentId, history);
        }

        // ISO 20022 MsgId is limited to 35 chars; a UUID with a prefix would overflow,
        // so compact the payment id (strip hyphens) and use a short prefix.
        var messageId = "FI" + paymentId.Replace("-", string.Empty);
        var pacs008 = MessageMapper.Pain001ToPacs008(pain, messageId);
        var aggregate = PaymentOrderAggregate.Create(paymentId, pacs008);
        await SaveAsync(aggregate);
        return aggregate;
    }

    /// <summary>Load an aggregate by replaying its events.</summary>
    /// <param name="paymentId">The payment aggregate id.</param>
    /// <returns>The rehydrated aggregate, or null when unknown.</returns>
    public async Task<PaymentOrderAggregate?> LoadAsync(string paymentId)
    {
        var history = await _store.LoadAsync(paymentId);
        return history.Count == 0
            ? null
            : PaymentOrderAggregate.Rehydrate(paymentId, history);
    }

    /// <summary>Persist uncommitted changes and refresh the projection.</summary>
    /// <param name="aggregate">The aggregate to save.</param>
    public async Task SaveAsync(PaymentOrderAggregate aggregate)
    {
        var changes = aggregate.UncommittedChanges.ToList();
        if (changes.Count > 0)
        {
            await _store.AppendAsync(aggregate.PaymentId, changes);
            aggregate.MarkChangesCommitted();
        }
        Project(aggregate);
    }

    /// <summary>Return the projected read-model view for a payment id.</summary>
    /// <param name="paymentId">The payment aggregate id.</param>
    /// <returns>The view, or null when unknown.</returns>
    public PaymentOrderView? GetView(string paymentId) => _readModel.Get(paymentId);

    private void Project(PaymentOrderAggregate aggregate)
    {
        var reasonCode = aggregate.Status == TransactionStatus.RJCT ? "AM04" : null;
        _readModel.Upsert(new PaymentOrderView
        {
            PaymentId = aggregate.PaymentId,
            Status = aggregate.Status,
            Version = aggregate.Version,
            ReasonCode = reasonCode,
        });
    }
}
