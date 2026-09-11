# Payment Execution (.NET 8) + Rail Adapter (Python)

BIAN Service Domain: **Payment Execution**. Consumes the payment order, invokes the rail
adapter (mock rail by default, external sandbox behind a feature flag), and emits ISO
20022 `pacs.002` status.

Implemented in Task 6. See `/apis/payment-execution.openapi.yaml`.
