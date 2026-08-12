# Synthetic Equipment Data-Handling Note

> Synthetic-only document. This note is original test content and is not a vendor manual, operating instruction, safety instruction, or production engineering reference.

## Purpose

A future software workflow may receive a small record from a fictional equipment class called synthetic_demo_equipment. The record can contain a run identifier, a generic module label, scalar values with explicit units, event messages, provenance, and data-quality states.

The text in this note is source material for retrieval tests. A retrieval system should preserve the document identifier and chunk location when quoting it. It should not convert the text into commands, recipe settings, process limits, or conclusions about equipment behavior.

## Synthetic handling example

The fictional record writer can mark a numeric value as known only when the example contains the value and its unit. It can mark a value as missing when a field was expected but not captured. It can mark a value as unknown when the source gives no reliable interpretation. It can mark a field as not_applicable when the scenario does not call for that kind of value.

These labels describe data handling in this dataset. They are not a universal engineering taxonomy.

## Boundary

The equipment and module names in this document are deliberately generic. There is no real machine, site, customer, serial number, alarm standard, recipe, or process window behind the example. Any future report generator must retain this synthetic-only limitation.
