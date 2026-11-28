"""
Workflow View Component.

Displays multi-agent execution status, logic progression DAG, duration metrics,
and real-time execution monitoring for supervisors.
"""

import plotly.express as px
import streamlit as st
from src.scientific_discovery.memory.models import ExperimentRun, WorkflowStep
from src.scientific_discovery.memory.workflow_tracker import PIPELINE_STAGES, WorkflowTracker
from src.scientific_discovery.ui.theme import render_section_header


AGENT_METADATA = {
    "literature_reviewer": {
        "num": "01",
        "name": "Literature Reviewer",
        "icon": "📚",
        "desc": "ArXiv / PubMed Mining",
    },
    "hypothesis_generator": {
        "num": "02",
        "name": "Hypothesis Generator",
        "icon": "💡",
        "desc": "Multimodal Formulation",
    },
    "code_executor": {
        "num": "03",
        "name": "Code Executor",
        "icon": "💻",
        "desc": "Docker Sandbox Execution",
    },
    "critic_agent": {
        "num": "04",
        "name": "Statistical Critic",
        "icon": "⚖️",
        "desc": "Significance & P-Value Audit",
    },
    "synthesis": {
        "num": "05",
        "name": "Synthesis Engine",
        "icon": "📝",
        "desc": "Academic LaTeX Authoring",
    },
}

AGENT_DISPLAY_NAMES = {
    role: f"{data['num']}. {data['name']}" for role, data in AGENT_METADATA.items()
}

STATUS_CONFIG = {
    "completed": {
        "badge": "Completed",
        "icon": "✓",
        "bg": "#ecfdf5",
        "color": "#059669",
        "border": "#10b981",
        "pulse": False,
    },
    "running": {
        "badge": "Active",
        "icon": "●",
        "bg": "#eff6ff",
        "color": "#2563eb",
        "border": "#3b82f6",
        "pulse": True,
    },
    "retrying": {
        "badge": "RL Retry",
        "icon": "↻",
        "bg": "#fffbeb",
        "color": "#d97706",
        "border": "#f59e0b",
        "pulse": True,
    },
    "failed": {
        "badge": "Failed",
        "icon": "✕",
        "bg": "#fef2f2",
        "color": "#dc2626",
        "border": "#ef4444",
        "pulse": False,
    },
    "pending": {
        "badge": "Queued",
        "icon": "○",
        "bg": "#f8fafc",
        "color": "#64748b",
        "border": "#cbd5e1",
        "pulse": False,
    },
}

STATUS_BADGES = {
    "completed": "🟢 Completed",
    "running": "🔵 Running...",
    "pending": "⚪ Pending",
    "failed": "🔴 Failed",
    "retrying": "🟡 Retrying (RL Loop)",
}


def render_workflow_view(experiment: ExperimentRun) -> None:
    """Renders the agent workflow logic tree, pipeline DAG, and execution progress."""
    st.markdown(
        render_section_header(
            title="Autonomous Multi-Agent Workflow Monitoring",
            subtitle="Real-time execution DAG, agent handoffs, latency telemetry, and Docker sandbox audit trails.",
            icon="🤖",
        ),
        unsafe_allow_html=True,
    )

    # Workflow summary metrics from WorkflowTracker
    summary = WorkflowTracker.get_workflow_summary(experiment)

    # 1. Overview Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Experiment ID", experiment.experiment_id)
    with col2:
        st.metric("Research Domain", experiment.domain)
    with col3:
        st.metric("Pipeline State", experiment.status.upper())
    with col4:
        st.metric("Execution Steps", len(experiment.workflow_steps))

    # 2. Pipeline Progression Bar with clean header
    progress_val = min(1.0, summary["completed_stages"] / summary["total_stages"])
    prog_header = (
        f'<div style="margin-top: 20px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">'
        f'<span style="font-size: 0.85rem; font-weight: 700; color: #334155; text-transform: uppercase; letter-spacing: 0.05em;">Autonomous Pipeline Progress</span>'
        f'<span style="font-size: 0.82rem; font-weight: 700; color: #4f46e5; background: #eef2ff; padding: 2px 10px; border-radius: 9999px;">{summary["progress_percent"]}% ({summary["completed_stages"]} of {summary["total_stages"]} Stages Completed)</span>'
        f'</div>'
    )
    st.markdown(prog_header, unsafe_allow_html=True)
    st.progress(progress_val)

    # 3. Visual Multi-Agent Pipeline DAG Cards
    st.markdown(
        '<div style="margin-top: 24px; margin-bottom: 14px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">'
        '<span>🗺️</span><span>Multi-Agent Architecture Pipeline DAG</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    flow_cols = st.columns(len(PIPELINE_STAGES))

    for i, role in enumerate(PIPELINE_STAGES):
        meta = AGENT_METADATA.get(role, {"num": f"0{i+1}", "name": role, "icon": "⚙️", "desc": ""})
        status = summary["stage_status"].get(role, "pending")
        duration = summary["stage_durations"].get(role, 0)
        cfg = STATUS_CONFIG.get(status, STATUS_CONFIG["pending"])
        dur_label = f"{duration:,} ms" if duration > 0 else "Pending"
        pulse_dot = '<span class="live-pulse"></span>' if cfg["pulse"] else ""

        with flow_cols[i]:
            card_html = (
                f'<div style="background:#ffffff; border:1px solid {cfg["border"]}; border-top:4px solid {cfg["border"]}; border-radius:12px; padding:16px 10px; text-align:center; min-height:155px; box-shadow:0 2px 8px rgba(0,0,0,0.04); position:relative;">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">'
                f'<span style="font-size:0.68rem; font-weight:800; color:#94a3b8; letter-spacing:0.08em;">STAGE {meta["num"]}</span>'
                f'<span style="font-size:0.72rem; font-weight:700; background:{cfg["bg"]}; color:{cfg["color"]}; padding:2px 8px; border-radius:9999px; display:inline-flex; align-items:center; gap:3px;">'
                f'{pulse_dot}<span>{cfg["icon"]} {cfg["badge"]}</span></span></div>'
                f'<div style="font-size:1.5rem; margin-bottom:6px;">{meta["icon"]}</div>'
                f'<div style="font-weight:700; font-size:0.85rem; color:#0f172a; line-height:1.25; margin-bottom:4px;">{meta["name"]}</div>'
                f'<div style="font-size:0.72rem; color:#64748b; margin-bottom:12px; height:18px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{meta["desc"]}</div>'
                f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:3px 6px; font-size:0.74rem; font-weight:600; color:#475569; font-family:JetBrains Mono,monospace;">⏱️ {dur_label}</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("---")

    # 4. Latency & Performance Breakdown
    st.markdown(
        '<div style="margin-bottom: 14px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">'
        '<span>⚡</span><span>Pipeline Execution & Latency Telemetry</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Total Pipeline Latency", f"{summary['total_duration_ms']:,} ms")
    with p2:
        bottleneck = summary["bottleneck_stage"]
        b_label = AGENT_METADATA.get(bottleneck, {}).get("name", "None") if bottleneck else "N/A"
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
                "Completed": "#10b981",
                "Running": "#3b82f6",
                "Failed": "#ef4444",
                "Retrying": "#f59e0b",
            },
            orientation="h",
            title="Agent Stage Latency Breakdown (Execution Time in ms)",
            height=250,
        )
        fig_bar.update_layout(
            margin=dict(l=10, r=20, t=40, b=10),
            font=dict(family="Plus Jakarta Sans, sans-serif", size=12),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor="rgba(226, 232, 240, 0.7)"),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_bar, width="stretch")

    st.markdown("---")

    # 5. Formulated Scientific Hypothesis Section
    st.markdown(
        '<div style="margin-bottom: 10px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">'
        '<span>💡</span><span>Formulated Scientific Hypothesis</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    if experiment.hypothesis:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#eff6ff 0%,#f0fdf4 100%); border:1px solid #bfdbfe; border-left:5px solid #3b82f6; border-radius:12px; padding:18px 22px; box-shadow:0 1px 3px rgba(0,0,0,0.04);">'
            f'<div style="font-size:0.76rem; font-weight:700; text-transform:uppercase; color:#2563eb; letter-spacing:0.05em; margin-bottom:4px;">Active Testable Hypothesis</div>'
            f'<div style="font-size:1.05rem; color:#1e293b; font-weight:600; line-height:1.55;">"{experiment.hypothesis}"</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("No hypothesis has been generated for this run yet.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 6. Detailed Step-by-Step Execution Traces
    st.markdown(
        '<div style="margin-bottom: 12px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">'
        '<span>🔄</span><span>Step-by-Step Execution Traces & Agent Heartbeats</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    if not experiment.workflow_steps:
        st.info("No workflow steps recorded yet. Start an experiment to begin tracking.")
        return

    for idx, step in enumerate(experiment.workflow_steps, start=1):
        agent_label = AGENT_DISPLAY_NAMES.get(step.agent_role, step.agent_role)
        status_label = STATUS_BADGES.get(step.status, step.status)

        with st.expander(
            f"Step {idx}: {step.title} — {status_label}",
            expanded=(step.status in ["running", "failed", "retrying"]),
        ):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**Agent Role:** `{agent_label}`")
                st.markdown(f"**Description:** {step.description}")
            with col_b:
                if step.duration_ms > 0:
                    st.metric("Duration", f"{step.duration_ms} ms")
                if step.started_at:
                    st.caption(f"Timestamp: {step.started_at.strftime('%H:%M:%S UTC')}")

            if step.logs:
                st.markdown("**Execution Heartbeat Logs:**")
                log_text = "\n".join(f"[{i+1}] {line}" for i, line in enumerate(step.logs))
                st.code(log_text, language="text")

    # 7. Sandbox Code & Output Preview
    if experiment.generated_code or experiment.execution_stdout:
        st.markdown("---")
        st.markdown(
            '<div style="margin-bottom: 12px; font-size: 1.05rem; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 8px;">'
            '<span>🧪</span><span>Sandbox Code & Execution Output</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        tab_code, tab_out = st.tabs(["💻 Generated Python Code", "📄 Docker Sandbox Output"])

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
