"""
Autonomous Multimodal Scientific Discovery Agent - Streamlit Monitoring Dashboard.

Main entry point for supervisor oversight, agent workflow tracking, literature citation
visualization, execution cost auditing, and LaTeX research abstract generation.
"""

from datetime import datetime, timezone
import os
import sys
import time
from pathlib import Path

# Add project root to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from src.scientific_discovery.memory.experiment_store import ExperimentMemoryStore
from src.scientific_discovery.memory.models import Citation, ExperimentRun, TokenCostRecord, WorkflowStep
from src.scientific_discovery.ui.components.citation_view import render_citation_view
from src.scientific_discovery.ui.components.cost_view import render_cost_view
from src.scientific_discovery.ui.components.experiment_history_view import render_history_view
from src.scientific_discovery.ui.components.synthesis_preview import render_synthesis_preview
from src.scientific_discovery.ui.components.workflow_view import render_workflow_view
from src.scientific_discovery.ui.theme import GLOBAL_CSS, render_page_header


# Page configuration
st.set_page_config(
    page_title="Scientific Discovery Agent Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global design system CSS and page hero header
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(render_page_header(), unsafe_allow_html=True)


@st.cache_resource
def get_store() -> ExperimentMemoryStore:
    """Initialize and cache the ExperimentMemoryStore instance."""
    store = ExperimentMemoryStore()
    # Pre-seed if completely empty
    if len(store.list_experiments()) == 0:
        store.seed_sample_data()
    return store


store = get_store()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.2);
        ">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="
                    width: 38px;
                    height: 38px;
                    border-radius: 10px;
                    background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.25rem;
                ">
                    🔬
                </div>
                <div>
                    <div style="color: #ffffff; font-weight: 800; font-size: 1.02rem; letter-spacing: -0.01em;">
                        Supervisor Hub
                    </div>
                    <div style="color: #94a3b8; font-size: 0.75rem; font-weight: 500;">
                        UI & Telemetry
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    experiments = store.list_experiments()
    exp_options = {e.experiment_id: f"{e.experiment_id} ({e.name[:24]}...)" for e in experiments}

    # Track selected experiment in session state
    if "selected_exp_id" not in st.session_state and experiments:
        st.session_state.selected_exp_id = experiments[0].experiment_id

    current_index = 0
    exp_ids = list(exp_options.keys())
    if st.session_state.get("selected_exp_id") in exp_ids:
        current_index = exp_ids.index(st.session_state.selected_exp_id)

    selected_exp_id = st.selectbox(
        "Active Experiment:",
        options=exp_ids,
        format_func=lambda x: exp_options.get(x, x),
        index=current_index if exp_ids else 0,
    )
    st.session_state.selected_exp_id = selected_exp_id

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Quick Action: Create New Experiment
    with st.expander("➕ Configure New Experiment Run"):
        new_name = st.text_input("Experiment Name:", "Synthetic Gene Regulation")
        new_domain = st.selectbox(
            "Research Domain:",
            ["Functional Genomics", "Drug Discovery", "Neuroscience", "Structural Biology"],
        )
        new_hypo = st.text_area(
            "Initial Hypothesis:",
            "Promoter methylations inhibit transcriptional binding affinity non-linearly.",
        )
        if st.button("🚀 Initialize Pipeline Run", type="primary", width="stretch"):
            new_run = store.create_experiment(name=new_name, domain=new_domain, hypothesis=new_hypo)
            st.session_state.selected_exp_id = new_run.experiment_id
            st.success(f"Initialized {new_run.experiment_id} successfully!")
            st.rerun()

    # Quick Action: Run Interactive Simulation
    st.markdown("#### ⚡ Pipeline Simulator")
    if st.button("▶️ Trigger Simulated Step", width="stretch"):
        active_exp = store.get_experiment(st.session_state.selected_exp_id)
        if active_exp:
            step_num = len(active_exp.workflow_steps) + 1
            new_step = WorkflowStep(
                step_id=f"step-sim-{step_num}",
                agent_role="hypothesis_generator" if step_num % 2 == 0 else "code_executor",
                title=f"Autonomous Simulation Step {step_num}",
                description="Simulated multi-agent iteration with automated error-recovery.",
                status="completed",
                started_at=datetime.now(timezone.utc),
                duration_ms=650,
                logs=[
                    f"Execution heartbeat triggered at {datetime.now(timezone.utc).strftime('%H:%M:%S')}",
                    "Docker sandbox environment healthy.",
                ],
            )
            store.add_workflow_step(active_exp.experiment_id, new_step)
            store.update_cost(active_exp.experiment_id, "gemini-1.5-flash", 1200, 350)
            st.success("Simulated step recorded!")
            st.rerun()

    st.markdown("---")
    # Quick metrics snapshot in sidebar
    summary = store.get_summary_metrics()
    st.markdown("#### 📊 Supervisor Quick Stats")
    st.markdown(
        f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Total Pipeline Runs</span>
                <span style="font-size: 0.88rem; color: #0f172a; font-weight: 800; font-family: 'JetBrains Mono', monospace;">{summary['total_experiments']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Success Rate</span>
                <span style="font-size: 0.88rem; color: #10b981; font-weight: 800; font-family: 'JetBrains Mono', monospace;">{summary['success_rate']}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.8rem; color: #64748b; font-weight: 600;">Cumulative Spend</span>
                <span style="font-size: 0.88rem; color: #4f46e5; font-weight: 800; font-family: 'JetBrains Mono', monospace;">${summary['total_cost_usd']:.4f}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; font-size: 0.75rem; color: #64748b;">
            <div style="font-weight: 700; color: #334155; margin-bottom: 4px;">Node Telemetry Status</div>
            <div>• Runtime: Python 3.13 / Streamlit 1.67+</div>
            <div>• Multi-Agent Swarm: 5 Stage Orchestrator</div>
            <div>• Execution Sandbox: Docker Isolated</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------- MAIN VIEW -----------------
active_experiment = store.get_experiment(st.session_state.selected_exp_id) if st.session_state.get("selected_exp_id") else None

if not active_experiment:
    st.markdown(
        """
        <div style="
            background: #ffffff;
            border: 2px dashed #cbd5e1;
            border-radius: 16px;
            padding: 48px 32px;
            text-align: center;
            margin-top: 20px;
        ">
            <div style="font-size: 3rem; margin-bottom: 12px;">🔬</div>
            <div style="font-size: 1.3rem; font-weight: 800; color: #0f172a; margin-bottom: 6px;">
                No Active Experiment Selected
            </div>
            <div style="font-size: 0.92rem; color: #64748b; max-width: 500px; margin: 0 auto 20px auto;">
                Select an existing experimental run from the supervisor sidebar, or initialize a new scientific hypothesis discovery cycle.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Status badges map
    status_styles = {
        "completed": {"bg": "#ecfdf5", "color": "#059669", "border": "#10b981", "icon": "✓"},
        "in_progress": {"bg": "#eff6ff", "color": "#2563eb", "border": "#3b82f6", "icon": "●"},
        "running": {"bg": "#eff6ff", "color": "#2563eb", "border": "#3b82f6", "icon": "●"},
        "failed": {"bg": "#fef2f2", "color": "#dc2626", "border": "#ef4444", "icon": "✕"},
    }
    st_style = status_styles.get(active_experiment.status, status_styles["in_progress"])

    # Active Run Header Ribbon
    st.markdown(
        f"""
        <div style="
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        ">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="
                    width: 42px;
                    height: 42px;
                    border-radius: 10px;
                    background: #f1f5f9;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.4rem;
                ">
                    🧬
                </div>
                <div>
                    <div style="font-size: 1.15rem; font-weight: 800; color: #0f172a; line-height: 1.2;">
                        {active_experiment.name}
                    </div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <span>ID: <code style="color: #4f46e5; font-weight: 600;">{active_experiment.experiment_id}</code></span>
                        <span>•</span>
                        <span>Domain: <strong>{active_experiment.domain}</strong></span>
                        <span>•</span>
                        <span>Created: {active_experiment.created_at.strftime('%Y-%m-%d %H:%M UTC')}</span>
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="
                    background: {st_style['bg']};
                    color: {st_style['color']};
                    border: 1px solid {st_style['border']};
                    font-size: 0.78rem;
                    font-weight: 700;
                    padding: 5px 12px;
                    border-radius: 9999px;
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                ">
                    <span>{st_style['icon']}</span>
                    <span>{active_experiment.status.upper()}</span>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 5 Main Tabs matching Member 5 responsibilities
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🤖 Agent Workflow",
            "📚 Literature Citations",
            "💰 Cost & Telemetry",
            "📜 Experiment History",
            "📝 LaTeX Synthesis",
        ]
    )

    with tab1:
        render_workflow_view(active_experiment)

    with tab2:
        render_citation_view(active_experiment)

    with tab3:
        render_cost_view(active_experiment, summary)

    with tab4:
        selected_from_history = render_history_view(store)
        if selected_from_history and selected_from_history != st.session_state.selected_exp_id:
            st.session_state.selected_exp_id = selected_from_history
            st.rerun()

    with tab5:
        render_synthesis_preview(active_experiment)
