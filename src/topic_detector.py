"""
DepoIndex – LLM-based topic detection module.

Sends each TranscriptSegment to the LLM and assembles the responses
into a list of TopicRecord objects (one per segment at this stage).
Merging is handled by the index_builder module.
"""

from __future__ import annotations

from typing import Callable, Iterator, List, Optional

from pydantic import ValidationError

from src.llm_client import LLMClient
from src.models import (
    EventType,
    LLMTopicResult,
    TopicRecord,
    TranscriptSegment,
)

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert legal transcript analyst specializing in deposition indexing.

Your job is to analyze a passage from a legal deposition transcript and identify
the main topic being discussed.

You MUST respond with a single valid JSON object containing exactly these keys:
  "topic"       – A concise topic label (3–8 words). Use standard legal/deposition
                  categories such as: Employment History, Educational Background,
                  Company Structure, Business Relationships, Financial Transactions,
                  Contracts and Agreements, Email Communications, Meetings,
                  Documents and Records, Key People, Specific Incidents,
                  Legal Proceedings, Personal Background, or similar.
  "description" – One sentence describing what is specifically discussed in this passage.
  "event_type"  – One of: "new_topic", "continuation", "return", "digression",
                  "topic_transition".
                  Use "continuation" if the same topic from the previous context
                  continues here. Use "return" if a topic discussed earlier
                  reappears. Use "digression" for brief unrelated exchanges.
  "confidence"  – A float between 0.0 and 1.0 representing your confidence.

Rules:
- Base your answer ONLY on the supplied transcript text.
- Do NOT invent page numbers, names, or facts.
- If the passage is unclear, set confidence below 0.5 and topic to your best guess.
- Return only the JSON object, no additional text.
"""

USER_TEMPLATE = """\
PREVIOUS CONTEXT (do not index, for continuity only):
{context_before}

TRANSCRIPT SEGMENT TO ANALYZE:
{segment_text}

Previous topic (if any): {prev_topic}
"""


def _build_user_prompt(
    segment: TranscriptSegment, prev_topic: Optional[str]
) -> str:
    return USER_TEMPLATE.format(
        context_before=segment.context_before or "(none)",
        segment_text=segment.raw_text,
        prev_topic=prev_topic or "(none)",
    )


# ---------------------------------------------------------------------------
# Topic detection
# ---------------------------------------------------------------------------


def detect_topics(
    segments: List[TranscriptSegment],
    llm: LLMClient,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[TopicRecord]:
    """
    Call the LLM for each segment and return a preliminary list of TopicRecord
    objects (one per segment, before merging).

    Parameters
    ----------
    segments          : list of TranscriptSegment from the parser
    llm               : configured LLMClient
    progress_callback : optional function(current, total) called after each LLM call

    Returns
    -------
    List[TopicRecord] – one per segment, not yet merged
    """
    records: List[TopicRecord] = []
    prev_topic: Optional[str] = None
    total = len(segments)

    for idx, seg in enumerate(segments):
        user_prompt = _build_user_prompt(seg, prev_topic)

        try:
            raw = llm.chat(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.0,
            )
            result = LLMTopicResult(**raw)
        except (ValidationError, RuntimeError, KeyError, TypeError) as exc:
            # Graceful fallback – mark for review
            result = LLMTopicResult(
                topic="Unclassified",
                description=f"LLM error: {exc}",
                event_type=EventType.NEW_TOPIC,
                confidence=0.0,
            )

        record = TopicRecord(
            topic_id=f"SEG_{seg.segment_id}",  # will be replaced by index_builder
            topic=result.topic,
            description=result.description,
            start_page=seg.transcript_page_start,
            start_line=seg.start_line,
            end_page=seg.transcript_page_end,
            end_line=seg.end_line,
            event_type=result.event_type,
            confidence=result.confidence,
            source_text=seg.raw_text[:600],   # first 600 chars
            segment_ids=[seg.segment_id],
        )

        records.append(record)
        prev_topic = result.topic if result.topic != "Unclassified" else prev_topic

        if progress_callback:
            progress_callback(idx + 1, total)

    return records
