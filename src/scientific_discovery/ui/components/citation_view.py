"""
Citation and Research Sources View Component.

Visualizes academic literature sources retrieved from ArXiv and PubMed,
including vector similarity scores, author lists, and grounded findings.
"""

import pandas as pd
import streamlit as st
from src.scientific_discovery.memory.models import Citation, ExperimentRun
from src.scientific_discovery.ui.theme import render_section_header


SOURCE_THEMES = {
    "arxiv": {
        "label": "ArXiv Preprint",
        "bg": "#fef2f2",
        "color": "#dc2626",
        "border": "#fecaca",
        "icon": "🔴",
    },
    "pubmed": {
        "label": "PubMed Peer-Reviewed",
        "bg": "#eff6ff",
        "color": "#2563eb",
        "border": "#bfdbfe",
        "icon": "🔵",
    },
    "biorxiv": {
        "label": "BioRxiv Biology",
        "bg": "#ecfdf5",
        "color": "#059669",
        "border": "#a7f3d0",
        "icon": "🟢",
    },
    "manual": {
        "label": "Custom Grounding Reference",
        "bg": "#f8fafc",
        "color": "#475569",
        "border": "#e2e8f0",
        "icon": "⚪",
    },
}


def render_citation_view(experiment: ExperimentRun) -> None:
    """Renders literature citations, vector DB grounding, and literature matrix."""
    st.markdown(
        render_section_header(
            title="Literature Citations & RAG Grounding",
            subtitle="Peer-reviewed academic papers mined, chunked, and vector-embedded to prevent hallucinations.",
            icon="📚",
        ),
        unsafe_allow_html=True,
    )

    if not experiment.citations:
        st.info("No citations attached to this experiment. Run the Literature Reviewer agent to ingest papers.")
        return

    # Top metric summary row
    c_count = len(experiment.citations)
    avg_sim = (
        sum(c.similarity_score for c in experiment.citations) / c_count
        if c_count > 0
        else 0.0
    )
    sources_count = len(set(c.source for c in experiment.citations))
    arxiv_count = sum(1 for c in experiment.citations if c.source == "arxiv")
    pubmed_count = sum(1 for c in experiment.citations if c.source == "pubmed")

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Grounded Citations", c_count)
    with col_m2:
        st.metric("Avg Vector Match", f"{avg_sim * 100:.1f}%")
    with col_m3:
        st.metric("ArXiv Preprints", arxiv_count)
    with col_m4:
        st.metric("PubMed Papers", pubmed_count)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Search & Filter Controls + View Toggle (Thursday Deliverable)
    c_search, c_source, c_mode = st.columns([3, 1, 1])
    with c_search:
        search_query = st.text_input("🔍 Filter papers by title, author, or keyword:", "")
    with c_source:
        available_sources = ["All"] + sorted(list(set(c.source for c in experiment.citations)))
        source_filter = st.selectbox("Repository:", available_sources, index=0)
    with c_mode:
        view_mode = st.radio("Display Mode:", ["Detailed Cards", "Matrix Table"], horizontal=True)

    # Apply search and source filter
    filtered_citations = experiment.citations
    if search_query:
        q = search_query.lower()
        filtered_citations = [
            c for c in filtered_citations
            if q in c.title.lower()
            or any(q in a.lower() for a in c.authors)
            or q in c.key_findings.lower()
        ]
    if source_filter != "All":
        filtered_citations = [c for c in filtered_citations if c.source == source_filter]

    st.markdown(
        f"<div style='font-size: 0.82rem; color: #64748b; margin-bottom: 14px;'>Showing <strong>{len(filtered_citations)}</strong> of {c_count} literature references:</div>",
        unsafe_allow_html=True,
    )

    if not filtered_citations:
        st.info("No citations matched your current filter criteria.")
        return

    # Thursday Deliverable: Switchable Literature Matrix Table vs Detailed Cards
    if view_mode == "Matrix Table":
        matrix_rows = []
        for c in filtered_citations:
            matrix_rows.append({
                "Citation ID": c.citation_id,
                "Paper Title": c.title,
                "Source": c.source.upper(),
                "Year": c.year or "N/A",
                "Authors": ", ".join(c.authors) if c.authors else "Unknown",
                "Cosine Similarity": f"{c.similarity_score * 100:.1f}%",
                "Grounded Finding": c.key_findings[:80] + ("..." if len(c.key_findings) > 80 else "") if c.key_findings else "Verified",
                "URL": c.url or "",
            })
        df_matrix = pd.DataFrame(matrix_rows)
        st.dataframe(df_matrix, width="stretch", hide_index=True)
    else:
        for c in filtered_citations:
            theme = SOURCE_THEMES.get(c.source, SOURCE_THEMES["manual"])
            authors_str = ", ".join(c.authors) if c.authors else "Unknown Authors"
            year_str = f"({c.year})" if c.year else ""
            sim_pct = c.similarity_score * 100

            link_html = f'<a href="{c.url}" target="_blank" style="font-size: 0.84rem; font-weight: 600; color: #2563eb; text-decoration: none;">🔗 Open Full Paper / DOI Source ↗</a>' if c.url else '<span style="font-size: 0.82rem; color: #94a3b8;">Local Document Source</span>'
            findings_text = c.key_findings or 'Grounded evidence verified by literature reviewer agent.'

            card_html = (
                f'<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 22px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);">'
                f'<div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 14px; flex-wrap: wrap;">'
                f'<div style="flex: 1; min-width: 280px;">'
                f'<div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; line-height: 1.4; margin-bottom: 6px;">{c.title}</div>'
                f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; font-size: 0.82rem; color: #64748b;">'
                f'<span>👥 <strong>{authors_str}</strong> {year_str}</span>'
                f'<span style="background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 6px; font-family: JetBrains Mono, monospace; font-size: 0.74rem;">ID: {c.citation_id}</span>'
                f'</div></div>'
                f'<div style="background: {theme["bg"]}; color: {theme["color"]}; border: 1px solid {theme["border"]}; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 5px; white-space: nowrap;">'
                f'<span>{theme["icon"]}</span><span>{theme["label"]}</span>'
                f'</div></div>'
                f'<div style="margin-top: 14px; background: #f8fafc; border-left: 3px solid #3b82f6; padding: 12px 16px; border-radius: 0 8px 8px 0; font-size: 0.88rem; color: #334155; line-height: 1.5;">'
                f'<strong style="color: #0f172a;">💡 Grounded Findings:</strong> {findings_text}'
                f'</div>'
                f'<div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">'
                f'<div>{link_html}</div>'
                f'<div style="display: flex; align-items: center; gap: 8px;">'
                f'<span style="font-size: 0.78rem; color: #64748b; font-weight: 600;">Vector Cosine Match:</span>'
                f'<span style="background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; font-size: 0.8rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px; font-family: JetBrains Mono, monospace;">{sim_pct:.1f}%</span>'
                f'</div></div></div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            with st.expander("📄 View Paper Abstract Text"):
                st.write(c.abstract if c.abstract else "No abstract text recorded in citation store.")
