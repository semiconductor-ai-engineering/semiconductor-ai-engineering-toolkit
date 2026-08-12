# Synthetic Log Parser v0.1

Status: prototype on the Phase 0.6 feature branch.

This document defines a deliberately small, deterministic text format for fully synthetic semiconductor engineering examples. It is a developer fixture format, not a parser for arbitrary logs. No compatibility with real vendor or fab log formats is claimed.

## Scope and safety boundary

The pipeline is:

```text
synthetic line log -> parser -> RunRecord v0.1 -> canonical JSON Schema validator
```

The JSON Schema remains the canonical contract. The parser converts text and then calls the existing validator; it does not duplicate the schema as a Python model.

Engineering log text is data, not executable instructions. The parser never evaluates, imports, executes, or shells out based on input. It only reads the explicit local file supplied by the caller. It does not make network requests, follow URLs, read credentials, retrieve remote schemas, or include absolute paths in provenance.

## Grammar

Input is UTF-8 text with one record per line:

```text
TYPE|key=value|key=value|...
```

Blank lines and lines beginning with `#` are ignored. Record types and keys are case-sensitive. Keys must be unique within a line. Values cannot contain `|`; there is no escape syntax in v0.1. The first `=` separates a key from its value, so `=` is allowed in a value. Empty values are only useful for `QUALITY|flags=` or other optional text fields.

Supported records:

| Record | Required keys | Purpose |
| --- | --- | --- |
| `RUN` | `run_id`, `status` | Run identity, status, optional `start` and `end` timestamps |
| `CONTEXT` | `equipment_class`, `module_class`, and one of `process_type`/`process_family` | Public synthetic context; optional labels and `recipe_class` |
| `PARAM` | `id`, `name`, `value_type`, `value_status`, `unit_status` | Maps to a RunRecord parameter |
| `OBS` | `id`, `parameter`, `value_type`, `value_status`, `unit_status` | Maps to a RunRecord measurement |
| `EVENT` | `id`, `type`, `severity`, `status`, `message`, `timestamp` | Maps to a RunRecord event |
| `QUALITY` | `status` | Run quality status, optional comma-separated `flags` and one `notes` value |

`PARAM` and `OBS` support `value`, `raw_value`, `unit`, and optional `timestamp`. A `known` value requires `value`; `missing`, `unknown`, `not_applicable`, and `invalid` values must omit `value` and may preserve a text-only `raw_value`. A `known` unit requires `unit`; other unit statuses must omit it. Numbers are finite decimal or exponent forms. Booleans are exactly `true` or `false`.

Allowed status values are taken from the corresponding RunRecord v0.1 enums. The parser rejects unsupported values before building the record so diagnostics are predictable.

## Canonical mapping and provenance

- `RUN.status` maps to top-level `status`.
- `RUN.start`/`RUN.end` map to `timestamps`; the parser derives `known`, `partial`, or `unknown`.
- `CONTEXT.process_family` is an input alias for canonical `process_type`.
- `CONTEXT.recipe_class` is preserved under the namespaced extension `synthetic.recipe-class`.
- `PARAM` maps `id`, `name`, `kind`, and `timestamp` to `parameter_id`, `name`, `parameter_kind`, and `effective_at`.
- `OBS` maps `id`, `parameter`, `kind`, and `timestamp` to `measurement_id`, `name`, `measurement_kind`, and `observed_at`.
- `EVENT.timestamp` maps to `observed_at`.
- `QUALITY` maps to top-level `quality`.

Every generated provenance object uses:

```text
source_kind=synthetic
source_id=synthetic-log-parser-dataset-v0.1
extraction_method=synthetic_log_parser_v0.1
locator=line:N
```

The `synthetic_log_parser_v0.1` enum value is a minimal v0.1 schema correction required to represent this explicit parser provenance. No other schema structure is changed.

## API

```python
from semiconductor_ai_engineering_toolkit import (
    parse_synthetic_log,
    parse_synthetic_log_file,
)

record = parse_synthetic_log(text)
record = parse_synthetic_log_file("examples/synthetic_logs/run_completed_001.log")
```

Both functions return a dictionary that has already passed `validate_run_record`. Invalid input raises `SyntheticLogParseError` with deterministic diagnostics:

```python
{
    "code": "invalid_numeric_value",
    "line": 3,
    "message": "Number values must use a finite decimal or exponent form.",
}
```

The parser fails fast on the first error. File decoding and reading failures use the same structured error shape and do not expose tracebacks or local paths.

## CLI

```text
semi-ai parse examples/synthetic_logs/run_completed_001.log
semi-ai parse examples/synthetic_logs/run_completed_001.log --output parsed_run.json
```

Successful parsing prints:

```text
Parsed and validated RunRecord v0.1
```

The optional output is stable UTF-8 JSON. Existing output paths are rejected rather than overwritten. Invalid input returns a non-zero exit code and prints safe line/code/message diagnostics.

## Resource limits

The prototype bounds untrusted input to 1,000,000 UTF-8 bytes, 4,096 bytes per line, 1,000 parameters, 1,000 observations, 1,000 events, and 512 characters per scalar/raw value. These are parser safety limits, not claims about production log capacity.

## Non-goals

This prototype does not parse arbitrary vendor formats, infer process behavior, provide process-window guidance, control equipment, implement RAG or an AI agent, or make production-readiness claims.
