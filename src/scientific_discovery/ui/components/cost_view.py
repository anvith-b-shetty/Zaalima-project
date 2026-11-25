"""
Cost and Token Telemetry Component.

Tracks LLM token usage, calculates financial execution cost,
and displays resource expenditure across experimental runs.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.scientific_discovery.memory.config import MODEL_PRICING
from src.scientific_discovery.memory.models import ExperimentRun
from src.scientific_discovery.ui.theme import render_section_header


def render_cost_view(experiment: ExperimentRun, summary_metrics: dict) -> None:
    """Renders cost analytics, token counts, and platform expenditure."""
    st.markdown(
        render_section_header(
            title="Execution Cost & Token Telemetry",
            subtitle="Precision token auditing, real-time API cost calculation, and aggregate compute expenditure.",
            icon="💰",
        ),
        unsafe_allow_html=True,
    )

    # Experiment-level cost metrics
    st.markdown(
        f"""
        <div style="margin-bottom: 12px; font-size: 1.02rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
            <span>💳</span>
            <span>Resource Expenditure for Active Run: <code style="font-size: 0.9rem; color: #4f46e5;">{experiment.experiment_id}</code></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Foundation Model", experiment.cost.model_name)
    with c2:
        st.metric("Prompt Tokens (Input)", f"{experiment.cost.prompt_tokens:,}")
    with c3:
        st.metric("Completion Tokens (Output)", f"{experiment.cost.completion_tokens:,}")
    with c4:
        st.metric("Run Cost (USD)", f"${experiment.cost.cost_usd:.5f}")

    # Visual token split
    if experiment.cost.total_tokens > 0:
        ratio = (
            f"{experiment.cost.prompt_tokens / experiment.cost.completion_tokens:.1f}:1"
            if experiment.cost.completion_tokens > 0
            else "N/A"
        )
        avg_cost_1k = (
            (experiment.cost.cost_usd / experiment.cost.total_tokens) * 1000
            if experiment.cost.total_tokens > 0
            else 0.0
        )

        col_chart, col_stats = st.columns([2, 1])

        with col_chart:
            fig_donut = go.Figure(
                data=[
                    go.Pie(
                        labels=["Prompt (Input Context)", "Completion (Agent Output)"],
                        values=[experiment.cost.prompt_tokens, experiment.cost.completion_tokens],
                        hole=0.58,
                        marker=dict(
                            colors=["#4f46e5", "#10b981"],
                            line=dict(color="#ffffff", width=2),
                        ),
                        textinfo="label+percent",
                        hoverinfo="label+value+percent",
                    )
                ]
            )
            fig_donut.update_layout(
                title=dict(
                    text=f"Token Allocation Breakdown ({experiment.cost.total_tokens:,} Total Tokens)",
                    font=dict(family="Plus Jakarta Sans, sans-serif", size=13, color="#0f172a"),
                ),
                font=dict(family="Plus Jakarta Sans, sans-serif"),
                height=290,
                margin=dict(l=10, r=10, t=35, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
            )
            st.plotly_chart(fig_donut, width="stretch")

        with col_stats:
            st.markdown(
                f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 12px;
                    padding: 18px 20px;
                    margin-top: 15px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
                ">
                    <div style="font-size: 0.85rem; font-weight: 700; color: #0f172a; margin-bottom: 12px;">
                        Token Economy Diagnostics
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.8rem; color: #64748b;">Context Input Ratio:</span>
                        <span style="font-size: 0.82rem; font-weight: 700; color: #0f172a; font-family: 'JetBrains Mono', monospace;">
                            {(experiment.cost.prompt_tokens / experiment.cost.total_tokens)*100:.1f}%
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.8rem; color: #64748b;">Output Ratio:</span>
                        <span style="font-size: 0.82rem; font-weight: 700; color: #0f172a; font-family: 'JetBrains Mono', monospace;">
                            {(experiment.cost.completion_tokens / experiment.cost.total_tokens)*100:.1f}%
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.8rem; color: #64748b;">Prompt-to-Output:</span>
                        <span style="font-size: 0.82rem; font-weight: 700; color: #4f46e5; font-family: 'JetBrains Mono', monospace;">
                            {ratio}
                        </span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.8rem; color: #64748b;">Cost / 1k Tokens:</span>
                        <span style="font-size: 0.82rem; font-weight: 700; color: #10b981; font-family: 'JetBrains Mono', monospace;">
                            ${avg_cost_1k:.5f}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Platform-wide Aggregate Statistics
    st.markdown(
        """
        <div style="margin-bottom: 14px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
            <span>🌐</span>
            <span>Platform-Wide Discovery Telemetry (All Runs)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Total Discovery Runs", summary_metrics.get("total_experiments", 0))
    with p2:
        st.metric("Cumulative Tokens", f"{summary_metrics.get('total_tokens', 0):,}")
    with p3:
        st.metric("Total Multi-Agent Spend", f"${summary_metrics.get('total_cost_usd', 0.0):.4f}")
    with p4:
        st.metric("Platform Success Rate", f"{summary_metrics.get('success_rate', 0.0)}%")

    st.markdown("---")

    # Pricing reference table
    with st.expander("ℹ️ Foundation Model Pricing Reference (USD / 1M Tokens)"):
        pricing_data = [
            {
                "Model Identifier": model,
                "Prompt Input / 1M Tokens": f"${rates['prompt']:.2f}",
                "Completion Output / 1M Tokens": f"${rates['completion']:.2f}",
            }
            for model, rates in MODEL_PRICING.items()
        ]
        st.table(pricing_data)
