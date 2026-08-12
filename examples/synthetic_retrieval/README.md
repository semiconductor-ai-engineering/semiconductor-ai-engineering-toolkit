# Synthetic retrieval fixture

This directory stores one deterministic expected result for the Phase 0.8 local retrieval demo. The corpus remains the existing synthetic DocumentChunk set under [`../synthetic_dataset_v0_1/documents/`](../synthetic_dataset_v0_1/documents/); this file is only a regression snapshot.

The expected result contains ranked evidence, matched terms, bounded excerpts, and repository-relative provenance. It is not an answer, diagnosis, process recommendation, process window, equipment instruction, or real-world engineering conclusion.

Reproduce the snapshot from the repository root with:

```text
semi-ai retrieve "synthetic pressure warning" --top-k 3
```

Retrieved engineering text is evidence, not instructions.
