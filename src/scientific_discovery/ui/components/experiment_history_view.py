"""
Experiment History View Component.

Displays historical discovery cycles, statistical outcomes, run comparisons,
and provides data export and persistence management for researchers.
"""

import pandas as pd
import streamlit as st
from src.scientific_discovery.memory.experiment_store import ExperimentMemoryStore
from src.scientific_discovery.ui.theme import render_section_header


def render_history_view(store: ExperimentMemoryStore) -> str:
    """Renders the experiment history table and returns the selected experiment_id."""
    st.markdown(
        render_section_header(
            title="Experiment History & Research Archive",
            subtitle="Permanent discovery archive, multi-run parametric comparison, and verifiable research data export.",
            icon="📜",
        ),
        unsafe_allow_html=True,
    )

    experiments = store.list_experiments(limit=100)

    if not experiments:
        st.markdown(
            """
            <div style="
                background: #ffffff;
                border: 2px dashed #cbd5e1;
                border-radius: 14px;
                padding: 36px 24px;
                text-align: center;
                margin-top: 10px;
            ">
                <div style="font-size: 2.2rem; margin-bottom: 8px;">📜</div>
                <div style="font-weight: 700; color: #0f172a; font-size: 1.1rem; margin-bottom: 4px;">
                    No Experiment Runs Found
                </div>
                <div style="font-size: 0.88rem; color: #64748b; max-width: 450px; margin: 0 auto;">
                    Load sample discovery cycles to explore the archive interface.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🌱 Load Sample Discovery Cycles", width="stretch"):
            store.seed_sample_data()
            st.rerun()
        return ""

    # Search bar & Filters
    col_search, col_status, col_domain = st.columns([3, 2, 2])
    with col_search:
        search_query = st.text_input("🔍 Search Archive (Hypothesis, Name, Code, Findings):", "")
    with col_status:
        status_filter = st.selectbox(
            "Filter Status:",
            ["All", "completed", "in_progress", "failed"],
            index=0,
        )
    with col_domain:
        domain_list = sorted(list(set(e.domain for e in experiments)))
        domain_filter = st.selectbox("Filter Domain:", ["All"] + domain_list, index=0)

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
                "Experiment Name": e.name,
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

    st.markdown(
        f"<div style='font-size: 0.82rem; color: #64748b; margin-bottom: 8px;'>Showing <strong>{len(filtered)}</strong> of {len(experiments)} experiment runs:</div>",
        unsafe_allow_html=True,
    )

    st.dataframe(df, width="stretch", hide_index=True)

    # Action Toolbar: Export Data
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    col_exp1, col_exp2, col_dummy = st.columns([2, 2, 4])
    with col_exp1:
        csv_data = store.export_to_csv()
        st.download_button(
            label="📥 Export Archive (CSV)",
            data=csv_data,
            file_name="scientific_discovery_history.csv",
            mime="text/csv",
            width="stretch",
        )
    with col_exp2:
        json_data = store.export_to_json()
        st.download_button(
            label="📥 Export Archive (JSON)",
            data=json_data,
            file_name="scientific_discovery_history.json",
            mime="application/json",
            width="stretch",
        )

    st.markdown("---")

    # Side-by-side Experiment Comparison
    with st.expander("⚖️ Multi-Run Comparative Analysis (Side-by-Side)", expanded=False):
        if len(experiments) >= 2:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cmp_id1 = st.selectbox("Run A (Baseline):", [e.experiment_id for e in experiments], index=0, key="cmp_a")
            with col_c2:
                cmp_id2 = st.selectbox(
                    "Run B (Candidate):",
                    [e.experiment_id for e in experiments],
                    index=1 if len(experiments) > 1 else 0,
                    key="cmp_b",
                )

            comparison = store.compare_experiments(cmp_id1, cmp_id2)
            if comparison:
                c_col1, c_col2, c_col3 = st.columns(3)
                with c_col1:
                    st.markdown(
                        f"""
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #4f46e5; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                            <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem; margin-bottom: 10px;">
                                🅰️ Baseline: <code style="color: #4f46e5;">{cmp_id1}</code>
                            </div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>Name:</strong> {comparison['exp1']['name']}</div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>Status:</strong> {comparison['exp1']['status'].upper()}</div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>P-Value:</strong> {comparison['exp1']['p_value']}</div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>Tokens:</strong> {comparison['exp1']['tokens']:,}</div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>Cost:</strong> ${comparison['exp1']['cost_usd']:.4f}</div>
                            <div style="font-size: 0.83rem; color: #475569;"><strong>Runtime:</strong> {comparison['exp1']['runtime_ms']} ms</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_col2:
                    st.markdown(
                        f"""
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #10b981; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                            <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem; margin-bottom: 10px;">
                                🅱️ Candidate: <code style="color: #10b981;">{cmp_id2}</code>
                            </div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>Name:</strong> {comparison['exp2']['name']}</div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>Status:</strong> {comparison['exp2']['status'].upper()}</div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>P-Value:</strong> {comparison['exp2']['p_value']}</div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>Tokens:</strong> {comparison['exp2']['tokens']:,}</div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 5px;"><strong>Cost:</strong> ${comparison['exp2']['cost_usd']:.4f}</div>
                            <div style="font-size: 0.83rem; color: #475569;"><strong>Runtime:</strong> {comparison['exp2']['runtime_ms']} ms</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_col3:
                    p_diff = comparison.get("p_value_diff")
                    cost_diff = comparison["cost_diff"]
                    runtime_diff = comparison["runtime_diff_ms"]

                    # Color-code deltas
                    cost_color = "#10b981" if cost_diff <= 0 else "#ef4444"
                    runtime_color = "#10b981" if runtime_diff <= 0 else "#ef4444"

                    st.markdown(
                        f"""
                        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-top: 3px solid #f59e0b; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                            <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem; margin-bottom: 10px;">
                                📊 Comparison Delta
                            </div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 8px;">
                                <strong>P-Value Δ:</strong>
                                <span style="font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #0f172a;">
                                    {f'{p_diff:+.4f}' if p_diff is not None else 'N/A'}
                                </span>
                            </div>
                            <div style="font-size: 0.83rem; color: #475569; margin-bottom: 8px;">
                                <strong>Cost Δ:</strong>
                                <span style="font-weight: 700; font-family: 'JetBrains Mono', monospace; color: {cost_color};">
                                    ${cost_diff:+.5f}
                                </span>
                            </div>
                            <div style="font-size: 0.83rem; color: #475569;">
                                <strong>Runtime Δ:</strong>
                                <span style="font-weight: 700; font-family: 'JetBrains Mono', monospace; color: {runtime_color};">
                                    {runtime_diff:+d} ms
                                </span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Need at least 2 experiment runs to compare.")

    # Selector to inspect a specific experiment
    st.markdown(
        """
        <div style="margin-top: 10px; margin-bottom: 12px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">
            <span>🔍</span>
            <span>Switch Active Experiment or Purge Run</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_sel, col_del = st.columns([5, 1])
    with col_sel:
        selected_id = st.selectbox(
            "Select Experiment Run ID:",
            [e.experiment_id for e in experiments],
            format_func=lambda x: f"{x} - {next((e.name for e in experiments if e.experiment_id == x), '')}",
        )
    with col_del:
        st.write("")
        st.write("")
        if st.button("🗑️ Delete Run", type="secondary", width="stretch"):
            if store.delete_experiment(selected_id):
                st.success(f"Deleted {selected_id}")
                st.rerun()

    return selected_id
