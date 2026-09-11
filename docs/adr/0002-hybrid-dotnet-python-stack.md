# ADR 0002: Hybrid .NET 8 + Python 3.12 stack

- Status: Accepted
- Date: 2026-01-01

## Context

The team's experience is ASP.NET Core and Python. The platform has two kinds of work:
core domain logic with strong modeling and event sourcing (Payment Order, Payment
Execution), and edge/integration/data work (channel API, rail adapters, projections).

## Decision

- Implement core domain services (Payment Order, Payment Execution) in **ASP.NET Core
  (.NET 8, LTS)**. The static type system and mature libraries suit event-sourced
  aggregates and Saga logic.
- Implement the edge (Payment Initiation), rail adapters, and data/projection components
  in **Python 3.12 / FastAPI**. FastAPI gives fast, contract-friendly HTTP services.
- Share ISO 20022 DTOs as parallel libraries in each language rather than a single
  cross-language artifact, to keep each side idiomatic.

## Consequences

- Two toolchains to maintain (dotnet + uv/pip). CI must cover both.
- Contracts (OpenAPI) and event schemas become the cross-language source of truth.
- Idiomatic code on each side; some duplication in DTO definitions is accepted.
