import json
import urllib.request
from copy import deepcopy
from pathlib import Path

import pytest

from semiconductor_ai_engineering_toolkit import (
    validate_run_record,
    validate_run_record_file,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "examples" / "synthetic_data"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "fixture_name",
    ["run_completed_001.json", "run_incomplete_001.json", "run_warning_alarm_001.json"],
)
def test_synthetic_run_records_are_valid(fixture_name: str) -> None:
    result = validate_run_record(load_fixture(fixture_name))

    assert result == {"valid": True, "errors": []}


def test_missing_required_field() -> None:
    record = load_fixture("run_completed_001.json")
    del record["quality"]

    result = validate_run_record(record)

    assert result["valid"] is False
    assert any(error["validator"] == "required" for error in result["errors"])


def test_unknown_core_field() -> None:
    record = load_fixture("run_completed_001.json")
    record["unexpected_core_field"] = "synthetic"

    result = validate_run_record(record)

    assert result["valid"] is False
    assert any(error["validator"] == "additionalProperties" for error in result["errors"])


def test_invalid_enum() -> None:
    record = load_fixture("run_completed_001.json")
    record["status"] = "finished"

    result = validate_run_record(record)

    assert result["valid"] is False
    assert any(
        error["path"] == "status" and error["validator"] == "enum"
        for error in result["errors"]
    )


def test_invalid_json_type() -> None:
    record = load_fixture("run_completed_001.json")
    record["events"] = "not-an-array"

    result = validate_run_record(record)

    assert result["valid"] is False
    assert any(
        error["path"] == "events" and error["validator"] == "type"
        for error in result["errors"]
    )


def test_file_validation_reads_valid_fixture() -> None:
    result = validate_run_record_file(FIXTURE_DIR / "run_warning_alarm_001.json")

    assert result == {"valid": True, "errors": []}


def test_malformed_json_file(tmp_path: Path) -> None:
    path = tmp_path / "malformed.json"
    path.write_text('{ "record_type": }', encoding="utf-8")

    result = validate_run_record_file(path)

    assert result["valid"] is False
    assert result["errors"][0]["validator"] == "json"
    assert "traceback" not in json.dumps(result).lower()


def test_invalid_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "invalid-utf8.json"
    path.write_bytes(b"{\xff}")

    result = validate_run_record_file(path)

    assert result == {
        "valid": False,
        "errors": [
            {
                "path": "",
                "validator": "utf-8",
                "message": "Input file is not valid UTF-8.",
            }
        ],
    }


def test_error_formatting_is_deterministic() -> None:
    record = load_fixture("run_completed_001.json")
    record["status"] = "finished"
    del record["quality"]
    record["unexpected_core_field"] = True

    first = validate_run_record(deepcopy(record))
    second = validate_run_record(deepcopy(record))

    assert first == second
    assert first["errors"] == sorted(
        first["errors"],
        key=lambda error: (error["path"], error["validator"], error["message"]),
    )


def test_validation_does_not_request_remote_resources(monkeypatch) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("network access is not allowed during validation")

    monkeypatch.setattr(urllib.request, "urlopen", fail_if_called)

    result = validate_run_record(load_fixture("run_completed_001.json"))

    assert result["valid"] is True
