"""
DepoIndex – Streamlit Application
AI-Powered Deposition Topic Index
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Page configuration – MUST be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DepoIndex – AI Deposition Topic Index",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Inject custom CSS for premium look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Dark background */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #111827 50%, #0d1117 100%);
        color: #e2e8f0;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #141824 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.4rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
    }

    /* ── Download buttons ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5) !important;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        backdrop-filter: blur(10px) !important;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
    }

    /* ── Text inputs ── */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }

    /* ── Progress bar ── */
    .stProgress > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.04) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
    }

    /* ── Hero header ── */
    .hero-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 60%);
        animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.05); opacity: 1; }
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #a78bfa, #c4b5fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* ── Topic card ── */
    .topic-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .topic-card:hover {
        background: rgba(99, 102, 241, 0.08);
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateX(4px);
    }
    .topic-card.flagged {
        border-color: rgba(245, 158, 11, 0.4);
        background: rgba(245, 158, 11, 0.05);
    }

    /* ── Badge ── */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-new { background: rgba(99, 102, 241, 0.2); color: #a78bfa; border: 1px solid rgba(99,102,241,0.3); }
    .badge-continuation { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
    .badge-return { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
    .badge-digression { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
    .badge-transition { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
    .badge-review { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }

    /* ── Source text block ── */
    .source-block {
        background: rgba(0, 0, 0, 0.3);
        border-left: 3px solid #6366f1;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.2rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.7;
        max-height: 280px;
        overflow-y: auto;
        white-space: pre-wrap;
    }

    /* ── Info boxes ── */
    .info-box {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }

    /* ── Section heading ── */
    .section-heading {
        font-size: 1.1rem;
        font-weight: 600;
        color: #c4b5fd;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Import pipeline modules (after path setup)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

from src.llm_client import LLMClient
from src.models import IndexReport
from src.pdf_extractor import extract_pages
from src.provenance_validator import validate_report
from src.index_builder import build_index
from src.topic_detector import detect_topics
from src.transcript_parser import build_segments

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "report" not in st.session_state:
    st.session_state["report"] = None
if "processing" not in st.session_state:
    st.session_state["processing"] = False

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 1rem 0 1.5rem;">
            <span style="font-size: 2.5rem;">⚖️</span>
            <div style="font-size: 1.3rem; font-weight: 700; color: #a78bfa; margin-top: 0.3rem;">DepoIndex</div>
            <div style="font-size: 0.8rem; color: #64748b;">AI Deposition Indexer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-heading">🔑 API Configuration</div>', unsafe_allow_html=True)
    default_key = os.environ.get("OPENAI_API_KEY", "")
    api_key = st.text_input(
        "OpenAI API Key",
        value=default_key,
        type="password",
        placeholder="sk-...",
        help="Your OpenAI API key. Leave empty to use Offline Demo / Heuristic Mode.",
        key="api_key_input",
    )

    model_choice = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "Offline Demo (Heuristic Classifier)"],
        index=0 if default_key else 3,
        help="Use gpt-4o-mini for live AI indexing, or Offline Demo for testing without an API key.",
    )

    st.markdown('<div class="section-heading">⚙️ Processing Options</div>', unsafe_allow_html=True)
    lines_per_seg = st.slider(
        "Lines per Segment",
        min_value=10,
        max_value=40,
        value=20,
        step=5,
        help="Number of transcript lines analyzed per LLM call. Fewer = more granular topics, higher cost.",
    )
    overlap = st.slider(
        "Overlap Lines",
        min_value=2,
        max_value=8,
        value=4,
        step=1,
        help="Lines of context shared between adjacent segments for continuity.",
    )

    st.markdown('<div class="section-heading">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size: 0.82rem; color: #64748b; line-height: 1.6;">
        DepoIndex uses GPT-4o-mini to automatically identify topics in deposition transcripts and build a structured, searchable index with page and line references.<br><br>
        <b style="color: #94a3b8;">Pipeline:</b> PDF → Extract → Parse → LLM Detect → Validate → Index
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Hero header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-header">
        <h1 class="hero-title">⚖️ DepoIndex</h1>
        <p class="hero-subtitle">AI-Powered Deposition Topic Index · Automatic topic discovery with verifiable page & line references</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Main content tabs
# ---------------------------------------------------------------------------
tab_upload, tab_index, tab_export = st.tabs(
    ["📄 Upload & Process", "📋 Topic Index", "📤 Export"]
)

# ── Tab 1: Upload & Process ──────────────────────────────────────────────────
with tab_upload:
    col_l, col_r = st.columns([2, 1], gap="large")

    with col_l:
        st.markdown('<div class="section-heading">📂 Upload Deposition PDF</div>', unsafe_allow_html=True)
        sample_pdf_path = Path("sample_data/sample_deposition.pdf")
        if "use_sample" not in st.session_state:
            st.session_state["use_sample"] = False

        c_up1, c_up2 = st.columns([3, 2])
        with c_up2:
            if sample_pdf_path.exists():
                if st.button("📑 Load Sample Deposition PDF", use_container_width=True):
                    st.session_state["use_sample"] = True
                    st.rerun()

        uploaded_file = st.file_uploader(
            "Drop a deposition PDF here or click to browse",
            type=["pdf"],
            help="Standard US deposition transcript PDFs work best. Scanned PDFs may have reduced accuracy.",
            key="pdf_uploader",
        )

        # Handle sample PDF if user clicked load sample
        file_bytes = None
        file_name = None
        if uploaded_file:
            file_bytes = uploaded_file.getvalue()
            file_name = uploaded_file.name
            st.session_state["use_sample"] = False
        elif st.session_state.get("use_sample") and sample_pdf_path.exists():
            file_bytes = sample_pdf_path.read_bytes()
            file_name = "sample_deposition.pdf"
            st.info("📑 Using loaded **sample_deposition.pdf** (15-page deposition with continuations & returns)")

        if file_bytes and file_name:
            st.success(f"✅ **{file_name}** ready — {len(file_bytes) / 1024:.1f} KB")

            is_offline_mode = (not api_key) or ("Offline Demo" in model_choice)
            btn_label = "🚀 Run DepoIndex Pipeline (Offline Demo)" if is_offline_mode else "🚀 Run DepoIndex Pipeline (OpenAI)"
            run_btn = st.button(
                btn_label,
                use_container_width=True,
                key="run_btn",
            )

            if is_offline_mode:
                st.caption("ℹ️ Running in **Offline Demo Mode** (no API key required). To use OpenAI models, enter your API key in the sidebar.")

            if run_btn:
                st.session_state["processing"] = True
                report = None
                error_msg = None

                with st.status("Running DepoIndex pipeline…", expanded=True) as status:
                    try:
                        # 1. Save file temporarily
                        st.write("📄 Reading PDF…")
                        tmp_path = Path("/tmp/depoindex_upload.pdf")
                        tmp_path.write_bytes(file_bytes)

                        # 2. Extract pages
                        st.write("🔍 Extracting transcript text…")
                        pages = extract_pages(str(tmp_path))
                        st.write(f"   → {len(pages)} PDF pages extracted")

                        if not pages:
                            raise ValueError("No text could be extracted from the PDF. Is it a scanned-only document?")

                        # 3. Parse segments
                        st.write("✂️ Segmenting transcript…")
                        segments = build_segments(
                            pages,
                            lines_per_segment=lines_per_seg,
                            overlap=overlap,
                        )
                        st.write(f"   → {len(segments)} segments created")

                        if not segments:
                            raise ValueError("No transcript segments could be created. The PDF may have no extractable text lines.")

                        # 4. LLM topic detection
                        st.write(f"🤖 Running AI topic detection ({len(segments)} segments)…")
                        llm = LLMClient(api_key=api_key, model=model_choice)
                        progress_bar = st.progress(0)
                        progress_text = st.empty()

                        def update_progress(current: int, total: int) -> None:
                            pct = current / total
                            progress_bar.progress(pct)
                            progress_text.markdown(
                                f"<small style='color:#94a3b8'>Segment {current} / {total}</small>",
                                unsafe_allow_html=True,
                            )

                        raw_records = detect_topics(
                            segments, llm, progress_callback=update_progress
                        )
                        progress_bar.progress(1.0)
                        progress_text.empty()
                        st.write(f"   → {len(raw_records)} topic detections returned")

                        # 5. Build index
                        st.write("🔗 Building topic index…")
                        report = build_index(raw_records, pages, file_name)
                        st.write(f"   → {len(report.entries)} distinct topics identified")

                        # 6. Validate provenance
                        st.write("✅ Validating provenance…")
                        validate_report(report)
                        flagged = report.flagged_count
                        st.write(f"   → {flagged} entries flagged for review")

                        st.session_state["report"] = report
                        status.update(label="✅ Pipeline complete!", state="complete")

                    except Exception as exc:
                        error_msg = str(exc)
                        status.update(label=f"❌ Pipeline failed: {exc}", state="error")

                if error_msg:
                    st.error(f"**Pipeline error:** {error_msg}")
                elif report:
                    st.balloons()
                    st.success(
                        f"🎉 DepoIndex complete! **{len(report.entries)} topics** identified "
                        f"across **{report.total_pages} pages**. Switch to the **Topic Index** tab to explore."
                    )

    with col_r:
        st.markdown('<div class="section-heading">📊 Pipeline Steps</div>', unsafe_allow_html=True)
        steps = [
            ("1", "📄", "PDF Upload", "Upload your deposition PDF"),
            ("2", "🔍", "Text Extraction", "PyMuPDF extracts text page-by-page"),
            ("3", "✂️", "Segmentation", "Text split into overlapping windows"),
            ("4", "🤖", "AI Detection", "GPT-4o-mini classifies each segment"),
            ("5", "🔗", "Index Builder", "Merges topics, detects continuations"),
            ("6", "✅", "Validation", "Checks provenance and flags issues"),
        ]
        for num, icon, title, desc in steps:
            st.markdown(
                f"""
                <div style="display:flex; align-items:flex-start; margin-bottom:0.8rem; padding:0.8rem;
                            background:rgba(255,255,255,0.03); border-radius:10px;
                            border:1px solid rgba(99,102,241,0.15);">
                    <div style="min-width:28px; height:28px; background:linear-gradient(135deg,#6366f1,#8b5cf6);
                                border-radius:50%; display:flex; align-items:center; justify-content:center;
                                font-size:0.75rem; font-weight:700; color:white; margin-right:0.8rem;">{num}</div>
                    <div>
                        <div style="font-weight:600; color:#c4b5fd; font-size:0.9rem;">{icon} {title}</div>
                        <div style="font-size:0.78rem; color:#64748b; margin-top:0.15rem;">{desc}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.session_state["report"]:
            r = st.session_state["report"]
            st.markdown('<div class="section-heading">📈 Results</div>', unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("Topics", len(r.entries))
            m2.metric("Pages", r.total_pages)
            m3.metric("⚠️ Flagged", r.flagged_count)

# ── Tab 2: Topic Index ────────────────────────────────────────────────────────
with tab_index:
    report: Optional[IndexReport] = st.session_state.get("report")

    if not report:
        st.markdown(
            """
            <div style="text-align:center; padding: 4rem 2rem; color: #475569;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #64748b;">No index generated yet</div>
                <div style="font-size: 0.9rem; margin-top: 0.5rem;">Upload a PDF and run the pipeline to see results here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # ── Search and filter controls ──
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([3, 2, 2], gap="medium")

        with ctrl_col1:
            search_query = st.text_input(
                "🔍 Search topics",
                placeholder="e.g. financial, employment, meetings…",
                key="search_input",
            )

        with ctrl_col2:
            event_filter = st.selectbox(
                "Event Type",
                ["All", "new_topic", "continuation", "return", "digression", "topic_transition"],
                key="event_filter",
            )

        with ctrl_col3:
            review_filter = st.selectbox(
                "Review Status",
                ["All", "Needs Review", "OK"],
                key="review_filter",
            )

        # ── Apply filters ──
        entries = report.entries
        if search_query:
            q = search_query.lower()
            entries = [
                e for e in entries
                if q in e.topic.lower() or q in e.description.lower()
            ]
        if event_filter != "All":
            entries = [e for e in entries if e.event_type.value == event_filter]
        if review_filter == "Needs Review":
            entries = [e for e in entries if e.needs_review]
        elif review_filter == "OK":
            entries = [e for e in entries if not e.needs_review]

        # ── Summary bar ──
        st.markdown(
            f"""
            <div style="display:flex; gap:1rem; margin-bottom:1rem; flex-wrap:wrap;">
                <div class="info-box" style="flex:1; min-width:120px;">
                    <div style="font-size:1.5rem; font-weight:700; color:#a78bfa;">{len(entries)}</div>
                    <div style="font-size:0.8rem; color:#64748b;">Topics Shown</div>
                </div>
                <div class="info-box" style="flex:1; min-width:120px;">
                    <div style="font-size:1.5rem; font-weight:700; color:#34d399;">{len([e for e in entries if not e.needs_review])}</div>
                    <div style="font-size:0.8rem; color:#64748b;">Verified</div>
                </div>
                <div class="info-box" style="flex:1; min-width:120px;">
                    <div style="font-size:1.5rem; font-weight:700; color:#fbbf24;">{len([e for e in entries if e.needs_review])}</div>
                    <div style="font-size:0.8rem; color:#64748b;">Needs Review</div>
                </div>
                <div class="info-box" style="flex:1; min-width:120px;">
                    <div style="font-size:1.5rem; font-weight:700; color:#60a5fa;">{len([e for e in entries if e.event_type.value == 'return'])}</div>
                    <div style="font-size:0.8rem; color:#64748b;">Returns</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── View mode toggle ──
        view_mode = st.radio(
            "View Mode",
            ["📋 Table View", "🃏 Card View"],
            horizontal=True,
            key="view_mode",
        )

        if view_mode == "📋 Table View":
            # Build dataframe
            rows = []
            for e in entries:
                rows.append({
                    "ID": e.topic_id,
                    "Topic": e.topic,
                    "Description": e.description,
                    "Start Page": e.start_page,
                    "Start Line": e.start_line,
                    "End Page": e.end_page,
                    "End Line": e.end_line,
                    "Type": e.event_type.value,
                    "Confidence": f"{e.confidence:.0%}",
                    "Review": "⚠️ Yes" if e.needs_review else "✅ OK",
                    "Related": ", ".join(e.related_topic_ids) if e.related_topic_ids else "—",
                })

            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.TextColumn("ID", width="small"),
                        "Topic": st.column_config.TextColumn("Topic", width="medium"),
                        "Description": st.column_config.TextColumn("Description", width="large"),
                        "Start Page": st.column_config.NumberColumn("Start Pg", width="small"),
                        "Start Line": st.column_config.NumberColumn("Start Ln", width="small"),
                        "End Page": st.column_config.NumberColumn("End Pg", width="small"),
                        "End Line": st.column_config.NumberColumn("End Ln", width="small"),
                        "Type": st.column_config.TextColumn("Type", width="small"),
                        "Confidence": st.column_config.TextColumn("Conf.", width="small"),
                        "Review": st.column_config.TextColumn("Review", width="small"),
                        "Related": st.column_config.TextColumn("Related", width="small"),
                    },
                )
            else:
                st.info("No entries match the current filters.")

        else:  # Card View
            _BADGE_MAP = {
                "new_topic": "badge-new",
                "continuation": "badge-continuation",
                "return": "badge-return",
                "digression": "badge-digression",
                "topic_transition": "badge-transition",
            }

            if not entries:
                st.info("No entries match the current filters.")

            for entry in entries:
                badge_cls = _BADGE_MAP.get(entry.event_type.value, "badge-new")
                card_cls = "topic-card flagged" if entry.needs_review else "topic-card"

                with st.expander(
                    f"**{entry.topic_id}** · {entry.topic} "
                    f"{'⚠️' if entry.needs_review else '✅'}",
                    expanded=False,
                ):
                    detail_col1, detail_col2 = st.columns([3, 2])

                    with detail_col1:
                        st.markdown(
                            f"""
                            <div style="margin-bottom:0.8rem;">
                                <span class="badge {badge_cls}">{entry.event_type.value.replace('_', ' ')}</span>
                                {'<span class="badge badge-review" style="margin-left:0.4rem;">⚠️ Needs Review</span>' if entry.needs_review else ''}
                            </div>
                            <div style="color:#cbd5e1; font-size:0.95rem; margin-bottom:0.8rem;">{entry.description}</div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if entry.flags:
                            flags_html = " ".join(
                                f'<span class="badge badge-review">{f.value}</span>'
                                for f in entry.flags
                            )
                            st.markdown(
                                f'<div style="margin-bottom:0.8rem;"><b style="color:#94a3b8;">Flags:</b> {flags_html}</div>',
                                unsafe_allow_html=True,
                            )

                        if entry.related_topic_ids:
                            st.markdown(
                                f'<div style="color:#94a3b8; font-size:0.85rem;">🔗 Related: {", ".join(entry.related_topic_ids)}</div>',
                                unsafe_allow_html=True,
                            )

                    with detail_col2:
                        loc_col1, loc_col2 = st.columns(2)
                        loc_col1.metric(
                            "Start",
                            f"P{entry.start_page}" if entry.start_page else "—",
                            f"L{entry.start_line}" if entry.start_line else None,
                        )
                        loc_col2.metric(
                            "End",
                            f"P{entry.end_page}" if entry.end_page else "—",
                            f"L{entry.end_line}" if entry.end_line else None,
                        )
                        st.metric("Confidence", f"{entry.confidence:.0%}")

                    if entry.source_text:
                        st.markdown("**Source Excerpt:**")
                        st.markdown(
                            f'<div class="source-block">{entry.source_text}</div>',
                            unsafe_allow_html=True,
                        )

# ── Tab 3: Export ─────────────────────────────────────────────────────────────
with tab_export:
    report: Optional[IndexReport] = st.session_state.get("report")

    if not report:
        st.markdown(
            """
            <div style="text-align:center; padding: 4rem 2rem; color: #475569;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📤</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: #64748b;">Nothing to export yet</div>
                <div style="font-size: 0.9rem; margin-top: 0.5rem;">Run the pipeline first to generate an index.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="section-heading">📤 Export Topic Index</div>', unsafe_allow_html=True)

        # JSON export
        json_data = json.dumps(
            {
                "source_filename": report.source_filename,
                "total_pages": report.total_pages,
                "total_segments": report.total_segments,
                "entries": [e.to_export_dict() for e in report.entries],
            },
            indent=2,
        )

        # CSV export
        rows = [e.to_export_dict() for e in report.entries]
        df_export = pd.DataFrame(rows)
        csv_data = df_export.to_csv(index=False)

        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            st.markdown(
                """
                <div class="info-box">
                    <div style="font-size:1.5rem; margin-bottom:0.5rem;">{ }</div>
                    <div style="font-weight:600; color:#c4b5fd; margin-bottom:0.3rem;">JSON Format</div>
                    <div style="font-size:0.82rem; color:#64748b;">Machine-readable structured format. Ideal for integration with other tools or further analysis.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇️ Download JSON",
                data=json_data,
                file_name=f"depoindex_{Path(report.source_filename).stem}.json",
                mime="application/json",
                use_container_width=True,
            )

        with exp_col2:
            st.markdown(
                """
                <div class="info-box">
                    <div style="font-size:1.5rem; margin-bottom:0.5rem;">📊</div>
                    <div style="font-weight:600; color:#c4b5fd; margin-bottom:0.3rem;">CSV Format</div>
                    <div style="font-size:0.82rem; color:#64748b;">Spreadsheet-friendly format. Open in Excel, Google Sheets, or any data tool.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                "⬇️ Download CSV",
                data=csv_data,
                file_name=f"depoindex_{Path(report.source_filename).stem}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown('<div class="section-heading">👁️ Preview</div>', unsafe_allow_html=True)
        st.markdown(
            f"**{len(report.entries)} entries** · Source: `{report.source_filename}` · "
            f"{report.total_pages} pages · {report.flagged_count} flagged"
        )
        st.dataframe(df_export, use_container_width=True, hide_index=True)

        st.markdown('<div class="section-heading">🔍 Validation Report</div>', unsafe_allow_html=True)
        if report.flagged_count == 0:
            st.success("✅ All entries passed provenance validation. No issues detected.")
        else:
            st.warning(
                f"⚠️ **{report.flagged_count} entries** require manual review. "
                "These are included in the export but are marked with `needs_review: true`."
            )
            flagged_entries = [e for e in report.entries if e.needs_review]
            for entry in flagged_entries:
                with st.expander(f"⚠️ {entry.topic_id} – {entry.topic}"):
                    st.markdown(f"**Flags:** {', '.join(f.value for f in entry.flags)}")
                    st.markdown(f"**Location:** Page {entry.start_page}:{entry.start_line} → {entry.end_page}:{entry.end_line}")
                    st.markdown(f"**Description:** {entry.description}")
