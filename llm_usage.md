# LLM Usage and AI Engineering Architecture

This document describes the design, prompts, models, structured outputs, failure recovery, and development methodology for all Artificial Intelligence and Large Language Model (LLM) components in **DepoIndex**.

---

## 1. Executive Overview

In DepoIndex, the Large Language Model acts as a **semantic discourse analyst**. While traditional legal search relies on exact keyword matching (which fails when identical concepts are described using colloquial terms or indirect testimony), DepoIndex leverages LLMs to:
1. **Identify the core topic** of question-and-answer testimony passages.
2. **Classify discourse transitions** (`new_topic`, `continuation`, `return`, `digression`).
3. **Summarize testimony** in a concise, factual sentence.
4. **Calibrate confidence scores** reflecting the clarity of the witness's statements.

All LLM operations are bounded by **strict anti-hallucination prompt constraints** and piped into **Pydantic validation schemas** before any coordinates are registered into the index.

---

## 2. Models & API Configuration

| Parameter | Configuration | Rationale |
| :--- | :--- | :--- |
| **Primary Model** | `gpt-4o-mini` | High-speed, cost-effective reasoning optimized for structured extraction and legal document parsing. |
| **Advanced Model Option** | `gpt-4o` | Available in sidebar for complex, highly contentious, or multi-party colloquy. |
| **Sampling Temperature** | `0.0` | Eliminates creative variance, ensuring deterministic, reproducible topic classifications across multiple runs. |
| **Output Mode** | `json_object` | Enforces valid JSON response schemas matching `LLMTopicResult`. |
| **Retry Policy** | Exponential Backoff (3 retries) | Handles transient HTTP errors, connection drops, and OpenAI API rate limits. |

---

## 3. Prompt Engineering Architecture

The prompt system is implemented in [`src/topic_detector.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/topic_detector.py) and consists of a strict two-part prompt architecture:

### 3.1 System Prompt
The system prompt establishes the legal domain, output schema, taxonomy categories, and anti-hallucination boundaries:

```text
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
```

### 3.2 Dynamic Context Injection (User Prompt)
To allow the model to recognize continuations and returns without sending the entire transcript (which would exceed context windows and inflate cost), the user prompt dynamically injects the **immediate preceding context**:

```text
PREVIOUS CONTEXT (do not index, for continuity only):
{context_before}

TRANSCRIPT SEGMENT TO ANALYZE:
{segment_text}

Previous topic (if any): {prev_topic}
```

This context-window chaining enables the model to distinguish between:
- A continuation of the previous question.
- An abrupt topic shift by the examining attorney.
- A procedural digression by defending counsel.

---

## 4. Structured Output & Defensive Parsing

To prevent malformed AI text from breaking downstream code, all outputs are validated using Pydantic:

```python
class LLMTopicResult(BaseModel):
    topic: str
    description: str
    event_type: EventType = EventType.NEW_TOPIC
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

    @field_validator("topic")
    @classmethod
    def topic_not_empty(cls, v: str) -> str:
        return v.strip() if v else "Unknown"
```

### Graceful Fallback Strategy
If an LLM call fails due to validation errors, API timeout, or invalid JSON, the system does not crash or omit the passage. Instead, it yields a safe fallback record:

```python
result = LLMTopicResult(
    topic="Unclassified",
    description=f"LLM error: {exc}",
    event_type=EventType.NEW_TOPIC,
    confidence=0.0,
)
```
The provenance validator subsequently flags this entry with `needs_review = True`, ensuring complete human visibility.

---

## 5. Offline Heuristic Fallback Engine

In [`src/llm_client.py`](file:///Users/aradhyamishra/Desktop/Programming/docu3cproject/src/llm_client.py), DepoIndex includes a deterministic, keyword-scoring offline engine.

### Why was this built?
1. **Testing & Demonstrations**: Enables running the complete test suite (45 tests) and interactive UI without requiring active OpenAI credentials or incurring API costs.
2. **Air-Gapped & Privacy Constraints**: Some legal workflows prohibit sending confidential deposition testimony across external commercial APIs.
3. **Deterministic Verification**: Provides a perfectly reproducible baseline for stability testing across runs.

The offline engine scores legal terms across 7 core legal categories (*Employment, Acquisitions, Offshore Accounts, Emails, Board Meetings, Contracts, Objections*), computes boundary relationships, and outputs the exact schema expected from the live model.

---

## 6. Token Economics & Cost Optimization

| Metric | Measurement (15-Page Deposition) |
| :--- | :--- |
| **Total Segments Analyzed** | 28 segments |
| **Average Prompt Tokens / Segment** | ~350 tokens (including context window) |
| **Average Output Tokens / Segment** | ~55 tokens |
| **Total Tokens per Deposition** | ~11,340 tokens |
| **Estimated Cost (`gpt-4o-mini`)** | **< $0.003 USD** per 15-page transcript |
| **Estimated Processing Time** | ~12–18 seconds (streaming / parallelizable) |

By segmenting the transcript into overlapping 20-line windows rather than sending the full deposition in one mega-prompt, the system achieves **predictable linear cost scaling** ($O(N)$ with page count) and avoids context degradation at the middle of long prompts.

---

## 7. AI Use in Software Development Disclosure

In accordance with transparent AI engineering practices:

- **AI Pair Programming**: Development of this codebase was assisted by **Antigravity AI** (Claude Sonnet / Gemini models).
- **Assisted Components**:
  - Drafting regex patterns for US court reporter transcripts (`src/pdf_extractor.py`).
  - Formulating Pydantic v2 schemas and validation flags (`src/models.py`).
  - Authoring comprehensive pytest test fixtures covering corner cases (`tests/`).
  - ReportLab code synthesis for the realistic 15-page sample deposition (`sample_data/generate_sample.py`).
- **Human/Architect Verification**: Every line of generated code, regex rule, test case, and validation check was audited, verified through pytest execution, and pushed to source control.
