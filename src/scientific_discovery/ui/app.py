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


# Page configuration
st.set_page_config(
    page_title="Scientific Discovery Agent Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom header styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a237e;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #5c6bc0;
        margin-bottom: 20px;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    </style>
    <div>
        <div class="main-title">🔬 Autonomous Multimodal Scientific Discovery Agent</div>
        <div class="sub-title">Supervisor Live Monitoring, Memory Management & Research Reporting Engine</div>
    </div>
    """,
    unsafe_allow_html=True,
)


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
    st.image(
        "https://img.icons8.com/fluency/96/artificial-intelligence.png",
        width=64,
    )
    st.markdown("### 🎛️ Control Panel")

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

    st.markdown("---")

    # Quick Action: Create New Experiment
    with st.expander("➕ New Experiment Run"):
        new_name = st.text_input("Name:", "Synthetic Gene Regulation")
        new_domain = st.selectbox(
            "Domain:",
            ["Functional Genomics", "Drug Discovery", "Neuroscience", "Structural Biology"],
        )
        new_hypo = st.text_area(
            "Hypothesis:",
            "Promoter methylations inhibit transcriptional binding affinity non-linearly.",
        )
        if st.button("🚀 Initialize Pipeline", width="stretch"):
            new_run = store.create_experiment(name=new_name, domain=new_domain, hypothesis=new_hypo)
            st.session_state.selected_exp_id = new_run.experiment_id
            st.success(f"Created {new_run.experiment_id}!")
            st.rerun()

    # Quick Action: Run Interactive Simulation
    st.markdown("#### ⚡ Pipeline Simulator")
    if st.button("▶️ Simulate Discovery Step", width="stretch"):
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
    st.markdown("#### 📊 Quick Stats")
    st.write(f"• Total Runs: **{summary['total_experiments']}**")
    st.write(f"• Success Rate: **{summary['success_rate']}%**")
    st.write(f"• Total Spend: **${summary['total_cost_usd']:.4f}**")

# ----------------- MAIN VIEW -----------------
active_experiment = store.get_experiment(st.session_state.selected_exp_id) if st.session_state.get("selected_exp_id") else None

if not active_experiment:
    st.warning("No active experiment selected. Please create or choose an experiment from the sidebar.")
else:
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
