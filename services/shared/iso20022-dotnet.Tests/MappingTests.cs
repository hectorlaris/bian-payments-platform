using Xunit;

namespace Iso20022.Tests;

/// <summary>Mapping tests for the ISO 20022 lifecycle transformations.</summary>
public class MappingTests
{
    [Fact]
    public void Pain001ToPacs008_PreservesTransactions()
    {
        var pain = TestData.ValidPain001();
        var pacs008 = MessageMapper.Pain001ToPacs008(pain, "FITOFI-0001");

        Assert.Equal("FITOFI-0001", pacs008.GroupHeader.MessageId);
        Assert.Equal(pain.Transactions, pacs008.Transactions);
    }

    [Fact]
    public void Pacs008ToPacs002_Settled_MapsToAcsc()
    {
        var pacs008 = MessageMapper.Pain001ToPacs008(TestData.ValidPain001(), "FITOFI-0001");
        var pacs002 = MessageMapper.Pacs008ToPacs002(pacs008, TransactionStatus.ACSC);

        Assert.Equal(TransactionStatus.ACSC, pacs002.TransactionStatus);
        Assert.Equal("FITOFI-0001", pacs002.OriginalMessageId);
        Assert.Equal("E2E-0001", pacs002.OriginalEndToEndId);
        Assert.Null(pacs002.StatusReasonCode);
    }

    [Fact]
    public void Pacs008ToPacs002_Rejected_CarriesReason()
    {
        var pacs008 = MessageMapper.Pain001ToPacs008(TestData.ValidPain001(), "FITOFI-0001");
        var pacs002 = MessageMapper.Pacs008ToPacs002(pacs008, TransactionStatus.RJCT, "AM04");

        Assert.Equal(TransactionStatus.RJCT, pacs002.TransactionStatus);
        Assert.Equal("AM04", pacs002.StatusReasonCode);
    }

    [Fact]
    public void FullLifecycle_PreservesCorrelation()
    {
        var pain = TestData.ValidPain001();
        var pacs008 = MessageMapper.Pain001ToPacs008(pain, "FITOFI-0001");
        var pacs002 = MessageMapper.Pacs008ToPacs002(pacs008, TransactionStatus.ACSC);

        Assert.Equal(pain.Transactions[0].EndToEndId, pacs002.OriginalEndToEndId);
    }
}
