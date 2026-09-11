using Iso20022;
using PaymentOrder.Application;
using Xunit;

namespace PaymentOrder.Tests;

/// <summary>Tests for the application service, event store, and projection.</summary>
public class ServiceTests
{
    private static PaymentOrderService NewService()
        => new(new InMemoryEventStore(), new InMemoryPaymentOrderReadModel());

    [Fact]
    public async Task HandlePaymentInitiated_CreatesOrder_AndProjectsAcsp()
    {
        var service = NewService();

        var aggregate = await service.HandlePaymentInitiatedAsync("p1", TestData.ValidPain001());

        Assert.Equal(TransactionStatus.ACSP, aggregate.Status);
        var view = service.GetView("p1");
        Assert.NotNull(view);
        Assert.Equal(TransactionStatus.ACSP, view!.Status);
        Assert.Equal(1, view.Version);
    }

    [Fact]
    public async Task HandlePaymentInitiated_IsIdempotent()
    {
        var service = NewService();

        var first = await service.HandlePaymentInitiatedAsync("p1", TestData.ValidPain001());
        var second = await service.HandlePaymentInitiatedAsync("p1", TestData.ValidPain001());

        // Re-handling does not add more events; version stays at 1.
        Assert.Equal(1, first.Version);
        Assert.Equal(1, second.Version);
    }

    [Fact]
    public async Task Load_AfterPersist_ReplaysFromStore()
    {
        var store = new InMemoryEventStore();
        var service = new PaymentOrderService(store, new InMemoryPaymentOrderReadModel());
        await service.HandlePaymentInitiatedAsync("p1", TestData.ValidPain001());

        var reloaded = await service.LoadAsync("p1");

        Assert.NotNull(reloaded);
        Assert.Equal(TransactionStatus.ACSP, reloaded!.Status);
    }

    [Fact]
    public async Task Complete_PersistsAndProjectsAcsc()
    {
        var service = NewService();
        var aggregate = await service.HandlePaymentInitiatedAsync("p1", TestData.ValidPain001());

        aggregate.Complete();
        await service.SaveAsync(aggregate);

        var view = service.GetView("p1");
        Assert.Equal(TransactionStatus.ACSC, view!.Status);
        Assert.Equal(2, view.Version);
    }

    [Fact]
    public async Task Fail_ProjectsRjctWithReason()
    {
        var service = NewService();
        var aggregate = await service.HandlePaymentInitiatedAsync("p1", TestData.ValidPain001());

        aggregate.Fail("AM04");
        await service.SaveAsync(aggregate);

        var view = service.GetView("p1");
        Assert.Equal(TransactionStatus.RJCT, view!.Status);
        Assert.Equal("AM04", view.ReasonCode);
    }
}
