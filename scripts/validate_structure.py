"""Validate that the monorepo skeleton matches the agreed structure.

This is a lightweight guard used locally and in CI to ensure the foundational
folders and key architecture artifacts exist. It intentionally has no external
dependencies so it runs anywhere Python 3.12+ is available.
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_PATHS: tuple[str, ...] = (
    "apis",
    "services",
    "services/payment-initiation",
    "services/payment-order",
    "services/payment-execution",
    "services/shared",
    "infra",
    "docs",
    "docs/architecture/overview.md",
    "docs/architecture/c4-container.md",
    "docs/architecture/eda-flow.md",
    "docs/architecture/bian-iso20022-mapping.md",
    "docs/adr",
    ".editorconfig",
    "pyproject.toml",
)


def find_missing(root: Path, required: tuple[str, ...]) -> list[str]:
    """Return the list of required paths that do not exist under ``root``.

    Args:
        root: Repository root to validate.
        required: Relative paths expected to exist.

    Returns:
        A list of missing relative paths (empty when the structure is valid).
    """
    return [rel for rel in required if not (root / rel).exists()]


def main() -> int:
    """Run the structure validation and report the result.

    Returns:
        Process exit code: ``0`` when valid, ``1`` when paths are missing.
    """
    root = Path(__file__).resolve().parent.parent
    missing = find_missing(root, REQUIRED_PATHS)
    if missing:
        print("Structure validation FAILED. Missing paths:")
        for rel in missing:
            print(f"  - {rel}")
        return 1
    print(f"Structure validation OK ({len(REQUIRED_PATHS)} paths present).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
