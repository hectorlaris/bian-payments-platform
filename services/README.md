# Services

Service implementations, one folder per bounded context.

| Folder                | Tech             | Bounded context                          |
| --------------------- | ---------------- | ---------------------------------------- |
| `payment-initiation`  | Python / FastAPI | Payment Initiation (channel, pain.001)   |
| `payment-order`       | .NET 8           | Payment Order (ES + CQRS + Saga, pacs.008)|
| `payment-execution`   | .NET 8 + Python  | Payment Execution + rail adapter (pacs.002)|
| `shared`              | .NET + Python    | Shared ISO 20022 DTO libraries           |

Each service owns its build, tests, and README. Contracts live in `/apis`.
