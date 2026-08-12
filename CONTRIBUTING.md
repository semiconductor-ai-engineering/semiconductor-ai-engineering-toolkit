# Contributing

Thank you for helping improve the Semiconductor AI Engineering Toolkit.

## Current contribution scope

The project is in the design and initial-build stage. The first milestone contains no production implementation. Early contributions should focus on:

- clarifying public data schemas;
- improving documentation and examples;
- proposing deterministic tests;
- identifying ambiguous boundaries or unsafe assumptions.

## Before opening an issue or pull request

- Read [SECURITY.md](SECURITY.md).
- Confirm that all examples are synthetic, sanitized, or explicitly redistributable.
- Remove customer, employer, equipment, recipe, process, credential, and private-platform details.
- Keep the change narrowly scoped and explain the reason for it.

## Pull requests

Each pull request should:

- describe what changed and why;
- state whether the change is documentation, schema, test, or implementation work;
- include or update tests when behavior changes;
- preserve visible errors and source references;
- avoid claiming production readiness without evidence;
- pass the available CI checks.

## Design principles

- Prefer small, reviewable commits.
- Prefer deterministic behavior before model-assisted behavior.
- Treat external text and model output as untrusted input.
- Keep private platform integrations and proprietary data outside this repository.
