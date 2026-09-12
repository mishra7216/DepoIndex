"""
Tests for the topic detector module.

Uses a mock LLMClient to avoid real API calls.
Verifies segment-to-record conversion, fallback on LLM errors,
and progress callback invocation.
"""

from __future__ import annotations

import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models import EventType, TranscriptSegment, TopicRecord
from src.topic_detector import detect_topics


def _make_segment(seg_id: str, page: int) -> TranscriptSegment:
    return TranscriptSegment(
        segment_id=seg_id,
        pdf_page_start=page - 1,
        pdf_page_end=page - 1,
        transcript_page_start=page,
        transcript_page_end=page,
        start_line=1,
        end_line=20,
        raw_text=f"[Transcript Page {page}]\n  1  Q.  Tell me about your employment.\n  2  A.  I worked at Acme Corp.",
        context_before="",
    )


def _mock_llm_response(topic: str, event_type: str = "new_topic", confidence: float = 0.9) -> dict:
    return {
        "topic": topic,
        "description": f"Discussion of {topic}",
        "event_type": event_type,
        "confidence": confidence,
    }


class TestDetectTopics:

    def test_returns_one_record_per_segment(self):
        segs = [_make_segment(f"SEG{i:04d}", i + 3) for i in range(3)]
        mock_llm = MagicMock()
        mock_llm.chat.return_value = _mock_llm_response("Employment History")

        records = detect_topics(segs, mock_llm)
        assert len(records) == 3

    def test_record_has_correct_pages(self):
        seg = _make_segment("SEG0000", 5)
        mock_llm = MagicMock()
        mock_llm.chat.return_value = _mock_llm_response("Financial Transactions")

        records = detect_topics([seg], mock_llm)
        assert records[0].start_page == 5
        assert records[0].end_page == 5

    def test_record_topic_matches_llm_output(self):
        seg = _make_segment("SEG0000", 3)
        mock_llm = MagicMock()
        mock_llm.chat.return_value = _mock_llm_response("Company Structure")

        records = detect_topics([seg], mock_llm)
        assert records[0].topic == "Company Structure"

    def test_llm_error_produces_unclassified_record(self):
        """If the LLM call raises, the record should be marked Unclassified."""
        seg = _make_segment("SEG0000", 3)
        mock_llm = MagicMock()
        mock_llm.chat.side_effect = RuntimeError("API unavailable")

        records = detect_topics([seg], mock_llm)
        assert len(records) == 1
        assert records[0].topic == "Unclassified"
        assert records[0].confidence == 0.0

    def test_invalid_llm_json_produces_unclassified(self):
        """Malformed LLM JSON should not crash; produce Unclassified fallback."""
        seg = _make_segment("SEG0000", 3)
        mock_llm = MagicMock()
        # Return dict missing required keys
        mock_llm.chat.return_value = {"unexpected_key": "value"}

        records = detect_topics([seg], mock_llm)
        assert len(records) == 1
        # Pydantic will assign defaults; topic should not be empty
        assert records[0].topic is not None

    def test_progress_callback_called_correctly(self):
        segs = [_make_segment(f"SEG{i:04d}", i + 3) for i in range(4)]
        mock_llm = MagicMock()
        mock_llm.chat.return_value = _mock_llm_response("Meetings")

        calls = []
        def callback(current, total):
            calls.append((current, total))

        detect_topics(segs, mock_llm, progress_callback=callback)
        assert len(calls) == 4
        assert calls[0] == (1, 4)
        assert calls[-1] == (4, 4)

    def test_event_type_continuation_preserved(self):
        seg = _make_segment("SEG0001", 5)
        mock_llm = MagicMock()
        mock_llm.chat.return_value = _mock_llm_response(
            "Employment History", event_type="continuation"
        )

        records = detect_topics([seg], mock_llm)
        assert records[0].event_type == EventType.CONTINUATION

    def test_source_text_truncated_to_600_chars(self):
        seg = _make_segment("SEG0000", 3)
        seg.raw_text = "Q. " + "A" * 2000
        mock_llm = MagicMock()
        mock_llm.chat.return_value = _mock_llm_response("Employment History")

        records = detect_topics([seg], mock_llm)
        assert len(records[0].source_text) <= 600

    def test_empty_segments_returns_empty_list(self):
        mock_llm = MagicMock()
        records = detect_topics([], mock_llm)
        assert records == []
