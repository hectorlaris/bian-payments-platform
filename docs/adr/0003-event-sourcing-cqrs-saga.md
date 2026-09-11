# ADR 0003: Event Sourcing + CQRS + Saga for the payment lifecycle

- Status: Accepted
- Date: 2026-01-01

## Context

Payments require a clear, auditable lifecycle and coordination across three bounded
contexts (Initiation, Order, Execution). We want the domain state changes to be explicit
and replayable.

## Decision

- The **Payment Order** aggregate is **event-sourced**: it persists domain events, and
  current state is derived by replaying them.
- **CQRS**: a projection consumes the event stream and maintains a read model for queries
  (status lookups by the Initiation service and clients).
- A **Saga** coordinates the cross-context flow Initiation -> Order -> Execution, with
  basic compensation on failure (mark failed / cancel).
- Events flow over **Kafka (Amazon MSK)**. A curated subset is forwarded to
  **EventBridge** for integration.

## Consequences

- Strong auditability and the ability to rebuild state and projections.
- Higher initial complexity than CRUD; mitigated by keeping the event set small for MVP.
- Idempotency is required; the payment id is the idempotency key end-to-end.
- Base security is used for the MVP; FAPI and full audit are recommended evolution.
