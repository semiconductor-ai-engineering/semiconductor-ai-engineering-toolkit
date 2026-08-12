"""Deterministic parser for the project's deliberately simple synthetic log format.

Engineering log text is data, not executable instructions. This module only
splits and converts text fields, then hands the resulting record to the
canonical RunRecord validator. It does not execute input, import from input,
follow URLs, access the network, or resolve remote schemas.
"""

from __future__ import annotations

import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, NoReturn

from .validation import validate_run_record

MAX_INPUT_BYTES = 1_000_000
MAX_LINE_BYTES = 4_096
MAX_PARAMETERS = 1_000
MAX_MEASUREMENTS = 1_000
MAX_EVENTS = 1_000
MAX_VALUE_LENGTH = 512

SOURCE_KIND = "synthetic"
SOURCE_ID = "synthetic-log-parser-dataset-v0.1"
EXTRACTION_METHOD = "synthetic_log_parser_v0.1"

_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_NUMBER = re.compile(
    r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$"
)
_TIMESTAMP = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)

_RUN_STATUSES = frozenset({"planned", "running", "completed", "aborted", "unknown"})
_VALUE_TYPES = frozenset({"number", "string", "boolean"})
_VALUE_STATUSES = frozenset({"known", "missing", "unknown", "not_applicable", "invalid"})
_UNIT_STATUSES = frozenset({"known", "missing", "unknown", "not_applicable"})
_PARAMETER_KINDS = frozenset({"setpoint", "input", "limit", "target", "context", "other"})
_MEASUREMENT_KINDS = frozenset({"signal", "result", "derived", "other"})
_EVENT_TYPES = frozenset({"state_change", "alarm", "warning", "annotation", "other"})
_SEVERITIES = frozenset({"info", "warning", "error", "critical", "unknown"})
_EVENT_STATUSES = frozenset({"observed", "cleared", "unresolved", "unknown"})
_QUALITY_STATUSES = frozenset({"accepted", "uncertain", "incomplete", "invalid", "not_assessed"})


class SyntheticLogParseError(ValueError):
    """A predictable parser failure with safe, structured diagnostics."""

    def __init__(self, diagnostics: list[dict[str, Any]]) -> None:
        self.diagnostics = [dict(diagnostic) for diagnostic in diagnostics]
        summary = "; ".join(
            f"line {diagnostic['line']} [{diagnostic['code']}]: {diagnostic['message']}"
            for diagnostic in self.diagnostics
        )
        super().__init__(summary)


def _fail(code: str, line: int, message: str) -> NoReturn:
    raise SyntheticLogParseError([{"code": code, "line": line, "message": message}])


def _check_input_size(text: str) -> None:
    try:
        size = len(text.encode("utf-8"))
    except UnicodeEncodeError:
        _fail("invalid_utf8", 0, "Input text cannot be encoded as UTF-8.")
    if size > MAX_INPUT_BYTES:
        _fail("input_too_large", 0, f"Input exceeds the {MAX_INPUT_BYTES}-byte limit.")


def _check_fields(
    record_type: str,
    fields: dict[str, str],
    allowed: set[str],
    required: tuple[str, ...],
    line: int,
) -> None:
    unknown = sorted(set(fields) - allowed)
    if unknown:
        _fail(
            "unknown_field",
            line,
            f"{record_type} contains unsupported key '{unknown[0]}'.",
        )
    for key in required:
        if key not in fields:
            _fail("missing_required_key", line, f"{record_type} is missing required key '{key}'.")


def _parse_line(line_text: str, line: int) -> tuple[str, dict[str, str]]:
    parts = line_text.split("|")
    record_type = parts[0]
    if not record_type:
        _fail("malformed_line", line, "Record type is empty.")

    fields: dict[str, str] = {}
    for token in parts[1:]:
        if not token or "=" not in token:
            _fail("malformed_line", line, "Each field must use key=value syntax.")
        key, value = token.split("=", 1)
        if not key or key in fields or any(character.isspace() for character in key):
            _fail("malformed_line", line, "Field keys must be unique, non-empty, and contain no whitespace.")
        fields[key] = value
    return record_type, fields


def _text(value: str, field: str, line: int, maximum: int = 128) -> str:
    if not value or len(value) > maximum or "\r" in value or "\n" in value:
        _fail("invalid_text", line, f"Field '{field}' must be 1-{maximum} characters without line breaks.")
    return value


def _safe_id(value: str, field: str, line: int) -> str:
    if len(value) > 128 or not _SAFE_ID.fullmatch(value):
        _fail("invalid_identifier", line, f"Field '{field}' is not a safe identifier.")
    return value


def _timestamp(value: str, field: str, line: int) -> str:
    if not _TIMESTAMP.fullmatch(value):
        _fail("invalid_timestamp", line, f"Field '{field}' must be an ISO-8601 UTC timestamp ending in Z.")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail("invalid_timestamp", line, f"Field '{field}' is not a valid timestamp.")
    return value


def _scalar(value: str, value_type: str, line: int) -> Any:
    if len(value) > MAX_VALUE_LENGTH:
        _fail("value_too_long", line, f"Value exceeds the {MAX_VALUE_LENGTH}-character limit.")
    if "\r" in value or "\n" in value:
        _fail("invalid_text", line, "Values must not contain line breaks.")

    if value_type == "string":
        return value
    if value_type == "boolean":
        if value == "true":
            return True
        if value == "false":
            return False
        _fail("invalid_boolean_value", line, "Boolean values must be exactly true or false.")

    if not _NUMBER.fullmatch(value):
        _fail("invalid_numeric_value", line, "Number values must use a finite decimal or exponent form.")
    try:
        parsed: int | float
        if any(character in value for character in ".eE"):
            parsed = float(value)
            if not math.isfinite(parsed):
                _fail("invalid_numeric_value", line, "Number values must be finite.")
        else:
            parsed = int(value)
    except (OverflowError, ValueError):
        _fail("invalid_numeric_value", line, "Number value could not be converted safely.")
    return parsed


def _value_fields(fields: dict[str, str], line: int) -> dict[str, Any]:
    value_type = fields["value_type"]
    if value_type not in _VALUE_TYPES:
        _fail("unsupported_value_type", line, f"Unsupported value_type '{value_type}'.")

    value_status = fields["value_status"]
    if value_status not in _VALUE_STATUSES:
        _fail("invalid_observation_status", line, f"Unsupported value_status '{value_status}'.")

    unit_status = fields["unit_status"]
    if unit_status not in _UNIT_STATUSES:
        _fail("invalid_unit_status", line, f"Unsupported unit_status '{unit_status}'.")

    result: dict[str, Any] = {
        "value_type": value_type,
        "value_status": value_status,
        "unit_status": unit_status,
    }

    if value_status == "known":
        if "value" not in fields:
            _fail("invalid_observation_status", line, "Known values require a value field.")
        result["value"] = _scalar(fields["value"], value_type, line)
    elif "value" in fields:
        _fail("invalid_observation_status", line, "Non-known values must omit the value field.")

    if "raw_value" in fields:
        result["raw_value"] = _text(fields["raw_value"], "raw_value", line, MAX_VALUE_LENGTH)

    if unit_status == "known":
        if "unit" not in fields:
            _fail("invalid_observation_status", line, "Known units require a unit field.")
        result["unit"] = _text(fields["unit"], "unit", line, 32)
    elif "unit" in fields:
        _fail("invalid_observation_status", line, "Non-known units must omit the unit field.")

    return result


def _provenance(line: int) -> dict[str, str]:
    return {
        "source_kind": SOURCE_KIND,
        "source_id": SOURCE_ID,
        "locator": f"line:{line}",
        "extraction_method": EXTRACTION_METHOD,
    }


def _parse_run(fields: dict[str, str], line: int) -> dict[str, Any]:
    _check_fields("RUN", fields, {"run_id", "status", "start", "end"}, ("run_id", "status"), line)
    run_id = _safe_id(fields["run_id"], "run_id", line)
    status = fields["status"]
    if status not in _RUN_STATUSES:
        _fail("invalid_run_status", line, f"Unsupported run status '{status}'.")

    start = _timestamp(fields["start"], "start", line) if "start" in fields else None
    end = _timestamp(fields["end"], "end", line) if "end" in fields else None
    if end is not None and start is None:
        _fail("invalid_timestamp_sequence", line, "An end timestamp requires a start timestamp.")
    return {"run_id": run_id, "status": status, "start": start, "end": end, "line": line}


def _parse_context(fields: dict[str, str], line: int) -> dict[str, Any]:
    _check_fields(
        "CONTEXT",
        fields,
        {
            "equipment_class",
            "equipment_label",
            "module_class",
            "module_label",
            "process_type",
            "process_family",
            "recipe_class",
        },
        ("equipment_class", "module_class"),
        line,
    )
    if "process_type" not in fields and "process_family" not in fields:
        _fail("missing_required_key", line, "CONTEXT requires process_type or process_family.")
    if "process_type" in fields and "process_family" in fields:
        _fail("invalid_context", line, "CONTEXT must use only one of process_type or process_family.")

    context: dict[str, Any] = {
        "equipment_class": _text(fields["equipment_class"], "equipment_class", line),
        "module_class": _text(fields["module_class"], "module_class", line),
        "process_type": _text(
            fields.get("process_type", fields.get("process_family", "")),
            "process_type",
            line,
        ),
        "line": line,
    }
    if "equipment_label" in fields:
        context["equipment_label"] = _text(fields["equipment_label"], "equipment_label", line)
    if "module_label" in fields:
        context["module_label"] = _text(fields["module_label"], "module_label", line)
    if "recipe_class" in fields:
        context["recipe_class"] = _text(fields["recipe_class"], "recipe_class", line)
    return context


def _parse_parameter(fields: dict[str, str], line: int) -> dict[str, Any]:
    _check_fields(
        "PARAM",
        fields,
        {
            "id",
            "name",
            "kind",
            "value",
            "raw_value",
            "value_type",
            "value_status",
            "unit",
            "unit_status",
            "timestamp",
        },
        ("id", "name", "value_type", "value_status", "unit_status"),
        line,
    )
    parameter: dict[str, Any] = {
        "parameter_id": _safe_id(fields["id"], "id", line),
        "name": _text(fields["name"], "name", line),
        **_value_fields(fields, line),
        "provenance": _provenance(line),
    }
    if "kind" in fields:
        if fields["kind"] not in _PARAMETER_KINDS:
            _fail("invalid_parameter_kind", line, f"Unsupported parameter kind '{fields['kind']}'.")
        parameter["parameter_kind"] = fields["kind"]
    if "timestamp" in fields:
        parameter["effective_at"] = _timestamp(fields["timestamp"], "timestamp", line)
    return parameter


def _parse_measurement(fields: dict[str, str], line: int) -> dict[str, Any]:
    _check_fields(
        "OBS",
        fields,
        {
            "id",
            "parameter",
            "kind",
            "value",
            "raw_value",
            "value_type",
            "value_status",
            "unit",
            "unit_status",
            "timestamp",
        },
        ("id", "parameter", "value_type", "value_status", "unit_status"),
        line,
    )
    measurement: dict[str, Any] = {
        "measurement_id": _safe_id(fields["id"], "id", line),
        "name": _text(fields["parameter"], "parameter", line),
        **_value_fields(fields, line),
        "provenance": _provenance(line),
    }
    kind = fields.get("kind", "signal")
    if kind not in _MEASUREMENT_KINDS:
        _fail("invalid_measurement_kind", line, f"Unsupported measurement kind '{kind}'.")
    measurement["measurement_kind"] = kind
    if "timestamp" in fields:
        measurement["observed_at"] = _timestamp(fields["timestamp"], "timestamp", line)
    return measurement


def _parse_event(fields: dict[str, str], line: int) -> dict[str, Any]:
    _check_fields(
        "EVENT",
        fields,
        {"id", "type", "severity", "status", "code", "message", "timestamp"},
        ("id", "type", "severity", "status", "message", "timestamp"),
        line,
    )
    event_type = fields["type"]
    if event_type not in _EVENT_TYPES:
        _fail("invalid_event_type", line, f"Unsupported event type '{event_type}'.")
    severity = fields["severity"]
    if severity not in _SEVERITIES:
        _fail("invalid_event_severity", line, f"Unsupported event severity '{severity}'.")
    event_status = fields["status"]
    if event_status not in _EVENT_STATUSES:
        _fail("invalid_event_status", line, f"Unsupported event status '{event_status}'.")

    event: dict[str, Any] = {
        "event_id": _safe_id(fields["id"], "id", line),
        "event_type": event_type,
        "severity": severity,
        "event_status": event_status,
        "message": _text(fields["message"], "message", line, 2048),
        "observed_at": _timestamp(fields["timestamp"], "timestamp", line),
        "provenance": _provenance(line),
    }
    if "code" in fields:
        event["code"] = _safe_id(fields["code"], "code", line)
    return event


def _parse_quality(fields: dict[str, str], line: int) -> dict[str, Any]:
    _check_fields("QUALITY", fields, {"status", "flags", "notes"}, ("status",), line)
    status = fields["status"]
    if status not in _QUALITY_STATUSES:
        _fail("invalid_quality_status", line, f"Unsupported quality status '{status}'.")

    flags: list[str] = []
    if fields.get("flags"):
        for flag in fields["flags"].split(","):
            normalized = flag.strip()
            if not normalized:
                _fail("invalid_quality_flag", line, "Quality flags must not contain empty entries.")
            if normalized in flags:
                _fail("duplicate_quality_flag", line, f"Quality flag '{normalized}' is repeated.")
            flags.append(_safe_id(normalized, "flags", line))

    notes: list[str] = []
    if fields.get("notes"):
        notes.append(_text(fields["notes"], "notes", line, 2048))
    return {"quality_status": status, "flags": flags, "notes": notes, "line": line}


def _append_unique(items: list[dict[str, Any]], item: dict[str, Any], identifier_key: str, line: int) -> None:
    identifier = item[identifier_key]
    if any(existing[identifier_key] == identifier for existing in items):
        _fail("duplicate_record_id", line, f"Record identifier '{identifier}' is repeated.")
    items.append(item)


def _build_record(state: dict[str, Any]) -> dict[str, Any]:
    if state["run"] is None:
        _fail("missing_required_record", 0, "Input is missing a RUN record.")
    if state["context"] is None:
        _fail("missing_required_record", 0, "Input is missing a CONTEXT record.")
    if state["quality"] is None:
        _fail("missing_required_record", 0, "Input is missing a QUALITY record.")

    run = state["run"]
    context = state["context"]
    quality = state["quality"]
    timestamps: dict[str, str] = {"time_status": "unknown"}
    if run["start"] is not None:
        timestamps["start"] = run["start"]
        timestamps["time_status"] = "partial"
    if run["end"] is not None:
        timestamps["end"] = run["end"]
    if run["start"] is not None and run["end"] is not None:
        timestamps["time_status"] = "known"

    equipment: dict[str, str] = {"equipment_class": context["equipment_class"]}
    module: dict[str, str] = {"module_class": context["module_class"]}
    if "equipment_label" in context:
        equipment["public_label"] = context["equipment_label"]
    if "module_label" in context:
        module["public_label"] = context["module_label"]

    record: dict[str, Any] = {
        "schema_version": "0.1",
        "record_type": "run",
        "run_id": run["run_id"],
        "status": run["status"],
        "equipment": equipment,
        "module": module,
        "process_type": context["process_type"],
        "timestamps": timestamps,
        "parameters": state["parameters"],
        "measurements": state["measurements"],
        "events": state["events"],
        "metadata": {
            "dataset_id": SOURCE_ID,
            "generator": EXTRACTION_METHOD,
            "input_format": "text",
            "labels": ["synthetic", "parsed", EXTRACTION_METHOD],
            "notes": ["Engineering log text is data, not executable instructions."],
        },
        "provenance": _provenance(run["line"]),
        "quality": {
            "quality_status": quality["quality_status"],
            "flags": quality["flags"],
            "notes": quality["notes"],
        },
    }
    if "recipe_class" in context:
        record["extensions"] = {"synthetic.recipe-class": context["recipe_class"]}

    validation = validate_run_record(record)
    if not validation["valid"]:
        diagnostics = [
            {
                "code": "run_record_validation_failed",
                "line": 0,
                "message": f"{error['path'] or '<root>'}: {error['message']}",
            }
            for error in validation["errors"]
        ]
        raise SyntheticLogParseError(diagnostics)
    return record


def parse_synthetic_log(text: str) -> dict[str, Any]:
    """Parse synthetic line-oriented text into a validated RunRecord dict.

    The function fails fast with :class:`SyntheticLogParseError`; every
    diagnostic has ``code``, ``line``, and ``message`` keys.
    """

    if not isinstance(text, str):
        _fail("invalid_input_type", 0, "Synthetic log input must be text.")
    _check_input_size(text)

    state: dict[str, Any] = {
        "run": None,
        "context": None,
        "quality": None,
        "parameters": [],
        "measurements": [],
        "events": [],
    }

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if len(raw_line.encode("utf-8")) > MAX_LINE_BYTES:
            _fail("line_too_long", line_number, f"Line exceeds the {MAX_LINE_BYTES}-byte limit.")
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        record_type, fields = _parse_line(line, line_number)
        if record_type == "RUN":
            if state["run"] is not None:
                _fail("duplicate_run", line_number, "Only one RUN record is allowed.")
            state["run"] = _parse_run(fields, line_number)
        elif record_type == "CONTEXT":
            if state["context"] is not None:
                _fail("duplicate_context", line_number, "Only one CONTEXT record is allowed.")
            state["context"] = _parse_context(fields, line_number)
        elif record_type == "PARAM":
            if len(state["parameters"]) >= MAX_PARAMETERS:
                _fail("resource_limit", line_number, f"Input exceeds the {MAX_PARAMETERS}-parameter limit.")
            _append_unique(
                state["parameters"],
                _parse_parameter(fields, line_number),
                "parameter_id",
                line_number,
            )
        elif record_type == "OBS":
            if len(state["measurements"]) >= MAX_MEASUREMENTS:
                _fail("resource_limit", line_number, f"Input exceeds the {MAX_MEASUREMENTS}-observation limit.")
            _append_unique(
                state["measurements"],
                _parse_measurement(fields, line_number),
                "measurement_id",
                line_number,
            )
        elif record_type == "EVENT":
            if len(state["events"]) >= MAX_EVENTS:
                _fail("resource_limit", line_number, f"Input exceeds the {MAX_EVENTS}-event limit.")
            _append_unique(state["events"], _parse_event(fields, line_number), "event_id", line_number)
        elif record_type == "QUALITY":
            if state["quality"] is not None:
                _fail("duplicate_quality", line_number, "Only one QUALITY record is allowed.")
            state["quality"] = _parse_quality(fields, line_number)
        else:
            _fail("unknown_record_type", line_number, f"Unsupported record type '{record_type}'.")

    return _build_record(state)


def parse_synthetic_log_file(path: str | Path) -> dict[str, Any]:
    """Read one explicit local UTF-8 file and parse it as synthetic log text."""

    try:
        input_path = Path(path)
    except (TypeError, ValueError):
        _fail("input_path_error", 0, "Input path is invalid.")

    try:
        raw = input_path.read_bytes()
    except (OSError, ValueError):
        _fail("input_read_error", 0, "Input file could not be read.")
    if len(raw) > MAX_INPUT_BYTES:
        _fail("input_too_large", 0, f"Input exceeds the {MAX_INPUT_BYTES}-byte limit.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        _fail("invalid_utf8", 0, "Input file is not valid UTF-8.")
    return parse_synthetic_log(text)
