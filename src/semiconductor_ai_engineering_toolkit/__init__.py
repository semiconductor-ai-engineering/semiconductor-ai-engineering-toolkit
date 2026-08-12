"""Public APIs for RunRecord v0.1 validation and synthetic log parsing."""

from .synthetic_log_parser import (
    SyntheticLogParseError,
    parse_synthetic_log,
    parse_synthetic_log_file,
)
from .validation import validate_run_record, validate_run_record_file

__all__ = [
    "SyntheticLogParseError",
    "parse_synthetic_log",
    "parse_synthetic_log_file",
    "validate_run_record",
    "validate_run_record_file",
]
__version__ = "0.1.0a1"
