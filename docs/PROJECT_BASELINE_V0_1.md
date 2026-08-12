# Semiconductor AI Engineering Toolkit v0.1 Project Baseline

## 1. Positioning

Semiconductor AI Engineering Toolkit is an independent open-source project for exploring AI-assisted workflows in semiconductor engineering. It focuses on small, reproducible building blocks rather than claims of autonomous equipment control or production optimization.

Current maturity: `pre-alpha`, design and initial-build stage.

The first public milestone establishes repository governance and project boundaries. It does not include production source code, live equipment connections, customer validation, or real fab data.

## 2. Target users

- semiconductor engineers who want to structure and inspect run data;
- developers building engineering data tools in Python or similar environments;
- researchers exploring retrieval, reporting, and human-in-the-loop AI workflows;
- students learning engineering data concepts with synthetic examples.

## 3. Open-source boundary

### Public scope

- generic schemas and interfaces;
- synthetic or explicitly redistributable examples;
- deterministic parsing and reporting utilities;
- local retrieval demonstrations with source references;
- documentation, tests, evaluation notes, and CI configuration;
- code whose dependencies and licenses permit redistribution.

### Explicitly excluded

- customer or employer information;
- real fab logs and unredacted equipment logs;
- recipes, process windows, golden runs, trace data, metrology data, alarm histories, and internal validation results;
- private platform code, adapters, deployment configuration, or research conclusions;
- credentials, tokens, cookies, passwords, private keys, webhooks, and real `.env` files.

This repository is a public general-purpose foundation. It is not a public copy of any private semiconductor R&D platform. Future private adapters, if ever needed, must remain outside this repository and use reviewed interfaces with sanitized contract tests.

## 4. V0.1 scope

### `log parser`

Parse synthetic or sanitized CSV, JSON, or structured text into a testable run schema. Initial fields may include run identifier, event order, timestamp, parameter name, value, unit, alarm/event markers, and parse warnings.

The parser should make errors visible and should not imply that successful parsing proves an engineering conclusion.

### `engineering report generator`

Generate a readable Markdown report from structured run data. The initial report may include a run summary, field coverage, parameter ranges, event summaries, warnings, and input/source metadata.

Rules and templates come first. If a model-assisted layer is added later, the structured input, source references, uncertainty, and human review point must remain visible.

### `knowledge retrieval demo`

Demonstrate local retrieval over a small set of public or synthetic engineering documents. Results should include source references and should clearly state when the available evidence is insufficient.

This is a local demonstration, not a production knowledge platform or an unrestricted autonomous agent.

## 5. Non-goals

- controlling equipment or connecting to a production line;
- automatic recipe generation, tuning, optimization, or closed-loop control;
- replacing engineering judgment;
- accepting or publishing proprietary semiconductor data;
- presenting demos as validated industrial products;
- building a full SaaS platform, vendor adapter matrix, or autonomous agent in the first milestone.

## 6. Data and security principles

- Use synthetic, sanitized, or clearly redistributable data by default.
- Keep secrets outside the repository; retain only safe templates such as `.env.example`.
- Treat documents, issues, logs, links, and model output as untrusted input.
- Require human review for workflow, dependency, data-handling, and deployment changes.
- Preserve schema versions, source references, warnings, and reproducibility information.

## 7. Planned repository structure

```text
semiconductor-ai-engineering-toolkit/
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── docs/
│   ├── PROJECT_BASELINE_V0_1.md
│   ├── ROADMAP.md
│   └── ARCHITECTURE.md
├── examples/
│   └── README.md
└── .github/
    ├── ISSUE_TEMPLATE/
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/
```

The structure is intentionally small. Source packages, tests, and synthetic datasets will be added in later commits after the public boundary is reviewed.
