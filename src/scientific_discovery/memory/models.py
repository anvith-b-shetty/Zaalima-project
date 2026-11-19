"""
Data models for Memory, Workflow Tracking, and Experiment History.

Defines schemas used across the Multi-Agent architecture to record
workflow states, citations, token costs, and experiment logs.
"""

from datetime import datetime, timezone
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

from .config import DEFAULT_MODEL, MODEL_PRICING


AgentRole = Literal[
    "literature_reviewer",
    "hypothesis_generator",
    "code_executor",
    "critic_agent",
    "synthesis",
]

StepStatus = Literal[
    "pending",
    "running",
    "completed",
    "failed",
    "retrying",
]


class WorkflowStep(BaseModel):
    """Represents a single atomic execution step inside the multi-agent pipeline."""

    step_id: str = Field(..., description="Unique step identifier")
    agent_role: AgentRole = Field(..., description="Agent role executing the step")
    title: str = Field(..., description="Short summary of the step action")
    description: str = Field(default="", description="Detailed step context")
    status: StepStatus = Field(default="pending", description="Current step execution status")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="End timestamp")
    duration_ms: int = Field(default=0, ge=0, description="Step duration in milliseconds")
    logs: list[str] = Field(default_factory=list, description="Step execution logs")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata")


class Citation(BaseModel):
    """Academic literature citation and source retrieved from ArXiv or PubMed."""

    citation_id: str = Field(..., description="Unique citation identifier")
    title: str = Field(..., description="Paper title")
    authors: list[str] = Field(default_factory=list, description="List of paper authors")
    year: Optional[int] = Field(default=None, description="Publication year")
    source: Literal["arxiv", "pubmed", "biorxiv", "manual"] = Field(
        default="arxiv", description="Repository source"
    )
    url: Optional[str] = Field(default=None, description="Direct URL to paper or PDF")
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier")
    abstract: str = Field(default="", description="Paper abstract")
    similarity_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Embedding vector similarity score"
    )
    key_findings: str = Field(default="", description="Summarized relevance or findings")


class TokenCostRecord(BaseModel):
    """Tracks token consumption and financial execution cost for LLM calls."""

    model_name: str = Field(default=DEFAULT_MODEL, description="LLM model identifier")
    prompt_tokens: int = Field(default=0, ge=0, description="Input prompt tokens")
    completion_tokens: int = Field(default=0, ge=0, description="Generated completion tokens")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens consumed")
    cost_usd: float = Field(default=0.0, ge=0.0, description="Calculated cost in USD")

    def calculate_cost(self) -> float:
        """Calculates cost based on model pricing rates."""
        rates = MODEL_PRICING.get(
            self.model_name,
            {"prompt": 1.0, "completion": 2.0}
        )
        prompt_cost = (self.prompt_tokens / 1_000_000) * rates["prompt"]
        completion_cost = (self.completion_tokens / 1_000_000) * rates["completion"]
        self.cost_usd = round(prompt_cost + completion_cost, 6)
        self.total_tokens = self.prompt_tokens + self.completion_tokens
        return self.cost_usd


class ExperimentRun(BaseModel):
    """Complete record of an autonomous scientific discovery cycle."""

    experiment_id: str = Field(..., description="Unique identifier for the experiment")
    name: str = Field(..., description="Readable experiment name")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    domain: str = Field(default="Biology / Medicine", description="Research domain")
    hypothesis: str = Field(default="", description="Scientific hypothesis formulated")
    status: Literal["in_progress", "completed", "failed", "rejected"] = Field(
        default="in_progress", description="Overall experiment outcome"
    )
    generated_code: str = Field(default="", description="Python code written by agent")
    execution_stdout: str = Field(default="", description="Code executor stdout")
    execution_stderr: str = Field(default="", description="Code executor stderr")
    execution_time_ms: int = Field(default=0, ge=0, description="Sandbox run duration")
    p_value: Optional[float] = Field(default=None, description="Calculated p-value")
    confidence_interval: Optional[tuple[float, float]] = Field(
        default=None, description="Statistical confidence interval (e.g. 95%)"
    )
    critic_verdict: Optional[str] = Field(
        default=None, description="Statistical critic agent feedback"
    )
    citations: list[Citation] = Field(
        default_factory=list, description="Referenced literature sources"
    )
    workflow_steps: list[WorkflowStep] = Field(
        default_factory=list, description="Ordered pipeline execution steps"
    )
    cost: TokenCostRecord = Field(
        default_factory=TokenCostRecord, description="Total experiment LLM cost"
    )
    latex_abstract: Optional[str] = Field(
        default=None, description="Generated LaTeX research abstract"
    )
