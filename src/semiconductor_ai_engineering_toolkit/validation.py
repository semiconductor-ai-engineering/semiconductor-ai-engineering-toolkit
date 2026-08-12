"""RunRecord v0.1 validation backed by the repository JSON Schema.

The JSON Schema remains the canonical contract. This module only loads the
local schema, invokes the Draft 2020-12 validator, and formats deterministic
results for callers.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

_SCHEMA_FILENAME = "run_record_v0_1.schema.json"


class SchemaConfigurationError(RuntimeError):
    """Raised when the repository's canonical schema cannot be loaded safely."""


def _canonical_schema_path() -> Path:
    """Return the schema path inside a source checkout or editable install."""

    return Path(__file__).resolve().parents[2] / "schema" / _SCHEMA_FILENAME


def _schema_text() -> str:
    """Read the build-bundled schema, or the canonical checkout file."""

    try:
        bundled = resources.files("semiconductor_ai_engineering_toolkit").joinpath(_SCHEMA_FILENAME)
        if bundled.is_file():
            return bundled.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError, UnicodeError):
        pass

    return _canonical_schema_path().read_text(encoding="utf-8")


def _external_references(node: Any) -> list[str]:
    """Collect non-local JSON Schema references without resolving them."""

    references: list[str] = []
    if isinstance(node, dict):
        for key in ("$ref", "$dynamicRef"):
            value = node.get(key)
            if isinstance(value, str) and not value.startswith("#"):
                references.append(value)
        for value in node.values():
            references.extend(_external_references(value))
    elif isinstance(node, list):
        for value in node:
            references.extend(_external_references(value))
    return references


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    """Load and compile only the checked-in local schema.

    The current schema uses internal ``#`` references only. External
    references are rejected before validator construction so validation cannot
    trigger uncontrolled schema retrieval.
    """

    try:
        schema_text = _schema_text()
    except (OSError, UnicodeError) as exc:
        raise SchemaConfigurationError("Canonical RunRecord schema is unavailable.") from exc

    try:
        schema = json.loads(schema_text)
    except json.JSONDecodeError as exc:
        raise SchemaConfigurationError("Canonical RunRecord schema is not valid JSON.") from exc

    external_refs = _external_references(schema)
    if external_refs:
        raise SchemaConfigurationError("Canonical schema contains an external reference.")

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise SchemaConfigurationError("Canonical RunRecord schema is invalid.") from exc

    return Draft202012Validator(schema, format_checker=FormatChecker())


def _path_string(path: Any) -> str:
    """Render a jsonschema path as a stable dotted path."""

    return ".".join(str(part) for part in path)


def _error_sort_key(error: Any) -> tuple[tuple[str, ...], str, str]:
    return (
        tuple(str(part) for part in error.absolute_path),
        str(error.validator),
        error.message,
    )


def _format_error(error: Any) -> dict[str, str]:
    return {
        "path": _path_string(error.absolute_path),
        "validator": str(error.validator),
        "message": error.message,
    }


def _failure(path: str, validator: str, message: str) -> dict[str, Any]:
    return {
        "valid": False,
        "errors": [
            {
                "path": path,
                "validator": validator,
                "message": message,
            }
        ],
    }


def validate_run_record(record: Any) -> dict[str, Any]:
    """Validate an in-memory value against RunRecord v0.1.

    The returned object always has ``valid`` and ``errors`` keys. Validation
    errors contain only stable path, validator, and message fields; no
    traceback is returned for invalid data.
    """

    errors = sorted(_validator().iter_errors(record), key=_error_sort_key)
    formatted = [_format_error(error) for error in errors]
    return {"valid": not formatted, "errors": formatted}


def validate_run_record_file(path: str | Path) -> dict[str, Any]:
    """Read exactly one explicit local UTF-8 JSON file and validate it."""

    try:
        input_path = Path(path)
    except (TypeError, ValueError):
        return _failure("", "file", "Input path is invalid.")

    try:
        raw = input_path.read_bytes()
    except (OSError, ValueError):
        return _failure("", "file", "Input file could not be read.")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _failure("", "utf-8", "Input file is not valid UTF-8.")

    try:
        record = json.loads(text)
    except json.JSONDecodeError as exc:
        message = f"Invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})."
        return _failure("", "json", message)

    return validate_run_record(record)
