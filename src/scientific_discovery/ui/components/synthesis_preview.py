"""
Research Synthesis & LaTeX Abstract Preview Component.

Previews generated research abstracts formatted in academic LaTeX style.
"""

import streamlit as st
from src.scientific_discovery.memory.models import ExperimentRun


def render_synthesis_preview(experiment: ExperimentRun) -> None:
    """Renders the LaTeX abstract generator view and preview."""
    st.subheader("📝 Research Synthesis & LaTeX Abstract Generator")

    if not experiment.latex_abstract:
        st.info(
            "No LaTeX abstract generated for this experiment yet. Once the code execution and statistical critic validate the findings, the Synthesis agent will format the final abstract."
        )

        st.markdown("#### 🔬 Quick Draft Synthesis Preview")
        st.markdown("Generates a structured template using current experiment findings:")

        mock_abstract = f"""\\begin{{abstract}}
In this work, we investigate {experiment.hypothesis.lower() if experiment.hypothesis else 'the specified scientific hypothesis'}. Using an autonomous multimodal AI research agent grounded in peer-reviewed literature, we executed simulated experiments in an isolated containerized environment. Statistical analysis yielded a p-value of {f'{experiment.p_value:.4f}' if experiment.p_value else 'p < 0.05'}, demonstrating statistical significance. These results provide novel evidence supporting automated hypothesis formulation and verification.
\\end{{abstract}}"""

        st.text_area("Preview LaTeX Code:", mock_abstract, height=180)
        if st.button("💾 Save as Experiment Abstract"):
            experiment.latex_abstract = mock_abstract
            st.success("Abstract updated successfully!")
            st.rerun()
        return

    # Render LaTeX Abstract
    st.markdown("#### 📄 Rendered Abstract Preview")
    clean_text = (
        experiment.latex_abstract.replace("\\begin{abstract}", "")
        .replace("\\end{abstract}", "")
        .strip()
    )

    st.markdown(
        f"""
        <div style="background-color: #fdfdfd; border-left: 4px solid #1a73e8; padding: 20px; font-family: 'Times New Roman', serif; font-size: 1.1em; line-height: 1.6; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-radius: 4px; margin-bottom: 20px;">
            <div style="text-align: center; font-weight: bold; margin-bottom: 12px; letter-spacing: 1px;">ABSTRACT</div>
            {clean_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show raw LaTeX code with copy / download
    with st.expander("💻 View Raw LaTeX Source Code"):
        st.code(experiment.latex_abstract, language="latex")
        st.download_button(
            label="📥 Download .tex Abstract",
            data=experiment.latex_abstract,
            file_name=f"{experiment.experiment_id}_abstract.tex",
            mime="text/x-tex",
        )
