# Architecture Overview

This document is a lightweight TOGAF-flavored architecture description for the
Payments MVP. It is intentionally concise: it captures the architecture vision,
the building blocks, and the key views (business, data, application, technology).

## 1. Architecture Vision (TOGAF Phase A)

Deliver a production-grade MVP of a next-generation financial APIs platform for the
**Payments** business domain. The platform must be:

- **API-first**: contracts precede code and are the source of truth.
- **Standards-aligned**: BIAN Service Domains for structure, ISO 20022 for message content.
- **Event-driven**: domain state changes are events; integration is decoupled.
- **Cloud-native**: deployable to AWS via Terraform, demoable end-to-end.

### Stakeholders and concerns

| Stakeholder        | Concern                                                       |
| ------------------ | ------------------------------------------------------------- |
| Business / Product | A working, demoable payment flow; clear domain boundaries     |
| Architecture       | Standards alignment (TOGAF, BIAN, ISO 20022), traceability    |
| Engineering        | Clean bounded contexts, testability, hybrid .NET + Python     |
| Security / Risk    | OAuth2/OIDC, TLS, throttling; a path to FAPI and full audit   |
| Operations         | IaC, CI/CD, observability of the event flow                   |

## 2. Business Architecture (TOGAF Phase B) — BIAN

The MVP is organized as three DDD bounded contexts. Two map directly to official BIAN
Service Domains; the third is a design partition we introduced (see the note below):

1. **Payment Initiation** — the channel/entry point. Captures the customer's payment
   intent and expresses it as ISO 20022 `pain.001`. *(Our design partition — the
   customer-facing channel of Payment Order, not a distinct SD in the BIAN catalog.)*
2. **Payment Order** — order fulfillment. Validates, applies rules, orchestrates the
   Saga, and translates to ISO 20022 `pacs.008`. *(Official BIAN SD: Payment Order.)*
3. **Payment Execution** — executes against a payment rail (mock or sandbox) and
   reports status as ISO 20022 `pacs.002`. *(Official BIAN SD: Payment Execution.)*

> **Naming note.** BIAN's official catalog defines a single **Payment Order** Service
> Domain that covers both initiating and managing the payment order. We deliberately
> split the customer-facing channel into a separate **Payment Initiation** bounded
> context (a DDD decision). It is our label, not an official SD.

See [bian-iso20022-mapping.md](bian-iso20022-mapping.md) for the message-level mapping
and the full official-SD-vs-design-partition explanation.

## 3. Data Architecture (TOGAF Phase C — Data)

- **Canonical messages**: ISO 20022 (`pain.001`, `pacs.008`, `pacs.002`), modeled as
  custom validated DTOs. JSON internally, XML at the edges.
- **Event Sourcing**: the `PaymentOrder` aggregate persists a stream of domain events;
  current state is derived by replay.
- **CQRS**: a read model (projection) is built from the event stream for queries.

## 4. Application Architecture (TOGAF Phase C — Application)

- Hybrid: **.NET 8** for the core domain (Order, Execution), **Python 3.12 / FastAPI**
  for the edge (Initiation), rail adapters, and data/projection components.
- **Saga** coordinates the cross-context flow Initiation -> Order -> Execution with
  basic compensation on failure.

See [c4-container.md](c4-container.md) and [eda-flow.md](eda-flow.md) for the views.

## 5. Technology Architecture (TOGAF Phase D) — AWS

| Capability        | AWS service                                   |
| ----------------- | --------------------------------------------- |
| Domain events     | Amazon MSK (Kafka)                            |
| Integration/route | Amazon EventBridge                            |
| API exposure      | Amazon API Gateway (throttling, TLS)          |
| Identity          | Amazon Cognito (OAuth2 / OIDC)                |
| Compute           | ECS / Fargate (or Lambda for light adapters)  |
| Read model store  | DynamoDB or Amazon RDS (Postgres)             |
| Secrets / keys    | Secrets Manager / KMS                         |
| IaC               | Terraform                                     |

## 6. Cross-cutting concerns

- **Security (MVP)**: OAuth2/OIDC via Cognito, TLS, API Gateway throttling. Scopes per
  operation. FAPI, mTLS, and full audit trail are recommended evolution (out of MVP scope).
- **Idempotency**: payment execution is idempotent by payment id.
- **Observability**: structured logging and event tracing across the flow.

## 7. Evolutionary recommendations (out of MVP scope)

- FAPI profile (mTLS, signed request objects, PKCE).
- Full audit trail with tamper-evidence.
- KMS/Secrets Manager hardening and key rotation policies.
