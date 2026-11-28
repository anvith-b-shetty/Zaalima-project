"""
Agent Monitoring Integration Client.

Provides the standardized integration layer for Members 1, 2, 3, and 4
to report execution events, literature citations, code outputs, and statistical
evaluations directly to the supervisor dashboard.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Optional
import requests

from .experiment_store import ExperimentMemoryStore
from .models import Citation, ExperimentRun, TokenCostRecord, WorkflowStep

logger = logging.getLogger(__name__)


class AgentMonitorClient:
    """Integration client used by agents to publish live status to the dashboard."""

    def __init__(self, store: Optional[ExperimentMemoryStore] = None, executor_url: str = "http://127.0.0.1:8000"):
        self.store = store or ExperimentMemoryStore()
        self.executor_url = executor_url

    # --- Member 1 & 2 Integration: Literature Reviewer & Hypothesis Generator ---
    def record_literature_retrieval(
        self,
        experiment_id: str,
        citations: list[Citation],
        duration_ms: int = 0,
        logs: Optional[list[str]] = None,
    ) -> Optional[ExperimentRun]:
        """Called by Literature Reviewer agent after retrieving papers from Vector DB."""
        exp = self.store.get_experiment(experiment_id)
        if not exp:
            return None

        for c in citations:
            self.store.add_citation(experiment_id, c)

        step = WorkflowStep(
            step_id=f"step-lit-{datetime.now(timezone.utc).strftime('%H%M%S')}",
            agent_role="literature_reviewer",
            title="Literature Review & Vector Retrieval",
            description=f"Retrieved and grounded {len(citations)} papers from ArXiv/PubMed.",
            status="completed",
            started_at=datetime.now(timezone.utc),
            duration_ms=duration_ms,
            logs=logs or [f"Retrieved {len(citations)} relevant citations from vector index."],
        )
        return self.store.add_workflow_step(experiment_id, step)

    def record_hypothesis(
        self,
        experiment_id: str,
        hypothesis: str,
        duration_ms: int = 0,
        logs: Optional[list[str]] = None,
    ) -> Optional[ExperimentRun]:
        """Called by Hypothesis Generator agent when a novel hypothesis is drafted."""
        exp = self.store.get_experiment(experiment_id)
        if not exp:
            return None

        exp.hypothesis = hypothesis
        self.store.update_experiment(exp)

        step = WorkflowStep(
            step_id=f"step-hypo-{datetime.now(timezone.utc).strftime('%H%M%S')}",
            agent_role="hypothesis_generator",
            title="Formulate Grounded Hypothesis",
            description="Synthesized candidate hypothesis from peer-reviewed literature.",
            status="completed",
            started_at=datetime.now(timezone.utc),
            duration_ms=duration_ms,
            logs=logs or ["Drafted novel testable scientific hypothesis."],
        )
        return self.store.add_workflow_step(experiment_id, step)

    # --- Member 3 Integration: Code Executor Sandbox ---
    def record_code_execution(
        self,
        experiment_id: str,
        code: str,
        stdout: str,
        stderr: str,
        exit_code: int = 0,
        execution_time_ms: int = 0,
    ) -> Optional[ExperimentRun]:
        """Called by Code Executor agent after running Python scripts in Docker."""
        exp = self.store.get_experiment(experiment_id)
        if not exp:
            return None

        exp.generated_code = code
        exp.execution_stdout = stdout
        exp.execution_stderr = stderr
        exp.execution_time_ms = execution_time_ms
        self.store.update_experiment(exp)

        status = "completed" if exit_code == 0 and not stderr else "failed"
        step = WorkflowStep(
            step_id=f"step-exec-{datetime.now(timezone.utc).strftime('%H%M%S')}",
            agent_role="code_executor",
            title="Docker Sandbox Python Execution",
            description=f"Executed experimental script in isolated container (Exit: {exit_code}).",
            status=status,
            started_at=datetime.now(timezone.utc),
            duration_ms=execution_time_ms,
            logs=[
                f"Container executed with exit code {exit_code}.",
                f"Execution duration: {execution_time_ms}ms.",
            ],
        )
        return self.store.add_workflow_step(experiment_id, step)

    def dispatch_to_sandbox_api(
        self,
        code: str,
        timeout_seconds: int = 10,
    ) -> dict[str, Any]:
        """Directly dispatches Python code to Member 3's FastAPI Docker Executor."""
        endpoint = f"{self.executor_url}/execution/execute"
        payload = {
            "code": code,
            "language": "python",
            "timeout_seconds": timeout_seconds,
        }
        try:
            resp = requests.post(endpoint, json=payload, timeout=timeout_seconds + 5)
            if resp.status_code == 200:
                return resp.json()
            return {
                "status": "error",
                "stderr": f"HTTP {resp.status_code}: {resp.text}",
                "stdout": "",
                "exit_code": 1,
                "execution_time_ms": 0,
            }
        except Exception as e:
            return {
                "status": "error",
                "stderr": f"Sandbox API unreachable at {endpoint}: {str(e)}",
                "stdout": "",
                "exit_code": 1,
                "execution_time_ms": 0,
            }

    # --- Member 4 Integration: Statistical Critic Agent ---
    def record_critic_evaluation(
        self,
        experiment_id: str,
        p_value: float,
        verdict: str,
        confidence_interval: Optional[tuple[float, float]] = None,
        duration_ms: int = 0,
    ) -> Optional[ExperimentRun]:
        """Called by Statistical Critic agent after assessing p-value and significance."""
        exp = self.store.get_experiment(experiment_id)
        if not exp:
            return None

        exp.p_value = p_value
        exp.confidence_interval = confidence_interval
        exp.critic_verdict = verdict
        exp.status = "completed" if p_value < 0.05 else "rejected"
        self.store.update_experiment(exp)

        step = WorkflowStep(
            step_id=f"step-crit-{datetime.now(timezone.utc).strftime('%H%M%S')}",
            agent_role="critic_agent",
            title="Statistical Hypothesis Evaluation",
            description=f"Evaluated significance (p={p_value:.4f}). Verdict: {verdict}",
            status="completed",
            started_at=datetime.now(timezone.utc),
            duration_ms=duration_ms,
            logs=[
                f"Calculated p-value: {p_value:.4f}",
                f"Confidence Interval: {confidence_interval}",
                f"Verdict: {verdict}",
            ],
        )
        return self.store.add_workflow_step(experiment_id, step)
