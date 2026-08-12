"""Deterministic engineering reports for validated RunRecord v0.1 data.

The canonical RunRecord JSON Schema remains the only input contract. This
module copies observed source fields into an explicit ``observed_facts``
section and keeps count-based calculations under ``derived_summaries``. It
does not infer causes, recommendations, or process guidance from the data.
"""

from __future__ import annotations

import copy
import html
import json
from pathlib import Path
from typing import Any, Mapping, cast

from .validation import validate_run_record

REPORT_TYPE = "engineering_report"
REPORT_VERSION = "0.1"

LIMITATIONS = (
    "This report is a deterministic summary of one schema-valid RunRecord; it does not verify physical process behavior or measurement correctness.",
    "Messages, raw values, notes, labels, and extension values remain untrusted source data and are not executed or treated as instructions.",
    "The generator does not infer root cause, process safety conditions, recipes, process windows, or engineering recommendations.",
)
DISCLAIMER = (
    "For synthetic or explicitly redistributable engineering data only. "
    "Human review is required before any engineering or operational decision."
)


class EngineeringReportError(ValueError):
    """Base class for deterministic report-generation failures."""


class EngineeringReportInputError(EngineeringReportError):
    """Raised when the explicit local JSON input cannot be read safely."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class EngineeringReportValidationError(EngineeringReportError):
    """Raised when the input fails the canonical RunRecord validator."""

    def __init__(self, errors: list[dict[str, str]]) -> None:
        self.errors = copy.deepcopy(errors)
        super().__init__("RunRecord validation failed.")


def _copy(value: Any) -> Any:
    """Copy JSON-like input so report generation never mutates the caller's data."""

    return copy.deepcopy(value)


def _count_by(items: list[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = item.get(key)
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return {name: counts[name] for name in sorted(counts)}


def _quality_items(record: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    items: list[Mapping[str, Any]] = [cast(Mapping[str, Any], record["quality"])]
    for collection_name in ("parameters", "measurements", "events"):
        for item in record[collection_name]:
            if isinstance(item.get("quality"), Mapping):
                items.append(cast(Mapping[str, Any], item["quality"]))
    return items


def _derived_summaries(record: Mapping[str, Any]) -> dict[str, Any]:
    parameters = cast(list[Mapping[str, Any]], record["parameters"])
    measurements = cast(list[Mapping[str, Any]], record["measurements"])
    events = cast(list[Mapping[str, Any]], record["events"])
    quality_items = _quality_items(record)

    counts = {
        "parameter_count": len(parameters),
        "measurement_count": len(measurements),
        "event_count": len(events),
        "alarm_count": sum(item.get("event_type") == "alarm" for item in events),
        "warning_count": sum(item.get("event_type") == "warning" for item in events),
        "unresolved_event_count": sum(
            item.get("event_status") == "unresolved" for item in events
        ),
        "known_parameter_value_count": sum(
            item.get("value_status") == "known" for item in parameters
        ),
        "known_measurement_value_count": sum(
            item.get("value_status") == "known" for item in measurements
        ),
        "non_accepted_quality_item_count": sum(
            item.get("quality_status") != "accepted" for item in quality_items
        ),
    }
    return {
        "counts": counts,
        "event_type_counts": _count_by(events, "event_type"),
        "event_severity_counts": _count_by(events, "severity"),
        "event_status_counts": _count_by(events, "event_status"),
        "quality_status_counts": _count_by(quality_items, "quality_status"),
    }


def generate_engineering_report(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one RunRecord and return a deterministic report dictionary.

    The returned object has two deliberately separate data areas:
    ``observed_facts`` contains copied source fields, while
    ``derived_summaries`` contains only deterministic counts. No input field
    is interpreted as an instruction or used to make a causal claim.
    """

    validation = validate_run_record(record)
    if not validation["valid"]:
        raise EngineeringReportValidationError(validation["errors"])

    validated_record = cast(dict[str, Any], _copy(record))
    observed_facts = {
        "run_identity_status": {
            "schema_version": validated_record["schema_version"],
            "record_type": validated_record["record_type"],
            "run_id": validated_record["run_id"],
            "status": validated_record["status"],
            "equipment": _copy(validated_record["equipment"]),
            "module": _copy(validated_record["module"]),
            "process_type": validated_record["process_type"],
        },
        "time_window": _copy(validated_record["timestamps"]),
        "context": {
            "parameters": _copy(validated_record["parameters"]),
        },
        "observation_summary": {
            "measurements": _copy(validated_record["measurements"]),
        },
        "events_alarms": _copy(validated_record["events"]),
        "data_quality_provenance": {
            "metadata": _copy(validated_record["metadata"]),
            "run_quality": _copy(validated_record["quality"]),
            "run_provenance": _copy(validated_record["provenance"]),
        },
    }
    return {
        "report_version": REPORT_VERSION,
        "report_type": REPORT_TYPE,
        "observed_facts": observed_facts,
        "derived_summaries": _derived_summaries(validated_record),
        "limitations": list(LIMITATIONS),
        "disclaimer": DISCLAIMER,
    }


def _read_json_file(path: str | Path) -> Any:
    try:
        input_path = Path(path)
    except (TypeError, ValueError):
        raise EngineeringReportInputError("file", "Input path is invalid.") from None

    try:
        raw = input_path.read_bytes()
    except (OSError, ValueError):
        raise EngineeringReportInputError(
            "file", "Input file could not be read."
        ) from None

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise EngineeringReportInputError(
            "utf-8", "Input file is not valid UTF-8."
        ) from None

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        message = f"Invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})."
        raise EngineeringReportInputError("json", message) from None


def generate_engineering_report_file(path: str | Path) -> dict[str, Any]:
    """Read one explicit local UTF-8 JSON file, validate it, and summarize it."""

    record = _read_json_file(path)
    return generate_engineering_report(record)


def _scalar_text(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _safe_text(value: Any) -> str:
    """Escape untrusted values before placing them in Markdown."""

    text = html.escape(_scalar_text(value), quote=False)
    replacements = {
        "#": "&#35;",
        "\\": "&#92;",
        "`": "&#96;",
        "*": "&#42;",
        "_": "&#95;",
        "[": "&#91;",
        "]": "&#93;",
        "(": "&#40;",
        ")": "&#41;",
        "|": "&#124;",
        ">": "&#62;",
        "\r": "",
        "\n": "<br>",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _list_text(values: Any) -> str:
    if not values:
        return "—"
    return ", ".join(_safe_text(value) for value in values)


def _provenance_source(item: Mapping[str, Any]) -> Any:
    provenance = item.get("provenance")
    if not isinstance(provenance, Mapping):
        return "—"
    return provenance.get("locator") or provenance.get("source_id") or "—"


def _quality_status(item: Mapping[str, Any]) -> Any:
    quality = item.get("quality")
    if not isinstance(quality, Mapping):
        return "—"
    return quality.get("quality_status", "—")


def _value_text(item: Mapping[str, Any]) -> str:
    status = item.get("value_status", "unknown")
    if status == "known":
        return _scalar_text(item.get("value"))
    raw_value = item.get("raw_value")
    if raw_value is not None:
        return f"{_scalar_text(status)}; raw={_scalar_text(raw_value)}"
    return _scalar_text(status)


def _unit_text(item: Mapping[str, Any]) -> str:
    if item.get("unit_status") == "known":
        return _scalar_text(item.get("unit"))
    return _scalar_text(item.get("unit_status", "unknown"))


def _table(lines: list[str], headers: list[str], rows: list[list[Any]]) -> None:
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    if not rows:
        rows = [["—" for _ in headers]]
    for row in rows:
        lines.append("| " + " | ".join(_safe_text(value) for value in row) + " |")


def _render_count_map(lines: list[str], title: str, values: Mapping[str, int]) -> None:
    lines.extend([f"### {title}", ""])
    _table(lines, ["Value", "Count"], [[key, values[key]] for key in sorted(values)])
    lines.append("")


def render_engineering_report(report: Mapping[str, Any]) -> str:
    """Render a generated report dictionary as stable UTF-8 Markdown."""

    observed = report["observed_facts"]
    run = observed["run_identity_status"]
    time_window = observed["time_window"]
    context = observed["context"]
    observation = observed["observation_summary"]
    events = observed["events_alarms"]
    quality_data = observed["data_quality_provenance"]
    derived = report["derived_summaries"]

    equipment = run["equipment"]
    module = run["module"]
    lines = [
        "# Engineering Report",
        "",
        "## Report metadata",
        "",
        f"- Report type: {_safe_text(report['report_type'])}",
        f"- Report version: {_safe_text(report['report_version'])}",
        "",
        "## Run identity/status (observed facts)",
        "",
        f"- Schema version: {_safe_text(run['schema_version'])}",
        f"- Record type: {_safe_text(run['record_type'])}",
        f"- Run ID: {_safe_text(run['run_id'])}",
        f"- Status: {_safe_text(run['status'])}",
        f"- Process type: {_safe_text(run['process_type'])}",
        f"- Equipment class: {_safe_text(equipment.get('equipment_class'))}",
        f"- Equipment label: {_safe_text(equipment.get('public_label', '—'))}",
        f"- Module class: {_safe_text(module.get('module_class'))}",
        f"- Module label: {_safe_text(module.get('public_label', '—'))}",
        "",
        "## Time window (observed facts)",
        "",
        f"- Start: {_safe_text(time_window.get('start', '—'))}",
        f"- End: {_safe_text(time_window.get('end', '—'))}",
        f"- Time status: {_safe_text(time_window['time_status'])}",
        "",
        "## Context (observed facts)",
        "",
        "### Parameters",
        "",
    ]
    parameter_rows = [
        [
            item.get("parameter_id"),
            item.get("name"),
            item.get("parameter_kind", "—"),
            _value_text(item),
            item.get("value_status"),
            _unit_text(item),
            item.get("unit_status"),
            _quality_status(item),
            _provenance_source(item),
        ]
        for item in context["parameters"]
    ]
    _table(
        lines,
        ["ID", "Name", "Kind", "Value", "Value status", "Unit", "Unit status", "Quality", "Source"],
        parameter_rows,
    )
    lines.extend(["", "## Observation summary (observed facts)", "", "### Measurements", ""])
    measurement_rows = [
        [
            item.get("measurement_id"),
            item.get("name"),
            item.get("measurement_kind", "—"),
            _value_text(item),
            item.get("value_status"),
            _unit_text(item),
            item.get("unit_status"),
            item.get("observed_at", "—"),
            _quality_status(item),
            _provenance_source(item),
        ]
        for item in observation["measurements"]
    ]
    _table(
        lines,
        [
            "ID",
            "Name",
            "Kind",
            "Value",
            "Value status",
            "Unit",
            "Unit status",
            "Observed at",
            "Quality",
            "Source",
        ],
        measurement_rows,
    )
    lines.extend(["", "## Events/alarms (observed facts)", ""])
    event_rows = [
        [
            item.get("event_id"),
            item.get("event_type"),
            item.get("severity"),
            item.get("event_status"),
            item.get("observed_at", "—"),
            item.get("code", "—"),
            item.get("message", "—"),
            _quality_status(item),
            _provenance_source(item),
        ]
        for item in events
    ]
    _table(
        lines,
        ["ID", "Type", "Severity", "Status", "Observed at", "Code", "Message", "Quality", "Source"],
        event_rows,
    )
    lines.extend(["", "## Derived summaries", "", "These values are deterministic counts over the observed fields; they are not diagnoses or recommendations.", ""])
    _table(
        lines,
        ["Metric", "Count"],
        [[key, derived["counts"][key]] for key in derived["counts"]],
    )
    lines.append("")
    _render_count_map(lines, "Event type counts", derived["event_type_counts"])
    _render_count_map(lines, "Event severity counts", derived["event_severity_counts"])
    _render_count_map(lines, "Event status counts", derived["event_status_counts"])
    _render_count_map(lines, "Quality status counts", derived["quality_status_counts"])

    run_quality = quality_data["run_quality"]
    run_provenance = quality_data["run_provenance"]
    metadata = quality_data["metadata"]
    lines.extend(
        [
            "## Data quality/provenance (observed facts)",
            "",
            f"- Run quality status: {_safe_text(run_quality.get('quality_status'))}",
            f"- Run quality flags: {_list_text(run_quality.get('flags'))}",
            f"- Run quality notes: {_list_text(run_quality.get('notes'))}",
            f"- Source kind: {_safe_text(run_provenance.get('source_kind'))}",
            f"- Source ID: {_safe_text(run_provenance.get('source_id'))}",
            f"- Source locator: {_safe_text(run_provenance.get('locator', '—'))}",
            f"- Extraction method: {_safe_text(run_provenance.get('extraction_method'))}",
            "",
            "### Metadata",
            "",
            f"- Dataset ID: {_safe_text(metadata.get('dataset_id', '—'))}",
            f"- Generator: {_safe_text(metadata.get('generator', '—'))}",
            f"- Input format: {_safe_text(metadata.get('input_format', '—'))}",
            f"- Created at: {_safe_text(metadata.get('created_at', '—'))}",
            f"- Labels: {_list_text(metadata.get('labels'))}",
            f"- Notes: {_list_text(metadata.get('notes'))}",
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {_safe_text(limitation)}" for limitation in report["limitations"])
    lines.extend(["", "## Disclaimer", "", _safe_text(report["disclaimer"]), ""])
    return "\n".join(lines)


__all__ = [
    "DISCLAIMER",
    "EngineeringReportError",
    "EngineeringReportInputError",
    "EngineeringReportValidationError",
    "LIMITATIONS",
    "REPORT_TYPE",
    "REPORT_VERSION",
    "generate_engineering_report",
    "generate_engineering_report_file",
    "render_engineering_report",
]
