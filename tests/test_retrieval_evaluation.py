import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from semiconductor_ai_engineering_toolkit import (
    DEFAULT_EVALUATION_CASES_PATH,
    EVALUATION_NOTICE,
    FAILURE_CATEGORIES,
    MAX_EVALUATION_FILE_BYTES,
    RetrievalEvaluationInputError,
    build_local_index,
    evaluate_retrieval,
    load_retrieval_evaluation_cases,
    summarize_retrieval_evaluation,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = REPO_ROOT / "examples" / "synthetic_dataset_v0_1" / "documents"
DEFAULT_CASES = REPO_ROOT / DEFAULT_EVALUATION_CASES_PATH
EVALUATION_MODULE = (
    REPO_ROOT
    / "src"
    / "semiconductor_ai_engineering_toolkit"
    / "retrieval_evaluation.py"
)
GLOSSARY_CHUNK = "synthetic-dataset-v0-1-chunk-glossary-001"
ALARM_CHUNK = "synthetic-dataset-v0-1-chunk-alarm-001"
TROUBLESHOOTING_CHUNK = "synthetic-dataset-v0-1-chunk-troubleshooting-001"


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    source_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = source_path + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "semiconductor_ai_engineering_toolkit", *arguments],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def clone_cases() -> list[dict[str, object]]:
    return json.loads(DEFAULT_CASES.read_text(encoding="utf-8"))


def write_cases(path: Path, cases: object) -> None:
    path.write_text(
        json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def make_case(
    case_id: str,
    query: str,
    expected_top1: str | None,
    expected_chunk_ids: list[str],
    *,
    top_k: int = 1,
    expect_no_results: bool = False,
    minimum_score: float | None = None,
    scenario: str = "test_case",
) -> dict[str, object]:
    return {
        "case_id": case_id,
        "query": query,
        "top_k": top_k,
        "expected_top1_chunk_id": expected_top1,
        "expected_chunk_ids": expected_chunk_ids,
        "expect_no_results": expect_no_results,
        "minimum_score": minimum_score,
        "scenario": scenario,
        "notes": "Synthetic test case.",
    }


def test_default_cases_load_with_utf8_and_stable_order() -> None:
    cases = load_retrieval_evaluation_cases()

    assert len(cases) == 14
    assert [case["case_id"] for case in cases] == sorted(
        case["case_id"] for case in cases
    )
    assert len({case["case_id"] for case in cases}) == len(cases)
    assert next(case for case in cases if case["case_id"] == "retrieval-eval-007")[
        "query"
    ] == "压力 pressure"


def test_duplicate_case_id_is_rejected(tmp_path: Path) -> None:
    cases = clone_cases()
    cases[-1]["case_id"] = cases[0]["case_id"]
    path = tmp_path / "duplicate.json"
    write_cases(path, cases)

    with pytest.raises(RetrievalEvaluationInputError) as error:
        load_retrieval_evaluation_cases(path)

    assert error.value.code == "duplicate_case_id"


def test_malformed_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "malformed.json"
    path.write_text("{bad json", encoding="utf-8")

    with pytest.raises(RetrievalEvaluationInputError) as error:
        load_retrieval_evaluation_cases(path)

    assert error.value.code == "json"


@pytest.mark.parametrize(
    ("mutator", "code"),
    [
        (lambda case: case.update({"top_k": True}), "top_k_type"),
        (lambda case: case.update({"query": 123}), "query_type"),
        (lambda case: case.update({"expected_chunk_ids": "not-a-list"}), "expected_chunk_ids_type"),
        (
            lambda case: case.update(
                {
                    "expect_no_results": True,
                    "expected_top1_chunk_id": GLOSSARY_CHUNK,
                }
            ),
            "case_combination",
        ),
    ],
)
def test_invalid_case_type_or_combination_is_rejected(
    tmp_path: Path,
    mutator,
    code: str,
) -> None:
    case = clone_cases()[0]
    mutator(case)
    path = tmp_path / f"invalid-{code}.json"
    write_cases(path, [case])

    with pytest.raises(RetrievalEvaluationInputError) as error:
        load_retrieval_evaluation_cases(path)

    assert error.value.code == code


def test_invalid_utf8_and_bom_are_rejected(tmp_path: Path) -> None:
    invalid_utf8 = tmp_path / "invalid-utf8.json"
    invalid_utf8.write_bytes(b"[\xff]")
    with pytest.raises(RetrievalEvaluationInputError) as encoding_error:
        load_retrieval_evaluation_cases(invalid_utf8)
    assert encoding_error.value.code == "utf-8"

    bom = tmp_path / "bom.json"
    bom.write_bytes(b"\xef\xbb\xbf[]")
    with pytest.raises(RetrievalEvaluationInputError) as bom_error:
        load_retrieval_evaluation_cases(bom)
    assert bom_error.value.code == "utf8_bom"


def test_oversized_evaluation_file_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "oversized.json"
    path.write_bytes(b"x" * (MAX_EVALUATION_FILE_BYTES + 1))

    with pytest.raises(RetrievalEvaluationInputError) as error:
        load_retrieval_evaluation_cases(path)

    assert error.value.code == "cases_file_too_large"


def test_url_like_evaluation_case_path_is_rejected() -> None:
    with pytest.raises(RetrievalEvaluationInputError) as error:
        load_retrieval_evaluation_cases("https://example.invalid/cases.json")

    assert error.value.code == "network_path"

    with pytest.raises(RetrievalEvaluationInputError) as path_error:
        load_retrieval_evaluation_cases(Path("https://example.invalid/cases.json"))

    assert path_error.value.code == "network_path"


def test_default_baseline_metrics_and_failure_taxonomy() -> None:
    index = build_local_index(DEFAULT_CORPUS)
    results = evaluate_retrieval(index, load_retrieval_evaluation_cases())
    summary = summarize_retrieval_evaluation(results)

    assert summary == {
        "total_cases": 14,
        "passed_cases": 12,
        "failed_cases": 2,
        "non_empty_cases": 12,
        "expected_empty_cases": 2,
        "top1_hits": 12,
        "top1_accuracy": 1.0,
        "top_k_hits": 12,
        "top_k_hit_rate": 1.0,
        "expected_empty_correct": 1,
        "empty_case_accuracy": 0.5,
        "failed_case_ids": ["retrieval-eval-005", "retrieval-eval-010"],
        "failure_counts": {
            "no_match": 0,
            "wrong_rank": 0,
            "unexpected_match": 1,
            "below_minimum_score": 1,
            "case_error": 0,
            "tie_instability": 0,
        },
    }


def test_evaluation_results_are_repeatable_and_do_not_expose_paths() -> None:
    index = build_local_index(DEFAULT_CORPUS)
    cases = load_retrieval_evaluation_cases()

    first = evaluate_retrieval(index, cases)
    second = evaluate_retrieval(index, cases)

    assert first == second
    assert json.dumps(first, ensure_ascii=False, sort_keys=True) == json.dumps(
        second, ensure_ascii=False, sort_keys=True
    )
    assert str(REPO_ROOT) not in json.dumps(first, ensure_ascii=False)


def test_all_failure_categories_are_measurable_without_tie_instability_claim() -> None:
    index = build_local_index(DEFAULT_CORPUS)
    cases = [
        make_case("test-no-match", "qzxv", GLOSSARY_CHUNK, [GLOSSARY_CHUNK]),
        make_case(
            "test-wrong-rank",
            "machine action",
            ALARM_CHUNK,
            [ALARM_CHUNK, TROUBLESHOOTING_CHUNK],
            top_k=2,
        ),
        make_case(
            "test-unexpected-match",
            "pressure",
            None,
            [],
            expect_no_results=True,
        ),
        make_case(
            "test-below-score",
            "synthetic pressure warning",
            GLOSSARY_CHUNK,
            [GLOSSARY_CHUNK],
            minimum_score=0.6,
        ),
        make_case("test-pass", "pressure", GLOSSARY_CHUNK, [GLOSSARY_CHUNK], minimum_score=1.0),
        {"case_id": "test-case-error", "query": "pressure"},
    ]

    results = evaluate_retrieval(index, cases)
    summary = summarize_retrieval_evaluation(results)

    assert {result["failure_category"] for result in results if not result["passed"]} == {
        "no_match",
        "wrong_rank",
        "unexpected_match",
        "below_minimum_score",
        "case_error",
    }
    assert summary["failure_counts"] == {
        "no_match": 1,
        "wrong_rank": 1,
        "unexpected_match": 1,
        "below_minimum_score": 1,
        "case_error": 1,
        "tie_instability": 0,
    }


def test_utf8_and_instruction_like_text_remain_measurement_data() -> None:
    index = build_local_index(DEFAULT_CORPUS)
    cases = load_retrieval_evaluation_cases()
    results = evaluate_retrieval(index, cases)

    utf8_result = next(result for result in results if result["case_id"] == "retrieval-eval-007")
    instruction_result = next(
        result for result in results if result["case_id"] == "retrieval-eval-008"
    )
    assert utf8_result["query"] == "压力 pressure"
    assert utf8_result["passed"] is True
    assert instruction_result["actual_top1_chunk_id"] == TROUBLESHOOTING_CHUNK
    assert instruction_result["failure_category"] is None
    assert EVALUATION_NOTICE.endswith("not engineering advice.")


def test_summarizer_initializes_all_failure_categories() -> None:
    summary = summarize_retrieval_evaluation([])

    assert summary["total_cases"] == 0
    assert summary["failed_case_ids"] == []
    assert set(summary["failure_counts"]) == set(FAILURE_CATEGORIES)
    assert summary["top1_accuracy"] == 0.0
    assert summary["empty_case_accuracy"] == 0.0


def test_evaluate_retrieval_requires_local_index() -> None:
    with pytest.raises(RetrievalEvaluationInputError) as error:
        evaluate_retrieval(object(), [])  # type: ignore[arg-type]

    assert error.value.code == "index_type"


def test_cli_evaluate_retrieval_is_json_and_repeatable() -> None:
    first = run_cli("evaluate-retrieval")
    second = run_cli("evaluate-retrieval")

    assert first.returncode == 0
    assert first.stderr == ""
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert set(payload) == {"evaluation_notice", "results", "summary"}
    assert payload["summary"]["total_cases"] == 14
    assert payload["summary"]["failed_case_ids"] == [
        "retrieval-eval-005",
        "retrieval-eval-010",
    ]
    assert "Traceback" not in first.stdout
    assert str(REPO_ROOT) not in first.stdout


def test_cli_evaluate_retrieval_rejects_url_like_cases_path() -> None:
    completed = run_cli(
        "evaluate-retrieval",
        "--cases",
        "https://example.invalid/cases.json",
    )

    assert completed.returncode == 1
    assert completed.stdout.startswith("Evaluation failed\n- network_path:")
    assert "Traceback" not in completed.stdout
    assert completed.stderr == ""


def test_retrieval_evaluation_module_has_no_network_or_dynamic_execution() -> None:
    tree = ast.parse(EVALUATION_MODULE.read_text(encoding="utf-8"), filename=str(EVALUATION_MODULE))
    forbidden_imports = {
        "http",
        "https",
        "importlib",
        "openai",
        "requests",
        "socket",
        "subprocess",
        "urllib",
    }
    forbidden_name_calls = {"__import__", "compile", "eval", "exec"}
    forbidden_attribute_calls = {"__import__", "eval", "exec", "system", "popen", "run"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name.split(".")[0] not in forbidden_imports for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_imports
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_name_calls
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_attribute_calls
