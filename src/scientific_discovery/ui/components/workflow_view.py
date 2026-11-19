"""
Workflow View Component.

Displays multi-agent execution status, logic progression, and real-time logs.
"""

import streamlit as st
from src.scientific_discovery.memory.models import ExperimentRun, WorkflowStep


AGENT_DISPLAY_NAMES = {
    "literature_reviewer": "1. Literature Reviewer (ArXiv / PubMed)",
    "hypothesis_generator": "2. Hypothesis Generator (RAG)",
    "code_executor": "3. Code Executor (Docker Sandbox)",
    "critic_agent": "4. Statistical Critic (Significance & p-values)",
    "synthesis": "5. Synthesis (LaTeX Abstract)",
}

STATUS_BADGES = {
    "completed": "🟢 Completed",
    "running": "🔵 Running...",
    "pending": "⚪ Pending",
    "failed": "🔴 Failed",
    "retrying": "🟡 Retrying (RL Loop)",
}


def render_workflow_view(experiment: ExperimentRun) -> None:
    """Renders the agent workflow logic tree and execution progress."""
    st.subheader("🤖 Autonomous Agent Workflow & Logic Tree")

    # Workflow progress overview cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Experiment ID", experiment.experiment_id)
    with col2:
        st.metric("Domain", experiment.domain)
    with col3:
        status_color = "green" if experiment.status == "completed" else "blue"
        st.metric("Status", experiment.status.upper())
    with col4:
        st.metric("Total Steps", len(experiment.workflow_steps))

    st.markdown("---")

    # Hypothesis Section
    with st.container():
        st.markdown("#### 💡 Formulated Scientific Hypothesis")
        if experiment.hypothesis:
            st.info(f"**Hypothesis:** {experiment.hypothesis}")
        else:
            st.warning("No hypothesis has been generated for this run yet.")

    st.markdown("#### 🔄 Pipeline Execution Steps")

    if not experiment.workflow_steps:
        st.info("No workflow steps recorded yet. Start an experiment to begin tracking.")
        return

    # Visual representation of pipeline steps
    for idx, step in enumerate(experiment.workflow_steps, start=1):
        agent_label = AGENT_DISPLAY_NAMES.get(step.agent_role, step.agent_role)
        status_label = STATUS_BADGES.get(step.status, step.status)

        with st.expander(f"**Step {idx}: {step.title}** — {status_label}", expanded=(step.status == "running" or step.status == "failed")):
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

    # Code and Output Preview
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
