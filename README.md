# Next-Generation Financial APIs Platform — Payments MVP

A production-grade MVP for a next-generation financial APIs platform focused on the
**Payments** domain. The solution is framed by an enterprise architecture approach
(TOGAF) and implemented with BIAN domains, Domain-Driven Design (DDD), BIAN Semantic
APIs, ISO 20022 messaging, an API-first workflow, event-driven architecture (EDA),
and AWS deployment.

## Architecture at a glance

| Concern            | Choice                                                              |
| ------------------ | ------------------------------------------------------------------- |
| Enterprise framing | TOGAF (lightweight), BIAN Service Domains, DDD bounded contexts     |
| API style          | API-first, OpenAPI 3.1, BIAN Semantic APIs                          |
| Messaging          | ISO 20022 (pain.001, pacs.008, pacs.002) via custom DTOs            |
| Core services      | ASP.NET Core (.NET 8) — Payment Order, Payment Execution            |
| Edge / integration | Python 3.12 / FastAPI — Payment Initiation, rail adapters, data     |
| Data pattern       | Event Sourcing + CQRS + Saga                                        |
| Event backbone     | Amazon MSK (Kafka) for domain events + EventBridge for integration  |
| Security           | OAuth2 / OIDC (Cognito), TLS, API Gateway throttling                |
| IaC                | Terraform                                                           |

## BIAN Service Domains and the payment flow

```
Payment Initiation  ->  Payment Order  ->  Payment Execution
   (pain.001)             (pacs.008)          (pacs.002)
   Python/FastAPI         .NET 8 ES+CQRS      .NET 8 + Python rail adapter
```

## Repository layout

```
/apis        OpenAPI 3.1 contracts (source of truth, API-first)
/services    Service implementations
  /payment-initiation      Python 3.12 / FastAPI (channel/BFF)
  /payment-order           .NET 8 (Event Sourcing + CQRS + Saga)
  /payment-execution       .NET 8 (execution) + rail adapter (Python)
  /shared                  Shared libraries (ISO 20022 DTOs: .NET + Python)
/infra       Terraform (landing zone, MSK, EventBridge, API GW, Cognito, compute)
/docs        Architecture: TOGAF notes, C4/EDA diagrams, ADRs, BIAN<->ISO 20022 mapping
/deploy      Local orchestration (docker-compose for Kafka, etc.)
```

## Getting started

Each service has its own README with build and test instructions. Start with the
architecture docs in `/docs`, then the API contracts in `/apis`.

- Architecture overview: [docs/architecture/overview.md](docs/architecture/overview.md)
- BIAN <-> ISO 20022 mapping: [docs/architecture/bian-iso20022-mapping.md](docs/architecture/bian-iso20022-mapping.md)
- Architecture Decision Records: [docs/adr/](docs/adr/)

## Testing & CI/CD

Run the entire verification suite locally with one command:

```powershell
pwsh scripts/run_all_tests.ps1
```

This installs the Python packages, validates structure/contracts/diagrams, runs all
Python and .NET test suites, and executes the end-to-end smoke test.

CI runs on GitHub Actions (`.github/workflows/`):

- `python-tests.yml` — lint (Ruff) + pytest per Python package.
- `dotnet-tests.yml` — `dotnet test` per .NET project.
- `contracts.yml` — Spectral OpenAPI lint + structure/examples/diagram validation.
- `terraform.yml` — `fmt`/`init`/`validate`, then gated `plan` and approval-gated `apply`.
- `e2e.yml` — end-to-end payment-flow smoke test.

## Status

Delivered incrementally; all MVP tasks complete. See the task breakdown and verification
summary in [docs/architecture/roadmap.md](docs/architecture/roadmap.md).
