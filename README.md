# Semiconductor AI Engineering Toolkit

[![CI](https://github.com/semiconductor-ai-engineering/semiconductor-ai-engineering-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/semiconductor-ai-engineering/semiconductor-ai-engineering-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python >=3.10](https://img.shields.io/badge/python-%3E%3D3.10-3776AB.svg)](https://www.python.org/)

An open-source foundation for exploring AI-assisted workflows in semiconductor engineering.

## Status

This project is in the design and initial-build stage (`pre-alpha`). The public baseline, run-centric data schema, validation toolkit, and synthetic dataset are documented. Phase 0.5.5 prepares an alpha release but does not create a tag or GitHub Release. The project does not claim production readiness, customer validation, or connection to a live fab or equipment system.

## Quick Start

From PowerShell on Windows:

```powershell
git clone https://github.com/semiconductor-ai-engineering/semiconductor-ai-engineering-toolkit.git
cd semiconductor-ai-engineering-toolkit
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
semi-ai validate examples/synthetic_dataset_v0_1/runs/completed/run_completed_001.json
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead. Expected validation output:

```text
Valid RunRecord v0.1
```

For local tests, install the test extra and run `python -m pytest -q`.

## V0.1 scope

- `log parser`: convert synthetic or explicitly sanitized run logs into structured data;
- `run-centric data schema`: normalize run identity, equipment/module context, parameters, measurements, events, metadata, provenance, and quality;
- `engineering report generator`: turn structured run data into traceable Markdown reports;
- `knowledge retrieval demo`: demonstrate local retrieval over public or synthetic engineering documents with source references.

The current milestone contains documentation, governance files, a machine-readable JSON Schema, small synthetic fixtures, a local schema validation toolkit, and a fully synthetic dataset v0.1. Parser and workflow implementation will be added in later, reviewable steps.

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
- [Validation toolkit](docs/VALIDATION_TOOLKIT_V0_1.md)
- [Changelog](CHANGELOG.md)
- [Public release readiness](docs/RELEASE_READINESS_V0_1.md)
- [Security policy](SECURITY.md)
- [Contributing guide](CONTRIBUTING.md)
- [Synthetic examples policy](examples/README.md)
- [Synthetic run fixtures](examples/synthetic_data/)
- [Synthetic dataset v0.1](examples/synthetic_dataset_v0_1/)

## Development philosophy

The project will grow through small, inspectable commits:

1. project baseline;
2. run-centric data schema;
3. synthetic RunRecord fixtures;
4. schema validation toolkit;
5. synthetic dataset v0.1;
6. parser implementation;
7. tests and expanded CI.

The project will prefer deterministic inputs, visible errors, source-linked outputs, and human review over broad automation claims.
