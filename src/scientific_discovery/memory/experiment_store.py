"""
Persistent Experiment Store and Memory Repository.

Provides thread-safe storage, serialization, and retrieval for
multi-agent experiment runs, workflow traces, and literature citations.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import uuid

from .config import DEFAULT_EXPERIMENTS_FILE
from .models import Citation, ExperimentRun, TokenCostRecord, WorkflowStep

logger = logging.getLogger(__name__)


class ExperimentMemoryStore:
    """Manages storage, retrieval, and metrics aggregation for experiments."""

    def __init__(self, storage_path: Path = DEFAULT_EXPERIMENTS_FILE):
        self.storage_path = Path(storage_path)
        self._experiments: dict[str, ExperimentRun] = {}
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.load_from_disk()

    def create_experiment(
        self,
        name: str,
        hypothesis: str,
        domain: str = "Molecular Biology",
        experiment_id: Optional[str] = None,
    ) -> ExperimentRun:
        """Initialize and persist a new experiment run."""
        exp_id = experiment_id or f"exp-{uuid.uuid4().hex[:8]}"
        run = ExperimentRun(
            experiment_id=exp_id,
            name=name,
            hypothesis=hypothesis,
            domain=domain,
            status="in_progress",
            created_at=datetime.now(timezone.utc),
        )
        self._experiments[exp_id] = run
        self.save_to_disk()
        return run

    def get_experiment(self, experiment_id: str) -> Optional[ExperimentRun]:
        """Fetch an experiment by ID."""
        return self._experiments.get(experiment_id)

    def list_experiments(
        self,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[ExperimentRun]:
        """Return a sorted list of experiments (most recent first)."""
        runs = list(self._experiments.values())
        if status:
            runs = [r for r in runs if r.status == status]
        runs.sort(key=lambda x: x.created_at, reverse=True)
        return runs[:limit]

    def update_experiment(self, experiment: ExperimentRun) -> ExperimentRun:
        """Update an existing experiment record."""
        self._experiments[experiment.experiment_id] = experiment
        self.save_to_disk()
        return experiment

    def add_workflow_step(
        self,
        experiment_id: str,
        step: WorkflowStep,
    ) -> Optional[ExperimentRun]:
        """Append a workflow execution step to an experiment."""
        exp = self.get_experiment(experiment_id)
        if not exp:
            logger.warning(f"Experiment {experiment_id} not found.")
            return None

        # Replace existing step if step_id matches, else append
        existing_index = next(
            (i for i, s in enumerate(exp.workflow_steps) if s.step_id == step.step_id),
            None,
        )
        if existing_index is not None:
            exp.workflow_steps[existing_index] = step
        else:
            exp.workflow_steps.append(step)

        self.save_to_disk()
        return exp

    def add_citation(
        self,
        experiment_id: str,
        citation: Citation,
    ) -> Optional[ExperimentRun]:
        """Attach a literature citation to an experiment."""
        exp = self.get_experiment(experiment_id)
        if not exp:
            return None

        # Prevent duplicate citation IDs
        if not any(c.citation_id == citation.citation_id for c in exp.citations):
            exp.citations.append(citation)
            self.save_to_disk()
        return exp

    def update_cost(
        self,
        experiment_id: str,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> Optional[TokenCostRecord]:
        """Accumulate token usage and recalculate costs."""
        exp = self.get_experiment(experiment_id)
        if not exp:
            return None

        exp.cost.model_name = model_name
        exp.cost.prompt_tokens += prompt_tokens
        exp.cost.completion_tokens += completion_tokens
        exp.cost.calculate_cost()
        self.save_to_disk()
        return exp.cost

    def delete_experiment(self, experiment_id: str) -> bool:
        """Remove an experiment from memory and disk."""
        if experiment_id in self._experiments:
            del self._experiments[experiment_id]
            self.save_to_disk()
            return True
        return False

    def search_experiments(self, query: str) -> list[ExperimentRun]:
        """Search across experiment hypotheses, names, domains, and citations."""
        q = query.lower().strip()
        if not q:
            return self.list_experiments()

        results = []
        for exp in self._experiments.values():
            match = (
                q in exp.name.lower()
                or q in exp.hypothesis.lower()
                or q in exp.domain.lower()
                or any(q in c.title.lower() or any(q in a.lower() for a in c.authors) for c in exp.citations)
                or q in exp.generated_code.lower()
            )
            if match:
                results.append(exp)

        results.sort(key=lambda x: x.created_at, reverse=True)
        return results

    def compare_experiments(self, exp_id1: str, exp_id2: str) -> Optional[dict[str, Any]]:
        """Compare two experiments side-by-side for review."""
        e1 = self.get_experiment(exp_id1)
        e2 = self.get_experiment(exp_id2)
        if not e1 or not e2:
            return None

        return {
            "exp1": {
                "id": e1.experiment_id,
                "name": e1.name,
                "domain": e1.domain,
                "status": e1.status,
                "p_value": e1.p_value,
                "tokens": e1.cost.total_tokens,
                "cost_usd": e1.cost.cost_usd,
                "citations_count": len(e1.citations),
                "steps_count": len(e1.workflow_steps),
                "runtime_ms": e1.execution_time_ms,
            },
            "exp2": {
                "id": e2.experiment_id,
                "name": e2.name,
                "domain": e2.domain,
                "status": e2.status,
                "p_value": e2.p_value,
                "tokens": e2.cost.total_tokens,
                "cost_usd": e2.cost.cost_usd,
                "citations_count": len(e2.citations),
                "steps_count": len(e2.workflow_steps),
                "runtime_ms": e2.execution_time_ms,
            },
            "p_value_diff": (
                round(e1.p_value - e2.p_value, 4)
                if (e1.p_value is not None and e2.p_value is not None)
                else None
            ),
            "cost_diff": round(e1.cost.cost_usd - e2.cost.cost_usd, 5),
            "runtime_diff_ms": e1.execution_time_ms - e2.execution_time_ms,
        }

    def export_to_csv(self) -> str:
        """Export research experiment history to CSV format."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "experiment_id",
            "name",
            "domain",
            "status",
            "p_value",
            "tokens",
            "cost_usd",
            "citations_count",
            "steps_count",
            "runtime_ms",
            "created_at",
        ])

        for exp in self.list_experiments(limit=1000):
            writer.writerow([
                exp.experiment_id,
                exp.name,
                exp.domain,
                exp.status,
                exp.p_value if exp.p_value is not None else "",
                exp.cost.total_tokens,
                exp.cost.cost_usd,
                len(exp.citations),
                len(exp.workflow_steps),
                exp.execution_time_ms,
                exp.created_at.isoformat(),
            ])

        return output.getvalue()

    def export_to_json(self) -> str:
        """Export research experiment history as a JSON string."""
        return json.dumps(
            [e.model_dump(mode="json") for e in self.list_experiments(limit=1000)],
            indent=2,
            default=str,
        )

    def get_summary_metrics(self) -> dict[str, Any]:
        """Compute aggregate platform-level statistics for the dashboard."""
        total = len(self._experiments)
        completed = sum(1 for e in self._experiments.values() if e.status == "completed")
        failed = sum(1 for e in self._experiments.values() if e.status == "failed")
        in_progress = sum(1 for e in self._experiments.values() if e.status == "in_progress")
        total_tokens = sum(e.cost.total_tokens for e in self._experiments.values())
        total_cost_usd = sum(e.cost.cost_usd for e in self._experiments.values())
        total_citations = sum(len(e.citations) for e in self._experiments.values())

        success_rate = (completed / total * 100) if total > 0 else 0.0

        return {
            "total_experiments": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "success_rate": round(success_rate, 1),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost_usd, 4),
            "total_citations": total_citations,
        }

    def save_to_disk(self) -> None:
        """Persist all experiment records to disk as JSON."""
        data = {k: v.model_dump(mode="json") for k, v in self._experiments.items()}
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to persist experiments to disk: {e}")

    def load_from_disk(self) -> None:
        """Load experiment records from disk."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            self._experiments = {
                k: ExperimentRun.model_validate(v) for k, v in raw_data.items()
            }
        except Exception as e:
            logger.error(f"Failed to load experiments from disk: {e}")
            self._experiments = {}

    def seed_sample_data(self) -> None:
        """Seed realistic experiments for demonstration and dashboard visualization."""
        if len(self._experiments) > 0:
            return  # Don't overwrite if data exists

        sample_exp1 = ExperimentRun(
            experiment_id="exp-bio-001",
            name="CRISPR Off-Target Cleavage Prediction",
            domain="Functional Genomics",
            hypothesis="Cas9 off-target cleavage probability correlates inversely with local GC content in PAM proximal regions.",
            status="completed",
            created_at=datetime.now(timezone.utc),
            generated_code="import numpy as np\nfrom scipy import stats\n\ngc_content = np.array([0.25, 0.40, 0.55, 0.70])\ncleavage_rate = np.array([0.82, 0.61, 0.34, 0.12])\nres = stats.pearsonr(gc_content, cleavage_rate)\nprint(f'P-value: {res.pvalue:.4f}, r: {res.statistic:.3f}')",
            execution_stdout="P-value: 0.0042, r: -0.995\nSimulation finished with 10,000 iterations.",
            execution_stderr="",
            execution_time_ms=840,
            p_value=0.0042,
            confidence_interval=(-0.999, -0.950),
            critic_verdict="Statistically significant (p < 0.01). Strong negative correlation confirmed.",
            citations=[
                Citation(
                    citation_id="arxiv:2304.09123",
                    title="DeepCRISPR: Optimized Guide RNA Design via Deep Learning",
                    authors=["Shen, R.", "Joung, J.", "Zhang, F."],
                    year=2023,
                    source="arxiv",
                    url="https://arxiv.org/abs/2304.09123",
                    similarity_score=0.92,
                    key_findings="High PAM-proximal GC density stabilizes target R-loop formation."
                ),
                Citation(
                    citation_id="pmid:34190822",
                    title="Systematic Profiling of Cas9 Cleavage Specificity",
                    authors=["Hsu, P.", "Lander, E."],
                    year=2022,
                    source="pubmed",
                    similarity_score=0.88,
                    key_findings="Mismatch tolerance drops sharply when GC fraction exceeds 0.6."
                )
            ],
            workflow_steps=[
                WorkflowStep(
                    step_id="step-1",
                    agent_role="literature_reviewer",
                    title="Ingest ArXiv/PubMed Guides",
                    description="Retrieved 14 papers; top 2 matched query embedding.",
                    status="completed",
                    duration_ms=1200,
                    logs=["Query: Cas9 PAM GC content off-target", "Embedding cosine similarity computed."],
                ),
                WorkflowStep(
                    step_id="step-2",
                    agent_role="hypothesis_generator",
                    title="Formulate Genomic Hypothesis",
                    description="Synthesized hypothesis from RAG context.",
                    status="completed",
                    duration_ms=2100,
                    logs=["Formulated hypothesis H_1", "Grounded against PubMed ID 34190822."],
                ),
                WorkflowStep(
                    step_id="step-3",
                    agent_role="code_executor",
                    title="Execute Docker Simulation",
                    description="Executed Python simulation code in isolated sandbox.",
                    status="completed",
                    duration_ms=840,
                    logs=["Container launched", "Exit code 0", "Execution time: 840ms"],
                ),
                WorkflowStep(
                    step_id="step-4",
                    agent_role="critic_agent",
                    title="Evaluate Statistical Significance",
                    description="Critic analyzed p-value and confidence bounds.",
                    status="completed",
                    duration_ms=950,
                    logs=["p=0.0042 < 0.05 threshold.", "Passed hypothesis validation."],
                ),
            ],
            cost=TokenCostRecord(
                model_name="gemini-1.5-flash",
                prompt_tokens=4200,
                completion_tokens=1150,
                total_tokens=5350,
                cost_usd=0.00066,
            ),
            latex_abstract="""\\begin{abstract}
We investigate the functional dependence of CRISPR-Cas9 off-target cleavage probability on local GC content within PAM-proximal nucleotide sequences. Using an autonomous multi-agent discovery pipeline combining literature grounding and simulated kinetic modeling, we evaluate cleavage kinetics across varying GC fractions. Our findings demonstrate a strong inverse correlation ($r = -0.995, p = 0.0042$), establishing that proximal GC enrichment significantly suppresses spurious cleavage events. These results provide an empirical foundation for enhanced high-fidelity gRNA design.
\\end{abstract}"""
        )

        sample_exp2 = ExperimentRun(
            experiment_id="exp-bio-002",
            name="Kinase Inhibitor Binding Affinity",
            domain="Drug Discovery",
            hypothesis="Substituted pyrimidine derivatives show elevated binding affinity to EGFR T790M mutant kinases.",
            status="in_progress",
            created_at=datetime.now(timezone.utc),
            generated_code="import math\nprint('Running molecular docking affinity calculation...')",
            execution_stdout="Docking iteration 4/10 in progress...",
            execution_stderr="",
            execution_time_ms=1200,
            citations=[
                Citation(
                    citation_id="arxiv:2401.05512",
                    title="Generative Chemistry with Graph Neural Networks for Kinase Targeting",
                    authors=["AlQuraishi, M.", "Kohl, B."],
                    year=2024,
                    source="arxiv",
                    url="https://arxiv.org/abs/2401.05512",
                    similarity_score=0.94,
                    key_findings="Pyrimidine scaffold demonstrates selective binding to gatekeeper mutants."
                )
            ],
            workflow_steps=[
                WorkflowStep(
                    step_id="step-1",
                    agent_role="literature_reviewer",
                    title="Review Kinase Literature",
                    description="Scanned 8 preprints from ArXiv bio-pharma.",
                    status="completed",
                    duration_ms=1450,
                    logs=["Scraped ArXiv 2401.05512", "Extracted SMILES representations."],
                ),
                WorkflowStep(
                    step_id="step-2",
                    agent_role="hypothesis_generator",
                    title="Formulate Molecular Hypothesis",
                    description="Derived target scaffold hypothesis.",
                    status="completed",
                    duration_ms=1800,
                    logs=["Hypothesis drafted."],
                ),
                WorkflowStep(
                    step_id="step-3",
                    agent_role="code_executor",
                    title="Docker Docking Simulation",
                    description="Running docking script in container sandbox.",
                    status="running",
                    duration_ms=1200,
                    logs=["Container active", "Memory: 64MB / 128MB"],
                ),
            ],
            cost=TokenCostRecord(
                model_name="gemini-1.5-flash",
                prompt_tokens=3100,
                completion_tokens=680,
                total_tokens=3780,
                cost_usd=0.00044,
            ),
        )

        self._experiments[sample_exp1.experiment_id] = sample_exp1
        self._experiments[sample_exp2.experiment_id] = sample_exp2
        self.save_to_disk()
