
from typing import TypedDict, List, Dict, Any


class ResearchState(TypedDict, total=False):
    research_query: str
    retrieved_papers: List[Dict[str, Any]]
    research_findings: List[str]

    # Structured LLM-generated hypotheses
    generated_hypotheses: List[Dict[str, Any]]
    selected_hypothesis: str
    selected_hypothesis_details: Dict[str, Any]

    critic_feedback: str
    evaluation_status: str

    experiment_code: str
    execution_result: Dict[str, Any]
    experiment_history: List[Dict[str, Any]]

    final_report: str
    current_step: str
    iteration_count: int
    max_iterations: int
    errors: List[str]
