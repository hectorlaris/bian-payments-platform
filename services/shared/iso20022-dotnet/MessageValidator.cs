using System.Collections;
using System.ComponentModel.DataAnnotations;

namespace Iso20022;

/// <summary>
/// Recursively validates ISO 20022 DTOs using their DataAnnotations attributes.
/// DataAnnotations does not descend into nested objects or collections by default,
/// so this walker validates the full object graph.
/// </summary>
public static class MessageValidator
{
    /// <summary>Validate an object graph and return all validation results.</summary>
    /// <param name="instance">The root object to validate.</param>
    /// <returns>The list of validation errors; empty when valid.</returns>
    public static IReadOnlyList<ValidationResult> Validate(object instance)
    {
        var results = new List<ValidationResult>();
        var visited = new HashSet<object>(ReferenceEqualityComparer.Instance);
        ValidateGraph(instance, results, visited);
        return results;
    }

    /// <summary>Throws when the object graph is invalid.</summary>
    /// <param name="instance">The root object to validate.</param>
    /// <exception cref="ValidationException">Thrown on the first error.</exception>
    public static void EnsureValid(object instance)
    {
        var errors = Validate(instance);
        if (errors.Count > 0)
        {
            throw new ValidationException(errors[0].ErrorMessage);
        }
    }

    private static void ValidateGraph(
        object? instance,
        List<ValidationResult> results,
        HashSet<object> visited)
    {
        if (instance is null || instance is string || instance.GetType().IsValueType)
        {
            return;
        }

        if (!visited.Add(instance))
        {
            return;
        }

        var context = new ValidationContext(instance);
        Validator.TryValidateObject(instance, context, results, validateAllProperties: true);

        if (instance is IEnumerable enumerable)
        {
            foreach (var item in enumerable)
            {
                ValidateGraph(item, results, visited);
            }
            return;
        }

        foreach (var property in instance.GetType().GetProperties())
        {
            if (property.GetIndexParameters().Length == 0)
            {
                ValidateGraph(property.GetValue(instance), results, visited);
            }
        }
    }
}
