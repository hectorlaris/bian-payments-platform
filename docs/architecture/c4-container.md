# C4 — Container View

Container-level view of the Payments MVP. (System context is implicit: external clients
call the platform; the platform talks to a payment rail — mock or external sandbox.)

```mermaid
flowchart LR
    Client[Channel / Client app] -->|HTTPS + OAuth2/OIDC| APIGW[API Gateway<br/>+ Cognito authorizer]

    APIGW --> PI[Payment Initiation<br/>Python / FastAPI<br/>pain.001]
    PI -->|PaymentInitiated| Kafka[(Amazon MSK / Kafka<br/>domain event store)]

    Kafka --> PO[Payment Order<br/>.NET 8 — ES + CQRS + Saga<br/>pacs.008]
    PO -->|PaymentOrderCreated / ExecutePayment| Kafka

    Kafka --> PE[Payment Execution<br/>.NET 8<br/>pacs.002]
    PE --> ADP[Rail Adapter<br/>Python]
    ADP --> MOCK[Mock Rail]
    ADP -.->|feature flag| SBX[External Sandbox]
    PE -->|PaymentExecuted / PaymentFailed| Kafka

    PO --> READ[(Read Model<br/>projection store)]
    PI -->|status query| READ

    Kafka --> BR[Kafka -> EventBridge bridge]
    BR --> EB[Amazon EventBridge<br/>integration routing]
    EB --> NOTIF[Notification consumer]
```

## Containers

| Container          | Tech               | Responsibility                                             |
| ------------------ | ------------------ | ---------------------------------------------------------- |
| API Gateway        | Amazon API Gateway | TLS termination, throttling, Cognito JWT authorization     |
| Payment Initiation | Python / FastAPI   | Accept `pain.001`, validate, publish `PaymentInitiated`    |
| Payment Order      | .NET 8             | Event-sourced aggregate, Saga orchestration, `pacs.008`    |
| Payment Execution  | .NET 8             | Consume order, call rail adapter, emit `pacs.002`          |
| Rail Adapter       | Python             | Mock rail (default) + interface for external sandbox       |
| Event backbone     | Amazon MSK (Kafka) | Domain event store / stream                                |
| Integration bus    | Amazon EventBridge | Cross-domain routing to integrations (notifications, etc.) |
| Read model         | DynamoDB / RDS     | CQRS query side / projection                               |
