"""
DepoIndex – PDF text extraction module.

Uses PyMuPDF (fitz) to extract text page-by-page, preserving:
  - PDF page number (0-indexed)
  - Inferred transcript page number (printed in the header)
  - Line numbers (1–25, printed on the left margin in standard transcripts)
  - Speaker labels (Q / A)
  - Raw text per line
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

import fitz  # PyMuPDF

from src.models import TranscriptLine, TranscriptPage

# ---------------------------------------------------------------------------
# Regex patterns for standard US deposition transcript formatting
# ---------------------------------------------------------------------------

# Transcript page header: typically "  5" or "Page 5" or just "5" at the top
_PAGE_HEADER_RE = re.compile(
    r"^\s*(?:page\s+)?(\d{1,4})\s*$", re.IGNORECASE
)

# Line entries: "  1   Q.  Some text" or "  1   A.  Some text"
#              or just "  1   Some continuation text"
_LINE_RE = re.compile(
    r"^\s*(\d{1,2})\s+([QA]\.?|ATTORNEY:|WITNESS:|BY\s+\w+:)?\s*(.*?)\s*$",
    re.IGNORECASE,
)

_SPEAKER_RE = re.compile(r"^([QA]\.?|ATTORNEY:|WITNESS:)", re.IGNORECASE)


def _infer_transcript_page(text: str) -> Optional[int]:
    """Try to find a printed transcript page number in the page text."""
    for line in text.splitlines()[:5]:  # usually in first few lines
        m = _PAGE_HEADER_RE.match(line)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 9999:
                return val
    return None


def _parse_lines(raw_text: str) -> List[TranscriptLine]:
    """
    Parse the raw text of one PDF page into structured TranscriptLine objects.
    Falls back to splitting by newline with sequential numbering if no
    transcript line numbers are found.
    """
    parsed: List[TranscriptLine] = []
    raw_lines = raw_text.splitlines()

    has_line_numbers = any(
        _LINE_RE.match(ln) and _LINE_RE.match(ln).group(1)  # type: ignore
        for ln in raw_lines
    )

    if has_line_numbers:
        for raw_line in raw_lines:
            m = _LINE_RE.match(raw_line)
            if m:
                line_no = int(m.group(1))
                speaker_raw = (m.group(2) or "").strip().rstrip(".")
                speaker = speaker_raw.upper() if speaker_raw else None
                text = (m.group(3) or "").strip()
                if text:
                    parsed.append(
                        TranscriptLine(
                            line_number=line_no, speaker=speaker, text=text
                        )
                    )
    else:
        # Fallback: number lines sequentially, detect speakers inline
        for idx, raw_line in enumerate(raw_lines, start=1):
            text = raw_line.strip()
            if not text:
                continue
            speaker: Optional[str] = None
            sm = _SPEAKER_RE.match(text)
            if sm:
                speaker = sm.group(1).rstrip(".").upper()
                text = text[sm.end():].strip()
            parsed.append(
                TranscriptLine(line_number=idx, speaker=speaker, text=text)
            )

    return parsed


def extract_pages(pdf_path: str | Path) -> List[TranscriptPage]:
    """
    Open a PDF and return one TranscriptPage per PDF page.

    Parameters
    ----------
    pdf_path: path to the PDF file

    Returns
    -------
    List[TranscriptPage] — one element per PDF page, in order.
    """
    pdf_path = Path(pdf_path)
    doc = fitz.open(str(pdf_path))
    pages: List[TranscriptPage] = []

    for pdf_idx in range(len(doc)):
        page = doc[pdf_idx]
        raw_text = page.get_text("text")  # plain text extraction

        transcript_page_num = _infer_transcript_page(raw_text)
        lines = _parse_lines(raw_text)

        pages.append(
            TranscriptPage(
                pdf_page=pdf_idx,
                transcript_page=transcript_page_num,
                lines=lines,
                raw_text=raw_text,
            )
        )

    doc.close()
    return pages
