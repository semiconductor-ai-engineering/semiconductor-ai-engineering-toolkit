# Semiconductor AI Engineering Toolkit

An open-source foundation for exploring AI-assisted workflows in semiconductor engineering.

## Status

This project is in the design and initial-build stage (`pre-alpha`). The public baseline and first run-centric data schema are now documented. The project does not claim production readiness, customer validation, or connection to a live fab or equipment system.

## V0.1 scope

- `log parser`: convert synthetic or explicitly sanitized run logs into structured data;
- `run-centric data schema`: normalize run identity, equipment/module context, parameters, measurements, events, metadata, provenance, and quality;
- `engineering report generator`: turn structured run data into traceable Markdown reports;
- `knowledge retrieval demo`: demonstrate local retrieval over public or synthetic engineering documents with source references.

The current milestone contains documentation, governance files, a machine-readable JSON Schema, and small synthetic fixtures only. Parser and workflow implementation will be added in later, reviewable steps.

## Explicit boundary

This repository must not contain:

- customer information or confidential company information;
- real fab logs, unredacted equipment logs, or proprietary process information;
- recipes, process windows, golden runs, trace data, metrology data, or internal validation results;
- private platform code, adapters, credentials, tokens, cookies, passwords, webhooks, or real `.env` files;
- claims that a demo is a production control or optimization system.

This is a public, general-purpose foundation. It is not a public mirror of any private semiconductor R&D platform.

## Repository map

- [Project baseline](docs/PROJECT_BASELINE_V0_1.md)
- [Roadmap](docs/ROADMAP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data model v0.1](docs/DATA_MODEL_V0_1.md)
- [Machine-readable run schema](schema/run_record_v0_1.schema.json)
- [Security policy](SECURITY.md)
- [Contributing guide](CONTRIBUTING.md)
- [Synthetic examples policy](examples/README.md)
- [Synthetic run fixtures](examples/synthetic_data/)

## Development philosophy

The project will grow through small, inspectable commits:

1. project baseline;
2. run-centric data schema;
3. synthetic dataset;
4. parser implementation;
5. tests and expanded CI.

The project will prefer deterministic inputs, visible errors, source-linked outputs, and human review over broad automation claims.
