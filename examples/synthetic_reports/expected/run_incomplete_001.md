# Engineering Report

## Report metadata

- Report type: engineering&#95;report
- Report version: 0.1

## Run identity/status (observed facts)

- Schema version: 0.1
- Record type: run
- Run ID: synthetic-run-incomplete-001
- Status: aborted
- Process type: generic&#95;incomplete&#95;input&#95;demo
- Equipment class: synthetic&#95;chamber
- Equipment label: demo-equipment
- Module class: generic&#95;process&#95;module
- Module label: demo-module

## Time window (observed facts)

- Start: 2026-01-16T14:00:00Z
- End: —
- Time status: partial

## Context (observed facts)

### Parameters

| ID | Name | Kind | Value | Value status | Unit | Unit status | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| param-pressure-setpoint-002 | pressure&#95;setpoint | setpoint | unknown | unknown | Pa | known | incomplete | generated:run-incomplete-001&#35;parameter-pressure |
| param-power-setpoint-002 | power&#95;setpoint | setpoint | missing; raw=not recorded | missing | missing | missing | incomplete | generated:run-incomplete-001&#35;parameter-power |

## Observation summary (observed facts)

### Measurements

| ID | Name | Kind | Value | Value status | Unit | Unit status | Observed at | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| measurement-temperature-002 | module&#95;temperature | signal | 66.0 | known | unknown | unknown | 2026-01-16T14:02:00Z | uncertain | generated:run-incomplete-001&#35;measurement-temperature |

## Events/alarms (observed facts)

| ID | Type | Severity | Status | Observed at | Code | Message | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| event-run-started-002 | state&#95;change | info | observed | 2026-01-16T14:00:00Z | SYNTH&#95;RUN&#95;STARTED | — | — | generated:run-incomplete-001&#35;event-started |
| event-sensor-timeout-002 | alarm | error | unresolved | 2026-01-16T14:03:00Z | SYNTH&#95;SENSOR&#95;TIMEOUT | Synthetic measurement stream ended before the demo run completed. | accepted | generated:run-incomplete-001&#35;event-alarm |

## Derived summaries

These values are deterministic counts over the observed fields; they are not diagnoses or recommendations.

| Metric | Count |
| --- | --- |
| parameter&#95;count | 2 |
| measurement&#95;count | 1 |
| event&#95;count | 2 |
| alarm&#95;count | 1 |
| warning&#95;count | 0 |
| unresolved&#95;event&#95;count | 1 |
| known&#95;parameter&#95;value&#95;count | 0 |
| known&#95;measurement&#95;value&#95;count | 1 |
| non&#95;accepted&#95;quality&#95;item&#95;count | 4 |

### Event type counts

| Value | Count |
| --- | --- |
| alarm | 1 |
| state&#95;change | 1 |

### Event severity counts

| Value | Count |
| --- | --- |
| error | 1 |
| info | 1 |

### Event status counts

| Value | Count |
| --- | --- |
| observed | 1 |
| unresolved | 1 |

### Quality status counts

| Value | Count |
| --- | --- |
| accepted | 1 |
| incomplete | 3 |
| uncertain | 1 |

## Data quality/provenance (observed facts)

- Run quality status: incomplete
- Run quality flags: partial&#95;timestamps, incomplete&#95;inputs, unresolved&#95;alarm
- Run quality notes: Synthetic fixture; an incomplete record is expected to remain visibly incomplete.
- Source kind: synthetic
- Source ID: synthetic-dataset-v0.1
- Source locator: generated:run-incomplete-001
- Extraction method: synthetic&#95;generator

### Metadata

- Dataset ID: synthetic-dataset-v0.1
- Generator: hand-authored deterministic fixture
- Input format: generated
- Created at: 2026-01-16T14:10:00Z
- Labels: synthetic, incomplete, training&#95;fixture
- Notes: This fixture intentionally demonstrates unknown values, missing units, and an unresolved alarm.

## Limitations

- This report is a deterministic summary of one schema-valid RunRecord; it does not verify physical process behavior or measurement correctness.
- Messages, raw values, notes, labels, and extension values remain untrusted source data and are not executed or treated as instructions.
- The generator does not infer root cause, process safety conditions, recipes, process windows, or engineering recommendations.

## Disclaimer

For synthetic or explicitly redistributable engineering data only. Human review is required before any engineering or operational decision.
