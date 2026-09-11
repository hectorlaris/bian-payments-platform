# Payment Initiation (Python / FastAPI)

Bounded context: **Payment Initiation** — our design partition for the customer-facing
channel. It is *not* a distinct BIAN Service Domain; it is the channel/entry point of the
official BIAN **Payment Order** SD (see `docs/architecture/bian-iso20022-mapping.md`).

Accepts ISO 20022 `pain.001`, validates it, publishes a `PaymentInitiated` domain event,
and exposes payment status via a read projection.

Implemented in Task 4. See `/apis/payment-initiation.openapi.yaml` for the contract.
