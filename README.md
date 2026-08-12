# Semiconductor AI Engineering Toolkit

[![CI](https://github.com/semiconductor-ai-engineering/semiconductor-ai-engineering-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/semiconductor-ai-engineering/semiconductor-ai-engineering-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python >=3.10](https://img.shields.io/badge/python-%3E%3D3.10-3776AB.svg)](https://www.python.org/)

An open-source foundation for exploring AI-assisted workflows in semiconductor engineering.

## Status

This project is in the design and initial-build stage (`pre-alpha`). The public baseline, run-centric data schema, validation toolkit, synthetic dataset, and `v0.1.0-alpha.1` release are available. Phase 0.6 adds a deliberately small synthetic line-log parser prototype, Phase 0.7 adds a deterministic engineering report generator for validated RunRecord data, and Phase 0.8 adds a local lexical retrieval demo over synthetic DocumentChunk fixtures. The project does not claim production readiness, customer validation, or connection to a live fab or equipment system.

## Quick Start

From PowerShell on Windows:

```powershell
git clone https://github.com/semiconductor-ai-engineering/semiconductor-ai-engineering-toolkit.git
cd semiconductor-ai-engineering-toolkit
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
semi-ai validate examples/synthetic_dataset_v0_1/runs/completed/run_completed_001.json
semi-ai parse examples/synthetic_logs/run_completed_001.log
semi-ai report examples/synthetic_data/run_completed_001.json --output engineering_report.md
semi-ai retrieve "synthetic pressure warning" --top-k 3
semi-ai evaluate-retrieval
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
- `knowledge retrieval demo`: demonstrate deterministic local lexical retrieval over synthetic engineering documents with source references; it returns ranked evidence, not generated answers.

The current milestone contains documentation, governance files, a machine-readable JSON Schema, small synthetic fixtures, a local schema validation toolkit, a fully synthetic dataset v0.1, a deterministic parser for the deliberately simple synthetic line-log format documented in [Synthetic Log Parser v0.1](docs/SYNTHETIC_LOG_PARSER_V0_1.md), a deterministic Markdown report generator documented in [Engineering Report Generator v0.1](docs/ENGINEERING_REPORT_GENERATOR_V0_1.md), and a deterministic local retrieval demo documented in [Knowledge Retrieval Demo v0.1](docs/KNOWLEDGE_RETRIEVAL_DEMO_V0_1.md). The parser is not a general vendor-log adapter, the report generator does not diagnose causes or provide process guidance, and the retriever does not synthesize answers.

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
- [Synthetic log parser v0.1](docs/SYNTHETIC_LOG_PARSER_V0_1.md)
- [Engineering report generator v0.1](docs/ENGINEERING_REPORT_GENERATOR_V0_1.md)
- [Knowledge retrieval demo v0.1](docs/KNOWLEDGE_RETRIEVAL_DEMO_V0_1.md)
- [Retrieval evaluation harness v0.1](docs/RETRIEVAL_EVALUATION_HARNESS_V0_1.md)
- [Changelog](CHANGELOG.md)
- [Public release readiness](docs/RELEASE_READINESS_V0_1.md)
- [Security policy](SECURITY.md)
- [Contributing guide](CONTRIBUTING.md)
- [Synthetic examples policy](examples/README.md)
- [Synthetic run fixtures](examples/synthetic_data/)
- [Synthetic log fixtures](examples/synthetic_logs/)
- [Synthetic dataset v0.1](examples/synthetic_dataset_v0_1/)
- [Synthetic retrieval regression fixture](examples/synthetic_retrieval/)
- [Synthetic retrieval evaluation cases](examples/synthetic_retrieval/evaluation/)

## Development philosophy

The project will grow through small, inspectable commits:

1. project baseline;
2. run-centric data schema;
3. synthetic RunRecord fixtures;
4. schema validation toolkit;
5. synthetic dataset v0.1;
6. synthetic log parser prototype;
7. deterministic engineering report generator;
8. deterministic local knowledge retrieval;
9. retrieval evaluation and expanded CI.

The project will prefer deterministic inputs, visible errors, source-linked outputs, and human review over broad automation claims.
