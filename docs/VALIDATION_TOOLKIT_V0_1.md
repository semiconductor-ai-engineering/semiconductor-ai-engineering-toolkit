# Validation Toolkit v0.1

## Purpose

The validation toolkit provides a small local API and developer CLI for the RunRecord v0.1 JSON Schema. The JSON Schema at [../schema/run_record_v0_1.schema.json](../schema/run_record_v0_1.schema.json) remains the canonical contract. The Python package does not define a replacement data model.

This is a deterministic validation utility for synthetic and explicitly redistributable public examples. It is not a parser, report generator, RAG system, agent, equipment integration, or production control system.

## Install for development

From the repository root:

```text
python -m pip install -e ".[test]"
```

The runtime dependency is `jsonschema>=4.23,<5`. The upper bound avoids an unreviewed major-version contract change while allowing compatible 4.x fixes. The `test` extra adds pytest for local and CI tests. A non-editable build bundles the checked-in canonical schema automatically; the source checkout and editable install read the same root schema file directly.

## Python API

```python
from semiconductor_ai_engineering_toolkit import (
    validate_run_record,
    validate_run_record_file,
)

result = validate_run_record_file("examples/synthetic_data/run_warning_alarm_001.json")
if result["valid"]:
    print("accepted")
else:
    for error in result["errors"]:
        print(error["path"], error["validator"], error["message"])
```

Both functions return a dictionary with this stable shape:

```json
{
  "valid": false,
  "errors": [
    {
      "path": "status",
      "validator": "enum",
      "message": "'finished' is not one of [...]"
    }
  ]
}
```

Errors are sorted by path, validator, and message. File decoding and JSON parsing failures use the same structure and do not expose tracebacks.

## CLI

Validate one explicit local file:

```text
semi-ai validate examples/synthetic_data/run_warning_alarm_001.json
```

Success prints:

```text
Valid RunRecord v0.1
```

Invalid data prints `Validation failed` with one formatted line per error and returns exit code `1`. Command or validator configuration errors return a different non-zero exit code.

## Security boundary

- The validator reads only the explicit input path supplied to `validate_run_record_file`.
- Record text is data only. It is never executed, imported, interpolated into a shell command, or treated as an instruction.
- The validator does not make network requests or resolve external schemas.
- The checked-in schema is loaded locally, and non-local `$ref` or `$dynamicRef` values are rejected before validator construction.
- The schema currently uses only internal `#/$defs/...` references.
- No credentials, tokens, cookies, URLs, private paths, real fab data, HDP data, customer data, or proprietary process information belong in validation fixtures.

## Tests and CI

Run all tests with:

```text
python -m pytest -q
```

The tests cover valid synthetic runs, missing required fields, unknown core fields, invalid enums, invalid JSON types, malformed JSON, invalid UTF-8, deterministic error formatting, and the no-network boundary. GitHub Actions installs the package in editable mode with the test extra and runs the same test suite.
