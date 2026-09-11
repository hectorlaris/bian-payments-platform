# ADR 0004: Base security with OAuth2/OIDC (Cognito) and API Gateway

- Status: Accepted
- Date: 2026-01-01

## Context

The MVP requires base-level API security. The scope is OAuth2/OIDC with Amazon Cognito,
TLS, and API Gateway throttling — not the full FAPI profile.

## Decision

- APIs require an OAuth2 bearer token. Scopes are enforced per operation
  (`payments.initiate`, `payments.read`, etc.), matching the OpenAPI contracts.
- Token verification is abstracted behind `TokenVerifier`:
  - `CognitoTokenVerifier` validates RS256 tokens against the Cognito JWKS (runtime).
  - `LocalTokenVerifier` validates HS256 shared-secret tokens (local dev and tests).
- API Gateway terminates TLS and applies throttling/rate limiting (configured in IaC).
- Responses: 401 for a missing/invalid/expired token, 403 for an insufficient scope.

## Consequences

- Services stay independent of the identity provider via the verifier abstraction.
- Local development and tests do not require a live Cognito user pool.
- FAPI (mTLS, signed request objects, PKCE) and a full audit trail remain recommended
  evolution, out of MVP scope.
