"""
DepoIndex – Transcript parser and segmentation module.

Splits the list of TranscriptPage objects into overlapping TranscriptSegment
windows that are small enough to send to an LLM while still preserving
enough context for accurate topic detection.
"""

from __future__ import annotations

from typing import List, Optional

from src.models import TranscriptPage, TranscriptSegment

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LINES_PER_SEGMENT = 20   # target lines per segment (approximate)
OVERLAP_LINES = 4        # lines of context carried from previous segment


def _page_display(page: TranscriptPage) -> str:
    """Human-readable header for a page in a segment block."""
    tp = page.transcript_page
    pp = page.pdf_page + 1  # 1-indexed for display
    if tp:
        return f"[Transcript Page {tp}]"
    return f"[PDF Page {pp}]"


def _transcript_page_or_pdf(page: TranscriptPage) -> Optional[int]:
    return page.transcript_page if page.transcript_page else page.pdf_page + 1


def build_segments(
    pages: List[TranscriptPage],
    lines_per_segment: int = LINES_PER_SEGMENT,
    overlap: int = OVERLAP_LINES,
) -> List[TranscriptSegment]:
    """
    Convert a list of TranscriptPage objects into overlapping segments.

    Strategy
    --------
    - Flatten all lines across all pages into a single ordered list, tagging
      each with its source page.
    - Slide a window of `lines_per_segment` lines, advancing by
      (lines_per_segment - overlap) each step.
    - Each window becomes one TranscriptSegment.

    Parameters
    ----------
    pages            : extracted transcript pages
    lines_per_segment: approximate number of lines per segment
    overlap          : lines of overlap between consecutive segments

    Returns
    -------
    List[TranscriptSegment]
    """
    # Flatten lines across all pages
    flat: list[tuple[TranscriptPage, object]] = []  # (page, TranscriptLine)
    for page in pages:
        for line in page.lines:
            flat.append((page, line))

    if not flat:
        return []

    segments: List[TranscriptSegment] = []
    step = max(1, lines_per_segment - overlap)
    seg_idx = 0

    i = 0
    while i < len(flat):
        window = flat[i : i + lines_per_segment]
        prev_window = flat[max(0, i - overlap) : i]

        # Context before this segment
        context_parts: list[str] = []
        for _pg, ln in prev_window:
            speaker_prefix = f"{ln.speaker}: " if ln.speaker else ""  # type: ignore
            context_parts.append(
                f"  {ln.line_number:>3}  {speaker_prefix}{ln.text}"  # type: ignore
            )
        context_before = "\n".join(context_parts)

        # Build segment text
        text_parts: list[str] = []
        current_page_label: Optional[str] = None
        start_page = window[0][0]
        end_page = window[-1][0]

        for pg, ln in window:
            page_label = _page_display(pg)
            if page_label != current_page_label:
                text_parts.append(page_label)
                current_page_label = page_label
            speaker_prefix = f"{ln.speaker}: " if ln.speaker else ""  # type: ignore
            text_parts.append(
                f"  {ln.line_number:>3}  {speaker_prefix}{ln.text}"  # type: ignore
            )

        raw_text = "\n".join(text_parts)

        # Start / end line numbers
        start_ln = window[0][1].line_number if window else None   # type: ignore
        end_ln = window[-1][1].line_number if window else None     # type: ignore

        seg_id = f"SEG{seg_idx:04d}"
        segments.append(
            TranscriptSegment(
                segment_id=seg_id,
                pdf_page_start=start_page.pdf_page,
                pdf_page_end=end_page.pdf_page,
                transcript_page_start=_transcript_page_or_pdf(start_page),
                transcript_page_end=_transcript_page_or_pdf(end_page),
                start_line=start_ln,
                end_line=end_ln,
                raw_text=raw_text,
                context_before=context_before,
            )
        )

        seg_idx += 1
        i += step

    return segments
