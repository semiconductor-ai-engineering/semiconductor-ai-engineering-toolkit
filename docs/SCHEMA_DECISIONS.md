# Schema Decisions

This file records the decisions behind `DATA_MODEL_V0_1.md`. The decisions are intentionally conservative so the public model remains reusable and does not become a copy of one private system.

## Decision table

| ID | Decision | Rationale | Trade-off |
| --- | --- | --- | --- |
| D-001 | Use JSON-oriented canonical records. | JSON can represent nested provenance, quality, events, and document chunks without flattening everything into columns. | CSV users need a normalization step before downstream use. |
| D-002 | Keep CSV/text as future inputs, not canonical outputs. | Parsers can accept many formats while reports and RAG consume one stable shape. | The parser will need explicit mapping and error handling later. |
| D-003 | Every record has a stable string identity. | IDs let observations, events, chunks, and evidence references survive reordering and regeneration. | Producers must generate and preserve IDs. |
| D-004 | Use ISO 8601 UTC timestamps when trustworthy. | Cross-source ordering and report generation need an unambiguous time basis. | Unknown timezone input must remain visibly uncertain. |
| D-005 | Separate `value`, `raw_value`, `unit`, and status fields. | Normalization should not destroy the original safe token or hide missing units. | Records are more verbose than a simple key/value map. |
| D-006 | Distinguish `missing`, `unknown`, `not_applicable`, and `invalid`. | A missing field, an unavailable fact, an irrelevant field, and a failed parse have different meanings. | Consumers need to handle more than one null-like state. |
| D-007 | Require provenance on observations, events, documents, and chunks. | Report and RAG layers need evidence paths and reproducibility. | Synthetic fixtures must carry metadata even when generation is local. |
| D-008 | Make `source_kind` explicit and public-safe. | The public repository must distinguish synthetic data from sanitized or public material. | A future private deployment may need an adapter outside this public schema. |
| D-009 | Keep events separate from observations. | An alarm or state change is not necessarily a numeric measurement. | Report generators need two collections to summarize. |
| D-010 | Use a small, shared quality object. | Parser, report, and retrieval layers need a common way to expose incomplete or uncertain data. | Quality status is not a complete statistical confidence model. |
| D-011 | Add an `extensions` namespace. | Domain-specific fields can evolve without forcing vendor fields into the core model. | Extensions are not automatically interoperable and require their own documentation. |
| D-012 | Add document and chunk records in v0.1. | RAG workflows need stable document identity, chunk identity, source location, and retrieval metadata. | Embeddings and vector-store details remain implementation-specific. |
| D-013 | Evidence references distinguish direct and derived support. | Generated explanations must not be presented as raw observations. | Future report generation must preserve evidence links. |
| D-014 | Do not make LLM output a canonical observation. | Model output is an interpretation or suggestion, not a measurement. | Human review and a future derived-claim type are required for AI-assisted reports. |
| D-015 | Use additive evolution within the `0.1` design line. | Small additions are easier to review than hidden breaking changes. | A future breaking change will need a new schema version and migration note. |
| D-016 | Delay machine-readable JSON Schema and parser implementation. | This phase is for domain and boundary decisions; premature code would freeze unclear assumptions. | The current docs are not executable validation. |
| D-017 | Synthetic-only examples in the public repository. | The first dataset must be safe to redistribute and independent of private platform access. | Synthetic data cannot prove production performance. |
| D-018 | Prefer generic classes over real identifiers. | Classes such as `synthetic_chamber` are reusable without exposing serial numbers, site names, or proprietary tool models. | Some real-world specificity is deferred to private adapters or later public contributions. |

## Rejected shortcuts

### One flat table for every record

Rejected because events, measurements, documents, and evidence have different semantics. A flat table would encourage overloaded columns and ambiguous nulls.

### Implicit units

Rejected because a parameter name cannot safely establish a unit. Unit status must be explicit and missing units must remain visible.

### `null` as the only missing-value state

Rejected because `null` cannot distinguish missing input, unknown information, not-applicable fields, and invalid parsing.

### Embedding vectors as canonical fields

Rejected for v0.1 because embeddings depend on a model, version, dimension, and storage backend. They can be added under an extension with provenance later.

### Model-generated recommendations inside `Observation`

Rejected because recommendations are derived claims and must not be confused with measurements. A future report/evidence layer should carry them separately with human-review status.

## Open questions for a later phase

- Should the canonical version use full semantic versioning after the first executable schema?
- Should a formal `DerivedClaim` record be added for report and agent outputs?
- Which public unit vocabulary is small enough for v0.1 without becoming a full metrology standard?
- Should document chunks use character offsets, page/section locators, or both?
- How should a parser expose multiple candidate interpretations without silently choosing one?

These questions are intentionally not resolved by Phase 0.3.
