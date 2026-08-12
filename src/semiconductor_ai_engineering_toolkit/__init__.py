"""Public APIs for validation, parsing, and deterministic RunRecord reports."""

from .engineering_report import (
    EngineeringReportError,
    EngineeringReportInputError,
    EngineeringReportValidationError,
    generate_engineering_report,
    generate_engineering_report_file,
    render_engineering_report,
)

from .synthetic_log_parser import (
    SyntheticLogParseError,
    parse_synthetic_log,
    parse_synthetic_log_file,
)
from .validation import validate_run_record, validate_run_record_file

__all__ = [
    "SyntheticLogParseError",
    "EngineeringReportError",
    "EngineeringReportInputError",
    "EngineeringReportValidationError",
    "generate_engineering_report",
    "generate_engineering_report_file",
    "render_engineering_report",
    "parse_synthetic_log",
    "parse_synthetic_log_file",
    "validate_run_record",
    "validate_run_record_file",
]
__version__ = "0.1.0a1"
