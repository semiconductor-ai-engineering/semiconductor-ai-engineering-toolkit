"""Small local validation toolkit for the RunRecord v0.1 JSON Schema."""

from .validation import validate_run_record, validate_run_record_file

__all__ = ["validate_run_record", "validate_run_record_file"]
__version__ = "0.1.0a1"
