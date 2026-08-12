"""Deterministic evaluation of the local synthetic knowledge retriever."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .knowledge_retrieval import (
    MAX_QUERY_CHARS,
    MAX_TOP_K,
    KnowledgeRetrievalError,
    LocalKnowledgeIndex,
    build_local_index,
    retrieve_documents,
)

DEFAULT_EVALUATION_CASES_PATH = (
    Path("examples") / "synthetic_retrieval" / "evaluation" / "cases_v0_1.json"
)
EVALUATION_NOTICE = "Evaluation output is measurement data, not engineering advice."
MAX_EVALUATION_FILE_BYTES = 128 * 1024
MAX_EVALUATION_CASES = 20
MAX_CASE_ID_CHARS = 128
MAX_SCENARIO_CHARS = 128
MAX_CASE_NOTES_CHARS = 2048

FAILURE_CATEGORIES = (
    "no_match",
    "wrong_rank",
    "unexpected_match",
    "below_minimum_score",
    "case_error",
    "tie_instability",
)

_URL_SCHEME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
_SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_REQUIRED_CASE_FIELDS = {
    "case_id",
    "query",
    "top_k",
    "expected_top1_chunk_id",
    "expected_chunk_ids",
    "expect_no_results",
    "minimum_score",
    "scenario",
    "notes",
}


class RetrievalEvaluationError(ValueError):
    """Base error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class RetrievalEvaluationInputError(RetrievalEvaluationError):
    """Raised when an evaluation case file or API input is invalid."""


def _is_url_like(value: str) -> bool:
    stripped = value.strip()
    if _URL_SCHEME_PATTERN.match(stripped):
        return True
    normalized_separator = re.match(
        r"^[A-Za-z][A-Za-z0-9+.-]*:[\\/]", stripped
    )
    return bool(normalized_separator and not re.match(r"^[A-Za-z]:[\\/]", stripped))


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _evaluation_path(path: str | Path | None) -> Path:
    candidate_value: str | Path = (
        _repository_root() / DEFAULT_EVALUATION_CASES_PATH
        if path is None
        else path
    )
    try:
        candidate_text = str(candidate_value)
    except (TypeError, ValueError):
        raise RetrievalEvaluationInputError(
            "cases_path", "Evaluation cases path is invalid."
        ) from None

    if not candidate_text.strip():
        raise RetrievalEvaluationInputError(
            "cases_path", "Evaluation cases path cannot be empty."
        )
    if _is_url_like(candidate_text):
        raise RetrievalEvaluationInputError(
            "network_path",
            "Only explicit local evaluation case paths are allowed; URL-like paths are rejected.",
        )
    try:
        candidate = Path(candidate_value)
    except (TypeError, ValueError):
        raise RetrievalEvaluationInputError(
            "cases_path", "Evaluation cases path is invalid."
        ) from None
    if candidate.suffix.casefold() != ".json":
        raise RetrievalEvaluationInputError(
            "cases_format", "Evaluation cases must be provided as a JSON file."
        )
    if not candidate.exists():
        raise RetrievalEvaluationInputError(
            "cases_not_found", "Evaluation cases file does not exist."
        )
    if not candidate.is_file():
        raise RetrievalEvaluationInputError(
            "cases_path", "Evaluation cases path is not a file."
        )
    return candidate


def _required_field(payload: Mapping[str, Any], key: str) -> Any:
    if key not in payload:
        raise RetrievalEvaluationInputError(
            "case_fields", "Each evaluation case must contain the required fields."
        )
    return payload[key]


def _validated_identifier(value: Any, *, field: str, max_chars: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RetrievalEvaluationInputError(
            f"{field}_type", f"{field} must be a non-empty string."
        )
    if len(value) > max_chars:
        raise RetrievalEvaluationInputError(
            f"{field}_too_long", f"{field} exceeds its character limit."
        )
    if _SAFE_IDENTIFIER_PATTERN.fullmatch(value) is None:
        raise RetrievalEvaluationInputError(
            f"{field}_format", f"{field} contains unsupported characters."
        )
    return value


def _normalize_case(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise RetrievalEvaluationInputError(
            "case_shape", "Each evaluation case must be an object."
        )
    unknown_fields = set(payload) - _REQUIRED_CASE_FIELDS
    if unknown_fields:
        raise RetrievalEvaluationInputError(
            "unknown_case_field", "Unknown evaluation case fields are not allowed."
        )

    case_id = _validated_identifier(
        _required_field(payload, "case_id"), field="case_id", max_chars=MAX_CASE_ID_CHARS
    )
    query = _required_field(payload, "query")
    if not isinstance(query, str) or not query.strip():
        raise RetrievalEvaluationInputError(
            "query_type", "query must be a non-empty string."
        )
    if len(query) > MAX_QUERY_CHARS:
        raise RetrievalEvaluationInputError(
            "query_too_long", f"query exceeds the {MAX_QUERY_CHARS}-character limit."
        )

    top_k = _required_field(payload, "top_k")
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise RetrievalEvaluationInputError(
            "top_k_type", "top_k must be an integer."
        )
    if top_k <= 0 or top_k > MAX_TOP_K:
        raise RetrievalEvaluationInputError(
            "top_k_invalid", f"top_k must be between 1 and {MAX_TOP_K}."
        )

    expected_top1 = _required_field(payload, "expected_top1_chunk_id")
    if expected_top1 is not None:
        expected_top1 = _validated_identifier(
            expected_top1,
            field="expected_top1_chunk_id",
            max_chars=MAX_CASE_ID_CHARS,
        )

    expected_chunk_ids = _required_field(payload, "expected_chunk_ids")
    if not isinstance(expected_chunk_ids, list):
        raise RetrievalEvaluationInputError(
            "expected_chunk_ids_type", "expected_chunk_ids must be a list."
        )
    normalized_chunk_ids: list[str] = []
    for chunk_id in expected_chunk_ids:
        normalized_chunk_ids.append(
            _validated_identifier(
                chunk_id, field="expected_chunk_id", max_chars=MAX_CASE_ID_CHARS
            )
        )
    if len(normalized_chunk_ids) != len(set(normalized_chunk_ids)):
        raise RetrievalEvaluationInputError(
            "duplicate_expected_chunk_id",
            "expected_chunk_ids must not contain duplicates.",
        )
    if len(normalized_chunk_ids) > top_k:
        raise RetrievalEvaluationInputError(
            "expected_chunk_ids_too_many",
            "expected_chunk_ids cannot contain more items than top_k.",
        )

    expect_no_results = _required_field(payload, "expect_no_results")
    if not isinstance(expect_no_results, bool):
        raise RetrievalEvaluationInputError(
            "expect_no_results_type", "expect_no_results must be a boolean."
        )

    minimum_score = _required_field(payload, "minimum_score")
    if minimum_score is not None:
        if isinstance(minimum_score, bool) or not isinstance(minimum_score, (int, float)):
            raise RetrievalEvaluationInputError(
                "minimum_score_type", "minimum_score must be a number or null."
            )
        try:
            normalized_score = float(minimum_score)
        except (OverflowError, ValueError):
            raise RetrievalEvaluationInputError(
                "minimum_score_invalid", "minimum_score must be between 0 and 1."
            ) from None
        if not math.isfinite(normalized_score) or not 0.0 <= normalized_score <= 1.0:
            raise RetrievalEvaluationInputError(
                "minimum_score_invalid", "minimum_score must be between 0 and 1."
            )
        minimum_score = round(normalized_score, 6)

    scenario = _validated_identifier(
        _required_field(payload, "scenario"),
        field="scenario",
        max_chars=MAX_SCENARIO_CHARS,
    )
    notes = _required_field(payload, "notes")
    if not isinstance(notes, str):
        raise RetrievalEvaluationInputError(
            "notes_type", "notes must be a string."
        )
    if len(notes) > MAX_CASE_NOTES_CHARS:
        raise RetrievalEvaluationInputError(
            "notes_too_long", "notes exceed the character limit."
        )

    if expect_no_results:
        if expected_top1 is not None or normalized_chunk_ids or minimum_score is not None:
            raise RetrievalEvaluationInputError(
                "case_combination",
                "No-results cases must not declare expected chunks or a minimum score.",
            )
    elif (
        expected_top1 is None
        or not normalized_chunk_ids
        or expected_top1 not in normalized_chunk_ids
    ):
        raise RetrievalEvaluationInputError(
            "case_combination",
            "Non-empty cases must declare expected_top1_chunk_id in expected_chunk_ids.",
        )

    return {
        "case_id": case_id,
        "query": query,
        "top_k": top_k,
        "expected_top1_chunk_id": expected_top1,
        "expected_chunk_ids": normalized_chunk_ids,
        "expect_no_results": expect_no_results,
        "minimum_score": minimum_score,
        "scenario": scenario,
        "notes": notes,
    }


def load_retrieval_evaluation_cases(
    path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Load and validate a bounded local UTF-8 evaluation case file."""

    evaluation_path = _evaluation_path(path)
    try:
        raw = evaluation_path.read_bytes()
    except (OSError, ValueError):
        raise RetrievalEvaluationInputError(
            "cases_read", "Evaluation cases file could not be read."
        ) from None
    if len(raw) > MAX_EVALUATION_FILE_BYTES:
        raise RetrievalEvaluationInputError(
            "cases_file_too_large",
            f"Evaluation cases exceed the {MAX_EVALUATION_FILE_BYTES}-byte file limit.",
        )
    if raw.startswith(b"\xef\xbb\xbf"):
        raise RetrievalEvaluationInputError(
            "utf8_bom", "Evaluation cases must be UTF-8 without a BOM."
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise RetrievalEvaluationInputError(
            "utf-8", "Evaluation cases are not valid UTF-8."
        ) from None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RetrievalEvaluationInputError(
            "json", f"Evaluation cases are not valid JSON: {exc.msg}."
        ) from None
    if not isinstance(payload, list):
        raise RetrievalEvaluationInputError(
            "cases_shape", "Evaluation cases must be a JSON array."
        )
    if not payload:
        raise RetrievalEvaluationInputError(
            "cases_empty", "Evaluation cases must contain at least one case."
        )
    if len(payload) > MAX_EVALUATION_CASES:
        raise RetrievalEvaluationInputError(
            "case_limit",
            f"Evaluation cases cannot exceed {MAX_EVALUATION_CASES} cases.",
        )

    cases: list[dict[str, Any]] = []
    seen_case_ids: set[str] = set()
    for item in payload:
        case = _normalize_case(item)
        if case["case_id"] in seen_case_ids:
            raise RetrievalEvaluationInputError(
                "duplicate_case_id", "Evaluation case IDs must be unique."
            )
        seen_case_ids.add(case["case_id"])
        cases.append(case)
    return sorted(cases, key=lambda case: case["case_id"])


def _case_id_for_error(case: Any, position: int) -> str:
    if isinstance(case, Mapping):
        candidate = case.get("case_id")
        if (
            isinstance(candidate, str)
            and len(candidate) <= MAX_CASE_ID_CHARS
            and _SAFE_IDENTIFIER_PATTERN.fullmatch(candidate)
        ):
            return candidate
    return f"case-error-{position:04d}"


def _case_error_result(
    case: Any,
    position: int,
    error: RetrievalEvaluationError,
) -> dict[str, Any]:
    return {
        "case_id": _case_id_for_error(case, position),
        "case_valid": False,
        "scenario": "case_error",
        "query": "",
        "top_k": None,
        "expected_top1_chunk_id": None,
        "expected_chunk_ids": [],
        "expect_no_results": False,
        "minimum_score": None,
        "retrieved": [],
        "actual_top1_chunk_id": None,
        "actual_top1_score": None,
        "top1_hit": False,
        "top_k_hit": False,
        "empty_case_correct": False,
        "passed": False,
        "failure_category": "case_error",
        "failure_message": f"{error.code}: {error.message}",
    }


def _measurement_result(
    case: Mapping[str, Any],
    retrieved_raw: list[dict[str, Any]],
) -> dict[str, Any]:
    retrieved = [
        {
            "document_id": item["document_id"],
            "chunk_id": item["chunk_id"],
            "score": item["score"],
        }
        for item in retrieved_raw
    ]
    retrieved_chunk_ids = [item["chunk_id"] for item in retrieved]
    expected_top1 = case["expected_top1_chunk_id"]
    expected_chunk_ids = case["expected_chunk_ids"]
    actual_top1 = retrieved[0] if retrieved else None
    top1_hit = bool(actual_top1 and actual_top1["chunk_id"] == expected_top1)
    top_k_hit = bool(
        not case["expect_no_results"]
        and retrieved
        and set(expected_chunk_ids).issubset(set(retrieved_chunk_ids))
    )
    empty_case_correct = bool(case["expect_no_results"] and not retrieved)

    failure_category: str | None = None
    failure_message: str | None = None
    if case["expect_no_results"]:
        passed = not retrieved
        if not passed:
            failure_category = "unexpected_match"
            failure_message = "Expected no results but retrieval returned evidence."
    elif not retrieved:
        passed = False
        failure_category = "no_match"
        failure_message = "Expected evidence but retrieval returned no results."
    elif actual_top1["chunk_id"] != expected_top1 or not top_k_hit:
        passed = False
        failure_category = "wrong_rank"
        failure_message = "Expected relevant evidence was not ranked as specified."
    elif (
        case["minimum_score"] is not None
        and actual_top1["score"] < case["minimum_score"]
    ):
        passed = False
        failure_category = "below_minimum_score"
        failure_message = "Top-1 score is below the declared minimum score."
    else:
        passed = True

    return {
        "case_id": case["case_id"],
        "case_valid": True,
        "scenario": case["scenario"],
        "query": case["query"],
        "top_k": case["top_k"],
        "expected_top1_chunk_id": expected_top1,
        "expected_chunk_ids": list(expected_chunk_ids),
        "expect_no_results": case["expect_no_results"],
        "minimum_score": case["minimum_score"],
        "retrieved": retrieved,
        "actual_top1_chunk_id": actual_top1["chunk_id"] if actual_top1 else None,
        "actual_top1_score": actual_top1["score"] if actual_top1 else None,
        "top1_hit": top1_hit,
        "top_k_hit": top_k_hit,
        "empty_case_correct": empty_case_correct,
        "passed": passed,
        "failure_category": failure_category,
        "failure_message": failure_message,
    }


def evaluate_retrieval(
    index: LocalKnowledgeIndex,
    cases: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Evaluate cases by reusing the canonical local retrieval implementation."""

    if not isinstance(index, LocalKnowledgeIndex):
        raise RetrievalEvaluationInputError(
            "index_type", "index must be a LocalKnowledgeIndex."
        )
    if isinstance(cases, (str, bytes, bytearray)) or not isinstance(cases, Sequence):
        raise RetrievalEvaluationInputError(
            "cases_type", "cases must be a sequence of evaluation case objects."
        )
    if len(cases) > MAX_EVALUATION_CASES:
        raise RetrievalEvaluationInputError(
            "case_limit",
            f"Evaluation cases cannot exceed {MAX_EVALUATION_CASES} cases.",
        )

    results: list[dict[str, Any]] = []
    seen_case_ids: set[str] = set()
    for position, raw_case in enumerate(cases, start=1):
        try:
            case = _normalize_case(raw_case)
            if case["case_id"] in seen_case_ids:
                raise RetrievalEvaluationInputError(
                    "duplicate_case_id", "Evaluation case IDs must be unique."
                )
            seen_case_ids.add(case["case_id"])
            retrieved = retrieve_documents(index, case["query"], case["top_k"])
            results.append(_measurement_result(case, retrieved))
        except RetrievalEvaluationError as exc:
            results.append(_case_error_result(raw_case, position, exc))
        except KnowledgeRetrievalError as exc:
            results.append(
                _case_error_result(
                    raw_case,
                    position,
                    RetrievalEvaluationInputError(exc.code, exc.message),
                )
            )
        except Exception:
            results.append(
                _case_error_result(
                    raw_case,
                    position,
                    RetrievalEvaluationInputError(
                        "retrieval_error", "Retrieval failed for this evaluation case."
                    ),
                )
            )
    return results


def _ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def summarize_retrieval_evaluation(
    results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return stable aggregate metrics for evaluation results."""

    if isinstance(results, (str, bytes, bytearray)) or not isinstance(results, Sequence):
        raise RetrievalEvaluationInputError(
            "results_type", "results must be a sequence of result objects."
        )

    failure_counts = {category: 0 for category in FAILURE_CATEGORIES}
    total_cases = len(results)
    non_empty_cases = 0
    expected_empty_cases = 0
    top1_hits = 0
    top_k_hits = 0
    expected_empty_correct = 0
    passed_cases = 0
    failed_case_ids: list[str] = []

    for result in results:
        if not isinstance(result, Mapping):
            raise RetrievalEvaluationInputError(
                "result_shape", "Each evaluation result must be an object."
            )
        case_id = result.get("case_id")
        if not isinstance(case_id, str):
            raise RetrievalEvaluationInputError(
                "result_shape", "Each evaluation result must contain a case_id."
            )
        case_valid = result.get(
            "case_valid", result.get("failure_category") != "case_error"
        )
        if case_valid:
            if result.get("expect_no_results"):
                expected_empty_cases += 1
                if result.get("empty_case_correct"):
                    expected_empty_correct += 1
            else:
                non_empty_cases += 1
                if result.get("top1_hit"):
                    top1_hits += 1
                if result.get("top_k_hit"):
                    top_k_hits += 1

        if result.get("passed"):
            passed_cases += 1
        else:
            failed_case_ids.append(case_id)
        failure_category = result.get("failure_category")
        if failure_category is not None:
            if failure_category not in failure_counts:
                raise RetrievalEvaluationInputError(
                    "failure_category", "Unknown evaluation failure category."
                )
            failure_counts[failure_category] += 1

    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "failed_cases": total_cases - passed_cases,
        "non_empty_cases": non_empty_cases,
        "expected_empty_cases": expected_empty_cases,
        "top1_hits": top1_hits,
        "top1_accuracy": _ratio(top1_hits, non_empty_cases),
        "top_k_hits": top_k_hits,
        "top_k_hit_rate": _ratio(top_k_hits, non_empty_cases),
        "expected_empty_correct": expected_empty_correct,
        "empty_case_accuracy": _ratio(expected_empty_correct, expected_empty_cases),
        "failed_case_ids": sorted(failed_case_ids),
        "failure_counts": failure_counts,
    }


def run_retrieval_evaluation(
    cases_path: str | Path | None = None,
    corpus_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run the default local evaluation pipeline and return JSON-ready data."""

    cases = load_retrieval_evaluation_cases(cases_path)
    index = build_local_index(corpus_path)
    results = evaluate_retrieval(index, cases)
    return {
        "evaluation_notice": EVALUATION_NOTICE,
        "summary": summarize_retrieval_evaluation(results),
        "results": results,
    }


__all__ = [
    "DEFAULT_EVALUATION_CASES_PATH",
    "EVALUATION_NOTICE",
    "FAILURE_CATEGORIES",
    "MAX_CASE_NOTES_CHARS",
    "MAX_EVALUATION_CASES",
    "MAX_EVALUATION_FILE_BYTES",
    "RetrievalEvaluationError",
    "RetrievalEvaluationInputError",
    "evaluate_retrieval",
    "load_retrieval_evaluation_cases",
    "run_retrieval_evaluation",
    "summarize_retrieval_evaluation",
]
