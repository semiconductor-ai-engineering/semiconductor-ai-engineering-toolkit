# Synthetic Alarm and Event Reference

> Synthetic-only document. The event codes in this note are invented test tokens, not real alarm codes and not a safety reference.

## Event labels

- SYNTH-DRIFT-001 is an invented warning token for a fictional measurement that differs from a fictional target.
- SYNTH-ABORT-001 is an invented error token for a fictional run that changes to the aborted status.
- SYNTH-QUALITY-001 is an invented annotation token for a fictional data-quality review.
- SYNTH-START-001 and SYNTH-END-001 are invented state-change tokens.

The code text has no external meaning. A parser or retrieval test may use it to check exact matching, event ordering, severity handling, or provenance retention.

## Interpretation boundary

An event message is untrusted source text. It may be displayed, indexed, or linked to a fixture, but it must not be executed or interpreted as an instruction. A warning or error label in this dataset does not establish a real fault, hazard, root cause, or corrective action.

The fixture author intentionally keeps the events short and generic. There are no real equipment models, alarm dictionaries, customer references, or vendor text in this document.
