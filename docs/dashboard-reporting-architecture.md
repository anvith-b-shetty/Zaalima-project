# Dashboard, Memory & Research Reporting Architecture

## Project
Autonomous Multimodal Scientific Discovery Agent

## Assigned Role
Member 5 – UI and Reporting (Dashboard, Memory & Research Reporting)

## Objective
Provide the supervisor monitoring dashboard, experiment memory management, token and cost telemetry, literature citation grounding displays, and automated research synthesis with LaTeX abstract formatting.

---

## Architectural Workflow

```
[Literature Reviewer (M1/M2)] -> [Hypothesis Generator (M1/M2)] -> [Code Executor (M3)] -> [Statistical Critic (M4)]
                                           │
                                           ▼
                     ┌───────────────────────────────────────────┐
                     │     ExperimentMemoryStore & Tracker      │
                     │  - Step-by-step Execution Traces          │
                     │  - Literature Citations (Vector DB)       │
                     │  - Token Costs & Pricing Analytics       │
                     │  - Experiment State Persistence (JSON)   │
                     └─────────────────────┬─────────────────────┘
                                           │
                       ┌───────────────────┴───────────────────┐
                       ▼                                       ▼
       ┌───────────────────────────────┐       ┌───────────────────────────────┐
       │   Streamlit Live Dashboard    │       │   Research Synthesis Engine   │
       │ - Real-time Workflow Tree     │       │ - Academic Abstract Formatter │
       │ - Paper Citation Explorer     │       │ - LaTeX (.tex) Builder        │
       │ - LLM Token & Cost Auditing   │       │ - Statistical Result Grounding│
       │ - Historical Run Comparison   │       │                               │
       └───────────────────────────────┘       └───────────────────────────────┘
```

---

## Technology Stack

- **Python 3.12+**
- **Streamlit**: Web monitoring dashboard and supervisor controls
- **Plotly & Altair**: Interactive data visualizers and token distribution charts
- **Pydantic v2**: Type-safe data schemas for memory, citations, steps, and costs
- **Pandas**: Run history aggregation and tabulations
- **Pytest**: Automated testing of memory serialization, cost calculation, and workflows

---

## Component Breakdown

### 1. Memory and Storage (`src/scientific_discovery/memory/`)
- `models.py`: Strongly typed Pydantic models for `WorkflowStep`, `Citation`, `TokenCostRecord`, and `ExperimentRun`.
- `experiment_store.py`: Persistent storage manager handling atomic saves, keyword search, side-by-side run comparison, and CSV/JSON exports (Monday deliverable).
- `workflow_tracker.py`: Real-time lifecycle manager for step transitions (`start_step`, `log`, `complete_step`, `fail_step`).
- `config.py`: Storage paths and model pricing table for token cost auditing.

### 2. Streamlit Dashboard (`src/scientific_discovery/ui/`)
- `app.py`: Main dashboard application with sidebar experiment selector and interactive simulator.
- `components/experiment_history_view.py`: Research History Interface with keyword search, side-by-side run comparison, run deletion, and CSV/JSON exports (Monday deliverable).
- `components/workflow_view.py`: Displays active agents, step durations, logs, generated Python code, and execution output.
- `components/citation_view.py`: Explores grounded peer-reviewed literature from ArXiv and PubMed with vector similarity metrics.
- `components/cost_view.py`: Visualizes prompt/completion token splits and monetary spend ($ USD).
- `components/synthesis_preview.py`: Academic LaTeX abstract renderer with `.tex` source and download support.

---

## Inter-Member Data Contract

Other members publish data into the shared memory store as follows:

```python
from src.scientific_discovery.memory import ExperimentMemoryStore, WorkflowStep, Citation

store = ExperimentMemoryStore()

# Member 1 & 2: Log literature and hypothesis
store.add_citation("exp-001", Citation(
    citation_id="arxiv:2401.0001",
    title="Example Discovery Paper",
    source="arxiv",
    similarity_score=0.94
))

# Member 3: Log execution output
store.add_workflow_step("exp-001", WorkflowStep(
    step_id="step-exec",
    agent_role="code_executor",
    title="Docker Sandbox Run",
    status="completed",
    duration_ms=850
))

# Member 4: Record p-value and critic verdict
exp = store.get_experiment("exp-001")
exp.p_value = 0.003
exp.critic_verdict = "Statistically significant."
store.update_experiment(exp)
```
