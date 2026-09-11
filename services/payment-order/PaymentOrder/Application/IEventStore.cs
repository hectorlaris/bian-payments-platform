using PaymentOrder.Domain;

namespace PaymentOrder.Application;

/// <summary>
/// Append-only event store for Payment Order aggregates. The runtime binds this to
/// Kafka (Amazon MSK); unit tests use the in-memory implementation.
/// </summary>
public interface IEventStore
{
    /// <summary>Append events for an aggregate stream.</summary>
    /// <param name="paymentId">The aggregate id / stream key.</param>
    /// <param name="events">The events to append in order.</param>
    Task AppendAsync(string paymentId, IReadOnlyList<PaymentOrderEvent> events);

    /// <summary>Load the ordered event history for an aggregate stream.</summary>
    /// <param name="paymentId">The aggregate id / stream key.</param>
    /// <returns>The ordered events; empty when the stream does not exist.</returns>
    Task<IReadOnlyList<PaymentOrderEvent>> LoadAsync(string paymentId);
}

/// <summary>In-memory event store used by unit tests and local demos.</summary>
public sealed class InMemoryEventStore : IEventStore
{
    private readonly Dictionary<string, List<PaymentOrderEvent>> _streams = new();

    /// <inheritdoc />
    public Task AppendAsync(string paymentId, IReadOnlyList<PaymentOrderEvent> events)
    {
        if (!_streams.TryGetValue(paymentId, out var stream))
        {
            stream = new List<PaymentOrderEvent>();
            _streams[paymentId] = stream;
        }
        stream.AddRange(events);
        return Task.CompletedTask;
    }

    /// <inheritdoc />
    public Task<IReadOnlyList<PaymentOrderEvent>> LoadAsync(string paymentId)
    {
        IReadOnlyList<PaymentOrderEvent> result = _streams.TryGetValue(paymentId, out var stream)
            ? stream.ToList()
            : Array.Empty<PaymentOrderEvent>();
        return Task.FromResult(result);
    }
}
