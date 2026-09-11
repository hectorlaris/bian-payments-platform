using Iso20022;

namespace PaymentExecution;

/// <summary>The outcome returned by a payment rail for a submitted transfer.</summary>
public sealed record RailOutcome(
    TransactionStatus Status,
    string Rail,
    string? ReasonCode = null);

/// <summary>
/// Abstraction over the payment rail. At runtime this is backed by the Python rail
/// adapter (mock or external sandbox) invoked over HTTP; unit tests use a fake.
/// </summary>
public interface IRailClient
{
    /// <summary>Submit a pacs.008 transfer to the rail.</summary>
    /// <param name="pacs008">The interbank transfer.</param>
    /// <returns>The settlement outcome.</returns>
    Task<RailOutcome> SendAsync(Pacs008 pacs008);
}

/// <summary>
/// In-process fake mirroring the Python mock rail rule: zero-amount transfers are
/// rejected, all other positive amounts settle. Used by unit tests.
/// </summary>
public sealed class MockRailClient : IRailClient
{
    /// <inheritdoc />
    public Task<RailOutcome> SendAsync(Pacs008 pacs008)
    {
        var amount = pacs008.Transactions[0].Amount.Value;
        var settles = decimal.TryParse(
            amount,
            System.Globalization.NumberStyles.Any,
            System.Globalization.CultureInfo.InvariantCulture,
            out var parsed) && parsed > 0m;

        var outcome = settles
            ? new RailOutcome(TransactionStatus.ACSC, "mock")
            : new RailOutcome(TransactionStatus.RJCT, "mock", "AM04");
        return Task.FromResult(outcome);
    }
}
