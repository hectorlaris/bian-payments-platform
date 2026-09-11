namespace Iso20022;

/// <summary>
/// Pure mapping functions between ISO 20022 messages in the payment lifecycle:
/// pain.001 (initiation) -> pacs.008 (interbank order) -> pacs.002 (status report).
/// </summary>
public static class MessageMapper
{
    /// <summary>Translate a pain.001 initiation into a pacs.008 interbank transfer.</summary>
    /// <param name="pain">The validated customer credit transfer initiation.</param>
    /// <param name="messageId">The new FI-to-FI group message id to assign.</param>
    /// <returns>A pacs.008 message carrying the same transactions.</returns>
    public static Pacs008 Pain001ToPacs008(Pain001 pain, string messageId)
    {
        var header = new GroupHeader(messageId, NowIso());
        return new Pacs008(header, pain.Transactions);
    }

    /// <summary>Produce a pacs.002 status report for a pacs.008 transfer.</summary>
    /// <param name="pacs008">The interbank transfer whose status is reported.</param>
    /// <param name="status">The resulting transaction status.</param>
    /// <param name="statusReasonCode">Optional ISO reason code when rejected.</param>
    /// <returns>A pacs.002 status report correlated to the original message.</returns>
    public static Pacs002 Pacs008ToPacs002(
        Pacs008 pacs008,
        TransactionStatus status,
        string? statusReasonCode = null)
    {
        var header = new GroupHeader(StatusMessageId(pacs008.GroupHeader.MessageId), NowIso());
        var first = pacs008.Transactions[0];
        return new Pacs002(
            header,
            pacs008.GroupHeader.MessageId,
            status,
            first.EndToEndId,
            statusReasonCode);
    }

    private static string NowIso()
        => DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ");

    // ISO 20022 MsgId is limited to 35 characters; prefix then truncate to fit.
    private static string StatusMessageId(string originalMessageId)
    {
        var candidate = $"STS-{originalMessageId}";
        return candidate.Length <= 35 ? candidate : candidate[..35];
    }
}
