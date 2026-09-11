using Xunit;

namespace Iso20022.Tests;

/// <summary>Validation tests for the ISO 20022 DTOs.</summary>
public class ValidationTests
{
    [Fact]
    public void ValidPain001_HasNoErrors()
    {
        var errors = MessageValidator.Validate(TestData.ValidPain001());
        Assert.Empty(errors);
    }

    [Fact]
    public void Amount_RejectsNonNumericValue()
    {
        var pain = TestData.ValidPain001() with
        {
            Transactions = new[]
            {
                TestData.ValidPain001().Transactions[0] with
                {
                    Amount = new Amount("abc", "EUR")
                }
            }
        };

        var errors = MessageValidator.Validate(pain);
        Assert.NotEmpty(errors);
    }

    [Fact]
    public void Account_RejectsBadIban()
    {
        var tx = TestData.ValidPain001().Transactions[0] with
        {
            DebtorAccount = new Account("12345")
        };
        var pain = TestData.ValidPain001() with { Transactions = new[] { tx } };

        var errors = MessageValidator.Validate(pain);
        Assert.NotEmpty(errors);
    }

    [Fact]
    public void Party_RejectsBadBic()
    {
        var tx = TestData.ValidPain001().Transactions[0] with
        {
            Creditor = new Party("Bob", "lowercase")
        };
        var pain = TestData.ValidPain001() with { Transactions = new[] { tx } };

        var errors = MessageValidator.Validate(pain);
        Assert.NotEmpty(errors);
    }
}
