"""Validate example payloads against the shared ISO 20022 OpenAPI schemas.

The OpenAPI contracts reference reusable schemas in ``apis/components/iso20022.yaml``.
This script loads those component schemas, rewrites their internal ``$ref`` pointers to
a self-contained ``$defs`` bundle, and validates each example payload with jsonschema.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = ROOT / "apis" / "components" / "iso20022.yaml"

# (example file, component schema name) pairs to validate.
CASES: tuple[tuple[str, str], ...] = (
    ("apis/examples/pain001.sample.json", "Pain001"),
)


def load_component_schemas() -> dict[str, Any]:
    """Load the reusable schema map from the shared components file.

    Returns:
        A mapping of schema name to its JSON Schema definition.
    """
    document = yaml.safe_load(COMPONENTS.read_text(encoding="utf-8"))
    return document["components"]["schemas"]


def rebase_refs(node: Any) -> Any:
    """Rewrite OpenAPI component ``$ref`` pointers to local ``$defs`` pointers.

    Args:
        node: An arbitrary JSON-schema node (dict, list, or scalar).

    Returns:
        The node with every component ``$ref`` rebased to ``#/$defs/<Name>``.
    """
    if isinstance(node, dict):
        return {key: _rebase_value(key, value) for key, value in node.items()}
    if isinstance(node, list):
        return [rebase_refs(item) for item in node]
    return node


def _rebase_value(key: str, value: Any) -> Any:
    """Rebase a single key/value pair, handling the ``$ref`` special case.

    Args:
        key: The mapping key.
        value: The mapping value.

    Returns:
        The rebased value.
    """
    if key == "$ref" and isinstance(value, str):
        return f"#/$defs/{value.rsplit('/', 1)[-1]}"
    return rebase_refs(value)


def build_validator(schema_name: str, schemas: dict[str, Any]) -> Draft202012Validator:
    """Build a validator for one component schema with all defs bundled.

    Args:
        schema_name: The root component schema to validate against.
        schemas: The full component schema map.

    Returns:
        A configured JSON Schema validator.
    """
    defs = {name: rebase_refs(body) for name, body in schemas.items()}
    root_schema = {"$ref": f"#/$defs/{schema_name}", "$defs": defs}
    return Draft202012Validator(root_schema)


def main() -> int:
    """Validate every configured example payload.

    Returns:
        Process exit code: ``0`` when all examples validate, ``1`` otherwise.
    """
    schemas = load_component_schemas()
    failures = 0
    for example_rel, schema_name in CASES:
        payload = json.loads((ROOT / example_rel).read_text(encoding="utf-8"))
        validator = build_validator(schema_name, schemas)
        errors = sorted(validator.iter_errors(payload), key=lambda error: error.path)
        if errors:
            failures += 1
            print(f"FAIL {example_rel} against {schema_name}:")
            for error in errors:
                print(f"  - {list(error.path)}: {error.message}")
        else:
            print(f"OK   {example_rel} against {schema_name}")
    print(f"\n{len(CASES) - failures}/{len(CASES)} example payloads valid.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
