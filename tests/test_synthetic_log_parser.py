import json
from pathlib import Path

import pytest

from semiconductor_ai_engineering_toolkit import (
    SyntheticLogParseError,
    parse_synthetic_log,
    parse_synthetic_log_file,
    validate_run_record,
)
from semiconductor_ai_engineering_toolkit.synthetic_log_parser import (
    MAX_INPUT_BYTES,
    MAX_LINE_BYTES,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = REPO_ROOT / "examples" / "synthetic_logs"
INVALID_LOG_DIR = LOG_DIR / "invalid"


def diagnostic_for(text: str) -> dict:
    with pytest.raises(SyntheticLogParseError) as caught:
        parse_synthetic_log(text)
    assert len(caught.value.diagnostics) == 1
    return caught.value.diagnostics[0]


@pytest.mark.parametrize(
    "filename",
    [
        "run_completed_001.log",
        "run_warning_alarm_001.log",
        "run_aborted_001.log",
        "run_incomplete_001.log",
    ],
)
def test_valid_synthetic_logs_are_validated_run_records(filename: str) -> None:
    record = parse_synthetic_log_file(LOG_DIR / filename)

    assert validate_run_record(record) == {"valid": True, "errors": []}
    assert record["record_type"] == "run"
    assert record["provenance"] == {
        "source_kind": "synthetic",
        "source_id": "synthetic-log-parser-dataset-v0.1",
        "locator": "line:2",
        "extraction_method": "synthetic_log_parser_v0.1",
    }
    assert all(item["provenance"]["locator"].startswith("line:") for item in record["events"])
    assert str(REPO_ROOT) not in json.dumps(record)


def test_warning_fixture_preserves_warning_and_alarm_events() -> None:
    record = parse_synthetic_log_file(LOG_DIR / "run_warning_alarm_001.log")

    assert {event["event_type"] for event in record["events"]} == {"warning", "alarm"}
    assert record["quality"]["quality_status"] == "uncertain"
    assert record["extensions"]["synthetic.recipe-class"] == "synthetic_recipe_b"


def test_incomplete_fixture_preserves_unknown_and_missing_values() -> None:
    record = parse_synthetic_log_file(LOG_DIR / "run_incomplete_001.log")

    assert record["timestamps"] == {"time_status": "unknown"}
    assert record["parameters"][0]["value_status"] == "unknown"
    assert "value" not in record["parameters"][0]
    assert record["measurements"][0]["value_status"] == "missing"
    assert "value" not in record["measurements"][0]


@pytest.mark.parametrize(
    ("filename", "code"),
    [
        ("malformed_line.log", "malformed_line"),
        ("missing_run_id.log", "missing_required_key"),
        ("bad_numeric_value.log", "invalid_numeric_value"),
        ("duplicate_run.log", "duplicate_run"),
        ("unknown_record_type.log", "unknown_record_type"),
        ("bad_timestamp.log", "invalid_timestamp"),
        ("unsupported_value_type.log", "unsupported_value_type"),
        ("invalid_observation_status.log", "invalid_observation_status"),
    ],
)
def test_invalid_fixtures_have_structured_deterministic_errors(filename: str, code: str) -> None:
    with pytest.raises(SyntheticLogParseError) as caught:
        parse_synthetic_log_file(INVALID_LOG_DIR / filename)

    assert caught.value.diagnostics[0]["code"] == code
    assert set(caught.value.diagnostics[0]) == {"code", "line", "message"}
    assert "Traceback" not in str(caught.value)


def test_invalid_enum_and_unknown_field_are_rejected() -> None:
    invalid_status = "\n".join(
        [
            "RUN|run_id=synthetic-invalid-status-001|status=finished",
            "CONTEXT|equipment_class=synthetic_chamber|module_class=synthetic_module|process_type=synthetic_demo",
            "QUALITY|status=accepted",
        ]
    )
    assert diagnostic_for(invalid_status)["code"] == "invalid_run_status"

    unknown_field = invalid_status.replace("status=finished", "status=completed|unexpected=value")
    assert diagnostic_for(unknown_field)["code"] == "unknown_field"


def test_diagnostics_are_deterministic() -> None:
    text = (INVALID_LOG_DIR / "bad_numeric_value.log").read_text(encoding="utf-8")

    first = diagnostic_for(text)
    second = diagnostic_for(text)

    assert first == second


def test_invalid_utf8_file_has_safe_diagnostic(tmp_path: Path) -> None:
    path = tmp_path / "invalid.log"
    path.write_bytes(b"RUN|run_id=synthetic-invalid-utf8-001|status=completed\xff")

    with pytest.raises(SyntheticLogParseError) as caught:
        parse_synthetic_log_file(path)

    assert caught.value.diagnostics == [
        {
            "code": "invalid_utf8",
            "line": 0,
            "message": "Input file is not valid UTF-8.",
        }
    ]
    assert str(path) not in str(caught.value)


def test_resource_limits_are_enforced() -> None:
    with pytest.raises(SyntheticLogParseError) as large_input:
        parse_synthetic_log("x" * (MAX_INPUT_BYTES + 1))
    assert large_input.value.diagnostics[0]["code"] == "input_too_large"

    long_line = "#" + ("x" * MAX_LINE_BYTES)
    with pytest.raises(SyntheticLogParseError) as long_line_error:
        parse_synthetic_log(long_line)
    assert long_line_error.value.diagnostics[0]["code"] == "line_too_long"


def test_input_text_is_kept_as_data() -> None:
    text = "\n".join(
        [
            "RUN|run_id=synthetic-data-only-001|status=completed",
            "CONTEXT|equipment_class=synthetic_chamber|module_class=synthetic_module|process_type=synthetic_data_only_demo",
            "OBS|id=obs-data-only-001|parameter=note|value=__import__('os').system('do-not-run')|value_type=string|value_status=known|unit_status=not_applicable",
            "QUALITY|status=accepted",
        ]
    )

    record = parse_synthetic_log(text)

    assert record["measurements"][0]["value"] == "__import__('os').system('do-not-run')"
