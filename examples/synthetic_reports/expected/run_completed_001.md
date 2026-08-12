# Engineering Report

## Report metadata

- Report type: engineering&#95;report
- Report version: 0.1

## Run identity/status (observed facts)

- Schema version: 0.1
- Record type: run
- Run ID: synthetic-run-completed-001
- Status: completed
- Process type: generic&#95;pressure&#95;temperature&#95;demo
- Equipment class: synthetic&#95;chamber
- Equipment label: demo-equipment
- Module class: generic&#95;process&#95;module
- Module label: demo-module

## Time window (observed facts)

- Start: 2026-01-15T10:00:00Z
- End: 2026-01-15T10:12:00Z
- Time status: known

## Context (observed facts)

### Parameters

| ID | Name | Kind | Value | Value status | Unit | Unit status | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| param-pressure-setpoint-001 | pressure&#95;setpoint | setpoint | 15.0 | known | Pa | known | accepted | generated:run-completed-001&#35;parameter-pressure |
| param-power-setpoint-001 | power&#95;setpoint | setpoint | 250.0 | known | W | known | accepted | generated:run-completed-001&#35;parameter-power |

## Observation summary (observed facts)

### Measurements

| ID | Name | Kind | Value | Value status | Unit | Unit status | Observed at | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| measurement-pressure-001 | pressure | signal | 14.8 | known | Pa | known | 2026-01-15T10:04:00Z | accepted | generated:run-completed-001&#35;measurement-pressure |
| measurement-temperature-001 | module&#95;temperature | signal | 68.0 | known | C | known | 2026-01-15T10:05:00Z | accepted | generated:run-completed-001&#35;measurement-temperature |

## Events/alarms (observed facts)

| ID | Type | Severity | Status | Observed at | Code | Message | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| event-run-started-001 | state&#95;change | info | observed | 2026-01-15T10:00:00Z | SYNTH&#95;RUN&#95;STARTED | Synthetic run entered the active state. | accepted | generated:run-completed-001&#35;event-started |
| event-stability-warning-001 | warning | warning | cleared | 2026-01-15T10:03:00Z | SYNTH&#95;STABILITY&#95;DELAY | Synthetic stability check took longer than the demo threshold. | accepted | generated:run-completed-001&#35;event-warning |

## Derived summaries

These values are deterministic counts over the observed fields; they are not diagnoses or recommendations.

| Metric | Count |
| --- | --- |
| parameter&#95;count | 2 |
| measurement&#95;count | 2 |
| event&#95;count | 2 |
| alarm&#95;count | 0 |
| warning&#95;count | 1 |
| unresolved&#95;event&#95;count | 0 |
| known&#95;parameter&#95;value&#95;count | 2 |
| known&#95;measurement&#95;value&#95;count | 2 |
| non&#95;accepted&#95;quality&#95;item&#95;count | 0 |

### Event type counts

| Value | Count |
| --- | --- |
| state&#95;change | 1 |
| warning | 1 |

### Event severity counts

| Value | Count |
| --- | --- |
| info | 1 |
| warning | 1 |

### Event status counts

| Value | Count |
| --- | --- |
| cleared | 1 |
| observed | 1 |

### Quality status counts

| Value | Count |
| --- | --- |
| accepted | 7 |

## Data quality/provenance (observed facts)

- Run quality status: accepted
- Run quality flags: —
- Run quality notes: Synthetic fixture; not a production observation.
- Source kind: synthetic
- Source ID: synthetic-dataset-v0.1
- Source locator: generated:run-completed-001
- Extraction method: synthetic&#95;generator

### Metadata

- Dataset ID: synthetic-dataset-v0.1
- Generator: hand-authored deterministic fixture
- Input format: generated
- Created at: 2026-01-15T10:20:00Z
- Labels: synthetic, complete, training&#95;fixture
- Notes: All values and messages are invented for public schema testing.

## Limitations

- This report is a deterministic summary of one schema-valid RunRecord; it does not verify physical process behavior or measurement correctness.
- Messages, raw values, notes, labels, and extension values remain untrusted source data and are not executed or treated as instructions.
- The generator does not infer root cause, process safety conditions, recipes, process windows, or engineering recommendations.

## Disclaimer

For synthetic or explicitly redistributable engineering data only. Human review is required before any engineering or operational decision.
