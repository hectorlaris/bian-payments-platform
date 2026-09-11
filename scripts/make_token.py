"""Mint a local HS256 bearer token for the guided walkthrough.

Usage:
    python scripts/make_token.py "payments.initiate payments.read"

Prints a signed JWT whose ``scope`` claim carries the space-delimited scopes given
on the command line (defaults to both initiate and read). The secret matches the
service default (``PAYMENTS_JWT_SECRET`` or the built-in dev secret).
"""

from __future__ import annotations

import os
import sys
import time

import jwt

DEV_SECRET = "dev-secret-change-me-0123456789abcdef"


def build_token(scopes: str) -> str:
    """Build a signed HS256 token carrying the given scopes.

    Args:
        scopes: Space-delimited OAuth2 scopes to embed in the token.

    Returns:
        The encoded JWT string.
    """
    secret = os.environ.get("PAYMENTS_JWT_SECRET", DEV_SECRET)
    claims = {
        "sub": "walkthrough-client",
        "scope": scopes,
        "exp": int(time.time()) + 900,
    }
    return jwt.encode(claims, secret, algorithm="HS256")


def main() -> int:
    """Print a token for the scopes passed on the command line.

    Returns:
        Process exit code (always ``0``).
    """
    scopes = sys.argv[1] if len(sys.argv) > 1 else "payments.initiate payments.read"
    print(build_token(scopes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
