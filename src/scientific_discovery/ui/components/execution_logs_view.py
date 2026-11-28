"""
Execution Logs View Component.

Provides a dedicated developer terminal and log inspector for multi-agent
execution traces, Docker sandbox stdout/stderr, and runtime diagnostic filtering.
"""

from datetime import datetime
import streamlit as st
from src.scientific_discovery.memory.models import ExperimentRun
from src.scientific_discovery.ui.theme import render_section_header


def render_execution_logs_view(experiment: ExperimentRun) -> None:
    """Renders the execution logs console and container diagnostic view."""
    st.markdown(
        render_section_header(
            title="Real-Time Execution Logs & Console",
            subtitle="Developer terminal, multi-agent heartbeat telemetry, and containerized stdout/stderr auditing.",
            icon="📟",
        ),
        unsafe_allow_html=True,
    )

    if not experiment.workflow_steps and not experiment.execution_stdout and not experiment.execution_stderr:
        st.info("No execution logs recorded for this experiment yet.")
        return

    # Aggregate all logs from steps and sandbox
    all_log_entries = []
    for step in experiment.workflow_steps:
        time_str = step.started_at.strftime("%H:%M:%S") if step.started_at else "--:--:--"
        agent_tag = step.agent_role.upper()

        # Add initial step log
        all_log_entries.append({
            "timestamp": time_str,
            "agent": step.agent_role,
            "level": "INFO",
            "message": f"[{agent_tag}] Started: {step.title} - {step.description}",
        })

        for log_line in step.logs:
            lvl = "ERROR" if "error" in log_line.lower() or "fail" in log_line.lower() else "INFO"
            all_log_entries.append({
                "timestamp": time_str,
                "agent": step.agent_role,
                "level": lvl,
                "message": f"[{agent_tag}] {log_line}",
            })

        if step.status == "completed":
            all_log_entries.append({
                "timestamp": time_str,
                "agent": step.agent_role,
                "level": "SUCCESS",
                "message": f"[{agent_tag}] Completed successfully in {step.duration_ms}ms",
            })
        elif step.status == "failed":
            all_log_entries.append({
                "timestamp": time_str,
                "agent": step.agent_role,
                "level": "ERROR",
                "message": f"[{agent_tag}] Step FAILED after {step.duration_ms}ms",
            })

    # Add Docker sandbox logs
    if experiment.execution_stdout:
        for line in experiment.execution_stdout.strip().split("\n"):
            all_log_entries.append({
                "timestamp": "SANDBOX",
                "agent": "code_executor",
                "level": "INFO",
                "message": f"[DOCKER STDOUT] {line}",
            })

    if experiment.execution_stderr:
        for line in experiment.execution_stderr.strip().split("\n"):
            all_log_entries.append({
                "timestamp": "SANDBOX",
                "agent": "code_executor",
                "level": "ERROR",
                "message": f"[DOCKER STDERR] {line}",
            })

    # Summary metrics top row
    err_count = sum(1 for e in all_log_entries if e["level"] == "ERROR")
    succ_count = sum(1 for e in all_log_entries if e["level"] == "SUCCESS")
    l1, l2, l3, l4 = st.columns(4)
    with l1:
        st.metric("Total Log Entries", len(all_log_entries))
    with l2:
        st.metric("Success Events", succ_count)
    with l3:
        st.metric("Errors Detected", err_count)
    with l4:
        st.metric("Docker Captures", len([e for e in all_log_entries if e["timestamp"] == "SANDBOX"]))

    # Filter Toolbar
    c_search, c_agent, c_level = st.columns([3, 2, 2])
    with c_search:
        log_query = st.text_input("🔍 Search Terminal Logs:", "", key="log_search_input")
    with c_agent:
        agent_options = ["All"] + sorted(list(set(e["agent"] for e in all_log_entries)))
        selected_agent = st.selectbox("Agent Role:", agent_options, index=0)
    with c_level:
        level_options = ["All", "INFO", "SUCCESS", "ERROR", "WARNING"]
        selected_level = st.selectbox("Log Severity:", level_options, index=0)

    # Filter matching entries
    filtered_logs = all_log_entries
    if selected_agent != "All":
        filtered_logs = [e for e in filtered_logs if e["agent"] == selected_agent]
    if selected_level != "All":
        filtered_logs = [e for e in filtered_logs if e["level"] == selected_level]
    if log_query:
        filtered_logs = [e for e in filtered_logs if log_query.lower() in e["message"].lower()]

    st.markdown(f"<div style='font-size: 0.82rem; color: #64748b; margin-bottom: 8px;'>Showing <strong>{len(filtered_logs)}</strong> of {len(all_log_entries)} console lines:</div>", unsafe_allow_html=True)

    # Terminal styling
    formatted_lines = []
    for entry in filtered_logs:
        lvl = entry["level"]
        color = "#10b981" if lvl == "SUCCESS" else ("#ef4444" if lvl == "ERROR" else "#e2e8f0")
        tag_bg = "#064e3b" if lvl == "SUCCESS" else ("#7f1d1d" if lvl == "ERROR" else "#334155")
        formatted_lines.append(
            f'<div style="font-family: \'JetBrains Mono\', Consolas, monospace; font-size: 0.82rem; line-height: 1.6; color: {color}; margin-bottom: 2px;">'
            f'<span style="color: #64748b;">[{entry["timestamp"]}]</span> '
            f'<span style="background: {tag_bg}; color: #ffffff; padding: 1px 6px; border-radius: 4px; font-weight: 700; font-size: 0.72rem;">{entry["level"]}</span> '
            f'<span>{entry["message"]}</span>'
            f'</div>'
        )

    log_box_html = (
        '<div style="background-color: #0f172a; border-radius: 10px; padding: 18px; max-height: 440px; overflow-y: auto; border: 1px solid #1e293b; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5); margin-bottom: 14px;">'
        + ("".join(formatted_lines) if formatted_lines else '<div style="color: #64748b; font-family: \'JetBrains Mono\', monospace;">No matching log records found for current filter.</div>')
        + '</div>'
    )

    st.markdown(log_box_html, unsafe_allow_html=True)

    # Raw log download
    raw_log_text = "\n".join(f"[{e['timestamp']}] [{e['level']}] {e['message']}" for e in all_log_entries)
    st.download_button(
        label="📥 Download Full Execution Log (.log)",
        data=raw_log_text,
        file_name=f"{experiment.experiment_id}_execution.log",
        mime="text/plain",
        width="stretch",
    )
