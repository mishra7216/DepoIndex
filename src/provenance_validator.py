"""
DepoIndex – Provenance validation module.

Validates each TopicRecord to ensure its metadata is internally consistent
and references real positions in the transcript.
"""

from __future__ import annotations

from typing import List, Set

from src.models import IndexReport, TopicRecord, ValidationFlag


def _flag(record: TopicRecord, flag: ValidationFlag) -> None:
    if flag not in record.flags:
        record.flags.append(flag)
    record.needs_review = True


def validate_record(
    record: TopicRecord,
    valid_transcript_pages: Set[int],
) -> TopicRecord:
    """
    Validate a single TopicRecord against the known set of transcript pages.

    Checks performed
    ----------------
    1. Topic name is not empty or generic "Unclassified".
    2. start_page ≤ end_page (no reversed references).
    3. start_page and end_page are within the extracted page range.
    4. source_text is not empty.
    5. confidence < 0.4 → low-confidence flag.

    Parameters
    ----------
    record               : TopicRecord to validate (mutated in place)
    valid_transcript_pages: set of all transcript page numbers seen in extraction

    Returns
    -------
    The same TopicRecord, now with flags and needs_review set if applicable.
    """
    # 1. Empty / generic topic
    if not record.topic or record.topic.strip().lower() in ("", "unknown", "unclassified"):
        _flag(record, ValidationFlag.EMPTY_TOPIC)

    # 2. Reversed pages
    if record.start_page is not None and record.end_page is not None:
        if record.end_page < record.start_page:
            _flag(record, ValidationFlag.REVERSED_PAGES)

    # 3. Pages exist in the document
    if valid_transcript_pages:
        if record.start_page is not None and record.start_page not in valid_transcript_pages:
            _flag(record, ValidationFlag.PAGE_OUT_OF_RANGE)
        if record.end_page is not None and record.end_page not in valid_transcript_pages:
            _flag(record, ValidationFlag.PAGE_OUT_OF_RANGE)

    # 4. Source text present
    if not record.source_text or not record.source_text.strip():
        _flag(record, ValidationFlag.SOURCE_TEXT_MISSING)

    # 5. Low confidence
    if record.confidence < 0.4:
        _flag(record, ValidationFlag.LOW_CONFIDENCE)

    return record


def validate_report(report: IndexReport) -> IndexReport:
    """
    Validate all entries in an IndexReport.

    Collects the set of valid transcript page numbers from the report metadata
    and validates each entry.

    Parameters
    ----------
    report : IndexReport to validate (mutated in place)

    Returns
    -------
    The same IndexReport with validation flags applied.
    """
    # Collect valid page numbers from all entries
    all_pages: Set[int] = set()
    for entry in report.entries:
        if entry.start_page is not None:
            all_pages.add(entry.start_page)
        if entry.end_page is not None:
            all_pages.add(entry.end_page)

    for entry in report.entries:
        validate_record(entry, all_pages)

    return report
