# Synthetic Semiconductor Engineering Dataset v0.1

## Synthetic-only notice

This dataset is fully synthetic. Every value, identifier, unit, event code, message, document, and relationship is fictional and authored for public software testing, evaluation, and education only.

The synthetic dataset is intended for software testing, evaluation, and education only. It does not represent real semiconductor process windows, equipment behavior, recipe limits, or root-cause relationships.

It is not a real fab benchmark, process-control guidance, recipe guidance, equipment safety guidance, or evidence of real-world failure mechanisms. It must not be used to operate equipment, set a process, diagnose a production event, or infer a corrective action.

## Purpose

The dataset gives later parser, report-generation, retrieval, and agent-evaluation work a small deterministic public input set. This phase adds data only. It does not add parser, RAG, Agent, OpenAI API, or network-access implementation.

RunRecord fixtures use the existing RunRecord v0.1 schema. See [the canonical schema](../../schema/run_record_v0_1.schema.json). Document chunks follow the repository's v0.1 example shape for future local retrieval experiments; they are not RunRecord instances.

## Scenario coverage

| Scenario | RunRecord fixture | Expected schema result |
| --- | --- | --- |
| Normal completed run | [run_completed_001.json](runs/completed/run_completed_001.json) | valid |
| Warning and parameter drift | [run_warning_drift_001.json](runs/warning/run_warning_drift_001.json) | valid |
| Aborted or failed run | [run_aborted_001.json](runs/aborted/run_aborted_001.json) | valid |
| Missing and unknown data | [run_incomplete_unknown_001.json](runs/incomplete/run_incomplete_unknown_001.json) | valid |
| Data-quality issue | [run_data_quality_001.json](runs/quality_cases/run_data_quality_001.json) | valid schema record with quality status invalid |

The scenarios use explicit fictional units where a value is known. Missing, unknown, not-applicable, and invalid states are represented by the schema status fields instead of invented values.

## Document coverage

Each document is original synthetic text and has a matching DocumentChunk-compatible JSON fixture.

- [Equipment data-handling note](documents/engineering_notes/synthetic_equipment_data_handling_note.md) and [chunk](documents/engineering_notes/synthetic_equipment_data_handling_note.json)
- [Synthetic process glossary](documents/glossary/synthetic_process_glossary.md) and [chunk](documents/glossary/synthetic_process_glossary.json)
- [Synthetic alarm and event reference](documents/alarm_reference/synthetic_alarm_event_reference.md) and [chunk](documents/alarm_reference/synthetic_alarm_event_reference.json)
- [Synthetic troubleshooting note](documents/troubleshooting/synthetic_troubleshooting_note.md) and [chunk](documents/troubleshooting/synthetic_troubleshooting_note.json)

The documents intentionally avoid vendor terminology, real alarm standards, real equipment identifiers, process limits, and claims about real failure mechanisms.

## Directory layout

    synthetic_dataset_v0_1/
    ├── README.md
    ├── manifest.json
    ├── runs/
    │   ├── completed/
    │   ├── warning/
    │   ├── aborted/
    │   ├── incomplete/
    │   └── quality_cases/
    └── documents/
        ├── engineering_notes/
        ├── glossary/
        ├── alarm_reference/
        └── troubleshooting/

The [manifest](manifest.json) is the machine-readable index. It records fixture IDs, relative paths, scenario labels, expected validity, validation scope, intended use, prohibited interpretations, and dataset limitations.

## Validation

From the repository root, install the existing development dependencies and run the full test suite:

    python -m pip install -e ".[test]"
    python -m pytest -q

To validate one RunRecord directly:

    semi-ai validate examples/synthetic_dataset_v0_1/runs/completed/run_completed_001.json

All five RunRecord fixtures listed above are expected to pass the existing validator. The document JSON files are parsed and checked by the dataset integrity tests but are intentionally not sent to the RunRecord validator.

## Contribution rules

Contributions must remain synthetic, original, and public-safe. Do not add real fab logs, customer information, HDP private data, vendor manual text, equipment serials, recipe names, proprietary process knowledge, credentials, private paths, or copied alarm tables. New scenarios must state their limitations and must not present synthetic values or text as operating guidance, safety guidance, process limits, or root-cause evidence.
