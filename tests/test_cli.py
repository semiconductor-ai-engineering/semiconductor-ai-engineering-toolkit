import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "synthetic_data" / "run_warning_alarm_001.json"


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
