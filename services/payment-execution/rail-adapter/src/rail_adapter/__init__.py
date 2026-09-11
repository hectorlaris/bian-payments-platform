"""Payment rail adapter package.

Provides a rail abstraction with a default in-process mock implementation and an
external-sandbox implementation selected by configuration. The adapter takes a
pacs.008 transfer and returns a settlement outcome that maps to a pacs.002 status.
"""

from rail_adapter.adapter import (
    MockRail,
    RailAdapter,
    RailOutcome,
    SandboxRail,
    build_rail,
)

__all__ = [
    "MockRail",
    "RailAdapter",
    "RailOutcome",
    "SandboxRail",
    "build_rail",
]
