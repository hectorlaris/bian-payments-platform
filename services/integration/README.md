# Payments Integration (Kafka -> EventBridge)

Separates the two event planes:

- **Domain events** (Kafka) drive the Saga and rebuild aggregate/read state.
- **Integration events** (Amazon EventBridge) are a curated subset forwarded to
  downstream systems (notifications, analytics) and never required to advance the Saga.

## Components

- `bridge.py` — `DomainToIntegrationBridge` forwards only `PaymentCompleted` and
  `PaymentFailed` domain events, normalized to integration events.
- `eventbridge.py` — `EventBridgeClient` abstraction with `InMemoryEventBridgeClient`
  (tests/local) and `Boto3EventBridgeClient` (runtime via boto3 PutEvents).
- `notifications.py` — `Rule` (source + detail-type matching) and a sample
  `NotificationConsumer` target.

## Test

```powershell
cd services/integration
python -m pytest -q
```
