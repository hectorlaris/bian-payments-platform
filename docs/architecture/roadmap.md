# Delivery Roadmap

The MVP is delivered incrementally. Each task produces a demoable increment.

| # | Task                                                            | Status |
| - | --------------------------------------------------------------- | ------ |
| 1 | Repository foundations and architecture artifacts               | done   |
| 2 | API-first contracts (OpenAPI 3.1) aligned to BIAN               | done   |
| 3 | ISO 20022 domain models (DTOs) and shared library               | done   |
| 4 | Payment Initiation (Python/FastAPI) over stubs                  | done   |
| 5 | Local event backbone (Kafka) + Event Sourcing base (.NET Order) | done   |
| 6 | Payment Execution (.NET) + Rail Adapter (Python) mock/sandbox   | done   |
| 7 | End-to-end Saga orchestration (Initiation -> Order -> Execution)| done   |
| 8 | EventBridge integration (cross-domain routing)                  | done   |
| 9 | Base security (OAuth2/OIDC with Cognito + API Gateway)          | done   |
| 10| Infrastructure as Code (Terraform) + AWS deployment baseline    | done   |
| 11| CI/CD and end-to-end verification                               | done   |

## Verification summary

- Python: 39 tests (iso20022 12, payment-initiation 14, rail-adapter 6, integration 7).
- .NET: 25 tests (iso20022 8, payment-order 13 incl. Saga e2e, payment-execution 4).
- Contracts: Spectral lint passes; example payloads validate; 3/3 mermaid diagrams render.
- Terraform: `init`/`validate` succeed, `fmt -check` passes.
- End-to-end smoke: happy path settles (ACSC), failure path compensates (RJCT).

Run everything locally: `pwsh scripts/run_all_tests.ps1`.

## Out of MVP scope (evolutionary)

- FAPI profile (mTLS, signed JWTs, PKCE).
- Full audit trail with tamper-evidence.
- KMS / Secrets Manager hardening and key rotation.
- Multi-rail routing and settlement reconciliation.
