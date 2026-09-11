# Event-Driven Architecture — Payment Flow

The payment lifecycle is coordinated by domain events on Kafka (Amazon MSK). Integration
concerns (e.g., notifications) are routed via EventBridge, keeping domain events and
integration events separated.

## Saga sequence (happy path + failure)

```mermaid
sequenceDiagram
    participant C as Client
    participant PI as Payment Initiation
    participant PO as Payment Order (Saga)
    participant PE as Payment Execution
    participant R as Rail Adapter (mock/sandbox)
    participant EB as EventBridge

    C->>PI: POST /payment-initiations (pain.001)
    PI->>PI: Validate pain.001
    PI-->>C: 201 { id, status: ACTC }
    PI->>PO: PaymentInitiated (event)

    PO->>PO: Validate + build pacs.008
    PO->>PO: append PaymentOrderCreated (status ACSP)
    PO->>PE: ExecutePayment (command event)

    PE->>R: send(pacs.008)
    alt rail success
        R-->>PE: settled
        PE->>PO: PaymentExecuted (pacs.002 ACSC)
        PO->>PO: append PaymentCompleted (status ACSC)
        PO->>EB: PaymentCompleted (integration event)
        EB->>EB: route to Notification consumer
    else rail failure
        R-->>PE: rejected
        PE->>PO: PaymentFailed (pacs.002 RJCT)
        PO->>PO: append PaymentFailed + compensate (status RJCT)
        PO->>EB: PaymentFailed (integration event)
    end

    C->>PI: GET /payment-initiations/{id}/status
    PI->>PO: read projection
    PO-->>PI: current status
    PI-->>C: status
```

## Domain events (Kafka topics)

| Event                 | Producer           | Topic                      | Consumers                     |
| --------------------- | ------------------ | -------------------------- | ----------------------------- |
| `PaymentInitiated`    | Payment Initiation | `payments.initiation.v1`   | Payment Order                 |
| `PaymentOrderCreated` | Payment Order      | `payments.order.v1`        | Payment Execution, projection |
| `PaymentExecuted`     | Payment Execution  | `payments.execution.v1`    | Payment Order (Saga)          |
| `PaymentFailed`       | Payment Execution  | `payments.execution.v1`    | Payment Order (Saga)          |
| `PaymentCompleted`    | Payment Order      | `payments.order.v1`        | projection, EventBridge bridge|

## Event envelope

All domain events share a common envelope for correlation and idempotency:

```json
{
  "eventId": "uuid",
  "eventType": "PaymentInitiated",
  "occurredAt": "2026-01-01T12:00:00Z",
  "paymentId": "uuid",
  "correlationId": "uuid",
  "schemaVersion": 1,
  "payload": { }
}
```

- `paymentId` is the aggregate id and the idempotency key across the flow.
- `correlationId` ties all events of a single business transaction together.
- `schemaVersion` supports forward-compatible evolution.

## Saga states (implemented)

The orchestrated Saga lives in Payment Order (`PaymentSaga`). Its states:

| State              | Meaning                                  |
| ------------------ | ---------------------------------------- |
| `NotStarted`       | No order exists yet                      |
| `OrderCreated`     | Order created from initiation (ACSP)     |
| `AwaitingExecution`| Submitted to execution, awaiting outcome |
| `Completed`        | Execution settled (ACSC)                 |
| `Failed`           | Execution rejected; order compensated (RJCT) |

Compensation: when execution returns a non-`ACSC` status, the Saga marks the order
failed (`Fail(reasonCode)`), moving it to `RJCT`. The status then flows back to the
Initiation read model via the CQRS status update path.

## Domain vs integration events

- **Domain events** stay on Kafka. They drive the Saga and rebuild aggregate/read state.
- **Integration events** are a curated subset forwarded to EventBridge by a bridge
  component. They are for downstream systems (notifications, analytics) and must not be
  required to advance the core Saga.
