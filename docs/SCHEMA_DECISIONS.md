# Schema Decisions

This file records the decisions behind [DATA_MODEL_V0_1.md](DATA_MODEL_V0_1.md) and [run_record_v0_1.schema.json](../schema/run_record_v0_1.schema.json). The decisions keep the public model small, inspectable, and independent of any private semiconductor platform.

## Decision table

| ID | Decision | Rationale | Trade-off |
| --- | --- | --- | --- |
| D-001 | Use a JSON-oriented canonical RunRecord. | Nested context, values, events, quality, and provenance remain explicit for parsers and downstream consumers. | CSV and free-form text inputs need a normalization step. |
| D-002 | Keep the model run-centric. | A run is the smallest useful unit for future parsing, reporting, retrieval, and human review. | Cross-run analytics and lot-level entities are deferred. |
| D-003 | Make equipment, module, and process_type explicit top-level concepts. | These are required engineering context without forcing vendor-specific fields into the core. | More detailed equipment identity must wait for a reviewed public taxonomy or private adapter. |
| D-004 | Separate parameters from measurements. | Inputs/setpoints and observed/results values have different meanings and should not be confused in a report. | A producer must classify an item during normalization. |
| D-005 | Keep events separate from values. | Alarms, warnings, and state changes are discrete events, not numeric measurements. | Event summaries require a separate collection. |
| D-006 | Use ISO 8601 UTC timestamps and an explicit time_status. | Ordering and report generation need an unambiguous time basis without inventing unknown times. | Ambiguous or incomplete source timestamps remain visibly incomplete. |
| D-007 | Do not use null for canonical missingness. | missing, unknown, not_applicable, and invalid have different meanings and are easier to validate as statuses. | Consumers need to handle status fields instead of a single null case. |
| D-008 | Require value_type, value_status, and unit_status on parameters and measurements. | A normalized consumer can distinguish an unavailable value from a zero and a missing unit from a known unit. | Records are more verbose than a flat name/value map. |
| D-009 | Keep units free-form but explicit in v0.1. | A universal unit registry would be premature; an explicit short string still prevents silent inference. | Unit equivalence and conversion are deferred. |
| D-010 | Use enums only for stable workflow states and event classes. | Statuses and event categories need predictable downstream behavior. | Process taxonomy and domain names remain less constrained. |
| D-011 | Keep equipment classes, module classes, process types, names, and units free-form. | This avoids early binding to private PVD, CVD, etch, vendor, or tool vocabularies. | Interoperability across public contributions will require later vocabulary work. |
| D-012 | Require provenance at the run and item levels. | Reports, RAG results, and human review need to trace a value or event to a safe source. | Small synthetic fixtures carry repeated metadata. |
| D-013 | Allow only public-safe source kinds in the contract. | synthetic, sanitized_public, and public make redistribution intent explicit. | Private sources require a separate controlled system and adapter. |
| D-014 | Restrict provenance locator to an identifier, not a path or URL. | File and network references create exfiltration, access, and reproducibility risks in public records. | External source linking is deferred to reviewed documentation or a future allowlisted field. |
| D-015 | Reject unknown core fields with additionalProperties false. | Silent acceptance makes parser and agent behavior ambiguous and hides typos or unreviewed data. | Producers must update the schema or use a documented extension. |
| D-016 | Support additive extensions only through namespaced extensions. | Domain-specific fields can evolve without polluting the core contract. | Extensions are not automatically interoperable and remain subject to safety review. |
| D-017 | Add a machine-readable JSON Schema in this milestone. | Executable structure makes fixtures, future parsers, and CI checks more concrete. | JSON Schema does not replace semantic or secret-scanning review. |
| D-018 | Include two small synthetic JSON fixtures. | One complete and one incomplete case make the conditional status rules reviewable without adding parser code. | Synthetic values cannot demonstrate production performance. |
| D-019 | Treat text fields as untrusted data. | Logs, messages, documents, and model output can carry prompt injection or unsafe instructions. | RAG/report/agent layers must add escaping, provenance, and human review. |
| D-020 | Prohibit secrets and proprietary data in all examples and extensions. | The repository is public and has no authorization to receive real fab, HDP, customer, or private platform data. | Public examples remain intentionally generic. |
| D-021 | Keep schema_version at the string 0.1. | The first contract needs a stable identity and explicit breaking-change boundary. | Future breaking changes require migration notes and a new version. |
| D-022 | Do not add parser, report, RAG, or agent business code yet. | This milestone defines the contract before implementation and keeps review scope small. | Runnable behavior is deferred to later phases. |

## Rejected shortcuts

### One flat table for every record

Rejected because inputs, observations, and events have different semantics. A flat table encourages overloaded columns and ambiguous nulls.

### Implicit units or automatic conversion

Rejected because a parameter name cannot safely establish a unit. v0.1 records an explicit unit when known and leaves conversion to a reviewed later component.

### null as the only missing-value state

Rejected because null cannot distinguish missing input, unavailable information, an irrelevant field, and a failed parse.

### A universal process or equipment enum

Rejected because it would quickly become a private taxonomy disguised as a public standard. Generic classes and free-form names are safer for v0.1.

### Arbitrary top-level fields

Rejected because unknown data can be mistaken for validated context. Core fields are closed; additive fields need a namespace and documentation.

### URLs, paths, or opaque external references in provenance

Rejected because public records should not create implicit network access, leak private locations, or make an agent follow unreviewed links.

### Model-generated recommendations inside parameters or measurements

Rejected because a recommendation is a derived claim, not a process input or observation. Future reports need a separate evidence and human-review contract.

## Open questions for later phases

- Should a public unit vocabulary or conversion registry be added after synthetic fixtures and parser tests exist?
- Should a formal DerivedClaim and EvidenceReference output contract be added for report and agent workflows?
- Should event timestamps support intervals and source timezone metadata in a future version?
- Which extension namespaces and public taxonomies are maintainable across contributors?
- How should parsers expose multiple candidate interpretations without silently selecting one?
