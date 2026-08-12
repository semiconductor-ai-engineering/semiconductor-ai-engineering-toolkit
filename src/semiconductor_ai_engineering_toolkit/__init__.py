"""Public APIs for validation, parsing, reporting, and local retrieval."""

from .knowledge_retrieval import (
    DEFAULT_TOP_K,
    EVIDENCE_NOTICE,
    KnowledgeCorpusError,
    KnowledgeRetrievalError,
    KnowledgeRetrievalInputError,
    LocalKnowledgeIndex,
    MAX_CHUNKS,
    MAX_CORPUS_FILE_BYTES,
    MAX_CORPUS_FILES,
    MAX_DOCUMENT_TEXT_CHARS,
    MAX_EXCERPT_CHARS,
    MAX_QUERY_CHARS,
    MAX_TOP_K,
    build_local_index,
    retrieve_documents,
)

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
    "KnowledgeRetrievalError",
    "KnowledgeRetrievalInputError",
    "KnowledgeCorpusError",
    "LocalKnowledgeIndex",
    "DEFAULT_TOP_K",
    "EVIDENCE_NOTICE",
    "MAX_CHUNKS",
    "MAX_CORPUS_FILE_BYTES",
    "MAX_CORPUS_FILES",
    "MAX_DOCUMENT_TEXT_CHARS",
    "MAX_EXCERPT_CHARS",
    "MAX_QUERY_CHARS",
    "MAX_TOP_K",
    "build_local_index",
    "retrieve_documents",
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
