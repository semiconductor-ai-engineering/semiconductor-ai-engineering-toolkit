# Engineering Report

## Report metadata

- Report type: engineering&#95;report
- Report version: 0.1

## Run identity/status (observed facts)

- Schema version: 0.1
- Record type: run
- Run ID: synthetic-run-warning-alarm-001
- Status: completed
- Process type: generic&#95;plasma&#95;conditioning&#95;demo
- Equipment class: synthetic&#95;chamber
- Equipment label: demo-equipment
- Module class: generic&#95;process&#95;module
- Module label: demo-module

## Time window (observed facts)

- Start: 2026-01-17T09:30:00Z
- End: 2026-01-17T09:42:00Z
- Time status: known

## Context (observed facts)

### Parameters

| ID | Name | Kind | Value | Value status | Unit | Unit status | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| param-pressure-target-003 | pressure&#95;target | target | 12.0 | known | Pa | known | accepted | generated:run-warning-alarm-001&#35;parameter-pressure |
| param-carrier-flow-003 | carrier&#95;flow | input | 40.0 | known | sccm | known | accepted | generated:run-warning-alarm-001&#35;parameter-flow |
| param-source-power-003 | source&#95;power | setpoint | 180.0 | known | W | known | accepted | generated:run-warning-alarm-001&#35;parameter-power |

## Observation summary (observed facts)

### Measurements

| ID | Name | Kind | Value | Value status | Unit | Unit status | Observed at | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| measurement-pressure-003 | pressure | signal | 12.4 | known | Pa | known | 2026-01-17T09:34:00Z | accepted | generated:run-warning-alarm-001&#35;measurement-pressure |
| measurement-flow-003 | carrier&#95;flow | signal | 39.6 | known | sccm | known | 2026-01-17T09:35:00Z | accepted | generated:run-warning-alarm-001&#35;measurement-flow |
| measurement-module-temperature-003 | module&#95;temperature | result | 72.0 | known | C | known | 2026-01-17T09:40:00Z | accepted | generated:run-warning-alarm-001&#35;measurement-temperature |

## Events/alarms (observed facts)

| ID | Type | Severity | Status | Observed at | Code | Message | Quality | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| event-run-started-003 | state&#95;change | info | observed | 2026-01-17T09:30:00Z | SYNTH&#95;RUN&#95;STARTED | Synthetic conditioning run entered the active state. | accepted | generated:run-warning-alarm-001&#35;event-started |
| event-flow-warning-003 | warning | warning | observed | 2026-01-17T09:35:00Z | SYNTH&#95;FLOW&#95;DRIFT | Synthetic flow signal crossed the demo warning threshold. | accepted | generated:run-warning-alarm-001&#35;event-warning |
| event-pressure-alarm-003 | alarm | error | cleared | 2026-01-17T09:36:00Z | SYNTH&#95;PRESSURE&#95;SPIKE | Synthetic pressure signal exceeded the demo alarm threshold and later returned to the target band. | accepted | generated:run-warning-alarm-001&#35;event-alarm |
| event-run-completed-003 | state&#95;change | info | observed | 2026-01-17T09:42:00Z | SYNTH&#95;RUN&#95;COMPLETED | Synthetic conditioning run entered the completed state. | accepted | generated:run-warning-alarm-001&#35;event-completed |

## Derived summaries

These values are deterministic counts over the observed fields; they are not diagnoses or recommendations.

| Metric | Count |
| --- | --- |
| parameter&#95;count | 3 |
| measurement&#95;count | 3 |
| event&#95;count | 4 |
| alarm&#95;count | 1 |
| warning&#95;count | 1 |
| unresolved&#95;event&#95;count | 0 |
| known&#95;parameter&#95;value&#95;count | 3 |
| known&#95;measurement&#95;value&#95;count | 3 |
| non&#95;accepted&#95;quality&#95;item&#95;count | 0 |

### Event type counts

| Value | Count |
| --- | --- |
| alarm | 1 |
| state&#95;change | 2 |
| warning | 1 |

### Event severity counts

| Value | Count |
| --- | --- |
| error | 1 |
| info | 2 |
| warning | 1 |

### Event status counts

| Value | Count |
| --- | --- |
| cleared | 1 |
| observed | 3 |

### Quality status counts

| Value | Count |
| --- | --- |
| accepted | 11 |

## Data quality/provenance (observed facts)

- Run quality status: accepted
- Run quality flags: warning&#95;observed, alarm&#95;cleared
- Run quality notes: Synthetic fixture; event presence does not imply a production fault or root-cause finding.
- Source kind: synthetic
- Source ID: synthetic-dataset-v0.1
- Source locator: generated:run-warning-alarm-001
- Extraction method: synthetic&#95;generator

### Metadata

- Dataset ID: synthetic-dataset-v0.1
- Generator: hand-authored deterministic fixture
- Input format: generated
- Created at: 2026-01-17T10:00:00Z
- Labels: synthetic, warning&#95;alarm, training&#95;fixture
- Notes: All values, thresholds, event codes, and messages are invented for public schema testing., Warning and alarm events are included to exercise event status handling before validator implementation.

## Limitations

- This report is a deterministic summary of one schema-valid RunRecord; it does not verify physical process behavior or measurement correctness.
- Messages, raw values, notes, labels, and extension values remain untrusted source data and are not executed or treated as instructions.
- The generator does not infer root cause, process safety conditions, recipes, process windows, or engineering recommendations.

## Disclaimer

For synthetic or explicitly redistributable engineering data only. Human review is required before any engineering or operational decision.
