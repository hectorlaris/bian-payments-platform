# Local orchestration

Local developer stack for the Payments MVP.

## Kafka event backbone

Kafka runs in KRaft mode (no ZooKeeper), mirroring the role of Amazon MSK in the cloud.

```powershell
# Start Kafka (and the optional UI)
docker compose -f deploy/docker-compose.kafka.yml up -d

# Kafka UI: http://localhost:8080
# Bootstrap servers (from host): localhost:9092

# Stop
docker compose -f deploy/docker-compose.kafka.yml down
```

Topics are auto-created on first use:

- `payments.initiation.v1`
- `payments.order.v1`
- `payments.execution.v1`

Unit tests do not require Kafka; they use the in-memory event store. Kafka is used
for the local end-to-end run (Task 7) and for the runtime hosting of the .NET services.
