"""
Unit tests for the Memory and Experiment Store Engine.
"""

from pathlib import Path
import tempfile
import pytest

from src.scientific_discovery.memory.experiment_store import ExperimentMemoryStore
from src.scientific_discovery.memory.models import (
    Citation,
    ExperimentRun,
    TokenCostRecord,
    WorkflowStep,
)
from src.scientific_discovery.memory.workflow_tracker import WorkflowTracker


@pytest.fixture
def temp_store():
    """Provides a clean temporary ExperimentMemoryStore."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        store_path = Path(tmp_dir) / "test_experiments.json"
        store = ExperimentMemoryStore(storage_path=store_path)
        yield store


def test_create_experiment(temp_store):
    """Test initial creation of an experiment run."""
    exp = temp_store.create_experiment(
        name="CRISPR Kinetic Profiling",
        hypothesis="GC content regulates cleavage kinetics.",
        domain="Genomics",
    )

    assert exp.name == "CRISPR Kinetic Profiling"
    assert exp.status == "in_progress"
    assert exp.domain == "Genomics"
    assert exp.cost.total_tokens == 0
    assert temp_store.get_experiment(exp.experiment_id) is not None


def test_add_workflow_step(temp_store):
    """Test adding workflow steps to an experiment."""
    exp = temp_store.create_experiment(
        name="Step Tracking Test",
        hypothesis="Step test",
    )

    step = WorkflowStep(
        step_id="step-001",
        agent_role="literature_reviewer",
        title="Ingesting Literature",
        description="Querying ArXiv API",
        status="completed",
        duration_ms=450,
        logs=["Found 12 matching papers."],
    )

    updated_exp = temp_store.add_workflow_step(exp.experiment_id, step)
    assert len(updated_exp.workflow_steps) == 1
    assert updated_exp.workflow_steps[0].title == "Ingesting Literature"
    assert updated_exp.workflow_steps[0].duration_ms == 450


def test_add_citation_deduplication(temp_store):
    """Test attaching academic literature citations without duplicates."""
    exp = temp_store.create_experiment(name="Citation Test", hypothesis="Test")

    cit1 = Citation(
        citation_id="arxiv:2401.12345",
        title="Graph Neural Networks in Molecular Design",
        authors=["Author A", "Author B"],
        year=2024,
        source="arxiv",
        similarity_score=0.91,
    )
    cit2 = Citation(
        citation_id="arxiv:2401.12345",  # Duplicate ID
        title="Graph Neural Networks in Molecular Design",
        authors=["Author A", "Author B"],
        year=2024,
        source="arxiv",
    )

    temp_store.add_citation(exp.experiment_id, cit1)
    temp_store.add_citation(exp.experiment_id, cit2)

    updated = temp_store.get_experiment(exp.experiment_id)
    assert len(updated.citations) == 1
    assert updated.citations[0].similarity_score == 0.91


def test_token_cost_calculation(temp_store):
    """Test token summation and USD cost estimation."""
    exp = temp_store.create_experiment(name="Cost Test", hypothesis="Test")

    cost = temp_store.update_cost(
        experiment_id=exp.experiment_id,
        model_name="gemini-1.5-flash",
        prompt_tokens=1_000_000,
        completion_tokens=1_000_000,
    )

    assert cost.total_tokens == 2_000_000
    assert cost.cost_usd == pytest.approx(0.375, rel=1e-3)


def test_summary_metrics(temp_store):
    """Test aggregation of platform-level statistics."""
    exp1 = temp_store.create_experiment(name="Exp 1", hypothesis="H1")
    exp1.status = "completed"
    temp_store.update_experiment(exp1)

    exp2 = temp_store.create_experiment(name="Exp 2", hypothesis="H2")
    exp2.status = "failed"
    temp_store.update_experiment(exp2)

    metrics = temp_store.get_summary_metrics()
    assert metrics["total_experiments"] == 2
    assert metrics["completed"] == 1
    assert metrics["failed"] == 1
    assert metrics["success_rate"] == 50.0


def test_workflow_tracker_lifecycle(temp_store):
    """Test WorkflowTracker start, log, and completion lifecycle."""
    exp = temp_store.create_experiment(name="Tracker Test", hypothesis="Testing")
    tracker = WorkflowTracker(store=temp_store, experiment_id=exp.experiment_id)

    step = tracker.start_step(
        agent_role="code_executor",
        title="Docker Container Run",
        description="Executing generated script",
    )
    assert step.status == "running"

    tracker.log(step.step_id, "Memory allocated: 64MB")
    completed_step = tracker.complete_step(step.step_id, logs=["Finished successfully"])

    assert completed_step.status == "completed"
    assert "Memory allocated: 64MB" in completed_step.logs
    assert "Finished successfully" in completed_step.logs
    assert completed_step.duration_ms >= 0


def test_persistence_reload(temp_store):
    """Test that records persist and reload accurately from JSON file."""
    temp_store.create_experiment(name="Persistent Exp", hypothesis="Testing persistence")
    
    new_store = ExperimentMemoryStore(storage_path=temp_store.storage_path)
    runs = new_store.list_experiments()
    assert len(runs) == 1
    assert runs[0].name == "Persistent Exp"


# ==================== MONDAY DELIVERABLES TESTS ====================

def test_search_and_delete(temp_store):
    """Test searching experiments by query and deleting by ID (Monday)."""
    e1 = temp_store.create_experiment(name="Cancer Immunology", hypothesis="PD-1 expression", domain="Immunology")
    e2 = temp_store.create_experiment(name="Kinase Docking", hypothesis="Inhibitor binding", domain="Biochemistry")

    search_res = temp_store.search_experiments("PD-1")
    assert len(search_res) == 1
    assert search_res[0].experiment_id == e1.experiment_id

    # Test delete
    assert temp_store.delete_experiment(e1.experiment_id) is True
    assert temp_store.get_experiment(e1.experiment_id) is None
    assert len(temp_store.list_experiments()) == 1


def test_export_csv_and_json(temp_store):
    """Test export of research history to CSV and JSON formats (Monday)."""
    temp_store.create_experiment(name="Export Test", hypothesis="Hypothesis for export")

    csv_text = temp_store.export_to_csv()
    assert "experiment_id" in csv_text
    assert "Export Test" in csv_text

    json_text = temp_store.export_to_json()
    assert "Export Test" in json_text
    assert "experiment_id" in json_text


def test_compare_experiments(temp_store):
    """Test side-by-side run comparison calculations (Monday)."""
    e1 = temp_store.create_experiment(name="Run A", hypothesis="H_A")
    e1.p_value = 0.01
    e1.execution_time_ms = 500
    temp_store.update_experiment(e1)

    e2 = temp_store.create_experiment(name="Run B", hypothesis="H_B")
    e2.p_value = 0.05
    e2.execution_time_ms = 800
    temp_store.update_experiment(e2)

    cmp = temp_store.compare_experiments(e1.experiment_id, e2.experiment_id)
    assert cmp is not None
    assert cmp["p_value_diff"] == -0.04
    assert cmp["runtime_diff_ms"] == -300
