# DepoIndex ⚖️
**AI-Powered Deposition Topic Index**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://depoindex-hsryuvqghk9sdxzukpaai8.streamlit.app/)
[![Tests](https://img.shields.io/badge/pytest-45%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](requirements.txt)
[![GitHub](https://img.shields.io/badge/GitHub-mishra7216%2FDepoIndex-black.svg)](https://github.com/mishra7216/DepoIndex)

> 🚀 **Live Deployed Application:** **[https://depoindex-hsryuvqghk9sdxzukpaai8.streamlit.app/](https://depoindex-hsryuvqghk9sdxzukpaai8.streamlit.app/)**  
> *Test the live application in your browser right now — click "Load Sample Deposition PDF" and run instant indexing without requiring any local installation or API key.*

DepoIndex is an AI-powered legal technology system that automatically analyzes legal deposition transcripts and constructs a structured, searchable, and verifiable topic index with exact page and line references.

---

## 📑 Table of Contents
- [Live Demo](#-live-demo)
- [Key Features](#-key-features)
- [System Requirements](#-system-requirements)
- [Quick Start & Execution](#-quick-start--execution)
- [Running Without an API Key (Offline Demo)](#-running-without-an-api-key-offline-demo)
- [Running Automated Tests](#-running-automated-tests)
- [Project Architecture & Directory Structure](#-project-architecture--directory-structure)
- [Technical Documentation & Reports](#-technical-documentation--reports)
- [Sample Output](#-sample-output)
- [Limitations & Future Enhancements](#-limitations--future-enhancements)

---

## 🌐 Live Demo

The application is deployed on Streamlit Community Cloud and available at:
👉 **[https://depoindex-hsryuvqghk9sdxzukpaai8.streamlit.app/](https://depoindex-hsryuvqghk9sdxzukpaai8.streamlit.app/)**

1. Open the URL in any browser.
2. Click **"📑 Load Sample Deposition PDF"** to load the pre-configured 15-page legal transcript.
3. Click **"🚀 Run DepoIndex Pipeline (Offline Demo)"** to index topics in seconds.
4. Or optionally enter your OpenAI API key in the sidebar for live GPT-4o-mini topic analysis.

---

## 🌟 Key Features

- 📄 **PDF Text & Layout Extraction** — High-speed extraction via PyMuPDF (`fitz`), preserving margin line numbers (1–25), header page numbers, and speaker labels (`Q.`, `A.`, objections).
- 🤖 **AI Topic Detection** — Uses `gpt-4o-mini` with strict JSON mode to identify topics, transition events (`new_topic`, `continuation`, `return`, `digression`), and calibrated confidence scores.
- 🔗 **Topic Continuity & Return Detection** — Merges adjacent segments discussing the same topic and detects when prior topics return, cross-linking them to earlier topic IDs.
- ✅ **Mathematical Provenance Validation** — Rigorous audit gate verifying that coordinates exist, spans are non-negative (`end_page >= start_page`), and text appears verbatim.
- 💻 **Modern Streamlit Dashboard** — Interactive table, real-time keyword search, event type filtering, provenance inspection drawer, and CSV/JSON export.
- ⚡ **Offline Demonstration Mode** — Includes an embedded heuristic engine allowing full local testing without an active OpenAI API key.

---

## 💻 System Requirements

- **Operating System**: macOS, Linux, or Windows
- **Python Version**: Python 3.9, 3.10, 3.11, or 3.12
- **Package Manager**: `pip` or `uv`
- **Optional**: OpenAI API Key (`sk-...`) for live LLM inference (not required in Offline Demo mode)

---

## 🚀 Quick Start & Execution

### 1. Clone the Repository
```bash
git clone https://github.com/mishra7216/DepoIndex.git
cd DepoIndex
```

### 2. Set Up a Virtual Environment & Install Dependencies
Using standard Python `venv`:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
*(Or if you use `uv`: `uv venv && uv pip install -r requirements.txt`)*

### 3. Generate the Sample Deposition PDF (Included)
```bash
python sample_data/generate_sample.py
```
This generates `sample_data/sample_deposition.pdf` — a realistic 15-page legal court reporter transcript with 25-line margins, multi-page continuations, and topic returns.

### 4. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
The application will open in your browser at **`http://localhost:8501`**.

---

## 🔌 Running Without an API Key (Offline Demo)

DepoIndex is designed to be fully testable without requiring an OpenAI API key:
1. Open the app at `http://localhost:8501`.
2. Click **"📑 Load Sample Deposition PDF"**.
3. In the sidebar, select **"Offline Demo (Heuristic Classifier)"** (or leave the API key blank).
4. Click **"🚀 Run DepoIndex Pipeline (Offline Demo)"**.
5. The pipeline will extract, segment, classify, validate, and index all topics locally in ~2 seconds!

---

## 🧪 Running Automated Tests

DepoIndex includes a comprehensive test suite of **45 automated tests** covering all pipeline layers:

```bash
pytest tests/ -v
```

### Test Coverage Areas:
- `tests/test_pdf_extractor.py`: PDF loading, 25-line parsing, speaker regex, and transcript page detection.
- `tests/test_index_builder.py`: Adjacent segment merging, topic ID sequencing, topic matching, and return-topic linking.
- `tests/test_provenance_validator.py`: Page bounds, reversed pages, out-of-range checks, source text presence, low-confidence flags.
- `tests/test_topic_detector.py`: Segment topic classification, prompt generation, error fallbacks, and callbacks.

---

## 📁 Project Architecture & Directory Structure

```
DepoIndex/
├── app.py                          # Streamlit UI & Interactive Dashboard
├── requirements.txt                # Pinned Dependency Specification
├── conftest.py                     # PyTest Configuration & Path Setup
├── .gitignore                      # Git Exclusions
├── README.md                       # Project Setup & Overview
├── llm_usage.md                    # Detailed LLM Prompts & AI Engineering Documentation
├── VALIDATION_REPORT.md            # 22-Entry Audit, 3-Run Stability & Failure Case Report
├── PROJECT_REPORT.md               # Technical Architecture & File Breakdown Report
├── src/                            # Core Pipeline Source Code
│   ├── __init__.py
│   ├── models.py                   # Pydantic v2 Schemas & Data Types
│   ├── pdf_extractor.py            # PyMuPDF PDF Text & Margin Line Extraction
│   ├── transcript_parser.py        # Line Flattening & Windowed Segmentation
│   ├── llm_client.py               # OpenAI Wrapper with Built-in Offline Fallback
│   ├── topic_detector.py           # LLM Prompt Orchestrator & Context Chaining
│   ├── index_builder.py            # Boundary Merge & Topic Return Linking
│   └── provenance_validator.py     # Provenance Coordinate & Verification Gate
├── sample_data/
│   ├── generate_sample.py          # Synthetic 15-Page Deposition PDF Generator
│   └── sample_deposition.pdf       # Generated Legal Deposition PDF
└── tests/                          # Automated PyTest Test Suite (45 Tests)
    ├── __init__.py
    ├── test_pdf_extractor.py
    ├── test_provenance_validator.py
    ├── test_index_builder.py
    └── test_topic_detector.py
```

---

## 📚 Technical Documentation & Reports

- **[`llm_usage.md`](llm_usage.md)**: Full disclosure of AI/LLM models, system prompts, few-shot rules, structured output schemas, error handling, token costs, and AI development assistance.
- **[`VALIDATION_REPORT.md`](VALIDATION_REPORT.md)**: Empirical verification report containing:
  - Methodology
  - Audit of **22 manual ground-truth entries**
  - **Three-run stability analysis** demonstrating 100% repeatability
  - Analysis of **3 concrete failure cases** with mitigations
  - Documented edge cases and limitations
- **[`PROJECT_REPORT.md`](PROJECT_REPORT.md)**: Detailed file-by-file component breakdown and technology analysis.

---

## 📊 Sample Index Output

```json
{
  "topic_id": "T005",
  "topic": "Board of Directors Meetings",
  "description": "Discussion of Vertex acquisition proposal approval by the board",
  "start_page": 9,
  "start_line": 11,
  "end_page": 9,
  "end_line": 5,
  "event_type": "return",
  "confidence": 0.92,
  "needs_review": false,
  "flags": [],
  "source_text": "[Transcript Page 9]\n   11  Q.  What did that refer to?\n   12  A.  It refers to Vertex's proposed acquisition...",
  "related_topic_ids": ["T002"]
}
```

---

## ⚠️ Limitations & Future Enhancements

### Limitations
- **Scanned / Image-Only PDFs**: Requires an embedded text layer; scanned PDFs without OCR extract empty text.
- **Line Window Horizon**: Fixed line windows (e.g. 20 lines) can split arguments spanning across 50+ lines.
- **Assistive Scope**: Output is an attorney-work-product acceleration tool, not a certified legal record.

### Future Enhancements
- Integration of Tesseract / AWS Textract for scanned bitmap OCR.
- Vector embeddings for semantic search across multi-deposition archives.
- Visual PDF highlighting directly overlaid on the original document pages.
