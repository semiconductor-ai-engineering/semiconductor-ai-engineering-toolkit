# Synthetic Data Examples

## Purpose

This directory is reserved for small, reproducible, public-safe fixtures for the v0.1 data model. Phase 0.3 adds this README only; it does not add parser code or synthetic data files yet.

## Planned fixture set

Future commits may add fixtures such as:

```text
examples/synthetic_data/
├── README.md
├── run_completed_001.json
├── run_missing_field_001.json
├── run_invalid_value_001.json
├── events_001.json
└── document_chunks_001.jsonl
```

The names above describe planned test cases, not files that already exist.

## Synthetic-data rules

- Every fixture must be labeled with `source_kind: synthetic`.
- Values must be deliberately generated and must not be copied from a real fab, tool, recipe, customer, or private platform.
- Generic labels such as `synthetic_chamber` and `synthetic_recipe_a` are preferred over real equipment identifiers.
- Timestamps, parameter values, event codes, and document text may be arbitrary, but they must be internally consistent enough to test parsing and reporting.
- Missing, unknown, not-applicable, and invalid cases should be represented explicitly rather than silently replaced with zero or an empty string.
- Document chunks must contain synthetic or explicitly redistributable text and a stable source locator.
- Do not include credentials, tokens, cookies, passwords, private paths, `.env` files, unredacted logs, or screenshots.

## Planned validation

Each future fixture should pass:

1. structural checks against the published data model;
2. semantic checks for IDs, timestamps, units, and status combinations;
3. provenance checks for the synthetic source marker;
4. public-safety checks for prohibited identifiers and secrets;
5. downstream checks showing how the fixture can feed a parser, report generator, or retrieval demo.

See [DATA_MODEL_V0_1.md](../../docs/DATA_MODEL_V0_1.md) and [SCHEMA_DECISIONS.md](../../docs/SCHEMA_DECISIONS.md) for the design contract.
