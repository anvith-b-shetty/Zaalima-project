"""
Experiment History View Component.

Displays historical discovery cycles, statistical outcomes, and past runs.
"""

import pandas as pd
import streamlit as st
from src.scientific_discovery.memory.experiment_store import ExperimentMemoryStore


def render_history_view(store: ExperimentMemoryStore) -> str:
    """Renders the experiment history table and returns the selected experiment_id."""
    st.subheader("📜 Experiment History & Run Archive")

    experiments = store.list_experiments(limit=100)

    if not experiments:
        st.info("No experiment runs found in the store.")
        if st.button("🌱 Load Sample Discovery Cycles"):
            store.seed_sample_data()
            st.rerun()
        return ""

    # Filters
    col_filter1, col_filter2 = st.columns([2, 2])
    with col_filter1:
        status_filter = st.selectbox(
            "Filter by Status:",
            ["All", "completed", "in_progress", "failed"],
            index=0,
        )
    with col_filter2:
        domain_list = sorted(list(set(e.domain for e in experiments)))
        domain_filter = st.selectbox("Filter by Domain:", ["All"] + domain_list, index=0)

    # Filter data
    filtered = experiments
    if status_filter != "All":
        filtered = [e for e in filtered if e.status == status_filter]
    if domain_filter != "All":
        filtered = [e for e in filtered if e.domain == domain_filter]

    # Convert to display table
    records = []
    for e in filtered:
        records.append(
            {
                "ID": e.experiment_id,
                "Name": e.name,
                "Domain": e.domain,
                "Status": e.status.upper(),
                "P-Value": f"{e.p_value:.4f}" if e.p_value is not None else "N/A",
                "Tokens": f"{e.cost.total_tokens:,}",
                "Cost ($)": f"${e.cost.cost_usd:.4f}",
                "Citations": len(e.citations),
                "Steps": len(e.workflow_steps),
                "Created (UTC)": e.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        )

    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Selector to inspect a specific experiment
    st.markdown("#### 🔍 Inspect Past Run")
    selected_id = st.selectbox(
        "Select Experiment ID to load into Dashboard:",
        [e.experiment_id for e in experiments],
        format_func=lambda x: f"{x} - {next((e.name for e in experiments if e.experiment_id == x), '')}",
    )

    return selected_id
