# Semiconductor AI Engineering Toolkit

An open-source foundation for exploring AI-assisted workflows in semiconductor engineering.

## Status

This project is in the design and initial-build stage (`pre-alpha`). The first milestone establishes the public project boundary and repository structure. It does not claim production readiness, customer validation, or connection to a live fab or equipment system.

## V0.1 scope

- `log parser`: convert synthetic or explicitly sanitized run logs into structured data;
- `engineering report generator`: turn structured run data into traceable Markdown reports;
- `knowledge retrieval demo`: demonstrate local retrieval over public or synthetic engineering documents with source references.

The first milestone contains documentation and governance files only. Implementation will be added in later, reviewable steps.

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
- [Security policy](SECURITY.md)
- [Contributing guide](CONTRIBUTING.md)
- [Synthetic examples policy](examples/README.md)

## Development philosophy

The project will grow through small, inspectable commits:

1. project baseline;
2. data schema design;
3. synthetic dataset;
4. parser implementation;
5. tests and expanded CI.

The project will prefer deterministic inputs, visible errors, source-linked outputs, and human review over broad automation claims.
