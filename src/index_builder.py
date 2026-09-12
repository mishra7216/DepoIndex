"""
DepoIndex – Index builder module.

Takes the raw per-segment TopicRecord list from topic_detector and:
  1. Merges consecutive segments that share the same topic (continuation).
  2. Detects "return" events where a previously-closed topic reappears.
  3. Assigns sequential topic IDs (T001, T002, …).
  4. Constructs the final IndexReport.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from src.models import EventType, IndexReport, TopicRecord, TranscriptPage

# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------


def _normalize_topic(topic: str) -> str:
    """Return a canonical lowercase form for topic comparison."""
    return topic.strip().lower()


def _topics_match(a: str, b: str) -> bool:
    """Return True if two topic labels are considered the same topic."""
    na, nb = _normalize_topic(a), _normalize_topic(b)
    if na == nb:
        return True
    # Allow partial overlap (one is a substring of the other)
    if len(na) > 3 and len(nb) > 3:
        if na in nb or nb in na:
            return True
    return False


# ---------------------------------------------------------------------------
# Merging logic
# ---------------------------------------------------------------------------


def _merge_into(base: TopicRecord, addition: TopicRecord) -> TopicRecord:
    """Extend base record to cover addition's page/line range."""
    # Extend end position
    if addition.end_page is not None:
        if base.end_page is None or addition.end_page > base.end_page:
            base.end_page = addition.end_page
            base.end_line = addition.end_line

    # Average confidence
    base.confidence = round((base.confidence + addition.confidence) / 2, 3)

    # Append a snippet to source text
    if addition.source_text and len(base.source_text) < 800:
        base.source_text += "\n…\n" + addition.source_text[:200]

    # Track segment ids
    base.segment_ids.extend(addition.segment_ids)

    # Use the most informative description (prefer longer one)
    if len(addition.description) > len(base.description):
        base.description = addition.description

    return base


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------


def build_index(
    raw_records: List[TopicRecord],
    pages: List[TranscriptPage],
    source_filename: str,
) -> IndexReport:
    """
    Merge raw per-segment records into a clean topic index.

    Parameters
    ----------
    raw_records     : one TopicRecord per segment (from topic_detector)
    pages           : extracted pages (for metadata)
    source_filename : name of the uploaded PDF

    Returns
    -------
    IndexReport with merged, ID-assigned entries.
    """
    if not raw_records:
        return IndexReport(
            source_filename=source_filename,
            total_pages=len(pages),
            total_segments=0,
            entries=[],
        )

    # Track topics that have been closed (for "return" detection)
    closed_topics: Dict[str, str] = {}   # normalized_topic -> topic_id

    merged: List[TopicRecord] = []
    current: Optional[TopicRecord] = None

    for record in raw_records:
        if current is None:
            current = record.model_copy(deep=True)
            continue

        is_continuation = (
            record.event_type == EventType.CONTINUATION
            or _topics_match(current.topic, record.topic)
        )

        if is_continuation and record.event_type not in (
            EventType.NEW_TOPIC, EventType.TOPIC_TRANSITION
        ):
            # Merge into current record
            _merge_into(current, record)
        else:
            # Close current record
            norm = _normalize_topic(current.topic)
            closed_topics[norm] = current.topic_id   # placeholder id
            merged.append(current)

            # Check if this is a "return" to a previously closed topic
            new_norm = _normalize_topic(record.topic)
            is_return = any(_topics_match(record.topic, ct) for ct in closed_topics)
            if is_return:
                record = record.model_copy(deep=True)
                record.event_type = EventType.RETURN
                # Link to the original occurrence
                for norm_key, old_id in closed_topics.items():
                    if _topics_match(record.topic, norm_key):
                        if old_id not in record.related_topic_ids:
                            record.related_topic_ids.append(old_id)
                        break

            current = record.model_copy(deep=True)

    if current is not None:
        merged.append(current)

    # Assign sequential IDs and update related_topic_ids
    id_map: Dict[str, str] = {}  # old_placeholder -> new Txxx
    for idx, rec in enumerate(merged, start=1):
        new_id = f"T{idx:03d}"
        id_map[rec.topic_id] = new_id
        rec.topic_id = new_id

    # Fix related_topic_ids to use new IDs
    for rec in merged:
        rec.related_topic_ids = [
            id_map.get(old, old) for old in rec.related_topic_ids
        ]

    return IndexReport(
        source_filename=source_filename,
        total_pages=len(pages),
        total_segments=len(raw_records),
        entries=merged,
    )
