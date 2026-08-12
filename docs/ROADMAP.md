# Roadmap

This roadmap is deliberately incremental. A planned item is not an implemented capability.

## Phase 0 — Public baseline

Status: `DONE` for the initial repository skeleton.

- define project positioning and non-goals;
- define public data and security boundaries;
- add license, security policy, contribution guide, templates, and CI placeholder.

## Phase 0.2 — Data schema design

Status: `TODO`.

- define a minimal run/event schema;
- document units, missing values, warnings, and schema versioning;
- add schema examples without real equipment data.

## Phase 0.3 — Synthetic dataset

Status: `TODO`.

- add small synthetic CSV/JSON logs;
- include normal, incomplete, malformed, and alarm/event cases;
- document how each example is generated and redistributed.

## Phase 0.4 — Parser implementation

Status: `TODO`.

- implement deterministic parsing;
- report visible validation errors;
- add focused tests for the synthetic dataset.

## Phase 0.5 — Tests and CI expansion

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
