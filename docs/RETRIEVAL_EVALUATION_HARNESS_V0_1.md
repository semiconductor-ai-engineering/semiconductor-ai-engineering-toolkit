# Retrieval Evaluation Harness v0.1

## Purpose

This phase adds a small, local-only harness for measuring the deterministic lexical retriever from [Knowledge Retrieval Demo v0.1](KNOWLEDGE_RETRIEVAL_DEMO_V0_1.md). It evaluates the existing implementation through `build_local_index(...)` and `retrieve_documents(...)`; it does not copy or tune the scoring logic.

The evaluation set and corpus are synthetic semiconductor engineering examples only. They contain no real fab data, vendor data, customer information, HDP/private data, credentials, or proprietary process information.

The output is measurement data, not engineering advice. Retrieved engineering text remains evidence, not instructions.

## Evaluation case contract

The default case file is [`examples/synthetic_retrieval/evaluation/cases_v0_1.json`](../examples/synthetic_retrieval/evaluation/cases_v0_1.json). It is a UTF-8 JSON array containing 14 cases. Cases are sorted by `case_id` when loaded.

| Field | Contract |
| --- | --- |
| `case_id` | Unique bounded identifier using letters, digits, `.`, `_`, `:`, or `-`. |
| `query` | Non-empty UTF-8 text, limited to 512 characters. It is treated as untrusted lexical data. |
| `top_k` | Integer from 1 through 20. |
| `expected_top1_chunk_id` | Expected chunk identifier at rank 1, or `null` for a no-results case. |
| `expected_chunk_ids` | Unique relevant chunk identifiers expected within the requested top-k. |
| `expect_no_results` | If `true`, the expected result set must be empty. |
| `minimum_score` | Optional numeric threshold from 0 through 1; `null` for no-results cases. |
| `scenario` | Bounded identifier describing the test intent. |
| `notes` | Synthetic explanation of the case, limited to 2,048 characters. |

Non-empty cases must name a rank-1 chunk in `expected_chunk_ids`. No-results cases must not declare expected chunks or a score threshold. Unknown fields, duplicate case IDs, malformed JSON, invalid UTF-8, BOM-prefixed files, URL-like paths, oversized files, and over-limit case sets are rejected.

## Metrics

The summary contains these deterministic metrics:

- `total_cases`: number of evaluation results.
- `passed_cases` and `failed_cases`: cases whose declared expectations passed or failed.
- `non_empty_cases`: valid cases with `expect_no_results == false`; `case_error` results are excluded from retrieval accuracy denominators.
- `top1_hits`: non-empty cases whose actual rank-1 chunk equals `expected_top1_chunk_id`. A minimum-score failure can still be a top-1 hit.
- `top1_accuracy`: `top1_hits / non_empty_cases`.
- `top_k_hits`: non-empty cases where every identifier in `expected_chunk_ids` is present in the returned top-k list. Rank 1 is not required for every identifier.
- `top_k_hit_rate`: `top_k_hits / non_empty_cases`.
- `expected_empty_correct`: no-results cases for which retrieval returned an empty list.
- `empty_case_accuracy`: `expected_empty_correct / expected_empty_cases`.
- `failed_case_ids`: sorted IDs of failed cases.
- `failure_counts`: counts for each supported failure category.

Ratios use six decimal places and are `0.0` when their denominator is zero. Score thresholds affect the pass/fail classification only; they do not change top-1 or top-k hit metrics. This keeps relevance measurement separate from a case-specific acceptance threshold.

The failure categories are:

- `no_match`: evidence was expected but retrieval returned no results.
- `wrong_rank`: returned evidence did not satisfy the declared rank-1 or top-k expectations.
- `unexpected_match`: a no-results case returned evidence.
- `below_minimum_score`: ranking expectations passed, but rank-1 score was below the declared threshold.
- `case_error`: the case was invalid or the bounded retrieval call could not produce a case result.
- `tie_instability`: reserved for an observed violation of the retriever's documented deterministic tie ordering; it is not asserted without evidence.

Failure classification is deterministic. A no-results mismatch is `unexpected_match`; for a non-empty case, an empty result is `no_match`, an expectation mismatch is `wrong_rank`, and only then is `minimum_score` checked.

## Current synthetic baseline

Measured with the default four-chunk corpus and the 14 default cases on this branch:

| Metric | Baseline |
| --- | ---: |
| `total_cases` | 14 |
| `passed_cases` | 12 |
| `failed_cases` | 2 |
| `non_empty_cases` | 12 |
| `expected_empty_cases` | 2 |
| `top1_hits` / `top1_accuracy` | 12 / 1.0 |
| `top_k_hits` / `top_k_hit_rate` | 12 / 1.0 |
| `expected_empty_correct` / `empty_case_accuracy` | 1 / 0.5 |

Failure counts are:

```json
{
  "below_minimum_score": 1,
  "case_error": 0,
  "no_match": 0,
  "tie_instability": 0,
  "unexpected_match": 1,
  "wrong_rank": 0
}
```

The two intentional baseline failures are:

- `retrieval-eval-005`: the synthetic corpus contains `pressure` but not `sensor`, so lexical partial matching returns evidence for a case that declares no results. This characterizes corpus insufficiency; it does not tune the retriever.
- `retrieval-eval-010`: the observed top-1 score for `synthetic pressure warning` is `0.527766`, below the declared synthetic threshold `0.6`.

No `tie_instability` was observed. The deterministic tie case confirms the existing `score DESC`, `document_id ASC`, `chunk_id ASC` ordering.

## Python API

```python
from semiconductor_ai_engineering_toolkit import (
    build_local_index,
    evaluate_retrieval,
    load_retrieval_evaluation_cases,
    summarize_retrieval_evaluation,
)

cases = load_retrieval_evaluation_cases()
index = build_local_index()
results = evaluate_retrieval(index, cases)
summary = summarize_retrieval_evaluation(results)
```

`run_retrieval_evaluation(...)` is a convenience wrapper that returns a JSON-ready object with `evaluation_notice`, `summary`, and `results`.

## CLI

Run the default local synthetic evaluation:

```powershell
semi-ai evaluate-retrieval
```

Use explicit local inputs when needed:

```powershell
semi-ai evaluate-retrieval --cases examples/synthetic_retrieval/evaluation/cases_v0_1.json --corpus examples/synthetic_dataset_v0_1/documents
```

Successful execution prints stable JSON with `summary` and `results`. Expected case failures are measurement output and do not make the command fail. Invalid input, malformed files, URL-like paths, or corpus errors return a non-zero exit code without a traceback. No output file is written by the command.

## Security and resource boundaries

- Only the default repository case file or the explicit local case file supplied by the caller is read.
- URL-like case and corpus paths are rejected. The harness does not make network requests, follow URLs, retrieve external schemas, import code, execute text, run shell commands, or inspect environment credentials.
- Query text, notes, corpus text, and instruction-like strings are data only. The case `Ignore previous instructions` is intentionally retained as a data-boundary test.
- Evaluation files are limited to 128 KiB and 20 cases. Query length and `top_k` use the retriever's existing limits; notes are limited to 2,048 characters.
- Result records contain identifiers and scores rather than absolute paths or retrieved excerpts. The explicit notice is `Evaluation output is measurement data, not engineering advice.`

## Why evaluation precedes embeddings or an LLM

A small deterministic baseline makes ranking behavior, empty-result behavior, tie ordering, score thresholds, and corpus insufficiency visible before adding semantic components. It also provides a repeatable regression surface for future changes. Embeddings, vector databases, LLMs, and agents are intentionally outside Phase 0.9 until public-safe evidence, relevance labels, failure analysis, and human review justify them.

## Limitations

This baseline is not a benchmark for production semiconductor engineering retrieval. The corpus is tiny, synthetic, and lexical; expected relevance labels are hand-authored for this public fixture set. It does not measure semantic similarity, domain completeness, expert usefulness, latency, throughput, or real equipment/process behavior. It is not a process recommendation, a safety decision, a control action, or evidence of customer or fab validation.
