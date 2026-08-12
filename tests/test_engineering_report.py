import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from semiconductor_ai_engineering_toolkit import (
    EngineeringReportInputError,
    EngineeringReportValidationError,
    generate_engineering_report,
    generate_engineering_report_file,
    render_engineering_report,
    validate_run_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_EXPECTED_DIR = REPO_ROOT / "examples" / "synthetic_reports" / "expected"
REPORT_CASES = [
    (
        "completed",
        REPO_ROOT / "examples" / "synthetic_data" / "run_completed_001.json",
        REPORT_EXPECTED_DIR / "run_completed_001.md",
    ),
    (
        "warning_alarm",
        REPO_ROOT / "examples" / "synthetic_data" / "run_warning_alarm_001.json",
        REPORT_EXPECTED_DIR / "run_warning_alarm_001.md",
    ),
    (
        "aborted_incomplete",
        REPO_ROOT / "examples" / "synthetic_data" / "run_incomplete_001.json",
        REPORT_EXPECTED_DIR / "run_incomplete_001.md",
    ),
    (
        "quality_issue",
        REPO_ROOT
        / "examples"
        / "synthetic_dataset_v0_1"
        / "runs"
        / "quality_cases"
        / "run_data_quality_001.json",
        REPORT_EXPECTED_DIR / "run_data_quality_001.md",
    ),
]


def load_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    source_path = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = source_path + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "semiconductor_ai_engineering_toolkit", *arguments],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("case_name,fixture_path,expected_path", REPORT_CASES, ids=[case[0] for case in REPORT_CASES])
def test_expected_reports_are_deterministic(
    case_name: str, fixture_path: Path, expected_path: Path
) -> None:
    del case_name
    record = load_record(fixture_path)

    first = render_engineering_report(generate_engineering_report(record))
    second = render_engineering_report(generate_engineering_report(record))

    assert first == second
    assert first == expected_path.read_text(encoding="utf-8")
    assert first.endswith("\n")
    assert str(fixture_path) not in first


def test_report_separates_observed_facts_from_derived_summaries() -> None:
    record = load_record(REPORT_CASES[1][1])

    report = generate_engineering_report(record)

    observed = report["observed_facts"]
    derived = report["derived_summaries"]
    assert observed["events_alarms"][2]["message"].startswith("Synthetic pressure")
    assert derived["counts"]["alarm_count"] == 1
    assert derived["counts"]["warning_count"] == 1
    assert "message" not in json.dumps(derived, ensure_ascii=False)


def test_invalid_run_record_is_rejected_by_canonical_validator() -> None:
    record = load_record(REPORT_CASES[0][1])
    record["status"] = "finished"

    with pytest.raises(EngineeringReportValidationError) as caught:
        generate_engineering_report(record)

    assert caught.value.errors == validate_run_record(record)["errors"]
    assert caught.value.errors[0]["path"] == "status"


@pytest.mark.parametrize(
    "payload,expected_code",
    [(b"{\xff}", "utf-8"), (b"{bad json", "json")],
)
def test_report_file_rejects_invalid_input_bytes(
    tmp_path: Path, payload: bytes, expected_code: str
) -> None:
    path = tmp_path / "invalid.json"
    path.write_bytes(payload)

    with pytest.raises(EngineeringReportInputError) as caught:
        generate_engineering_report_file(path)

    assert caught.value.code == expected_code


def test_cli_report_writes_expected_markdown_and_refuses_overwrite(tmp_path: Path) -> None:
    output_path = tmp_path / "report.md"
    fixture_path = REPORT_CASES[1][1]
    expected_path = REPORT_CASES[1][2]

    first = run_cli("report", str(fixture_path), "--output", str(output_path))
    second = run_cli("report", str(fixture_path), "--output", str(output_path))

    assert first.returncode == 0
    assert first.stdout == ""
    assert first.stderr == ""
    assert output_path.read_text(encoding="utf-8") == expected_path.read_text(encoding="utf-8")
    assert second.returncode == 2
    assert second.stdout == "Report failed\n- output file already exists; refusing to overwrite\n"
    assert second.stderr == ""


def test_cli_report_invalid_run_record_has_structured_failure_without_traceback(
    tmp_path: Path,
) -> None:
    record = load_record(REPORT_CASES[0][1])
    record["status"] = "finished"
    input_path = tmp_path / "invalid-run.json"
    input_path.write_text(json.dumps(record), encoding="utf-8")

    completed = run_cli("report", str(input_path))

    assert completed.returncode == 1
    assert completed.stdout.startswith("Report failed\n- status: ")
    assert "Traceback" not in completed.stdout
    assert completed.stderr == ""


def test_report_module_has_no_network_or_dynamic_execution() -> None:
    source_path = REPO_ROOT / "src" / "semiconductor_ai_engineering_toolkit" / "engineering_report.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    forbidden_imports = {"http", "https", "openai", "requests", "socket", "subprocess", "urllib"}
    forbidden_calls = {"compile", "eval", "exec", "__import__"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name.split(".")[0] not in forbidden_imports for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_imports
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_calls
