# ADR 0001: Record architecture decisions

- Status: Accepted
- Date: 2026-01-01

## Context

The Payments MVP spans several architectural approaches (TOGAF, BIAN, DDD, ISO 20022,
API-first, EDA, AWS). We need a lightweight, durable record of significant decisions so
the rationale survives beyond any single conversation.

## Decision

We use Architecture Decision Records (ADRs), one Markdown file per decision, stored in
`docs/adr/`, numbered sequentially. Each ADR states context, the decision, and its
consequences. ADRs are immutable once accepted; a superseding ADR replaces an old one.

## Consequences

- Decisions are traceable and reviewable.
- New contributors can read the ADR log to understand "why", not just "what".
