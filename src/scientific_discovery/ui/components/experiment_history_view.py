"""
Experiment History View Component.

Displays historical discovery cycles, statistical outcomes, run comparisons,
and provides data export and persistence management for researchers.
"""

import pandas as pd
import streamlit as st
from src.scientific_discovery.memory.experiment_store import ExperimentMemoryStore


def render_history_view(store: ExperimentMemoryStore) -> str:
    """Renders the experiment history table and returns the selected experiment_id."""
    st.subheader("📜 Experiment History & Research Archive")

    experiments = store.list_experiments(limit=100)

    if not experiments:
        st.info("No experiment runs found in the store.")
        if st.button("🌱 Load Sample Discovery Cycles"):
            store.seed_sample_data()
            st.rerun()
        return ""

    # Search bar & Filters
    col_search, col_status, col_domain = st.columns([3, 2, 2])
    with col_search:
        search_query = st.text_input("🔍 Search History (hypothesis, name, code, citation):", "")
    with col_status:
        status_filter = st.selectbox(
            "Status:",
            ["All", "completed", "in_progress", "failed"],
            index=0,
        )
    with col_domain:
        domain_list = sorted(list(set(e.domain for e in experiments)))
        domain_filter = st.selectbox("Domain:", ["All"] + domain_list, index=0)

    # Filter data
    filtered = store.search_experiments(search_query) if search_query else experiments
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

    # Action Toolbar: Export Data
    col_exp1, col_exp2, col_dummy = st.columns([2, 2, 4])
    with col_exp1:
        csv_data = store.export_to_csv()
        st.download_button(
            label="📥 Export History (CSV)",
            data=csv_data,
            file_name="scientific_discovery_history.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_exp2:
        json_data = store.export_to_json()
        st.download_button(
            label="📥 Export History (JSON)",
            data=json_data,
            file_name="scientific_discovery_history.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")

    # Side-by-side Experiment Comparison
    with st.expander("⚖️ Compare Two Experiments Side-by-Side"):
        if len(experiments) >= 2:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cmp_id1 = st.selectbox("Run A:", [e.experiment_id for e in experiments], index=0, key="cmp_a")
            with col_c2:
                cmp_id2 = st.selectbox(
                    "Run B:",
                    [e.experiment_id for e in experiments],
                    index=1 if len(experiments) > 1 else 0,
                    key="cmp_b",
                )

            comparison = store.compare_experiments(cmp_id1, cmp_id2)
            if comparison:
                c_col1, c_col2, c_col3 = st.columns(3)
                with c_col1:
                    st.markdown(f"**Run A: `{cmp_id1}`**")
                    st.write(f"• Name: {comparison['exp1']['name']}")
                    st.write(f"• Status: {comparison['exp1']['status'].upper()}")
                    st.write(f"• P-Value: {comparison['exp1']['p_value']}")
                    st.write(f"• Tokens: {comparison['exp1']['tokens']:,}")
                    st.write(f"• Cost: ${comparison['exp1']['cost_usd']:.4f}")
                    st.write(f"• Runtime: {comparison['exp1']['runtime_ms']} ms")
                with c_col2:
                    st.markdown(f"**Run B: `{cmp_id2}`**")
                    st.write(f"• Name: {comparison['exp2']['name']}")
                    st.write(f"• Status: {comparison['exp2']['status'].upper()}")
                    st.write(f"• P-Value: {comparison['exp2']['p_value']}")
                    st.write(f"• Tokens: {comparison['exp2']['tokens']:,}")
                    st.write(f"• Cost: ${comparison['exp2']['cost_usd']:.4f}")
                    st.write(f"• Runtime: {comparison['exp2']['runtime_ms']} ms")
                with c_col3:
                    st.markdown("**Comparison Delta (A vs B):**")
                    p_diff = comparison.get("p_value_diff")
                    st.metric("P-Value Delta", f"{p_diff:+.4f}" if p_diff is not None else "N/A")
                    st.metric("Cost Delta (USD)", f"${comparison['cost_diff']:+.5f}")
                    st.metric("Runtime Delta", f"{comparison['runtime_diff_ms']:+d} ms")
        else:
            st.info("Need at least 2 experiment runs to compare.")

    # Selector to inspect a specific experiment
    st.markdown("#### 🔍 Load Experiment into Dashboard")
    col_sel, col_del = st.columns([5, 1])
    with col_sel:
        selected_id = st.selectbox(
            "Select Experiment ID:",
            [e.experiment_id for e in experiments],
            format_func=lambda x: f"{x} - {next((e.name for e in experiments if e.experiment_id == x), '')}",
        )
    with col_del:
        st.write("")
        st.write("")
        if st.button("🗑️ Delete", type="secondary", use_container_width=True):
            if store.delete_experiment(selected_id):
                st.success(f"Deleted {selected_id}")
                st.rerun()

    return selected_id
