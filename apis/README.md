# API Contracts (API-first)

OpenAPI 3.1 contracts are the source of truth. Implement services against these.

| Contract                          | BIAN alignment                              | Primary message |
| --------------------------------- | ------------------------------------------- | --------------- |
| `payment-initiation.openapi.yaml` | Design partition (channel of Payment Order) | pain.001        |
| `payment-order.openapi.yaml`      | Official BIAN SD: Payment Order             | pacs.008        |
| `payment-execution.openapi.yaml`  | Official BIAN SD: Payment Execution         | pacs.002        |

> "Payment Initiation" is our label for the customer-facing channel, not a distinct BIAN
> Service Domain. See `docs/architecture/bian-iso20022-mapping.md` for the full rationale.

Shared ISO 20022 schema components live in `components/iso20022.yaml`.

## Linting

Contracts are linted with Spectral using `.spectral.yaml` at the repo root.

```
npx @stoplight/spectral-cli lint apis/*.openapi.yaml
```
