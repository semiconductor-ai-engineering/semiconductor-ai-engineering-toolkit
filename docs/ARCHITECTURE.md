# Architecture

## Current status

This is a planned architecture for an early-stage project. The repository currently contains documentation and governance files only; the modules below are not implemented yet.

## Intended flow

```text
synthetic or sanitized log
        |
        v
    log parser
        |
        v
 structured run data
        |
        +----------------------+
        |                      |
        v                      v
 report generator       evaluation / tests
        |
        v
  Markdown report

public or synthetic documents
        |
        v
 local retrieval demo
        |
        v
 answer with source references
```

## Module boundaries

### Parser

Responsible for input normalization, schema validation, warnings, and stable structured output. It should not control equipment or infer a root cause from parsing alone.

### Report generator

Responsible for readable, traceable Markdown output. It should distinguish observed fields, validation warnings, and optional interpretation.

### Retrieval demo

Responsible for local indexing/retrieval experiments and source-linked results. It should report insufficient evidence instead of inventing an answer.

## Data boundary

The public repository uses synthetic, sanitized, or explicitly redistributable data. Private adapters, private platforms, customer data, real fab logs, recipes, and production validation remain outside the repository.

## Future extension points

- alternate log readers behind a stable parser interface;
- report templates and structured output formats;
- optional model-assisted components with human review;
- evaluation fixtures that do not contain proprietary data.

These extension points are proposals, not current implementation commitments.
