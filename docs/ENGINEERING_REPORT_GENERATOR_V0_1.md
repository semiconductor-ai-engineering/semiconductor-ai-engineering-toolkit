# Engineering Report Generator v0.1

## Status

This phase adds a deterministic, non-LLM engineering report generator for canonical RunRecord v0.1 data. It is intended for synthetic or explicitly redistributable public examples. It does not claim physical-process correctness or production readiness.

## Contract

The generator accepts one in-memory RunRecord mapping or one explicit local UTF-8 JSON file. Every input is passed through the existing `validate_run_record` API before any report summary is built. The canonical JSON Schema at [`schema/run_record_v0_1.schema.json`](../schema/run_record_v0_1.schema.json) remains unchanged and remains the only RunRecord input contract.

The returned dictionary is a ReportRecord-compatible v0.1 structure with these stable top-level fields:

| Field | Meaning |
| --- | --- |
| `report_version` | Report contract version, currently `0.1`. |
| `report_type` | Fixed value `engineering_report`. |
| `observed_facts` | Copied RunRecord fields grouped as identity/status, time window, context, observations, events/alarms, and data quality/provenance. |
| `derived_summaries` | Deterministic counts only. Counts are never presented as a diagnosis or recommendation. |
| `limitations` | Fixed safety and interpretation boundaries. |
| `disclaimer` | Fixed human-review disclaimer. |

### Observed facts

`observed_facts` retains source values and item provenance. It includes:

- run identity, status, equipment, module, and process type;
- start/end values and the canonical `time_status`;
- parameters with value/unit status and provenance;
- measurements with value/unit status, observation time, and provenance;
- events and alarms with type, severity, status, message, and provenance;
- metadata, run-level quality, and run-level provenance.

The report renderer labels these sections as **observed facts**. Text fields are escaped before Markdown rendering. Messages, notes, labels, raw values, and extension values remain data, not instructions.

### Derived summaries

The generator calculates only stable counts from the observed arrays:

- parameter, measurement, and event totals;
- alarm, warning, unresolved-event, and known-value totals;
- non-accepted quality-item total;
- event type, severity, and status counts;
- quality status counts across the run and item-level quality objects.

The implementation does not calculate duration, thresholds, root cause, safety state, recipe guidance, process-window guidance, or recommendations.

## Python API

```python
from semiconductor_ai_engineering_toolkit import (
    generate_engineering_report,
    generate_engineering_report_file,
    render_engineering_report,
)

report = generate_engineering_report(record)
report_from_file = generate_engineering_report_file(
    "examples/synthetic_data/run_completed_001.json"
)
markdown = render_engineering_report(report_from_file)
```

Invalid RunRecord data raises `EngineeringReportValidationError` with the same stable error entries returned by the canonical validator. File decoding and JSON parsing failures raise `EngineeringReportInputError` with a safe error code and message.

## CLI

Print Markdown to standard output:

```text
semi-ai report examples/synthetic_data/run_completed_001.json
```

Write a report to a new file:

```text
semi-ai report examples/synthetic_data/run_completed_001.json --output report.md
```

An existing output file is never overwritten. The CLI creates the output with exclusive file creation and returns a non-zero status when the path already exists or cannot be written.

The renderer does not add the current time, random identifiers, absolute input paths, network URLs, or environment values. The same validated RunRecord produces byte-for-byte identical Markdown.

## Safety boundary

- No LLM, OpenAI API, RAG, Agent, network access, secret access, or dynamic execution is used.
- Only the caller-selected local input path is read.
- The validator rejects external JSON Schema references before validator construction.
- Untrusted text is escaped for Markdown and is never evaluated or obeyed.
- The report does not provide root-cause diagnosis, process safety advice, recipes, process windows, or engineering recommendations.

## Synthetic regression fixtures

Expected Markdown reports live under [`examples/synthetic_reports/expected/`](../examples/synthetic_reports/expected/). They cover:

| Scenario | Source fixture | Expected report |
| --- | --- | --- |
| Completed | [`run_completed_001.json`](../examples/synthetic_data/run_completed_001.json) | [`run_completed_001.md`](../examples/synthetic_reports/expected/run_completed_001.md) |
| Warning/alarm | [`run_warning_alarm_001.json`](../examples/synthetic_data/run_warning_alarm_001.json) | [`run_warning_alarm_001.md`](../examples/synthetic_reports/expected/run_warning_alarm_001.md) |
| Aborted/incomplete | [`run_incomplete_001.json`](../examples/synthetic_data/run_incomplete_001.json) | [`run_incomplete_001.md`](../examples/synthetic_reports/expected/run_incomplete_001.md) |
| Data quality issue | [`run_data_quality_001.json`](../examples/synthetic_dataset_v0_1/runs/quality_cases/run_data_quality_001.json) | [`run_data_quality_001.md`](../examples/synthetic_reports/expected/run_data_quality_001.md) |

Tests also cover an invalid RunRecord, malformed/invalid UTF-8 input files, output-file collision, deterministic repeated rendering, and a source-level no-network/no-eval/no-exec check.

## Schema decision

The canonical RunRecord v0.1 schema is not modified in this phase. The report contract is downstream output and does not add fields to the input schema.
