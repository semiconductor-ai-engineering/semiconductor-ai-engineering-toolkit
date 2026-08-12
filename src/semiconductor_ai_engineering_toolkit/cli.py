"""Command-line interface for local RunRecord validation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .validation import SchemaConfigurationError, validate_run_record_file


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="semi-ai",
        description="Local developer tools for the Semiconductor AI Engineering Toolkit.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate one local RunRecord JSON file")
    validate.add_argument("path", type=Path, help="explicit local JSON file path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "validate":
        try:
            result = validate_run_record_file(args.path)
        except SchemaConfigurationError:
            print("Validator configuration error")
            return 2

        if result["valid"]:
            print("Valid RunRecord v0.1")
            return 0

        print("Validation failed")
        for error in result["errors"]:
            path = error["path"] or "<root>"
            print(f"- {path}: {error['message']}")
        return 1

    return 2
