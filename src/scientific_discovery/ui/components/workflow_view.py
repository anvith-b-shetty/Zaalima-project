"""
Workflow View Component.

Displays multi-agent execution status, logic progression DAG, duration metrics,
and real-time execution monitoring for supervisors.
"""

import plotly.express as px
import streamlit as st
from src.scientific_discovery.memory.models import ExperimentRun, WorkflowStep
from src.scientific_discovery.memory.workflow_tracker import PIPELINE_STAGES, WorkflowTracker


AGENT_DISPLAY_NAMES = {
    "literature_reviewer": "1. Literature Reviewer",
    "hypothesis_generator": "2. Hypothesis Generator",
    "code_executor": "3. Code Executor",
    "critic_agent": "4. Statistical Critic",
    "synthesis": "5. Synthesis Engine",
}

STATUS_BADGES = {
    "completed": "🟢 Completed",
    "running": "🔵 Running...",
    "pending": "⚪ Pending",
    "failed": "🔴 Failed",
    "retrying": "🟡 Retrying (RL Loop)",
}

STATUS_BORDER_COLORS = {
    "completed": "#34a853",
    "running": "#4285f4",
    "failed": "#ea4335",
    "retrying": "#fbbc04",
    "pending": "#dadce0",
}


def render_workflow_view(experiment: ExperimentRun) -> None:
    """Renders the agent workflow logic tree, pipeline DAG, and execution progress."""
    st.subheader("🤖 Autonomous Agent Workflow Monitoring")

    # Workflow summary metrics from WorkflowTracker
    summary = WorkflowTracker.get_workflow_summary(experiment)

    # 1. Overview Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Experiment ID", experiment.experiment_id)
    with col2:
        st.metric("Domain", experiment.domain)
    with col3:
        st.metric("Overall Status", experiment.status.upper())
    with col4:
        st.metric("Total Execution Steps", len(experiment.workflow_steps))

    # 2. Pipeline Progression Bar
    progress_val = min(1.0, summary["completed_stages"] / summary["total_stages"])
    st.progress(
        progress_val,
        text=f"Pipeline Progress: {summary['progress_percent']}% ({summary['completed_stages']}/{summary['total_stages']} Stages Completed)",
    )

    # 3. Visual Multi-Agent Pipeline DAG Cards
    st.markdown("#### 🗺️ Multi-Agent Architecture Pipeline")
    flow_cols = st.columns(len(PIPELINE_STAGES))

    for i, role in enumerate(PIPELINE_STAGES):
        status = summary["stage_status"].get(role, "pending")
        duration = summary["stage_durations"].get(role, 0)
        badge = STATUS_BADGES.get(status, "⚪ Pending")
        border_color = STATUS_BORDER_COLORS.get(status, "#dadce0")
        dur_label = f"{duration:,} ms" if duration > 0 else "—"

        with flow_cols[i]:
            st.markdown(
                f"""
                <div style="border: 2px solid {border_color}; border-radius: 8px; padding: 12px 8px; text-align: center; background: #ffffff; min-height: 105px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
                    <div style="font-weight: 700; font-size: 0.82rem; color: #1a237e;">{AGENT_DISPLAY_NAMES[role]}</div>
                    <div style="margin-top: 6px; font-size: 0.78rem;">{badge}</div>
                    <div style="margin-top: 6px; font-size: 0.75rem; color: #5f6368; font-weight: 500;">⏱️ {dur_label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 4. Latency & Performance Breakdown
    st.markdown("#### ⚡ Pipeline Execution & Latency Telemetry")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Total Pipeline Latency", f"{summary['total_duration_ms']:,} ms")
    with p2:
        bottleneck = summary["bottleneck_stage"]
        b_label = AGENT_DISPLAY_NAMES.get(bottleneck, "None") if bottleneck else "N/A"
        st.metric("Bottleneck Stage", b_label)
    with p3:
        avg_dur = (
            int(summary["total_duration_ms"] / len(experiment.workflow_steps))
            if experiment.workflow_steps
            else 0
        )
        st.metric("Avg Step Duration", f"{avg_dur:,} ms")
    with p4:
        st.metric("Self-Debugging Retries", summary["retry_count"])

    # Latency Bar Chart
    durations_data = [
        {
            "Agent Stage": AGENT_DISPLAY_NAMES.get(role, role),
            "Duration (ms)": summary["stage_durations"].get(role, 0),
            "Status": summary["stage_status"].get(role, "pending").capitalize(),
        }
        for role in PIPELINE_STAGES
        if summary["stage_durations"].get(role, 0) > 0
    ]
    if durations_data:
        fig_bar = px.bar(
            durations_data,
            x="Duration (ms)",
            y="Agent Stage",
            color="Status",
            color_discrete_map={
                "Completed": "#34a853",
                "Running": "#4285f4",
                "Failed": "#ea4335",
                "Retrying": "#fbbc04",
            },
            orientation="h",
            title="Agent Stage Latency Breakdown (Execution Time in ms)",
            height=230,
        )
        fig_bar.update_layout(margin=dict(l=10, r=10, t=35, b=10))
        st.plotly_chart(fig_bar, width="stretch")

    st.markdown("---")

    # 5. Formulated Scientific Hypothesis Section
    st.markdown("#### 💡 Formulated Scientific Hypothesis")
    if experiment.hypothesis:
        st.info(f"**Hypothesis:** {experiment.hypothesis}")
    else:
        st.warning("No hypothesis has been generated for this run yet.")

    # 6. Detailed Step-by-Step Execution Traces
    st.markdown("#### 🔄 Step-by-Step Execution Traces")
    if not experiment.workflow_steps:
        st.info("No workflow steps recorded yet. Start an experiment to begin tracking.")
        return

    for idx, step in enumerate(experiment.workflow_steps, start=1):
        agent_label = AGENT_DISPLAY_NAMES.get(step.agent_role, step.agent_role)
        status_label = STATUS_BADGES.get(step.status, step.status)

        with st.expander(f"**Step {idx}: {step.title}** — {status_label}", expanded=(step.status in ["running", "failed", "retrying"])):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**Agent:** `{agent_label}`")
                st.markdown(f"**Description:** {step.description}")
            with col_b:
                if step.duration_ms > 0:
                    st.metric("Duration", f"{step.duration_ms} ms")
                if step.started_at:
                    st.caption(f"Started: {step.started_at.strftime('%H:%M:%S UTC')}")

            if step.logs:
                st.markdown("**Execution Logs:**")
                log_text = "\n".join(f"[{i+1}] {line}" for i, line in enumerate(step.logs))
                st.code(log_text, language="text")

    # 7. Sandbox Code & Output Preview
    if experiment.generated_code or experiment.execution_stdout:
        st.markdown("---")
        st.markdown("#### 🧪 Sandbox Code & Execution Output")
        tab_code, tab_out = st.tabs(["Generated Python Code", "Docker Sandbox Output"])

        with tab_code:
            if experiment.generated_code:
                st.code(experiment.generated_code, language="python")
            else:
                st.caption("No code generated yet.")

        with tab_out:
            if experiment.execution_stdout:
                st.code(experiment.execution_stdout, language="text")
            if experiment.execution_stderr:
                st.error(f"Stderr:\n{experiment.execution_stderr}")
            if not experiment.execution_stdout and not experiment.execution_stderr:
                st.caption("No execution output captured yet.")
