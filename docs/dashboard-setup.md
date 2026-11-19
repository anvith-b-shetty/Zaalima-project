# Dashboard & Memory - Environment Setup

## Project
Autonomous Multimodal Scientific Discovery Agent

## Assigned Role
Member 5 – UI and Reporting (Dashboard, Memory & Research Reporting)

## Development Environment
- Operating System: Windows 11
- Python Version: 3.12+ (or 3.13)
- Virtual Environment: `.venv`
- Code Editor: Visual Studio Code
- Version Control: Git

---

## Installation & Setup

1. **Activate or create the virtual environment:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. **Install project dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Streamlit Dashboard

Launch the supervisor live monitoring dashboard:

```bash
streamlit run src/scientific_discovery/ui/app.py
```

The application will be accessible at:
```text
Local URL: http://localhost:8501
Network URL: http://<ip>:8501
```

---

## Running Unit Tests

Run the memory and experiment tracking test suite:

```bash
pytest -v src/scientific_discovery/memory/tests/
```

Run all project tests (including Member 3's code executor tests):

```bash
pytest -v
```

---

## Features Implemented in Week 1

1. **Memory & Schema Foundation**:
   - Pydantic models for atomic steps, citations, token costs, and experiment cycles.
   - Persistent JSON store with sample discovery cycle pre-seeding.
   - Dynamic step tracker supporting start, log, and completion lifecycles.

2. **Streamlit Supervisor UI**:
   - Multi-agent workflow visualizer with status badges and execution logs.
   - Literature citation viewer with similarity scoring and search filters.
   - Cost & token telemetry with donut chart breakdown and platform totals.
   - Experiment history table with status/domain filtering and run selector.
   - LaTeX abstract previewer with `.tex` download capability.
   - Interactive pipeline simulator to demonstrate live step additions.
