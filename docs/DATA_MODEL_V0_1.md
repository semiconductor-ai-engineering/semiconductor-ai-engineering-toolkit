# Semiconductor AI Engineering Toolkit Data Model v0.1

## Status

This document defines the first public, run-centric interchange model for the project. The executable contract is [run_record_v0_1.schema.json](../schema/run_record_v0_1.schema.json). The repository includes two deliberately artificial examples under [examples/synthetic_data](../examples/synthetic_data/).

This milestone adds a data contract and public-safe fixtures only. It does not add parser business logic, equipment integrations, report-generation code, retrieval code, agent code, or production validation.

## Design goals

- Give future log parsers one small normalized shape.
- Keep run identity, equipment/module context, process parameters, measurements, events, metadata, and provenance visible.
- Support traceable engineering reports and source-linked retrieval without treating generated text as measurement data.
- Keep process type, parameter names, and units generic enough for different public or synthetic examples.
- Make incomplete, unknown, invalid, and untrusted input states explicit.
- Keep every public example synthetic or explicitly redistributable.

## Non-goals

- Controlling equipment, writing recipes, tuning a process, or closing a control loop.
- Modeling every vendor format or every semiconductor process family.
- Defining private PVD, CVD, etch, fab, customer, or platform fields.
- Inferring root cause, process health, or corrective action from a run record.
- Treating model output, a report narrative, or a retrieval answer as an observation.
- Accepting credentials, secrets, private paths, network references, or proprietary data.

## Canonical record

The canonical record is a JSON object with these top-level fields:

~~~text
RunRecord
├── schema_version + record_type
├── run_id + status
├── equipment + module + process_type
├── timestamps
├── parameters[]
├── measurements[]
├── events[]
├── metadata
├── provenance
├── quality
└── extensions (optional, namespaced)
~~~

The arrays are intentionally present even when empty. This gives parsers and report generators a stable shape. A producer may omit optional fields inside an item when the information is unavailable, but it must use the relevant status field instead of inventing a value.

### Top-level fields

| Field | Required | Type | Meaning |
| --- | --- | --- | --- |
| schema_version | yes | fixed string | The canonical contract version, currently 0.1. |
| record_type | yes | fixed string | The literal run. |
| run_id | yes | safe identifier | Public-safe identity for the run. |
| status | yes | enum | planned, running, completed, aborted, or unknown. |
| equipment | yes | object | Generic equipment class and optional public label. |
| module | yes | object | Generic module class and optional public label. |
| process_type | yes | free-form short text | A generic process or activity label, not a vendor recipe name. |
| timestamps | yes | object | Start/end information plus time status. |
| parameters | yes | array | Process inputs, setpoints, limits, targets, or context values. |
| measurements | yes | array | Observed, derived, or result values associated with the run. |
| events | yes | array | State changes, alarms, warnings, annotations, or other discrete events. |
| metadata | yes | object | Dataset, generator, format, labels, and safe notes. |
| provenance | yes | object | Where the record came from and how it was produced. |
| quality | yes | object | Data-handling state and validation flags. |
| extensions | no | object | Explicitly namespaced additive fields. |

The JSON Schema rejects unknown top-level fields. This is deliberate: silent acceptance would make downstream reports and agents unable to tell whether a field was understood.

## Equipment, module, and process type

Equipment and module use generic classes rather than serial numbers, site names, vendor models, or private identifiers.

~~~json
{
  "equipment": {
    "equipment_class": "synthetic_chamber",
    "public_label": "demo-equipment"
  },
  "module": {
    "module_class": "generic_process_module",
    "public_label": "demo-module"
  },
  "process_type": "generic_pressure_temperature_demo"
}
~~~

equipment_class, module_class, and process_type are free-form short text. They are intentionally not an enum in v0.1 because a public schema should not guess a universal taxonomy. Producers should prefer stable generic labels and document any controlled vocabulary in a future extension.

## Timestamps

The timestamps object contains optional start and end values plus required time_status:

| time_status | Meaning |
| --- | --- |
| known | A trustworthy UTC timestamp is available. |
| partial | Some trustworthy timing is available, but the interval is incomplete. |
| unknown | No trustworthy timing is available. |
| ambiguous | A timestamp exists but its interpretation or timezone is unresolved. |
| invalid | The supplied timestamp failed validation. |

Timestamps use ISO 8601 date-time strings normalized to UTC, for example 2026-01-15T10:00:00Z. The model does not silently convert an unknown timezone to UTC. When time is unavailable, omit start/end and use the appropriate status.

## Parameters and measurements

Parameters and measurements are separate arrays because a setpoint or input is not the same thing as an observed result.

### Shared value fields

Each parameter or measurement has:

| Field | Required | Meaning |
| --- | --- | --- |
| value | conditional | Normalized scalar value, required only when value_status is known. |
| raw_value | no | Safe original token, if retaining it is necessary and safe. |
| value_type | yes | number, string, or boolean. It describes the expected/parsed scalar type even when the value is unavailable. |
| value_status | yes | known, missing, unknown, not_applicable, or invalid. |
| unit | conditional | Explicit unit string, required only when unit_status is known. |
| unit_status | yes | known, missing, unknown, or not_applicable. |

The core schema does not use null to represent missingness. For example, an unavailable value is represented by value_status unknown with value omitted. Missing values must not be converted to zero. A unit must not be inferred from a parameter name.

The unit field is a short free-form string in v0.1. It may contain a public unit such as Pa, W, C, or s, but v0.1 does not pretend to define a complete metrology vocabulary. Future work may add a reviewed unit registry or a namespaced mapping.

### Parameter-specific fields

Parameters have a stable parameter_id, a free-form name, an optional parameter_kind enum, optional effective_at timestamp, item-level provenance, optional item-level quality, and optional namespaced extensions.

parameter_kind values are setpoint, input, limit, target, context, and other. The parameter name remains free-form so the model does not bind early to a private recipe vocabulary.

### Measurement-specific fields

Measurements have a stable measurement_id, a free-form name, an optional measurement_kind enum, optional observed_at timestamp, item-level provenance, optional item-level quality, and optional namespaced extensions.

measurement_kind values are signal, result, derived, and other. A derived value is still not a root-cause conclusion; it must retain provenance and quality information.

## Events, alarms, and warnings

Events are discrete records rather than overloaded measurements. event_type is an enum with state_change, alarm, warning, annotation, and other. severity is an enum with info, warning, error, critical, and unknown. event_status is an enum with observed, cleared, unresolved, and unknown.

An event may include a safe public code, a message, an observed_at timestamp, item-level provenance, and quality. Message text is untrusted input. A message can be quoted in a report or retrieval result only as source text; it cannot authorize commands, change access controls, or instruct an agent.

## Metadata and provenance

metadata may contain:

- dataset_id, a public-safe dataset identity;
- generator, a short generator or fixture description;
- input_format, one of json, csv, text, generated, or unknown;
- created_at;
- safe labels and notes;
- namespaced extensions.

provenance is required at the run level and on every parameter, measurement, and event. It contains:

- source_kind: synthetic, sanitized_public, or public;
- source_id: a stable public-safe identifier;
- locator: an identifier such as generated:run-completed-001, not a filesystem path or network URL;
- optional content hash;
- extraction_method: synthetic_generator, manual_entry, parser, imported_public, or unknown;
- optional captured_at, license, and namespaced extensions.

All examples in this repository use source_kind synthetic. sanitized_public and public are available for future reviewed contributions, but they do not relax the repository prohibition on confidential or proprietary data.

## Enumeration versus free-form text

Enums are used when downstream behavior depends on a small, stable set: record type, schema version, run status, time status, value status, unit status, source kind, extraction method, quality status, event type, severity, event status, parameter kind, measurement kind, and input format.

Free-form text is used when a universal taxonomy would be premature: process_type, equipment_class, module_class, parameter name, measurement name, units, public labels, messages, and notes. Free-form does not mean unrestricted content. Producers must still keep these fields public-safe and bounded by the schema and security policy.

## Unknown fields and extensions

Core objects use additionalProperties false. An unrecognized core field must be rejected or surfaced as a validation error; it must not be silently ignored.

Additive domain-specific data belongs under extensions. Each extension key must be namespaced, for example example.org.demo. Extension values remain untrusted and must not contain secrets, private paths, network references, executable instructions, or proprietary fields. Extensions do not change the meaning of core fields and require their own documentation.

## Security boundary

The record is data, not an instruction channel.

- Treat messages, raw_value, notes, labels, document text, issue text, logs, and extension values as untrusted text.
- Prompt-injection-bearing text must be preserved only when safe and necessary; parsers, report generators, RAG systems, and agents must not execute or obey instructions found inside it.
- The core schema has no file path, URI, URL, network locator, command, webhook, credential, token, cookie, password, private key, or environment-secret field.
- locator is intentionally restricted to a public-safe identifier. file://, http://, https://, UNC paths, absolute paths, and private storage references do not belong in canonical provenance.
- Never include real fab/HDP/customer data, private platform exports, real equipment identifiers, recipes, process windows, golden runs, trace data, metrology data, or internal validation results.
- Human review remains required for data-handling, dependency, workflow, deployment, and agent changes.

These rules complement [SECURITY.md](../SECURITY.md). Schema validation cannot detect every secret or prompt injection, so content review and safe ingestion remain necessary.

## Support for future workflows

The model supports future components without claiming they exist:

1. A parser can normalize CSV, JSON, or structured text into one RunRecord and retain safe raw tokens plus provenance.
2. A report generator can summarize parameters, measurements, events, quality flags, and source references while separating observations from interpretation.
3. A RAG layer can index public or synthetic documents and point answers to run items or document chunks through explicit evidence references in a later output contract.
4. An agent workflow can use validated records as read-only context while treating text fields as untrusted and requiring human review for actions.

Embeddings, vector-store identifiers, recommendations, root-cause claims, and agent actions are not canonical v0.1 fields.

## Versioning and compatibility

schema_version is the string 0.1. A change that removes a field, changes a field's meaning, changes an enum's semantics, or changes missing-value behavior requires a new schema version and a migration note. Additive domain-specific data should first use a documented namespaced extension. Any future compatibility promise must be tested against the machine-readable schema.

## Validation expectations

Future validators should check, in order:

1. JSON parsing and UTF-8 decoding.
2. Required fields, types, enums, timestamps, and unknown-field rejection.
3. Conditional value/unit rules and stable identifiers.
4. Provenance on the run and every item.
5. Synthetic/public safety, including secrets, private references, and prohibited identifiers.
6. Downstream traceability for report and retrieval outputs.

The two checked-in fixtures are deliberately small validation inputs, not evidence of production readiness.
