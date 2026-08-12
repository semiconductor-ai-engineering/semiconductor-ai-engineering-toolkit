import json
import re
from pathlib import Path

from semiconductor_ai_engineering_toolkit import validate_run_record_file

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = REPO_ROOT / "examples" / "synthetic_dataset_v0_1"
MANIFEST_PATH = DATASET_ROOT / "manifest.json"

EXTERNAL_URL_PATTERN = re.compile(r"https?://", re.IGNORECASE)
SECRET_PATTERN = re.compile(
    r"(?:api[_-]?key|password|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{8,}",
    re.IGNORECASE,
)
PRIVATE_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:\\|\\\\|/(?:Users|home|private)/)",
    re.IGNORECASE,
)


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def dataset_files() -> list[Path]:
    return sorted(
        path
        for path in DATASET_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md"}
    )


def test_all_dataset_json_files_parse() -> None:
    json_files = sorted(DATASET_ROOT.rglob("*.json"))

    assert json_files
    for path in json_files:
        json.loads(path.read_text(encoding="utf-8"))


def test_manifest_paths_exist_and_fixture_ids_are_unique() -> None:
    manifest = load_manifest()
    fixtures = manifest["fixtures"]
    fixture_ids = [fixture["fixture_id"] for fixture in fixtures]
    fixture_paths = [fixture["path"] for fixture in fixtures]

    assert len(fixture_ids) == len(set(fixture_ids))
    assert len(fixture_paths) == len(set(fixture_paths))
    for relative_path in fixture_paths:
        target = DATASET_ROOT / relative_path
        assert target.is_file(), relative_path


def test_expected_valid_run_records_pass_existing_validator() -> None:
    manifest = load_manifest()
    run_fixtures = [
        fixture
        for fixture in manifest["fixtures"]
        if fixture["kind"] == "run_record" and fixture["expected_valid"]
    ]
    assert len(run_fixtures) == 5
    assert {
        fixture["scenario"] for fixture in run_fixtures
    } == {
        "normal_completed_run",
        "warning_parameter_drift",
        "aborted_failed_run",
        "missing_unknown_data",
        "data_quality_issue",
    }

    run_ids = []
    for fixture in run_fixtures:
        path = DATASET_ROOT / fixture["path"]
        result = validate_run_record_file(path)
        assert result == {"valid": True, "errors": []}
        record = json.loads(path.read_text(encoding="utf-8"))
        run_ids.append(record["run_id"])
        event_ids = [event["event_id"] for event in record["events"]]
        assert len(event_ids) == len(set(event_ids))

    assert len(run_ids) == len(set(run_ids))


def test_quality_case_is_schema_valid_but_not_quality_accepted() -> None:
    path = DATASET_ROOT / "runs" / "quality_cases" / "run_data_quality_001.json"
    record = json.loads(path.read_text(encoding="utf-8"))

    assert record["quality"]["quality_status"] == "invalid"
    assert record["timestamps"]["time_status"] == "invalid"
    assert record["parameters"][0]["value_status"] == "invalid"
    assert validate_run_record_file(path)["valid"] is True


def test_document_chunk_fixtures_have_expected_shape() -> None:
    manifest = load_manifest()
    chunk_fixtures = [
        fixture
        for fixture in manifest["fixtures"]
        if fixture["kind"] == "document_chunk"
    ]

    assert len(chunk_fixtures) == 4
    chunk_ids = []
    for fixture in chunk_fixtures:
        record = json.loads((DATASET_ROOT / fixture["path"]).read_text(encoding="utf-8"))
        assert record["record_type"] == "document_chunk"
        assert record["provenance"]["source_kind"] == "synthetic"
        assert record["chunk_index"] == 0
        assert record["chunk_count"] == 1
        chunk_ids.append(record["chunk_id"])

    assert len(chunk_ids) == len(set(chunk_ids))


def test_dataset_files_are_utf8_and_have_no_external_or_secret_like_content() -> None:
    assert dataset_files()
    for path in dataset_files():
        text = path.read_bytes().decode("utf-8")
        assert not text.startswith("\ufeff"), path
        assert EXTERNAL_URL_PATTERN.search(text) is None, path
        assert SECRET_PATTERN.search(text) is None, path
        assert PRIVATE_PATH_PATTERN.search(text) is None, path


def test_manifest_declares_synthetic_limitations() -> None:
    manifest = load_manifest()

    assert manifest["synthetic_only"] is True
    assert "software testing" in manifest["synthetic_only_declaration"]
    assert "not a real fab benchmark" in manifest["prohibited_interpretation"]
    assert "not process-control guidance" in manifest["prohibited_interpretation"]
    assert "not recipe guidance" in manifest["prohibited_interpretation"]
    assert "not equipment safety guidance" in manifest["prohibited_interpretation"]
    assert "not evidence of real-world failure mechanisms" in manifest[
        "prohibited_interpretation"
    ]
