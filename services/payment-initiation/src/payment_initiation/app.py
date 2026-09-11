"""FastAPI application for the Payment Initiation Service Domain.

Implements the BIAN Semantic API operations: Initiate (POST), Retrieve (GET), and
the status behavior qualifier. Endpoints are protected by OAuth2/OIDC bearer tokens
with per-operation scope enforcement. Wiring uses simple dependency providers so the
in-memory collaborators and the token verifier can be swapped for real infrastructure.
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError

from payment_initiation.api_models import (
    Pain001In,
    PaymentInitiationState,
    PaymentStatusResponse,
)
from payment_initiation.events import EventPublisher, InMemoryEventPublisher
from payment_initiation.projection import (
    InMemoryStatusProjection,
    StatusProjection,
)
from payment_initiation.security import (
    LocalTokenVerifier,
    Principal,
    TokenVerifier,
    require_scope,
)
from payment_initiation.service import PaymentInitiationService

SCOPE_INITIATE = "payments.initiate"
SCOPE_READ = "payments.read"

# Precomputed scope dependencies (built once, reused per request).
_require_initiate = require_scope(SCOPE_INITIATE)
_require_read = require_scope(SCOPE_READ)

_publisher: EventPublisher = InMemoryEventPublisher()
_projection: StatusProjection = InMemoryStatusProjection()


def get_service() -> PaymentInitiationService:
    """Provide the initiation service with its configured collaborators.

    Returns:
        A ``PaymentInitiationService`` instance.
    """
    return PaymentInitiationService(_publisher, _projection)


def _default_verifier() -> TokenVerifier:
    """Build the default token verifier for local/dev use.

    Returns:
        A ``LocalTokenVerifier`` seeded from the environment (or a dev secret).
    """
    secret = os.environ.get(
        "PAYMENTS_JWT_SECRET", "dev-secret-change-me-0123456789abcdef"
    )
    return LocalTokenVerifier(secret=secret)


def create_app(token_verifier: TokenVerifier | None = None) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        token_verifier: The verifier to enforce OAuth2 tokens; defaults to a local
            HS256 verifier when not supplied.

    Returns:
        The configured FastAPI app.
    """
    app = FastAPI(
        title="Payment Initiation API",
        version="1.0.0",
        description="BIAN Payment Initiation Service Domain (pain.001).",
    )
    app.state.token_verifier = token_verifier or _default_verifier()

    @app.post(
        "/payment-initiations",
        status_code=201,
        response_model=PaymentInitiationState,
        tags=["PaymentInitiation"],
    )
    def initiate_payment(
        body: Pain001In,
        service: PaymentInitiationService = Depends(get_service),
        _principal: Principal = Depends(_require_initiate),
    ) -> PaymentInitiationState:
        """Initiate a payment (BIAN Initiate) from a pain.001 body."""
        try:
            pain = body.to_domain()
        except ValidationError as error:
            raise HTTPException(status_code=400, detail=error.errors()) from error
        result = service.initiate(pain)
        return PaymentInitiationState(
            initiation_id=result.initiation_id,
            payment_id=result.payment_id,
            status=result.status,
            end_to_end_id=result.end_to_end_id,
        )

    @app.get(
        "/payment-initiations/{payment_id}/status",
        response_model=PaymentStatusResponse,
        tags=["PaymentInitiation"],
    )
    def get_status(
        payment_id: str,
        service: PaymentInitiationService = Depends(get_service),
        _principal: Principal = Depends(_require_read),
    ) -> PaymentStatusResponse:
        """Retrieve the current payment status (BIAN Retrieve qualifier)."""
        view = service.get_status(payment_id)
        if view is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        return PaymentStatusResponse(
            payment_id=view.payment_id,
            status=view.status,
            updated_at=view.updated_at,
            reason_code=view.reason_code,
        )

    return app


app = create_app()
