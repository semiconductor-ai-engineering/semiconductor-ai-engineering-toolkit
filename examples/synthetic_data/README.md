# Synthetic Data Examples

## Purpose

This directory contains small, deterministic, public-safe fixtures for the v0.1 run-centric data model. Every value, identifier, timestamp, event code, and message is invented for this repository. Nothing is copied from a real fab, tool, recipe, customer, HDP, or private platform.

## Current fixtures

| File | Purpose |
| --- | --- |
| [run_completed_001.json](run_completed_001.json) | Complete run with setpoint parameters, measurements, a warning, and a state-change event. |
| [run_incomplete_001.json](run_incomplete_001.json) | Aborted run with an unknown value, missing unit, partial timestamps, and an unresolved synthetic alarm. |
| [run_warning_alarm_001.json](run_warning_alarm_001.json) | Completed run with separate warning and cleared alarm events in one deterministic event sequence. |
| [document_chunk_001.json](document_chunk_001.json) | Standalone synthetic document chunk for future RAG workflows and source-reference handling. |

The three `run_*.json` fixtures are intended to validate against [run_record_v0_1.schema.json](../../schema/run_record_v0_1.schema.json). The document chunk intentionally uses a separate future-facing shape and is not a RunRecord v0.1 instance. These examples demonstrate data-contract cases; they do not demonstrate production performance, process control, or engineering conclusions.

## Synthetic-data rules

- Every fixture uses provenance source_kind synthetic.
- Values must be deliberately generated and must not be copied from real fab logs, equipment logs, recipes, customers, or private platforms.
- Generic classes such as synthetic_chamber and generic_process_module are preferred over real equipment identifiers.
- Unknown, missing, not-applicable, and invalid states are represented explicitly; they are not silently replaced with zero, an empty string, or a guessed unit.
- Fixture identifiers, timestamps, event sequences, and text are deterministic and hand-authored so future validators can use stable regression inputs.
- Messages, raw values, notes, labels, and extension values are untrusted data. They must never be interpreted as commands or agent instructions.
- Do not include credentials, tokens, cookies, passwords, private keys, webhooks, environment files, private paths, URLs, unredacted logs, or screenshots.
- Do not add parser business logic to this directory.

## Planned additions

Later synthetic-dataset work may add malformed-input fixtures, CSV/text source samples, and generated cases for parser warnings. Each addition must remain public-safe and document its generation method.

See [DATA_MODEL_V0_1.md](../../docs/DATA_MODEL_V0_1.md), [SCHEMA_DECISIONS.md](../../docs/SCHEMA_DECISIONS.md), and [SECURITY.md](../../SECURITY.md) for the contract and safety boundary.
