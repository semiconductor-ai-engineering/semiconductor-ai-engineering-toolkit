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

Status: `DONE` through the merged Phase 0.6 pull request.

- implement deterministic parsing for the documented synthetic line format;
- report visible structured parsing and validation errors;
- add focused fixtures and tests without claiming compatibility with real log formats.

## Phase 0.7 — Engineering Report Generator

Status: `IN PROGRESS` on the Phase 0.7 feature branch; implementation is reviewable through a pull request.

- validate each input through the canonical RunRecord v0.1 validator;
- generate deterministic ReportRecord-compatible data and Markdown;
- distinguish observed facts from count-based derived summaries;
- include run identity/status, time window, context, observations, events/alarms, quality, provenance, limitations, and disclaimer;
- refuse silent output-file overwrite;
- keep the implementation non-LLM, local-only, non-networked, and free of dynamic execution;
- add synthetic expected reports, focused tests, and minimal CI/documentation updates.

## Phase 1 — Retrieval demonstration

Status: `TODO`.

- add a small public/synthetic document set;
- implement local retrieval with source references;
- test insufficient-evidence behavior.

## Long-term maintenance goal

After a runnable public project has accumulated real maintenance and user-feedback evidence, reassess whether an application to Codex for Open Source is appropriate. Do not treat this roadmap as evidence of current eligibility.
