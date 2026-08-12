# Roadmap

This roadmap is deliberately incremental. A planned item is not an implemented capability.

## Phase 0 — Public baseline

Status: `DONE` for the initial repository skeleton.

- define project positioning and non-goals;
- define public data and security boundaries;
- add license, security policy, contribution guide, templates, and CI placeholder.

## Phase 0.3 — Data schema design

Status: `DONE` for the first public run-centric contract.

- define a minimal run-centric record with equipment/module context, process type, parameters, measurements, events, metadata, provenance, and quality;
- document units, missing values, warnings, unknown-field handling, security boundaries, and schema versioning;
- add the machine-readable [JSON Schema](../schema/run_record_v0_1.schema.json);
- add complete and incomplete examples without real equipment data.

## Phase 0.4A — Synthetic RunRecord fixtures

Status: `DONE`.

- add completed, incomplete, and warning/alarm RunRecord fixtures;
- add a first document chunk example;
- document synthetic-only redistribution boundaries.

## Phase 0.4B — Schema validation toolkit

Status: `DONE`.

- provide a small `jsonschema`-based API and `semi-ai validate` CLI;
- report deterministic validation errors;
- run focused tests and CI checks.

## Phase 0.5 — Synthetic dataset v0.1

Status: `DONE`.

- add a small fully synthetic RunRecord scenario set;
- add original document and DocumentChunk fixtures for future retrieval evaluation;
- document manifest, limitations, and contribution boundaries.

## Phase 0.6 — Parser implementation

Status: `TODO`.

- implement deterministic parsing;
- report visible validation errors;
- add focused tests for the synthetic dataset.

## Phase 0.7 — Tests and CI expansion

Status: `TODO`.

- expand CI beyond the documentation placeholder;
- run unit tests and basic quality checks;
- verify a clean-environment example path.

## Phase 1 — Report generation

Status: `TODO`.

- generate Markdown reports from structured run data;
- retain source metadata and warnings;
- distinguish observations from interpretation.

## Phase 2 — Retrieval demonstration

Status: `TODO`.

- add a small public/synthetic document set;
- implement local retrieval with source references;
- test insufficient-evidence behavior.

## Long-term maintenance goal

After a runnable public project has accumulated real maintenance and user-feedback evidence, reassess whether an application to Codex for Open Source is appropriate. Do not treat this roadmap as evidence of current eligibility.
