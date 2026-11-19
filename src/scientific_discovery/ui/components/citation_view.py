"""
Citation and Research Sources View Component.

Visualizes academic literature sources retrieved from ArXiv and PubMed,
including vector similarity scores, author lists, and grounded findings.
"""

import streamlit as st
from src.scientific_discovery.memory.models import Citation, ExperimentRun


SOURCE_COLORS = {
    "arxiv": "🔴 ArXiv",
    "pubmed": "🔵 PubMed",
    "biorxiv": "🟢 BioRxiv",
    "manual": "⚪ Custom Reference",
}


def render_citation_view(experiment: ExperimentRun) -> None:
    """Renders literature citations and grounded vector DB sources."""
    st.subheader("📚 Literature Citations & Research Sources")

    if not experiment.citations:
        st.info("No citations attached to this experiment. Run the Literature Reviewer agent to ingest papers.")
        return

    st.markdown(
        f"Displaying **{len(experiment.citations)}** peer-reviewed papers grounded via Retrieval-Augmented Generation (RAG):"
    )

    # Search & Filter within citations
    search_query = st.text_input("🔍 Filter citations by title, author, or keyword:", "")

    filtered_citations = [
        c for c in experiment.citations
        if search_query.lower() in c.title.lower()
        or any(search_query.lower() in a.lower() for a in c.authors)
        or search_query.lower() in c.key_findings.lower()
    ] if search_query else experiment.citations

    for c in filtered_citations:
        source_badge = SOURCE_COLORS.get(c.source, c.source)
        authors_str = ", ".join(c.authors) if c.authors else "Unknown Authors"
        year_str = f"({c.year})" if c.year else ""

        with st.container():
            st.markdown(
                f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 12px; background-color: #fafafa;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #1a73e8;">{c.title}</h4>
                        <span style="font-weight: bold; background: #e8f0fe; padding: 4px 8px; border-radius: 4px;">{source_badge}</span>
                    </div>
                    <p style="margin: 6px 0; color: #5f6368; font-size: 0.9em;">
                        <strong>Authors:</strong> {authors_str} {year_str} &nbsp;|&nbsp; 
                        <strong>ID:</strong> <code>{c.citation_id}</code>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                if c.key_findings:
                    st.markdown(f"**Key Grounded Findings:** {c.key_findings}")
                if c.url:
                    st.markdown(f"🔗 [View Full Paper / PDF]({c.url})")
            with col2:
                st.metric("Vector Similarity", f"{c.similarity_score * 100:.1f}%")

            with st.expander("📄 View Paper Abstract"):
                st.write(c.abstract if c.abstract else "No abstract text recorded.")

            st.markdown("---")
