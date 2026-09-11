"""Payment Initiation service (BIAN Service Domain).

Channel entry point that accepts ISO 20022 pain.001, validates it, publishes a
``PaymentInitiated`` domain event, and exposes payment status via a read projection.
"""
