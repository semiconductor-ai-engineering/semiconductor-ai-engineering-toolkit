# Semiconductor AI Engineering Toolkit Data Model v0.1

## Status

This document defines a design-only public data model. It does not add parser code, a validator implementation, a JSON Schema file, or a real dataset.

The canonical interchange shape is JSON-oriented. CSV and text logs may be future parser inputs, but downstream modules should consume normalized records with explicit provenance and quality metadata.

## Design goals

- Use small, reusable structures instead of vendor-specific fields.
- Preserve the difference between an observation, an event, a derived statement, and a document citation.
- Keep raw values, normalized values, units, timestamps, source references, and quality state visible.
- Support future log parsing, Markdown report generation, and retrieval-augmented generation (RAG) without copying private data into the public repository.
- Make synthetic examples easy to validate and safe to redistribute.

## Non-goals

- controlling equipment or writing recipes;
- modeling every semiconductor process or vendor format;
- inferring a root cause from a single observation;
- treating model output as measurement data;
- accepting customer data, real fab logs, or private platform exports.

## Model overview

```text
RunRecord
├── SourceReference
├── RunContext
├── Observation[]
├── Event[]
├── QualitySummary
└── extensions

DocumentRecord
└── DocumentChunk[]
    └── SourceReference + RetrievalMetadata

ReportRecord (future output contract)
└── EvidenceReference[] → RunRecord / Observation / Event / DocumentChunk
```

## Shared conventions

### Schema version

Every canonical record carries `schema_version`. The v0.1 value is the string `"0.1"`. A schema change that changes meaning or removes a field requires an explicit decision and a new version.

### Record identity

Every record has a stable `record_id` within its record type. A human-readable `run_id`, `document_id`, or `chunk_id` may also be present, but consumers must not use array position as identity.

Recommended ID properties:

- string, not an integer;
- stable across parsing and report regeneration;
- safe to expose publicly;
- not derived from a customer name, equipment serial number, or private path.

### Time

Use ISO 8601 timestamps normalized to UTC when a trustworthy timestamp exists, for example `2026-01-15T10:00:00Z`. A future parser may retain an input timezone in provenance, but it must not silently treat an unknown timezone as UTC.

When time is unavailable or ambiguous, use `time_status` and a quality flag rather than inventing a timestamp.

### Values and units

An observation separates:

- `value`: normalized JSON value used by downstream consumers;
- `raw_value`: optional original token or text, only when safe to redistribute;
- `value_type`: number, string, boolean, or object;
- `unit`: explicit unit when applicable;
- `unit_status`: known, missing, not_applicable, or unknown;
- `value_status`: known, missing, unknown, not_applicable, or invalid.

Missing values must not be converted to zero. A unit must not be inferred from a parameter name alone.

### Provenance

`SourceReference` is required for observations, events, documents, chunks, and future reports. It records where a value or text came from without requiring a private filesystem path.

```json
{
  "source_kind": "synthetic",
  "source_id": "synthetic-dataset-v0.1",
  "locator": "generated:run-completed-001",
  "content_hash": "sha256:optional-public-fixture-hash",
  "extraction_method": "synthetic_generator"
}
```

Allowed public `source_kind` values in v0.1:

- `synthetic`: generated for this project and not copied from a real site;
- `sanitized_public`: derived from material that is explicitly safe to redistribute;
- `public`: a public source whose redistribution and excerpting rights are documented.

The value `private` is intentionally not a public example value. Private sources belong in a separate controlled system.

### Quality state

Quality metadata describes data handling, not business importance and not the probability that an interpretation is true.

```json
{
  "quality_status": "accepted",
  "flags": [],
  "notes": []
}
```

Recommended `quality_status` values:

- `accepted`: passed the checks currently applied;
- `uncertain`: usable but contains an unresolved ambiguity;
- `incomplete`: required context is missing;
- `invalid`: failed a structural or semantic check;
- `not_assessed`: quality has not yet been evaluated.

## Core records

### RunRecord

`RunRecord` is the run-level aggregate consumed by report generation and future evaluation.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Canonical schema version, `"0.1"` for this document. |
| `record_type` | string | yes | Literal `"run"`. |
| `record_id` | string | yes | Stable canonical record identity. |
| `run_id` | string | yes | Human-readable run identity within the source context. |
| `status` | enum | yes | `planned`, `running`, `completed`, `aborted`, or `unknown`. |
| `time_window` | object | yes | Start/end timestamps and time status. |
| `source` | SourceReference | yes | Origin of the record. |
| `context` | RunContext | no | Public, generic context labels. |
| `observations` | Observation[] | no | Normalized parameter observations. |
| `events` | Event[] | no | State changes, warnings, alarms, or annotations. |
| `quality` | QualitySummary | yes | Aggregate quality state and flags. |
| `extensions` | object | no | Namespaced additive fields. |

`RunContext` should prefer classes and public labels over real identifiers:

```json
{
  "equipment_class": "synthetic_chamber",
  "process_family": "generic_pressure_temperature_demo",
  "recipe_class": "synthetic_recipe_a",
  "labels": ["synthetic", "training_fixture"]
}
```

### Observation

`Observation` represents a value observed or parsed from a run. It is not automatically a recommendation or a root-cause statement.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `observation_id` | string | yes | Stable observation identity. |
| `parameter` | string | yes | Generic parameter key, for example `pressure`. |
| `value` | JSON value | conditional | Required when `value_status` is `known`. |
| `raw_value` | string | no | Safe original token before normalization. |
| `value_type` | enum | yes | `number`, `string`, `boolean`, or `object`. |
| `unit` | string | conditional | Required when a unit is known and applicable. |
| `unit_status` | enum | yes | `known`, `missing`, `not_applicable`, or `unknown`. |
| `value_status` | enum | yes | `known`, `missing`, `unknown`, `not_applicable`, or `invalid`. |
| `observed_at` | timestamp | no | Point timestamp when available. |
| `source` | SourceReference | yes | Source of the observation. |
| `quality` | QualitySummary | yes | Observation-level quality. |
| `tags` | string[] | no | Public, non-sensitive labels. |
| `extensions` | object | no | Namespaced additive fields. |

### Event

`Event` represents a discrete event or state marker. It is separate from `Observation` so that an event does not need to be forced into a numeric parameter shape.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `event_id` | string | yes | Stable event identity. |
| `event_type` | string | yes | Generic event class, for example `alarm`, `state_change`, or `operator_note`. |
| `severity` | enum | yes | `info`, `warning`, `error`, `critical`, or `unknown`. |
| `event_status` | enum | yes | `observed`, `cleared`, `unresolved`, or `unknown`. |
| `message_code` | string | no | Synthetic or public code; no private alarm code is required. |
| `message` | string | no | Sanitized human-readable description. |
| `observed_at` | timestamp | conditional | Point timestamp when known. |
| `time_window` | object | conditional | Start/end when the event spans an interval. |
| `source` | SourceReference | yes | Source of the event. |
| `quality` | QualitySummary | yes | Event-level quality. |
| `extensions` | object | no | Namespaced additive fields. |

### SourceReference

`SourceReference` is a reusable object, not a free-form string hidden in each module.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `source_kind` | enum | yes | `synthetic`, `sanitized_public`, or `public`. |
| `source_id` | string | yes | Stable public source identity. |
| `locator` | string | no | Public fixture name, document section, or safe record locator. |
| `content_hash` | string | no | Optional hash for reproducibility. |
| `extraction_method` | string | no | Parser, generator, manual entry, or other method. |
| `captured_at` | timestamp | no | When the source was captured or generated. |
| `license` | string | no | License or redistribution note when applicable. |

### QualitySummary

`QualitySummary` is intentionally small in v0.1.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `quality_status` | enum | yes | Overall data handling status. |
| `flags` | string[] | no | Machine-readable flags such as `missing_unit`. |
| `notes` | string[] | no | Short, safe explanations. |

Do not use `confidence` as a substitute for quality. If a future model produces a confidence-like score, it must be labeled with its source, scale, and interpretation.

## RAG-oriented records

### DocumentRecord

`DocumentRecord` identifies a public or synthetic source document.

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Canonical schema version. |
| `record_type` | string | yes | Literal `"document"`. |
| `document_id` | string | yes | Stable public document identity. |
| `title` | string | yes | Safe document title. |
| `document_type` | string | yes | Manual excerpt, procedure, glossary, or synthetic note. |
| `language` | string | no | Language tag such as `en`. |
| `version` | string | no | Source document version. |
| `source` | SourceReference | yes | Source and redistribution context. |
| `chunks` | DocumentChunk[] | no | Chunks prepared for retrieval. |
| `quality` | QualitySummary | yes | Document-level quality. |

### DocumentChunk

`DocumentChunk` is the unit returned by a retrieval layer.

```json
{
  "schema_version": "0.1",
  "record_type": "document_chunk",
  "chunk_id": "chunk-synth-0001",
  "document_id": "doc-synth-pressure-basics",
  "text": "Synthetic note: a pressure observation should carry an explicit unit.",
  "source": {
    "source_kind": "synthetic",
    "source_id": "synthetic-document-set-v0.1",
    "locator": "doc-synth-pressure-basics#unit-handling"
  },
  "retrieval_metadata": {
    "section": "unit-handling",
    "tags": ["units", "data-quality"]
  },
  "quality": {
    "quality_status": "accepted",
    "flags": [],
    "notes": []
  }
}
```

`text` must be safe to redistribute. Embeddings, vector database IDs, and model-specific fields are not canonical v0.1 fields; they may be placed under `extensions` in a future implementation.

### EvidenceReference

Future reports and RAG answers should point to evidence explicitly:

```json
{
  "evidence_id": "evidence-0001",
  "evidence_type": "observation",
  "record_id": "runrec-synth-0001",
  "locator": "observations/obs-synth-0001",
  "support_status": "direct"
}
```

Recommended `support_status` values are `direct`, `derived`, `contextual`, and `insufficient`. A generated explanation must not be labeled `direct` unless it points to an observed field or source text.

## Synthetic RunRecord example

The following is a deliberately artificial example. It is not copied from a real tool, fab, customer, recipe, or platform.

```json
{
  "schema_version": "0.1",
  "record_type": "run",
  "record_id": "runrec-synth-0001",
  "run_id": "synthetic-run-0001",
  "status": "completed",
  "time_window": {
    "start": "2026-01-15T10:00:00Z",
    "end": "2026-01-15T10:12:00Z",
    "time_status": "known"
  },
  "source": {
    "source_kind": "synthetic",
    "source_id": "synthetic-dataset-v0.1",
    "locator": "generated:run-completed-001",
    "extraction_method": "synthetic_generator"
  },
  "context": {
    "equipment_class": "synthetic_chamber",
    "process_family": "generic_pressure_temperature_demo",
    "recipe_class": "synthetic_recipe_a",
    "labels": ["synthetic", "training_fixture"]
  },
  "observations": [
    {
      "observation_id": "obs-synth-0001",
      "parameter": "pressure",
      "value": 12.4,
      "value_type": "number",
      "unit": "Pa",
      "unit_status": "known",
      "value_status": "known",
      "observed_at": "2026-01-15T10:04:00Z",
      "source": {
        "source_kind": "synthetic",
        "source_id": "synthetic-dataset-v0.1",
        "locator": "generated:run-completed-001#pressure-0001"
      },
      "quality": {
        "quality_status": "accepted",
        "flags": [],
        "notes": []
      }
    },
    {
      "observation_id": "obs-synth-0002",
      "parameter": "temperature",
      "value": 68.0,
      "value_type": "number",
      "unit": "C",
      "unit_status": "known",
      "value_status": "known",
      "observed_at": "2026-01-15T10:05:00Z",
      "source": {
        "source_kind": "synthetic",
        "source_id": "synthetic-dataset-v0.1",
        "locator": "generated:run-completed-001#temperature-0001"
      },
      "quality": {
        "quality_status": "accepted",
        "flags": [],
        "notes": []
      }
    }
  ],
  "events": [
    {
      "event_id": "event-synth-0001",
      "event_type": "state_change",
      "severity": "info",
      "event_status": "observed",
      "message_code": "SYNTH_RUN_STARTED",
      "message": "Synthetic run entered the active state.",
      "observed_at": "2026-01-15T10:00:00Z",
      "source": {
        "source_kind": "synthetic",
        "source_id": "synthetic-dataset-v0.1",
        "locator": "generated:run-completed-001#event-0001"
      },
      "quality": {
        "quality_status": "accepted",
        "flags": [],
        "notes": []
      }
    }
  ],
  "quality": {
    "quality_status": "accepted",
    "flags": [],
    "notes": ["Synthetic fixture; not a production observation."]
  }
}
```

## Future validation approach

Implementation is intentionally deferred, but future fixtures should be checked in layers:

1. **Structural validation** — required fields, types, enum values, and record type.
2. **Semantic validation** — timestamp ordering, unit status consistency, stable IDs, and value status rules.
3. **Provenance validation** — every observation, event, document, and chunk has a safe source reference.
4. **Safety validation** — synthetic/public source markers, no private paths, no secrets, and no prohibited identifiers.
5. **Downstream validation** — parser output can feed report generation; retrieved chunks can produce source-linked evidence references.

The next implementation phase may add a machine-readable JSON Schema and tests. This document does not claim that either exists yet.
