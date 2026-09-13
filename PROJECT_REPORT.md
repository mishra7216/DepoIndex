# DepoIndex: Detailed Technical Architecture, Technology Stack, and Limitations Report

---

## 1. Executive Summary

**DepoIndex** is an AI-powered legal technology solution designed to automate the discovery, boundary tracking, and indexing of subjects discussed in lengthy legal deposition transcripts. Unlike generic keyword search engines, DepoIndex preserves exact page and line references, detects topic transitions (continuations, returns, digressions), and subjects all generated entries to a deterministic provenance validation gate.

---

## 2. Technology Stack & Component Analysis

| Technology | Role in System | Key Rationale & Capabilities |
| :--- | :--- | :--- |
| **Python 3.9+** | Core Programming Language | High ecosystem maturity for document processing, NLP, and AI integration. |
| **PyMuPDF (`fitz`)** | PDF Text & Layout Extraction | Up to 10x faster than traditional PDF parsers (e.g. `pypdf`, `pdfminer`). Extracts raw text blocks with spatial coordinate awareness, preserving left-margin line numbers (1–25) and header metadata. |
| **OpenAI API (`gpt-4o-mini` / `gpt-4o`)** | AI Topic & Boundary Classifier | State-of-the-art reasoning for legal text comprehension. Enforces JSON structured responses, categorizing topics and identifying transition types (`new_topic`, `continuation`, `return`, `digression`). |
| **Pydantic v2** | Data Schema & Runtime Validation | Enforces strict typing and validation constraints across transcript segments, LLM outputs, index entries, and validation reports. Prevents malformed AI outputs from propagating downstream. |
| **Streamlit (v1.50)** | Interactive Web User Interface | Provides a reactive legal-tech dashboard with zero frontend bloat. Supports PDF drag-and-drop, real-time pipeline telemetry, interactive search/filter tables, provenance inspection drawers, and export handlers. |
| **ReportLab** | Test Deposition Synthesis | Programmatically generates realistic, 15-page court reporter transcripts adhering to 25-line legal formatting standards with timestamps, legal objections, and multi-topic narratives. |
| **Pandas & PyArrow** | Tabular Data Processing | Facilitates tabular filtering, confidence thresholding, and automated serialization of the topic index into CSV and structured JSON formats. |
| **Python Regular Expressions (`re`)** | Transcript Pattern Parsing | Specialized regex heuristics to detect legal transcript headers, line numbers (1–25), and speaker identifiers (`Q.`, `A.`, `BY MR. [NAME]:`, `THE WITNESS:`, `THE COURT:`). |
| **PyTest** | Automated Quality Assurance | Test suite (45 unit/integration tests) covering boundary conditions, speaker extraction, reversed page validation, low-confidence flags, and segment merging. |
| **uv** | Fast Dependency & Environment Manager | High-performance virtual environment manager by Astral, providing fast parallel resolution and caching of project packages. |
| **Git & GitHub** | Source Control & Collaboration | Version control hosted at [https://github.com/mishra7216/DepoIndex](https://github.com/mishra7216/DepoIndex). |

---

## 3. Detailed File-by-File Architecture Breakdown

```
docu3cproject/
├── app.py                      # Streamlit Frontend Web Application
├── requirements.txt            # Project Dependencies
├── conftest.py                 # PyTest Path Configuration
├── .gitignore                  # Git Ignore Rules
├── README.md                   # Setup and Overview Documentation
├── PROJECT_REPORT.md           # Technical Architecture & Limitations Report
├── src/                        # Core Engine Modules
│   ├── __init__.py             # Package Initializer
│   ├── models.py               # Pydantic Schemas & Data Structures
│   ├── pdf_extractor.py        # PDF & Transcript Layout Extraction
│   ├── transcript_parser.py    # Text Flattening & Windowed Segmentation
│   ├── llm_client.py           # OpenAI Client with Offline Heuristic Engine
│   ├── topic_detector.py       # Prompt Engineering & LLM Topic Extraction
│   ├── index_builder.py        # Boundary Merge, Continuity & Return Tracking
│   └── provenance_validator.py # Provenance Audit & Coordinate Verification
├── sample_data/
│   ├── generate_sample.py      # 15-Page Legal Deposition PDF Generator
│   └── sample_deposition.pdf   # Generated Sample Deposition
└── tests/                      # Automated Unit Test Suite
    ├── __init__.py             # Test Package Initializer
    ├── test_pdf_extractor.py   # PDF Layout & Line Extraction Tests
    ├── test_topic_detector.py  # AI Detection & Error Recovery Tests
    ├── test_index_builder.py   # Boundary Merging & Topic Return Tests
    └── test_provenance_validator.py # Provenance & Edge-Case Validation Tests
```

### File Details:

#### 1. [`app.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/app.py) (Streamlit Web Dashboard)
- **Purpose**: Serves as the complete graphical user interface for attorneys, paralegals, and legal researchers.
- **Key Features**:
  - **Upload Tab**: Drag-and-drop PDF uploader + a one-click **"Load Sample Deposition PDF"** button.
  - **Dual Engine Execution**: Allows running via live OpenAI API (`gpt-4o-mini`, `gpt-4o`) or completely offline using the built-in **Heuristic Classifier**.
  - **Topic Index Tab**: Real-time search by keyword, filter by event type (`new_topic`, `continuation`, `return`, `digression`), confidence threshold slider, and review-flag indicators.
  - **Provenance Drawer**: Expandable inspection panel displaying the exact verbatim excerpt and page/line references.
  - **Export Center**: One-click downloads of the final index in structured JSON or tabular CSV.

#### 2. [`src/models.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/models.py) (Data Schemas)
- **Purpose**: Establishes the type-safe foundation for the entire pipeline using Pydantic.
- **Key Models**:
  - `TranscriptLine`: Represents an individual line with line number (1–25), speaker label (`Q`, `A`, `colloquy`), and raw text.
  - `TranscriptPage`: Represents an extracted PDF page containing parsed lines and detected transcript page numbers.
  - `TranscriptSegment`: Chunk of consecutive lines sent to the LLM, containing start/end page and line coordinates, speaker context, and previous dialogue.
  - `LLMTopicResult`: Structured JSON response model validated against the LLM's raw output.
  - `TopicRecord`: The canonical index entry with topic title, summary description, page/line coordinates, event type, confidence score, and validation status.
  - `IndexReport`: Top-level index entity containing document metadata, total page counts, and summary metrics.

#### 3. [`src/pdf_extractor.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/pdf_extractor.py) (PDF Layout Parser)
- **Purpose**: Converts unstructured PDF bytes into structured transcript lines.
- **Mechanisms**:
  - Detects printed transcript page headers (e.g. `Page 14` or `14` centered at the top).
  - Uses regex to isolate left-margin line numbers (1–25) from testimony text.
  - Identifies speaker roles: `Q.` (Examining Attorney), `A.` (Deponent), objections by opposing counsel (`MR. [NAME]:`), and witness/court interjections.
  - Provides a sequential line numbering fallback for non-standard transcripts.

#### 4. [`src/transcript_parser.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/transcript_parser.py) (Segmentation Engine)
- **Purpose**: Prepares transcript text for LLM consumption without cutting off Q&A exchanges.
- **Mechanisms**:
  - Flattens page lines into a continuous stream.
  - Employs a sliding window algorithm (default 20 lines per window with 4 lines of overlap).
  - Preserves prior context (`context_before`) to enable the LLM to assess continuity across window boundaries.

#### 5. [`src/llm_client.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/llm_client.py) (Resilient LLM Interface)
- **Purpose**: Provides a fault-tolerant wrapper for language model completions.
- **Mechanisms**:
  - Implements exponential backoff retry logic for transient network failures or OpenAI rate limits (`RateLimitError`).
  - Supports strict `json_object` response mode.
  - **Offline Fallback Engine**: If no API key is supplied or offline mode is chosen, runs a deterministic heuristic classifier that scores legal terminology (Employment, Acquisitions, Offshore Accounts, Board Meetings, Objections) to allow testing and demonstrations without API costs.

#### 6. [`src/topic_detector.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/topic_detector.py) (Prompt Orchestrator)
- **Purpose**: Connects transcript segments to the LLM client.
- **Mechanisms**:
  - Implements legal prompt engineering that constrains the model to factual testimony only and prohibits hallucinating names or page numbers.
  - Injects previous segment topic context to evaluate whether current testimony is a `continuation` or `return`.
  - Catches validation and parsing errors gracefully, marking failed segments as `Unclassified` with zero confidence rather than halting execution.

#### 7. [`src/index_builder.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/index_builder.py) (Index Consolidation Engine)
- **Purpose**: Merges individual segment detections into cohesive macro-topic entries.
- **Mechanisms**:
  - Consolidates adjacent segments discussing the same topic into a single unified record with expanded start/end bounds.
  - Re-evaluates historical topic appearances: if a topic was discussed earlier, marks the new entry as a `return` and creates cross-reference links (`related_topic_ids`) back to the original topic ID.
  - Formats unique sequential Topic Identifiers (`T001`, `T002`, ...).

#### 8. [`src/provenance_validator.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/provenance_validator.py) (Verification Gate)
- **Purpose**: Guarantees that every indexed topic is grounded in the source PDF.
- **Mechanisms**:
  - Checks that `start_page` and `end_page` exist within the physical document.
  - Enforces `end_page >= start_page` (and `end_line >= start_line` when on the same page).
  - Verifies that referenced text excerpt is non-empty.
  - Flags low-confidence entries (< 0.40) or entries flagged with reversed/out-of-bound pages for manual human review (`needs_review = True`).

#### 9. [`sample_data/generate_sample.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/sample_data/generate_sample.py) (Synthetic Legal Data)
- **Purpose**: Generates reproducible legal deposition transcripts formatted to professional court reporting standards.
- **Mechanisms**:
  - Builds an 11-to-15 page PDF using ReportLab with exact 25-line margins, line numbers, and case captions.
  - Injects realistic legal scenarios:
    - *Employment Background* (Pages 1–2)
    - *Board of Directors Meetings* (Pages 2–3)
    - *Contractual Agreements & Closing* (Pages 3–4)
    - *Email Communications & Disputes* (Pages 4–8)
    - *Return to Board Meetings* (Page 9)
    - *Return to Contractual Agreements & Offshore Transfers* (Pages 10–11)

#### 10. [`tests/`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/tests) (PyTest Suite)
- **`test_pdf_extractor.py`**: Validates PDF file loading, line number parsing, speaker tokenization, and error handling on missing files.
- **`test_topic_detector.py`**: Tests segment processing, prompt generation, LLM error recovery, and callback hooks.
- **`test_index_builder.py`**: Tests consecutive segment merging, sequential ID assignment, confidence score averaging, and topic return detection.
- **`test_provenance_validator.py`**: Tests boundary validation flags (`REVERSED_PAGES`, `PAGE_OUT_OF_RANGE`, `SOURCE_TEXT_MISSING`, `LOW_CONFIDENCE`).

---

## 4. Shortcomings, Edge Cases & Model Limitations

While DepoIndex provides a robust pipeline, AI-driven legal transcript indexing has inherent technical and operational limitations:

### 4.1 LLM-Specific Shortcomings
1. **Topic Granularity Inconsistency**:
   - LLMs can oscillate in labeling granularity across segments (e.g. labeling one segment as *"Employment History"* and a subsequent related segment as *"Prior Engineering Roles at Acme Corp"*). While fuzzy matching in `index_builder.py` mitigates this, slight semantic shifts can sometimes produce adjacent split entries rather than a single merged topic.
2. **Context Window Boundary Splitting**:
   - The sliding window operates at fixed line intervals (e.g. 20 lines). If an attorney begins an objection on line 18 that carries into line 3 of the next page, the boundary between segments can split the argumentative context.
3. **Multi-Topic Density within Single Exchanges**:
   - In contentious depositions, a single question/answer exchange may touch upon an email, an offshore bank account, and a board meeting simultaneously. A single primary topic label per segment simplifies multi-layered testimony.

### 4.2 Document & PDF Extraction Limitations
1. **Scanned Documents & Image-Only PDFs**:
   - PyMuPDF reads embedded text layers. If a deposition is a scanned photocopy without an embedded OCR layer, PyMuPDF will extract empty text. A production upgrade requires an integrated OCR fallback (such as Tesseract or AWS Textract).
2. **Non-Standard Transcript Formats**:
   - US transcripts predominantly feature 25 lines with line numbers in the left margin. Transcripts formatted as condensed 4-up pages (four deposition pages per physical sheet) or transcripts lacking explicit line numbers require specialized layout unrolling.

### 4.3 Legal & Compliance Constraints
1. **Assistance vs. Official Legal Record**:
   - The AI-generated index is an attorney-work-product acceleration tool, not an official legal certification. The system is designed to flag unverified or low-confidence entries (`needs_review = True`), requiring legal professional review prior to court filings or trial examinations.

---

## 5. Summary of System Strengths

1. **Deterministic Provenance Verification**: Unlike standard LLM chat interfaces that hallucinate page numbers, DepoIndex mathematically validates coordinates against the PDF's internal line index.
2. **Topic Continuity & Return Detection**: Recognizes when an attorney returns to a topic after a digression or after examining another exhibit.
3. **Offline Operability**: Built-in heuristic classifier ensures complete pipeline execution and UI demonstration even in air-gapped or API-restricted environments.
4. **Comprehensive Test Coverage**: 45 unit and integration tests covering extraction, parsing, detection, merging, and validation.
