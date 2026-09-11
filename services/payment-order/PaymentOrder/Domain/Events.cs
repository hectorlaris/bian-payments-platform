using Iso20022;

namespace PaymentOrder.Domain;

/// <summary>Marker base for all Payment Order domain events (Event Sourcing).</summary>
public abstract record PaymentOrderEvent
{
    /// <summary>The payment aggregate id (idempotency key).</summary>
    public required string PaymentId { get; init; }

    /// <summary>When the event occurred (UTC, ISO 8601).</summary>
    public string OccurredAt { get; init; } = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");
}

/// <summary>Raised when a payment order is created from an accepted initiation.</summary>
public sealed record PaymentOrderCreated : PaymentOrderEvent
{
    /// <summary>The interbank transfer message built for this order.</summary>
    public required Pacs008 Pacs008 { get; init; }
}

/// <summary>Raised when a payment order is submitted for execution.</summary>
public sealed record PaymentOrderSubmitted : PaymentOrderEvent
{
}

/// <summary>Raised when execution completes successfully (settled).</summary>
public sealed record PaymentCompleted : PaymentOrderEvent
{
}

/// <summary>Raised when execution fails; carries the ISO reason code.</summary>
public sealed record PaymentFailed : PaymentOrderEvent
{
    /// <summary>ISO 20022 status reason code for the failure.</summary>
    public string? ReasonCode { get; init; }
}

/// <summary>Raised when a payment order is cancelled (compensation).</summary>
public sealed record PaymentCancelled : PaymentOrderEvent
{
    /// <summary>Free-text cancellation reason.</summary>
    public string? Reason { get; init; }
}
