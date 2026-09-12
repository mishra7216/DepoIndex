# DepoIndex ⚖️

**AI-Powered Deposition Topic Index**

DepoIndex automatically analyzes a legal deposition transcript PDF and creates a structured, searchable topic index with accurate page and line references — powered by GPT-4o-mini.

---

## Features

- 📄 **PDF Extraction** — Page-by-page text extraction with PyMuPDF, preserving page numbers, line numbers, and speaker labels (Q/A)
- 🤖 **AI Topic Detection** — GPT-4o-mini classifies each transcript segment by topic with structured JSON output
- 🔗 **Topic Continuity** — Detects when topics continue across segments, return after a digression, or transition
- ✅ **Provenance Validation** — Every index entry is validated: page range checks, source text verification, confidence scoring
- 🔍 **Searchable Index** — Filter by keyword, event type, or review status
- 📤 **Export** — Download results as JSON or CSV

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Sample Deposition PDF (Optional)

```bash
python sample_data/generate_sample.py
```

This creates `sample_data/sample_deposition.pdf` — a realistic synthetic 20-page deposition for demo/testing.

### 3. Run the Application

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**.

### 4. Use the App

1. Enter your **OpenAI API key** in the sidebar (sk-...).
2. Upload a deposition PDF in the **Upload & Process** tab.
3. Click **Run DepoIndex Pipeline**.
4. Explore results in the **Topic Index** tab.
5. Download the index as JSON or CSV from the **Export** tab.

---

## Run Tests

```bash
pytest tests/ -v
```

Tests cover:
- PDF extraction structure and speaker detection
- Provenance validator (all validation rules and edge cases)
- Index builder (merging, return detection, ID assignment)
- Topic detector (mock LLM, error fallback, progress callback)

---

## Project Structure

```
docu3cproject/
├── app.py                          # Streamlit UI
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── models.py                   # Pydantic data models
│   ├── pdf_extractor.py            # PyMuPDF text extraction
│   ├── transcript_parser.py        # Segmentation
│   ├── llm_client.py               # OpenAI API wrapper
│   ├── topic_detector.py           # LLM topic detection
│   ├── provenance_validator.py     # Validation checks
│   └── index_builder.py            # Topic merging & index assembly
├── sample_data/
│   └── generate_sample.py          # Synthetic deposition PDF generator
└── tests/
    ├── test_pdf_extractor.py
    ├── test_provenance_validator.py
    ├── test_index_builder.py
    └── test_topic_detector.py
```

---

## Sample Output

```json
{
  "topic_id": "T004",
  "topic": "Financial Transactions",
  "description": "Discussion of royalty payments owed by Vertex Solutions",
  "start_page": 7,
  "start_line": 1,
  "end_page": 8,
  "end_line": 14,
  "event_type": "new_topic",
  "confidence": 0.93,
  "needs_review": false,
  "flags": [],
  "source_text": "[Transcript Page 7]\n   1  Q.  Did Vertex Solutions make that first royalty payment?\n   2  A.  No. They did not...",
  "related_topic_ids": []
}
```

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Main language |
| PyMuPDF (fitz) | PDF text extraction |
| OpenAI API (gpt-4o-mini) | Topic detection |
| Pydantic v2 | Structured data validation |
| Streamlit | User interface |
| Pandas | Tabular display & CSV export |
| ReportLab | Sample PDF generation |
| pytest | Testing |

---

## Limitations

- OCR not included — scanned-only PDFs without a text layer will not extract correctly.
- Some transcripts use non-standard formatting that may reduce line number accuracy.
- Topic names may vary slightly across runs; index building uses fuzzy topic matching.
- The generated index is an AI-assisted tool and should be reviewed by a legal professional before use in legal proceedings.

---

## Future Enhancements

- OCR fallback via pytesseract or AWS Textract
- Semantic embeddings for improved topic clustering
- PDF annotation / highlight export
- Multi-deposition database
- Human-in-the-loop topic correction UI
- Ground-truth evaluation against manually prepared indexes
