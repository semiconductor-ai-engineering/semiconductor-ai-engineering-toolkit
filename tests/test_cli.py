import json
import os
import subprocess
import sys
from pathlib import Path

from semiconductor_ai_engineering_toolkit import validate_run_record

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "synthetic_data" / "run_warning_alarm_001.json"
SYNTHETIC_LOG = REPO_ROOT / "examples" / "synthetic_logs" / "run_warning_alarm_001.log"
INVALID_SYNTHETIC_LOG = REPO_ROOT / "examples" / "synthetic_logs" / "invalid" / "bad_numeric_value.log"


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


def test_cli_valid_fixture() -> None:
    completed = run_cli("validate", str(FIXTURE))

    assert completed.returncode == 0
    assert completed.stdout.strip() == "Valid RunRecord v0.1"
    assert completed.stderr == ""


def test_cli_reports_validation_failure(tmp_path: Path) -> None:
    record = json.loads(FIXTURE.read_text(encoding="utf-8"))
    record["status"] = "finished"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(record), encoding="utf-8")

    completed = run_cli("validate", str(path))

    assert completed.returncode == 1
    assert completed.stdout.startswith("Validation failed\n")
    assert "- status: " in completed.stdout
    assert "Traceback" not in completed.stdout
    assert completed.stderr == ""


def test_cli_reports_malformed_json(tmp_path: Path) -> None:
    path = tmp_path / "malformed.json"
    path.write_text("{bad json", encoding="utf-8")

    completed = run_cli("validate", str(path))

    assert completed.returncode == 1
    assert completed.stdout.startswith("Validation failed\n- <root>: Invalid JSON:")
    assert "Traceback" not in completed.stdout


def test_cli_parses_and_validates_synthetic_log() -> None:
    completed = run_cli("parse", str(SYNTHETIC_LOG))

    assert completed.returncode == 0
    assert completed.stdout.strip() == "Parsed and validated RunRecord v0.1"
    assert completed.stderr == ""


def test_cli_parse_writes_stable_json_and_validates_output(tmp_path: Path) -> None:
    first_path = tmp_path / "parsed_first.json"
    second_path = tmp_path / "parsed_second.json"

    first = run_cli("parse", str(SYNTHETIC_LOG), "--output", str(first_path))
    second = run_cli("parse", str(SYNTHETIC_LOG), "--output", str(second_path))

    assert first.returncode == 0
    assert second.returncode == 0
    assert first.stdout.strip() == "Parsed and validated RunRecord v0.1"
    assert first_path.read_bytes() == second_path.read_bytes()
    output_record = json.loads(first_path.read_text(encoding="utf-8"))
    assert output_record["record_type"] == "run"
    assert validate_run_record(output_record) == {"valid": True, "errors": []}


def test_cli_parse_refuses_to_overwrite_output(tmp_path: Path) -> None:
    output_path = tmp_path / "existing.json"
    output_path.write_text('{"sentinel": true}\n', encoding="utf-8")

    completed = run_cli("parse", str(SYNTHETIC_LOG), "--output", str(output_path))

    assert completed.returncode == 2
    assert completed.stdout == "Parse failed\n- output file already exists; refusing to overwrite\n"
    assert output_path.read_text(encoding="utf-8") == '{"sentinel": true}\n'


def test_cli_parse_reports_structured_failure_without_traceback() -> None:
    completed = run_cli("parse", str(INVALID_SYNTHETIC_LOG))

    assert completed.returncode == 1
    assert completed.stdout.startswith("Parse failed\n- line 3 [invalid_numeric_value]:")
    assert "Traceback" not in completed.stdout
    assert completed.stderr == ""
