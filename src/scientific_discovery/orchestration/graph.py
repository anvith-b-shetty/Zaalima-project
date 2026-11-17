
from langgraph.graph import StateGraph, START, END

from scientific_discovery.orchestration.state import ResearchState


MAX_ITERATIONS = 3


# Agent 1: Literature Reviewer
def literature_reviewer(state: ResearchState):
    print("\n[Literature Reviewer] Reviewing research literature...")

    return {
        "research_findings": [
            "Existing research provides useful background.",
            "Further experimental investigation is required."
        ],
        "current_step": "hypothesis_generation"
    }


# Agent 2: Hypothesis Generator
def hypothesis_generator(state: ResearchState):
    print("\n[Hypothesis Generator] Generating hypotheses...")

    findings = state.get("research_findings", [])

    hypotheses = [
        f"Research hypothesis based on: {finding}"
        for finding in findings
    ]

    return {
        "generated_hypotheses": hypotheses,
        "selected_hypothesis": hypotheses[0] if hypotheses else "",
        "current_step": "code_execution"
    }


# Agent 3: Code Executor
def code_executor(state: ResearchState):
    print("\n[Code Executor] Executing experiment...")

    iteration = state.get("iteration_count", 0) + 1

    return {
        "execution_result": {
            "status": "success",
            "output": f"Sample experiment completed. Attempt {iteration}."
        },
        "iteration_count": iteration,
        "current_step": "critic_evaluation"
    }


# Agent 4: Critic
def critic_agent(state: ResearchState):
    print("\n[Critic Agent] Evaluating experiment results...")

    # Temporary evaluation logic for testing
    if state.get("iteration_count", 0) < 2:
        status = "needs_improvement"
        feedback = "More experimentation is required."
    else:
        status = "passed"
        feedback = "Experiment passed the sample evaluation."

    return {
        "critic_feedback": feedback,
        "evaluation_status": status,
        "current_step": "evaluation_decision"
    }


# Conditional routing
def route_after_critic(state: ResearchState):

    status = state.get("evaluation_status", "")
    iteration = state.get("iteration_count", 0)

    if status == "passed":
        return "research_synthesis"

    if iteration >= MAX_ITERATIONS:
        return "research_synthesis"

    return "hypothesis_generator"


# Agent 5: Research Synthesis
def research_synthesis(state: ResearchState):
    print("\n[Research Synthesis] Preparing final report...")

    report = (
        f"Research Question: {state.get('research_query', '')}\n"
        f"Hypothesis: {state.get('selected_hypothesis', '')}\n"
        f"Result: {state.get('execution_result', {})}\n"
        f"Evaluation: {state.get('critic_feedback', '')}\n"
        f"Total Attempts: {state.get('iteration_count', 0)}"
    )

    return {
        "final_report": report,
        "current_step": "completed"
    }


# Build the workflow
def build_research_graph():

    workflow = StateGraph(ResearchState)

    workflow.add_node("literature_reviewer", literature_reviewer)
    workflow.add_node("hypothesis_generator", hypothesis_generator)
    workflow.add_node("code_executor", code_executor)
    workflow.add_node("critic_agent", critic_agent)
    workflow.add_node("research_synthesis", research_synthesis)

    workflow.add_edge(START, "literature_reviewer")
    workflow.add_edge("literature_reviewer", "hypothesis_generator")
    workflow.add_edge("hypothesis_generator", "code_executor")
    workflow.add_edge("code_executor", "critic_agent")

    workflow.add_conditional_edges(
        "critic_agent",
        route_after_critic,
        {
            "hypothesis_generator": "hypothesis_generator",
            "research_synthesis": "research_synthesis"
        }
    )

    workflow.add_edge("research_synthesis", END)

    return workflow.compile()
