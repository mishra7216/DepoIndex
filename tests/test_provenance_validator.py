"""
Tests for the provenance validation module.

Tests all validation rules with constructed TopicRecord objects –
no PDF or LLM calls needed.
"""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models import EventType, TopicRecord, ValidationFlag, IndexReport
from src.provenance_validator import validate_record, validate_report


def _make_record(**kwargs) -> TopicRecord:
    defaults = dict(
        topic_id="T001",
        topic="Employment History",
        description="Discussion of employment",
        start_page=3,
        start_line=1,
        end_page=5,
        end_line=25,
        event_type=EventType.NEW_TOPIC,
        confidence=0.85,
        source_text="Q. Where do you work? A. Acme Corp.",
    )
    defaults.update(kwargs)
    return TopicRecord(**defaults)


VALID_PAGES = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}


class TestValidateRecord:

    def test_valid_record_no_flags(self):
        record = _make_record()
        result = validate_record(record, VALID_PAGES)
        assert result.flags == []
        assert result.needs_review is False

    def test_empty_topic_flagged(self):
        record = _make_record(topic="")
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.EMPTY_TOPIC in record.flags
        assert record.needs_review is True

    def test_unknown_topic_flagged(self):
        record = _make_record(topic="unknown")
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.EMPTY_TOPIC in record.flags

    def test_reversed_pages_flagged(self):
        record = _make_record(start_page=10, end_page=5)
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.REVERSED_PAGES in record.flags
        assert record.needs_review is True

    def test_equal_pages_not_flagged(self):
        """Same start and end page is valid (single-page topic)."""
        record = _make_record(start_page=3, end_page=3)
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.REVERSED_PAGES not in record.flags

    def test_out_of_range_start_flagged(self):
        record = _make_record(start_page=999)
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.PAGE_OUT_OF_RANGE in record.flags

    def test_out_of_range_end_flagged(self):
        record = _make_record(end_page=999)
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.PAGE_OUT_OF_RANGE in record.flags

    def test_empty_source_text_flagged(self):
        record = _make_record(source_text="")
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.SOURCE_TEXT_MISSING in record.flags

    def test_whitespace_only_source_text_flagged(self):
        record = _make_record(source_text="   ")
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.SOURCE_TEXT_MISSING in record.flags

    def test_low_confidence_flagged(self):
        record = _make_record(confidence=0.2)
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.LOW_CONFIDENCE in record.flags

    def test_borderline_confidence_not_flagged(self):
        record = _make_record(confidence=0.4)
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.LOW_CONFIDENCE not in record.flags

    def test_empty_valid_pages_skips_range_check(self):
        """When no valid pages set is provided, page range checks are skipped."""
        record = _make_record(start_page=999, end_page=1000)
        validate_record(record, set())
        assert ValidationFlag.PAGE_OUT_OF_RANGE not in record.flags

    def test_multiple_flags_accumulate(self):
        record = _make_record(topic="", source_text="", confidence=0.1)
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.EMPTY_TOPIC in record.flags
        assert ValidationFlag.SOURCE_TEXT_MISSING in record.flags
        assert ValidationFlag.LOW_CONFIDENCE in record.flags

    def test_none_pages_skip_range_check(self):
        """Records with None pages should not trigger out-of-range flags."""
        record = _make_record(start_page=None, end_page=None)
        validate_record(record, VALID_PAGES)
        assert ValidationFlag.PAGE_OUT_OF_RANGE not in record.flags
        assert ValidationFlag.REVERSED_PAGES not in record.flags


class TestValidateReport:

    def test_validate_report_marks_flagged_entries(self):
        good = _make_record(topic_id="T001")
        bad = _make_record(topic_id="T002", topic="")
        report = IndexReport(
            source_filename="test.pdf",
            total_pages=10,
            total_segments=5,
            entries=[good, bad],
        )
        validate_report(report)
        assert good.needs_review is False
        assert bad.needs_review is True

    def test_flagged_count_property(self):
        r1 = _make_record(topic_id="T001")
        r2 = _make_record(topic_id="T002", confidence=0.1)
        r3 = _make_record(topic_id="T003", source_text="")
        report = IndexReport(
            source_filename="test.pdf",
            total_pages=5,
            total_segments=3,
            entries=[r1, r2, r3],
        )
        validate_report(report)
        assert report.flagged_count == 2
