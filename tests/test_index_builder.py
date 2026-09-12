"""
Tests for the index_builder module.

Uses mock TopicRecord objects (no LLM calls) to verify:
  - Consecutive same-topic segments are merged
  - Return events are detected and linked
  - Sequential topic IDs are assigned
  - New topics start fresh records
"""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models import EventType, TopicRecord, TranscriptPage, TranscriptLine
from src.index_builder import build_index, _topics_match, _normalize_topic


def _make_record(
    topic_id: str,
    topic: str,
    event_type: EventType,
    start_page: int,
    end_page: int,
    confidence: float = 0.8,
) -> TopicRecord:
    return TopicRecord(
        topic_id=topic_id,
        topic=topic,
        description=f"Discussion about {topic}",
        start_page=start_page,
        start_line=1,
        end_page=end_page,
        end_line=25,
        event_type=event_type,
        confidence=confidence,
        source_text=f"Excerpt about {topic}",
        segment_ids=[topic_id],
    )


def _make_page(n: int) -> TranscriptPage:
    return TranscriptPage(
        pdf_page=n - 1,
        transcript_page=n,
        lines=[TranscriptLine(line_number=1, text="Q. Test.")],
        raw_text="Q. Test.",
    )


PAGES = [_make_page(i) for i in range(1, 21)]


class TestTopicsMatch:
    def test_exact_match(self):
        assert _topics_match("Employment History", "Employment History")

    def test_case_insensitive(self):
        assert _topics_match("Employment History", "employment history")

    def test_substring_match(self):
        assert _topics_match("Financial Transactions", "Financial")

    def test_no_match(self):
        assert not _topics_match("Employment History", "Financial Transactions")

    def test_short_strings_no_partial(self):
        """Short strings should not partially match."""
        assert not _topics_match("Q&A", "Financial Transactions")


class TestBuildIndex:

    def test_empty_records_returns_empty_report(self):
        report = build_index([], PAGES, "test.pdf")
        assert report.entries == []
        assert report.total_segments == 0

    def test_single_record_gets_id(self):
        records = [_make_record("S1", "Employment History", EventType.NEW_TOPIC, 3, 5)]
        report = build_index(records, PAGES, "test.pdf")
        assert len(report.entries) == 1
        assert report.entries[0].topic_id == "T001"

    def test_consecutive_same_topic_merged(self):
        """Two consecutive segments with same topic should become one record."""
        records = [
            _make_record("S1", "Employment History", EventType.NEW_TOPIC, 3, 4),
            _make_record("S2", "Employment History", EventType.CONTINUATION, 4, 5),
        ]
        report = build_index(records, PAGES, "test.pdf")
        # Should be merged into 1 record
        assert len(report.entries) == 1
        assert report.entries[0].end_page == 5

    def test_different_topics_produce_separate_records(self):
        records = [
            _make_record("S1", "Employment History", EventType.NEW_TOPIC, 3, 5),
            _make_record("S2", "Financial Transactions", EventType.NEW_TOPIC, 6, 8),
        ]
        report = build_index(records, PAGES, "test.pdf")
        assert len(report.entries) == 2
        assert report.entries[0].topic_id == "T001"
        assert report.entries[1].topic_id == "T002"

    def test_return_topic_flagged(self):
        """A topic that reappears after closure should be flagged as RETURN."""
        records = [
            _make_record("S1", "Employment History", EventType.NEW_TOPIC, 3, 5),
            _make_record("S2", "Financial Transactions", EventType.NEW_TOPIC, 6, 8),
            _make_record("S3", "Employment History", EventType.NEW_TOPIC, 9, 11),
        ]
        report = build_index(records, PAGES, "test.pdf")
        assert len(report.entries) == 3
        return_entry = report.entries[2]
        assert return_entry.event_type == EventType.RETURN

    def test_return_topic_links_original(self):
        """The returning topic should reference the original topic_id."""
        records = [
            _make_record("S1", "Employment History", EventType.NEW_TOPIC, 3, 5),
            _make_record("S2", "Financial Transactions", EventType.NEW_TOPIC, 6, 8),
            _make_record("S3", "Employment History", EventType.NEW_TOPIC, 9, 11),
        ]
        report = build_index(records, PAGES, "test.pdf")
        return_entry = report.entries[2]
        # Should reference T001 (the original Employment History)
        assert "T001" in return_entry.related_topic_ids

    def test_sequential_ids_assigned(self):
        records = [
            _make_record("S1", "Topic A", EventType.NEW_TOPIC, 1, 2),
            _make_record("S2", "Topic B", EventType.NEW_TOPIC, 3, 4),
            _make_record("S3", "Topic C", EventType.NEW_TOPIC, 5, 6),
        ]
        report = build_index(records, PAGES, "test.pdf")
        ids = [e.topic_id for e in report.entries]
        assert ids == ["T001", "T002", "T003"]

    def test_confidence_averaged_on_merge(self):
        records = [
            _make_record("S1", "Employment History", EventType.NEW_TOPIC, 3, 4, confidence=0.9),
            _make_record("S2", "Employment History", EventType.CONTINUATION, 4, 5, confidence=0.7),
        ]
        report = build_index(records, PAGES, "test.pdf")
        assert len(report.entries) == 1
        # Averaged: (0.9 + 0.7) / 2 = 0.8
        assert abs(report.entries[0].confidence - 0.8) < 0.01

    def test_source_filename_preserved(self):
        report = build_index([], PAGES, "my_deposition.pdf")
        assert report.source_filename == "my_deposition.pdf"

    def test_total_pages_matches_pages_input(self):
        report = build_index([], PAGES, "test.pdf")
        assert report.total_pages == len(PAGES)
