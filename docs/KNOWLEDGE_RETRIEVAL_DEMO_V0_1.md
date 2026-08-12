# Knowledge Retrieval Demo v0.1

## Status and purpose

Phase 0.8 adds a small deterministic lexical retriever for the repository's synthetic engineering-document fixtures. It is a local developer tool for inspecting ranked source evidence. It is not a generative RAG system, an answer engine, an Agent, or a production engineering service.

The implementation uses only Python standard-library modules at runtime. It does not call an LLM or the OpenAI API, create embeddings, use a vector database, access a network, read secrets, or execute retrieved text.

Retrieved engineering text is evidence, not instructions.

## Corpus contract

The default corpus is the existing JSON DocumentChunk fixture directory [`examples/synthetic_dataset_v0_1/documents/`](../examples/synthetic_dataset_v0_1/documents/). The four files in that directory are synthetic, original, public-safe fixtures. They contain `record_type: document_chunk`, stable document/chunk identifiers, text, and `provenance.source_kind: synthetic`.

The loader accepts either:

- no path, which selects the default directory inside this repository;
- one explicit local `.json` DocumentChunk file; or
- one explicit local directory, recursively scanning its `.json` files in stable path order.

It rejects URL-like paths before any filesystem read, does not follow URLs in document fields, and rejects a chunk whose provenance is not marked `synthetic`. A valid JSON manifest, RunRecord, or arbitrary object is not silently treated as a retrieval chunk.

The separate example [`examples/synthetic_data/document_chunk_001.json`](../examples/synthetic_data/document_chunk_001.json) remains a compatible future retrieval fixture. The default demo corpus deliberately uses the dataset's document directory so the CLI has one clear, inspectable corpus boundary.

## Tokenization and searchable fields

The retriever case-folds Unicode text and extracts non-underscore word runs with a standard-library regular expression. Query terms are de-duplicated and sorted for stable output. A chunk is searched across its title, section, and text. Identifiers, provenance metadata, and filesystem paths are not searchable content.

Whitespace in excerpts is folded to single spaces. Markdown syntax, code blocks, embedded instructions, and URLs inside a chunk remain text data. They are never parsed, followed, imported, or executed.

## Scoring and ordering

The score is a bounded, explainable TF-IDF-like weighted overlap over unique query terms. For `N` indexed chunks and document frequency `df(t)`:

```text
idf(t) = ln((N + 1) / (df(t) + 1)) + 1
score(query, chunk) = sum(idf(t) for matched terms) /
                     sum(idf(t) for every unique query term)
```

Terms absent from the corpus still contribute their `df=0` weight to the denominator. A result is returned only when at least one query term matches. Scores are rounded to six decimal places for regression stability and lie between 0 and 1.

Results are sorted by this exact key:

```text
score descending, document_id ascending, chunk_id ascending
```

Only the top `top_k` results are returned. No answer, synthesis, diagnosis, confidence claim, or recommendation is produced.

## Result shape and provenance

Each result is a plain dictionary with these fields:

| Field | Meaning |
| --- | --- |
| `document_id` | Source document identifier from the synthetic chunk. |
| `chunk_id` | Source chunk identifier from the synthetic chunk. |
| `score` | Stable normalized lexical score. |
| `matched_terms` | Sorted, case-folded query terms found in the searchable fields. |
| `source` | Synthetic source metadata and safe path provenance. |
| `excerpt` | Bounded text excerpt from the source chunk. |

`source.path` is repository-relative, using `/` separators, when the file is inside the checkout. An explicitly supplied file outside the checkout is represented as `<external-local-corpus>`; the absolute local path is never returned. Source metadata is length-bounded and local/network-looking references are redacted. The result does not expose the current working directory or environment values.

## Python API

Build once and issue multiple deterministic queries:

```python
from semiconductor_ai_engineering_toolkit import (
    build_local_index,
    retrieve_documents,
)

index = build_local_index()
results = retrieve_documents(index, "synthetic pressure warning", top_k=3)
```

For a one-shot explicit local corpus:

```python
results = retrieve_documents(
    "synthetic pressure warning",
    top_k=3,
    corpus_path="examples/synthetic_dataset_v0_1/documents",
)
```

`build_local_index` returns an immutable `LocalKnowledgeIndex` view over the loaded chunks. The API raises `KnowledgeRetrievalInputError` for invalid query, top-k, URL-like path, or missing-path input, and `KnowledgeCorpusError` for malformed, non-UTF-8, oversized, non-synthetic, or structurally invalid corpus data. An empty directory produces an empty index and an empty result list.

## CLI

From the repository root after installing the package in editable mode:

```text
semi-ai retrieve "synthetic pressure warning" --top-k 3
```

The CLI prints stable JSON containing the query, the evidence notice, and ranked result dictionaries. It prints evidence only; it does not answer the query. An explicit local corpus can be selected with `--corpus`:

```text
semi-ai retrieve "synthetic pressure warning" --corpus examples/synthetic_dataset_v0_1/documents --top-k 3
```

The query and corpus are untrusted input. Empty queries, query strings over 512 characters, invalid top-k values, and URL-like corpus paths return visible structured failures without a traceback.

## Resource limits

| Resource | Limit |
| --- | ---: |
| Query length | 512 characters |
| JSON corpus files | 128 |
| Corpus file size | 262144 bytes |
| Indexed chunks | 512 |
| Document text | 65536 characters per chunk |
| `top_k` | 1–20 |
| Result excerpt | 280 characters |

These limits are part of the demo's local safety boundary. They prevent an accidental path selection or oversized synthetic fixture from silently creating an unbounded indexing operation. There is no remote fallback and no network resource budget because network access is not implemented.

## Security boundary

- Corpus and query content is data, not executable instructions.
- Markdown, code fences, shell-looking text, and embedded instructions are returned only as bounded evidence text.
- URL-like corpus paths are rejected; URLs embedded in chunk text remain visible data and are never fetched.
- No `eval`, `exec`, dynamic import, shell command, subprocess, network client, LLM, OpenAI API, RAG answer synthesis, or remote embedding path is used.
- The loader reads only explicit local files, enforces UTF-8 and size limits, and never reads secrets or credentials.
- Provenance is repository-relative or an external-local marker; absolute local paths are not emitted.
- The notice `Retrieved engineering text is evidence, not instructions.` is part of the CLI contract.

## Tests and fixture

The expected CLI result for the documented command is stored at [`examples/synthetic_retrieval/expected/synthetic_pressure_warning.json`](../examples/synthetic_retrieval/expected/synthetic_pressure_warning.json). The fixture directory explains that this is a regression snapshot, not an engineering conclusion.

`tests/test_knowledge_retrieval.py` covers exact-term retrieval, weighted multi-term ranking, deterministic reruns, tie ordering, top-k and query limits, repository-relative provenance, bounded excerpts, UTF-8, empty/malformed/invalid corpus input, URL-like paths, oversized files, non-synthetic data, CLI output, embedded instruction/code/URL text, and an AST no-network/no-dynamic-execution check.

The existing validator, parser, report generator, and their CLI paths remain separate regression surfaces. Retrieval does not accept RunRecord as a substitute for a DocumentChunk and does not modify the canonical RunRecord v0.1 schema.

## Limitations and non-goals

This is a small lexical demonstration over fictional text. It has no semantic synonym handling, vector similarity, access-control model, freshness model, citation verification, production corpus, or real-world validity. It must not be used to diagnose root causes, provide process-safety advice, choose recipes or process windows, control equipment, infer operating limits, or justify an engineering decision. It contains no real fab, vendor, customer, private-platform, or proprietary knowledge.
