using Iso20022;
using PaymentOrder.Domain;
using Xunit;

namespace PaymentOrder.Tests;

/// <summary>Given-when-then tests for the event-sourced aggregate.</summary>
public class AggregateTests
{
    [Fact]
    public void Create_RaisesCreatedEvent_AndSetsAcsp()
    {
        var aggregate = PaymentOrderAggregate.Create("p1", TestData.ValidPacs008());

        Assert.Equal(TransactionStatus.ACSP, aggregate.Status);
        Assert.Equal(1, aggregate.Version);
        Assert.Single(aggregate.UncommittedChanges);
        Assert.IsType<PaymentOrderCreated>(aggregate.UncommittedChanges[0]);
    }

    [Fact]
    public void Complete_FromAcsp_SetsAcsc()
    {
        var aggregate = PaymentOrderAggregate.Create("p1", TestData.ValidPacs008());
        aggregate.Complete();

        Assert.Equal(TransactionStatus.ACSC, aggregate.Status);
    }

    [Fact]
    public void Fail_FromAcsp_SetsRjct()
    {
        var aggregate = PaymentOrderAggregate.Create("p1", TestData.ValidPacs008());
        aggregate.Fail("AM04");

        Assert.Equal(TransactionStatus.RJCT, aggregate.Status);
        var failed = Assert.IsType<PaymentFailed>(aggregate.UncommittedChanges[^1]);
        Assert.Equal("AM04", failed.ReasonCode);
    }

    [Fact]
    public void Complete_AfterCompleted_Throws()
    {
        var aggregate = PaymentOrderAggregate.Create("p1", TestData.ValidPacs008());
        aggregate.Complete();

        Assert.Throws<InvalidOperationException>(() => aggregate.Complete());
    }

    [Fact]
    public void Cancel_AfterSettled_Throws()
    {
        var aggregate = PaymentOrderAggregate.Create("p1", TestData.ValidPacs008());
        aggregate.Complete();

        Assert.Throws<InvalidOperationException>(() => aggregate.Cancel("too late"));
    }

    [Fact]
    public void Rehydrate_ReconstructsStateFromEvents()
    {
        var history = new PaymentOrderEvent[]
        {
            new PaymentOrderCreated { PaymentId = "p1", Pacs008 = TestData.ValidPacs008() },
            new PaymentCompleted { PaymentId = "p1" },
        };

        var aggregate = PaymentOrderAggregate.Rehydrate("p1", history);

        Assert.Equal(TransactionStatus.ACSC, aggregate.Status);
        Assert.Equal(2, aggregate.Version);
        Assert.Empty(aggregate.UncommittedChanges);
    }
}
