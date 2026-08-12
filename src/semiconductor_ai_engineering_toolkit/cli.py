"""Command-line interface for local validation, parsing, reporting, and retrieval."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .engineering_report import (
    EngineeringReportInputError,
    EngineeringReportValidationError,
    generate_engineering_report_file,
    render_engineering_report,
)
from .knowledge_retrieval import (
    EVIDENCE_NOTICE,
    KnowledgeCorpusError,
    KnowledgeRetrievalInputError,
    build_local_index,
    retrieve_documents,
)
from .retrieval_evaluation import (
    RetrievalEvaluationError,
    run_retrieval_evaluation,
)
from .synthetic_log_parser import (
    SyntheticLogParseError,
    parse_synthetic_log_file,
)
from .validation import SchemaConfigurationError, validate_run_record_file


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="semi-ai",
        description="Local developer tools for the Semiconductor AI Engineering Toolkit.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate one local RunRecord JSON file")
    validate.add_argument("path", type=Path, help="explicit local JSON file path")
    parse = commands.add_parser("parse", help="parse one local synthetic log file")
    parse.add_argument("path", type=Path, help="explicit local UTF-8 synthetic log file path")
    parse.add_argument(
        "--output",
        type=Path,
        help="optional output JSON path; an existing path is never overwritten",
    )
    report = commands.add_parser(
        "report", help="generate a deterministic Markdown report from one RunRecord JSON file"
    )
    report.add_argument("path", type=Path, help="explicit local RunRecord JSON file path")
    report.add_argument(
        "--output",
        type=Path,
        help="optional output Markdown path; an existing path is never overwritten",
    )
    retrieve = commands.add_parser(
        "retrieve",
        help="retrieve ranked evidence from a local synthetic document corpus",
    )
    retrieve.add_argument("query", help="untrusted lexical query text")
    retrieve.add_argument(
        "--corpus",
        type=Path,
        help="optional explicit local .json file or directory of synthetic document chunks",
    )
    retrieve.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="maximum number of ranked evidence results (1-20; default: 3)",
    )
    evaluate_retrieval = commands.add_parser(
        "evaluate-retrieval",
        help="measure local retrieval against synthetic evaluation cases",
    )
    evaluate_retrieval.add_argument(
        "--cases",
        type=str,
        help="optional explicit local JSON evaluation case file",
    )
    evaluate_retrieval.add_argument(
        "--corpus",
        type=str,
        help="optional explicit local .json file or directory of synthetic document chunks",
    )
    return parser


def _print_parse_failure(error: SyntheticLogParseError) -> None:
    print("Parse failed")
    for diagnostic in error.diagnostics:
        print(
            f"- line {diagnostic['line']} [{diagnostic['code']}]: "
            f"{diagnostic['message']}"
        )


def _print_report_failure(error: EngineeringReportInputError | EngineeringReportValidationError) -> None:
    print("Report failed")
    if isinstance(error, EngineeringReportValidationError):
        for diagnostic in error.errors:
            path = diagnostic["path"] or "<root>"
            print(f"- {path}: {diagnostic['message']}")
        return
    print(f"- {error.code}: {error.message}")


def _write_new_text(path: Path, text: str) -> bool:
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except FileExistsError:
        print("Report failed")
        print("- output file already exists; refusing to overwrite")
        return False
    except OSError:
        print("Output failed")
        print("- output file could not be written")
        return False
    return True


def _print_retrieve_failure(error: KnowledgeRetrievalInputError | KnowledgeCorpusError) -> None:
    print("Retrieve failed")
    print(f"- {error.code}: {error.message}")


def _print_evaluation_failure(
    error: RetrievalEvaluationError | KnowledgeRetrievalInputError | KnowledgeCorpusError,
) -> None:
    print("Evaluation failed")
    print(f"- {error.code}: {error.message}")


def main(argv: Sequence[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
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

    if args.command == "parse":
        try:
            record = parse_synthetic_log_file(args.path)
        except SyntheticLogParseError as exc:
            _print_parse_failure(exc)
            return 1
        except SchemaConfigurationError:
            print("Validator configuration error")
            return 2

        if args.output is not None:
            if args.output.exists():
                print("Parse failed")
                print("- output file already exists; refusing to overwrite")
                return 2
            try:
                serialized = json.dumps(
                    record,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                ) + "\n"
                args.output.write_text(serialized, encoding="utf-8")
            except OSError:
                print("Output failed")
                print("- output file could not be written")
                return 2

        print("Parsed and validated RunRecord v0.1")
        return 0

    if args.command == "report":
        if args.output is not None and args.output.exists():
            print("Report failed")
            print("- output file already exists; refusing to overwrite")
            return 2
        try:
            report = generate_engineering_report_file(args.path)
        except (EngineeringReportInputError, EngineeringReportValidationError) as exc:
            _print_report_failure(exc)
            return 1
        except SchemaConfigurationError:
            print("Validator configuration error")
            return 2

        markdown = render_engineering_report(report)
        if args.output is not None:
            return 0 if _write_new_text(args.output, markdown) else 2
        print(markdown, end="")
        return 0

    if args.command == "retrieve":
        try:
            index = build_local_index(args.corpus)
            results = retrieve_documents(index, args.query, args.top_k)
        except (KnowledgeRetrievalInputError, KnowledgeCorpusError) as exc:
            _print_retrieve_failure(exc)
            return 1

        payload = {
            "evidence_notice": EVIDENCE_NOTICE,
            "query": args.query,
            "results": results,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if args.command == "evaluate-retrieval":
        try:
            payload = run_retrieval_evaluation(
                cases_path=args.cases,
                corpus_path=args.corpus,
            )
        except (
            RetrievalEvaluationError,
            KnowledgeRetrievalInputError,
            KnowledgeCorpusError,
        ) as exc:
            _print_evaluation_failure(exc)
            return 1

        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    return 2
