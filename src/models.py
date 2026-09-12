"""
DepoIndex – Pydantic data models for the entire pipeline.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class EventType(str, Enum):
    NEW_TOPIC = "new_topic"
    CONTINUATION = "continuation"
    RETURN = "return"
    DIGRESSION = "digression"
    TOPIC_TRANSITION = "topic_transition"


class ValidationFlag(str, Enum):
    EMPTY_TOPIC = "empty_topic"
    PAGE_OUT_OF_RANGE = "page_out_of_range"
    REVERSED_PAGES = "reversed_pages"
    SOURCE_TEXT_MISSING = "source_text_missing"
    LOW_CONFIDENCE = "low_confidence"


# ---------------------------------------------------------------------------
# Raw extraction layer
# ---------------------------------------------------------------------------


class TranscriptLine(BaseModel):
    """A single numbered line within a transcript page."""

    line_number: int
    speaker: Optional[str] = None   # 'Q' | 'A' | 'ATTY' | 'WITNESS' | None
    text: str


class TranscriptPage(BaseModel):
    """All text from one PDF page, with inferred transcript page number."""

    pdf_page: int                        # 0-indexed PDF page
    transcript_page: Optional[int] = None  # printed transcript page number
    lines: List[TranscriptLine] = Field(default_factory=list)
    raw_text: str = ""


# ---------------------------------------------------------------------------
# Parsing layer
# ---------------------------------------------------------------------------


class TranscriptSegment(BaseModel):
    """A window of consecutive lines used for LLM analysis."""

    segment_id: str
    pdf_page_start: int
    pdf_page_end: int
    transcript_page_start: Optional[int] = None
    transcript_page_end: Optional[int] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    raw_text: str
    context_before: str = ""   # a few lines before for continuity


# ---------------------------------------------------------------------------
# LLM layer
# ---------------------------------------------------------------------------


class LLMTopicResult(BaseModel):
    """Structured output returned by the LLM for a single segment."""

    topic: str
    description: str
    event_type: EventType = EventType.NEW_TOPIC
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

    @field_validator("topic")
    @classmethod
    def topic_not_empty(cls, v: str) -> str:
        return v.strip() if v else "Unknown"


# ---------------------------------------------------------------------------
# Validated index record
# ---------------------------------------------------------------------------


class TopicRecord(BaseModel):
    """One entry in the final topic index."""

    topic_id: str                         # e.g. "T001"
    topic: str
    description: str
    start_page: Optional[int] = None      # transcript page number
    start_line: Optional[int] = None
    end_page: Optional[int] = None
    end_line: Optional[int] = None
    event_type: EventType = EventType.NEW_TOPIC
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    source_text: str = ""
    flags: List[ValidationFlag] = Field(default_factory=list)
    needs_review: bool = False
    related_topic_ids: List[str] = Field(default_factory=list)

    # internal: which segments contributed
    segment_ids: List[str] = Field(default_factory=list, exclude=True)

    def to_export_dict(self) -> dict:
        return {
            "topic_id": self.topic_id,
            "topic": self.topic,
            "description": self.description,
            "start_page": self.start_page,
            "start_line": self.start_line,
            "end_page": self.end_page,
            "end_line": self.end_line,
            "event_type": self.event_type.value,
            "confidence": round(self.confidence, 3),
            "needs_review": self.needs_review,
            "flags": [f.value for f in self.flags],
            "source_text": self.source_text,
            "related_topic_ids": self.related_topic_ids,
        }


class IndexReport(BaseModel):
    """The complete topic index for one deposition."""

    source_filename: str
    total_pages: int
    total_segments: int
    entries: List[TopicRecord] = Field(default_factory=list)

    @property
    def flagged_count(self) -> int:
        return sum(1 for e in self.entries if e.needs_review)
