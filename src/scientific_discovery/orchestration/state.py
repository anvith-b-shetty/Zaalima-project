
from typing import TypedDict, List, Dict, Any


class ResearchState(TypedDict, total=False):
    """
    Shared state used by all agents in the
    Autonomous Multimodal Scientific Discovery Agent.
    """

    # User input
    research_query: str

    # Literature Reviewer Agent
    retrieved_papers: List[Dict[str, Any]]
    research_findings: List[str]

    # Hypothesis Generator Agent
    generated_hypotheses: List[str]
    selected_hypothesis: str

    # Critic Agent
    critic_feedback: str
    evaluation_status: str

    # Code Executor Agent
    experiment_code: str
    execution_result: Dict[str, Any]

    # Complete experiment history
    experiment_history: List[Dict[str, Any]]

    # Research Synthesis
    final_report: str

    # Workflow management
    current_step: str
    iteration_count: int
    max_iterations: int

    # Error tracking
    errors: List[str]
