"""OAuth2 / OIDC token verification and scope enforcement.

Provides a ``TokenVerifier`` abstraction with two implementations:

- ``LocalTokenVerifier`` — HS256 shared-secret verification for local dev and tests.
- ``CognitoTokenVerifier`` — RS256 verification against a Cognito JWKS for runtime.

Scopes follow the OAuth2 model exposed in the OpenAPI contract (``payments.initiate``,
``payments.read``). A ``require_scope`` FastAPI dependency enforces per-operation scopes
and returns 401 (missing/invalid token) or 403 (insufficient scope).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


@dataclass(frozen=True)
class Principal:
    """The authenticated caller derived from a validated token."""

    subject: str
    scopes: frozenset[str] = field(default_factory=frozenset)


class TokenVerifier(ABC):
    """Abstraction for verifying a bearer token and extracting a principal."""

    @abstractmethod
    def verify(self, token: str) -> Principal:
        """Verify a token and return the principal.

        Args:
            token: The raw bearer token.

        Returns:
            The authenticated principal.

        Raises:
            ValueError: When the token is invalid or expired.
        """
        raise NotImplementedError


def _extract_scopes(claims: dict) -> frozenset[str]:
    """Extract scopes from standard claim shapes.

    Supports the OAuth2 ``scope`` string (space-delimited) and Cognito's
    ``scope``/``cognito:groups`` conventions.

    Args:
        claims: The decoded token claims.

    Returns:
        The set of granted scopes.
    """
    raw = claims.get("scope", "")
    if isinstance(raw, str):
        return frozenset(part for part in raw.split(" ") if part)
    if isinstance(raw, list):
        return frozenset(raw)
    return frozenset()


class LocalTokenVerifier(TokenVerifier):
    """HS256 shared-secret verifier for local development and tests."""

    def __init__(self, secret: str, audience: str | None = None) -> None:
        """Create the verifier.

        Args:
            secret: The shared HMAC secret.
            audience: Optional expected audience claim.
        """
        self._secret = secret
        self._audience = audience

    def verify(self, token: str) -> Principal:
        """Verify an HS256 token and return the principal.

        Args:
            token: The raw bearer token.

        Returns:
            The authenticated principal.

        Raises:
            ValueError: When the token is invalid or expired.
        """
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                audience=self._audience,
                options={"verify_aud": self._audience is not None},
            )
        except jwt.PyJWTError as error:
            raise ValueError(f"Invalid token: {error}") from error
        return Principal(
            subject=str(claims.get("sub", "")),
            scopes=_extract_scopes(claims),
        )


class CognitoTokenVerifier(TokenVerifier):
    """RS256 verifier validating tokens against a Cognito JWKS (runtime)."""

    def __init__(self, jwks_client: jwt.PyJWKClient, issuer: str, audience: str) -> None:
        """Create the verifier.

        Args:
            jwks_client: A configured PyJWKClient pointing at the Cognito JWKS URL.
            issuer: The expected token issuer (Cognito user pool URL).
            audience: The expected audience (app client id).
        """
        self._jwks = jwks_client
        self._issuer = issuer
        self._audience = audience

    def verify(self, token: str) -> Principal:
        """Verify an RS256 Cognito token and return the principal.

        Args:
            token: The raw bearer token.

        Returns:
            The authenticated principal.

        Raises:
            ValueError: When the token is invalid or expired.
        """
        try:
            key = self._jwks.get_signing_key_from_jwt(token).key
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer,
            )
        except jwt.PyJWTError as error:
            raise ValueError(f"Invalid token: {error}") from error
        return Principal(
            subject=str(claims.get("sub", "")),
            scopes=_extract_scopes(claims),
        )


_bearer = HTTPBearer(auto_error=False)


def get_verifier(request: Request) -> TokenVerifier:
    """Resolve the token verifier from application state.

    Args:
        request: The incoming request.

    Returns:
        The configured token verifier.

    Raises:
        HTTPException: 500 when no verifier is configured.
    """
    verifier = getattr(request.app.state, "token_verifier", None)
    if verifier is None:
        raise HTTPException(status_code=500, detail="No token verifier configured")
    return verifier


def require_scope(required: str):
    """Build a FastAPI dependency enforcing a required scope.

    Args:
        required: The scope the caller must hold.

    Returns:
        A dependency callable that returns the authenticated principal.
    """

    def dependency(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
        verifier: TokenVerifier = Depends(get_verifier),
    ) -> Principal:
        """Authenticate the caller and enforce the required scope."""
        if credentials is None or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Missing bearer token")
        try:
            principal = verifier.verify(credentials.credentials)
        except ValueError as error:
            raise HTTPException(status_code=401, detail=str(error)) from error
        if required not in principal.scopes:
            raise HTTPException(
                status_code=403, detail=f"Missing required scope '{required}'"
            )
        return principal

    return dependency
