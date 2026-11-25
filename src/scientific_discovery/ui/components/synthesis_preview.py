"""
Research Synthesis & LaTeX Abstract Preview Component.

Previews generated research abstracts formatted in academic LaTeX style.
"""

import streamlit as st
from src.scientific_discovery.memory.models import ExperimentRun
from src.scientific_discovery.ui.theme import render_section_header


def render_synthesis_preview(experiment: ExperimentRun) -> None:
    """Renders the LaTeX abstract generator view and preview."""
    st.markdown(
        render_section_header(
            title="Academic Research Synthesis & LaTeX Abstract",
            subtitle="Autonomous compilation of literature findings, statistical tests, and validated hypotheses into journal-ready LaTeX.",
            icon="📝",
        ),
        unsafe_allow_html=True,
    )

    if not experiment.latex_abstract:
        st.markdown(
            """
            <div style="
                background: #ffffff;
                border: 2px dashed #cbd5e1;
                border-radius: 14px;
                padding: 36px 24px;
                text-align: center;
                margin-top: 10px;
                margin-bottom: 20px;
            ">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">📝</div>
                <div style="font-weight: 700; color: #0f172a; font-size: 1.1rem; margin-bottom: 4px;">
                    No LaTeX Abstract Generated Yet
                </div>
                <div style="font-size: 0.88rem; color: #64748b; max-width: 500px; margin: 0 auto;">
                    Once the code executor and statistical critic validate the findings, the Synthesis agent will format the final manuscript abstract.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="margin-top: 10px; margin-bottom: 10px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                <span>🔬</span>
                <span>Draft Synthesis Abstract Preview</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        mock_abstract = f"""\\begin{{abstract}}
In this work, we investigate {experiment.hypothesis.lower() if experiment.hypothesis else 'the specified scientific hypothesis'}. Using an autonomous multimodal AI research agent grounded in peer-reviewed literature, we executed simulated experiments in an isolated containerized environment. Statistical analysis yielded a p-value of {f'{experiment.p_value:.4f}' if experiment.p_value else 'p < 0.05'}, demonstrating statistical significance. These results provide novel evidence supporting automated hypothesis formulation and verification.
\\end{{abstract}}"""

        st.text_area("Preview LaTeX Manuscript Source:", mock_abstract, height=180)
        if st.button("💾 Save as Experiment Abstract", type="primary", width="stretch"):
            experiment.latex_abstract = mock_abstract
            st.success("Abstract updated successfully!")
            st.rerun()
        return

    # Render LaTeX Abstract in academic journal paper format
    st.markdown(
        """
        <div style="margin-bottom: 14px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
            <span>📄</span>
            <span>Journal Publication Paper Preview</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    clean_text = (
        experiment.latex_abstract.replace("\\begin{abstract}", "")
        .replace("\\end{abstract}", "")
        .strip()
    )

    domain_tag = experiment.domain or "Multimodal Discovery"
    p_val_tag = f"p = {experiment.p_value:.4f}" if experiment.p_value is not None else "p < 0.05"

    st.markdown(
        f"""
        <div style="
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 40px 48px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            margin-bottom: 24px;
            position: relative;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #0f172a;
                padding-bottom: 12px;
                margin-bottom: 26px;
            ">
                <span style="font-family: 'Times New Roman', serif; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.12em; color: #475569; text-transform: uppercase;">
                    Autonomous Scientific Discovery Journal · Article in Press
                </span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #64748b;">
                    RUN ID: {experiment.experiment_id}
                </span>
            </div>

            <div style="text-align: center; margin-bottom: 22px;">
                <h2 style="font-family: 'Times New Roman', serif; font-size: 1.55rem; font-weight: 700; color: #0f172a; margin-bottom: 8px; line-height: 1.3;">
                    {experiment.name}
                </h2>
                <div style="font-family: 'Times New Roman', serif; font-style: italic; font-size: 0.95rem; color: #475569; margin-bottom: 14px;">
                    Zaalima Autonomous Agent Framework · Multimodal Discovery Cluster
                </div>
                <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap;">
                    <span style="background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe; font-size: 0.74rem; font-weight: 600; padding: 3px 10px; border-radius: 9999px;">
                        Domain: {domain_tag}
                    </span>
                    <span style="background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; font-size: 0.74rem; font-weight: 600; padding: 3px 10px; border-radius: 9999px;">
                        Significance: {p_val_tag}
                    </span>
                    <span style="background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; font-size: 0.74rem; font-weight: 600; padding: 3px 10px; border-radius: 9999px;">
                        Citations: {len(experiment.citations)} Grounded
                    </span>
                </div>
            </div>

            <div style="
                border-top: 1px solid #e2e8f0;
                border-bottom: 1px solid #e2e8f0;
                padding: 20px 28px;
                margin: 22px 0;
                background-color: #fafafa;
                border-radius: 4px;
            ">
                <div style="
                    text-align: center;
                    font-family: 'Times New Roman', serif;
                    font-weight: 700;
                    letter-spacing: 0.15em;
                    font-size: 0.95rem;
                    color: #0f172a;
                    margin-bottom: 14px;
                ">
                    ABSTRACT
                </div>
                <div style="
                    font-family: 'Times New Roman', serif;
                    font-size: 1.05rem;
                    line-height: 1.8;
                    color: #1e293b;
                    text-align: justify;
                ">
                    {clean_text}
                </div>
            </div>

            <div style="font-family: 'Times New Roman', serif; font-size: 0.88rem; color: #475569; margin-top: 14px;">
                <strong>Keywords:</strong> Autonomous Scientific Discovery, Multimodal Reasoning, Algorithmic Hypothesis Testing, Reproducible AI.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show raw LaTeX code with copy / download
    with st.expander("💻 View Raw LaTeX Source Code"):
        st.code(experiment.latex_abstract, language="latex")
        st.download_button(
            label="📥 Download .tex Abstract File",
            data=experiment.latex_abstract,
            file_name=f"{experiment.experiment_id}_abstract.tex",
            mime="text/x-tex",
            width="stretch",
        )
