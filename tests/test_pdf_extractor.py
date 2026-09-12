"""
Tests for the PDF extraction module.

Creates a minimal in-memory PDF using reportlab (same dependency used
by the sample generator) and verifies that pdf_extractor correctly
identifies page structure and parses lines.
"""

from __future__ import annotations

import io
import sys
import os

import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_minimal_pdf(tmp_path) -> str:
    """Create a tiny deposition-style PDF using reportlab."""
    pytest.importorskip("reportlab")
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT

    style = ParagraphStyle("mono", fontName="Courier", fontSize=10, leading=14)

    lines = [
        "3",
        " 1   Q.  What is your name?",
        " 2   A.  John Smith.",
        " 3   Q.  Where do you work?",
        " 4   A.  I work at Acme Corp.",
        " 5   Q.  How long have you been there?",
        " 6   A.  Ten years.",
    ]

    pdf_path = str(tmp_path / "test_depo.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = [Paragraph(ln.replace("&", "&amp;"), style) for ln in lines]
    doc.build(story)
    return pdf_path


def test_extract_pages_returns_list(tmp_path):
    """extract_pages should return a non-empty list for a valid PDF."""
    pytest.importorskip("fitz")
    from src.pdf_extractor import extract_pages

    pdf_path = _make_minimal_pdf(tmp_path)
    pages = extract_pages(pdf_path)
    assert isinstance(pages, list)
    assert len(pages) >= 1


def test_transcript_page_object_structure(tmp_path):
    """Each page should be a TranscriptPage with required fields."""
    pytest.importorskip("fitz")
    from src.pdf_extractor import extract_pages
    from src.models import TranscriptPage

    pdf_path = _make_minimal_pdf(tmp_path)
    pages = extract_pages(pdf_path)

    for page in pages:
        assert isinstance(page, TranscriptPage)
        assert page.pdf_page >= 0
        assert isinstance(page.raw_text, str)
        assert isinstance(page.lines, list)


def test_raw_text_not_empty(tmp_path):
    """Raw text should be non-empty for a text-layer PDF."""
    pytest.importorskip("fitz")
    from src.pdf_extractor import extract_pages

    pdf_path = _make_minimal_pdf(tmp_path)
    pages = extract_pages(pdf_path)
    total_text = "".join(p.raw_text for p in pages)
    assert len(total_text.strip()) > 0


def test_line_parsing_detects_speakers(tmp_path):
    """Parser should detect Q/A speaker labels in standard transcript format."""
    pytest.importorskip("fitz")
    pytest.importorskip("reportlab")
    from src.pdf_extractor import extract_pages

    pdf_path = _make_minimal_pdf(tmp_path)
    pages = extract_pages(pdf_path)

    all_speakers = [
        ln.speaker
        for page in pages
        for ln in page.lines
        if ln.speaker is not None
    ]
    # Our minimal PDF has Q and A lines
    assert len(all_speakers) > 0, "Expected at least one detected speaker"


def test_invalid_path_raises():
    """extract_pages should raise an exception for a non-existent file."""
    pytest.importorskip("fitz")
    from src.pdf_extractor import extract_pages

    with pytest.raises(Exception):
        extract_pages("/does/not/exist.pdf")
