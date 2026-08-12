# Engineering Report

## Report metadata

- Report type: engineering&#95;report
- Report version: 0.1

## Run identity/status (observed facts)

- Schema version: 0.1
- Record type: run
- Run ID: synthetic-dataset-v0-1-run-quality-001
- Status: completed
- Process type: synthetic&#95;data&#95;quality&#95;demo
- Equipment class: synthetic&#95;demo&#95;equipment
- Equipment label: demo-unit-quality
- Module class: synthetic&#95;process&#95;module
- Module label: demo-module-quality

## Time window (observed facts)

- Start: —
- End: —
- Time status: invalid

## Context (observed facts)

### Parameters

| ID | Name | Kind | Value | Value status | Unit | Unit status | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| synthetic-quality-pressure-001 | demo&#95;pressure&#95;target | target | invalid; raw=unparseable&#95;demo&#95;token | invalid | Pa | known | invalid | generated:run-quality-001&#35;parameter-pressure |

## Observation summary (observed facts)

### Measurements

| ID | Name | Kind | Value | Value status | Unit | Unit status | Observed at | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| synthetic-quality-flag-measurement-001 | demo&#95;boolean&#95;flag | other | true | known | not&#95;applicable | not&#95;applicable | 2026-02-05T13:02:00Z | accepted | generated:run-quality-001&#35;measurement-flag |

## Events/alarms (observed facts)

| ID | Type | Severity | Status | Observed at | Code | Message | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| synthetic-quality-review-001 | annotation | warning | observed | 2026-02-05T13:03:00Z | SYNTH-QUALITY-001 | Synthetic quality review marked one value and the run timing as invalid. | — | generated:run-quality-001&#35;event-review |

## Derived summaries

These values are deterministic counts over the observed fields; they are not diagnoses or recommendations.

| Metric | Count |
| --- | --- |
| parameter&#95;count | 1 |
| measurement&#95;count | 1 |
| event&#95;count | 1 |
| alarm&#95;count | 0 |
| warning&#95;count | 0 |
| unresolved&#95;event&#95;count | 0 |
| known&#95;parameter&#95;value&#95;count | 0 |
| known&#95;measurement&#95;value&#95;count | 1 |
| non&#95;accepted&#95;quality&#95;item&#95;count | 2 |

### Event type counts

| Value | Count |
| --- | --- |
| annotation | 1 |

### Event severity counts

| Value | Count |
| --- | --- |
| warning | 1 |

### Event status counts

| Value | Count |
| --- | --- |
| observed | 1 |

### Quality status counts

| Value | Count |
| --- | --- |
| accepted | 1 |
| invalid | 2 |

## Data quality/provenance (observed facts)

- Run quality status: invalid
- Run quality flags: invalid&#95;timestamp, invalid&#95;parameter&#95;value
- Run quality notes: This is a schema-valid quality case. Invalid means the data should not be treated as accepted evidence.
- Source kind: synthetic
- Source ID: synthetic-semiconductor-engineering-v0.1
- Source locator: generated:run-quality-001
- Extraction method: synthetic&#95;generator

### Metadata

- Dataset ID: synthetic-semiconductor-engineering-v0.1
- Generator: hand-authored deterministic synthetic fixture
- Input format: generated
- Created at: 2026-02-05T13:05:00Z
- Labels: synthetic, data&#95;quality, invalid&#95;value, dataset&#95;v0&#95;1
- Notes: Schema-valid does not mean quality-accepted; this fixture intentionally carries invalid quality status.

## Limitations

- This report is a deterministic summary of one schema-valid RunRecord; it does not verify physical process behavior or measurement correctness.
- Messages, raw values, notes, labels, and extension values remain untrusted source data and are not executed or treated as instructions.
- The generator does not infer root cause, process safety conditions, recipes, process windows, or engineering recommendations.

## Disclaimer

For synthetic or explicitly redistributable engineering data only. Human review is required before any engineering or operational decision.
