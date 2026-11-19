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


def render_cost_view(experiment: ExperimentRun, summary_metrics: dict) -> None:
    """Renders cost analytics, token counts, and platform expenditure."""
    st.subheader("💰 Execution Cost & Token Telemetry")

    # Experiment-level cost metrics
    st.markdown(f"#### Run Cost for `{experiment.experiment_id}`")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Model", experiment.cost.model_name)
    with c2:
        st.metric("Prompt Tokens", f"{experiment.cost.prompt_tokens:,}")
    with c3:
        st.metric("Completion Tokens", f"{experiment.cost.completion_tokens:,}")
    with c4:
        st.metric("Run Cost (USD)", f"${experiment.cost.cost_usd:.5f}")

    # Visual token split
    if experiment.cost.total_tokens > 0:
        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=["Prompt (Input)", "Completion (Output)"],
                    values=[experiment.cost.prompt_tokens, experiment.cost.completion_tokens],
                    hole=0.45,
                    marker=dict(colors=["#4285F4", "#34A853"]),
                )
            ]
        )
        fig_donut.update_layout(
            title_text=f"Token Breakdown ({experiment.cost.total_tokens:,} total tokens)",
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("---")

    # Platform-wide Aggregate Statistics
    st.markdown("#### 🌐 Platform-Wide Aggregates (All Runs)")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Total Platform Runs", summary_metrics.get("total_experiments", 0))
    with p2:
        st.metric("Total Tokens Consumed", f"{summary_metrics.get('total_tokens', 0):,}")
    with p3:
        st.metric("Total LLM Spend", f"${summary_metrics.get('total_cost_usd', 0.0):.4f}")
    with p4:
        st.metric("Platform Success Rate", f"{summary_metrics.get('success_rate', 0.0)}%")

    st.markdown("---")

    # Pricing reference table
    with st.expander("ℹ️ Model Pricing Reference Table (USD / 1M Tokens)"):
        pricing_data = [
            {
                "Model": model,
                "Prompt / 1M Tokens": f"${rates['prompt']:.2f}",
                "Completion / 1M Tokens": f"${rates['completion']:.2f}",
            }
            for model, rates in MODEL_PRICING.items()
        ]
        st.table(pricing_data)
