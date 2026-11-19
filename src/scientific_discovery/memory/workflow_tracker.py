"""
Workflow Step Tracker for the Multi-Agent System.

Allows agent components to record real-time step progress, execution logs,
and duration, seamlessly publishing them into the experiment memory.
"""

from datetime import datetime, timezone
import time
from typing import Any, Optional
import uuid

from .models import AgentRole, StepStatus, WorkflowStep
from .experiment_store import ExperimentMemoryStore


class WorkflowTracker:
    """Manages active pipeline steps and records state transitions."""

    def __init__(self, store: ExperimentMemoryStore, experiment_id: str):
        self.store = store
        self.experiment_id = experiment_id
        self._active_steps: dict[str, tuple[WorkflowStep, float]] = {}

    def start_step(
        self,
        agent_role: AgentRole,
        title: str,
        description: str = "",
        metadata: Optional[dict[str, Any]] = None,
    ) -> WorkflowStep:
        """Start tracking a new execution step."""
        step_id = f"step-{uuid.uuid4().hex[:6]}"
        step = WorkflowStep(
            step_id=step_id,
            agent_role=agent_role,
            title=title,
            description=description,
            status="running",
            started_at=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        self._active_steps[step_id] = (step, time.time())
        self.store.add_workflow_step(self.experiment_id, step)
        return step

    def log(self, step_id: str, message: str) -> None:
        """Append a log message to an in-progress step."""
        if step_id in self._active_steps:
            step, start_t = self._active_steps[step_id]
            step.logs.append(message)
            self.store.add_workflow_step(self.experiment_id, step)

    def complete_step(
        self,
        step_id: str,
        logs: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[WorkflowStep]:
        """Mark a step as successfully completed."""
        if step_id not in self._active_steps:
            return None

        step, start_t = self._active_steps.pop(step_id)
        step.status = "completed"
        step.completed_at = datetime.now(timezone.utc)
        step.duration_ms = int((time.time() - start_t) * 1000)
        if logs:
            step.logs.extend(logs)
        if metadata:
            step.metadata.update(metadata)

        self.store.add_workflow_step(self.experiment_id, step)
        return step

    def fail_step(
        self,
        step_id: str,
        error_message: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[WorkflowStep]:
        """Mark a step as failed with an error message."""
        if step_id not in self._active_steps:
            return None

        step, start_t = self._active_steps.pop(step_id)
        step.status = "failed"
        step.completed_at = datetime.now(timezone.utc)
        step.duration_ms = int((time.time() - start_t) * 1000)
        step.logs.append(f"ERROR: {error_message}")
        if metadata:
            step.metadata.update(metadata)

        self.store.add_workflow_step(self.experiment_id, step)
        return step
