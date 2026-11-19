
from langgraph.graph import StateGraph, START, END

from scientific_discovery.orchestration.state import ResearchState
from scientific_discovery.agents.hypothesis_generator.generator import (
    generate_hypothesis
)


MAX_ITERATIONS = 3


# -----------------------------------------
# Agent 1: Literature Reviewer
# -----------------------------------------

def literature_reviewer(state: ResearchState):
    print("\n[Literature Reviewer] Reviewing research literature...")

    return {
        "research_findings": [
            "Existing research provides useful background.",
            "Further experimental investigation is required."
        ],
        "current_step": "hypothesis_generation"
    }


# -----------------------------------------
# Agent 2: LLM Hypothesis Generator
# -----------------------------------------

def hypothesis_generator(state: ResearchState):
    print("\n[Hypothesis Generator] Generating structured hypothesis using Gemma...")

    findings = state.get("research_findings", [])
    feedback = state.get("critic_feedback", "")
    research_query = state.get("research_query", "")

    # Generate structured hypothesis using Gemma.
    hypothesis_details = generate_hypothesis(
        research_query=research_query,
        research_findings=findings,
        critic_feedback=feedback
    )

    # Extract the actual hypothesis text.
    hypothesis = hypothesis_details["hypothesis"]

    # Preserve all structured hypotheses.
    hypotheses = list(state.get("generated_hypotheses", []))
    hypotheses.append(hypothesis_details)

    print("\nGenerated Hypothesis:")
    print(hypothesis)

    print("\nScientific Reasoning:")
    print(hypothesis_details["reasoning"])

    print("\nVariables:")
    for variable in hypothesis_details["variables"]:
        print("-", variable)

    return {
        "generated_hypotheses": hypotheses,
        "selected_hypothesis": hypothesis,
        "selected_hypothesis_details": hypothesis_details,
        "current_step": "code_execution"
    }

# -----------------------------------------
# Agent 3: Code Executor (Placeholder)
# -----------------------------------------

def code_executor(state: ResearchState):
    print("\n[Code Executor] Running experiment...")

    iteration = state.get("iteration_count", 0) + 1
    errors = list(state.get("errors", []))
    history = list(state.get("experiment_history", []))

    try:
        # Placeholder experiment result.
        # Real Python execution will be integrated later.
        result = {
            "status": "success",
            "output": f"Sample experiment completed. Attempt {iteration}."
        }

    except Exception as exc:
        error_message = str(exc)
        errors.append(error_message)

        result = {
            "status": "error",
            "output": None,
            "error": error_message
        }

    history.append({
        "attempt": iteration,
        "hypothesis": state.get("selected_hypothesis", ""),
        "experiment_code": state.get("experiment_code", ""),
        "result": result,
        "critic_feedback": "",
        "evaluation_status": "pending"
    })

    return {
        "execution_result": result,
        "experiment_history": history,
        "iteration_count": iteration,
        "errors": errors,
        "current_step": "critic_evaluation"
    }


# -----------------------------------------
# Agent 4: Critic
# -----------------------------------------

def critic_agent(state: ResearchState):
    print("\n[Critic Agent] Evaluating experiment...")

    iteration = state.get("iteration_count", 0)
    result = state.get("execution_result", {})

    if result.get("status") != "success":
        status = "needs_improvement"
        feedback = (
            "Experiment execution failed. Review the error "
            "and correct the experiment."
        )

    elif iteration == 1:
        status = "needs_improvement"
        feedback = (
            "Improve the experimental design and investigate "
            "additional relevant research variables."
        )

    else:
        status = "passed"
        feedback = "The sample experiment passed the evaluation."

    history = list(state.get("experiment_history", []))

    if history:
        history[-1] = {
            **history[-1],
            "critic_feedback": feedback,
            "evaluation_status": status
        }

    print(f"Evaluation: {status}")
    print(f"Feedback: {feedback}")

    return {
        "critic_feedback": feedback,
        "evaluation_status": status,
        "experiment_history": history,
        "current_step": "evaluation_decision"
    }


# -----------------------------------------
# Conditional Routing
# -----------------------------------------

def route_after_critic(state: ResearchState):

    status = state.get("evaluation_status", "")
    iteration = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", MAX_ITERATIONS)

    if status == "passed":
        return "research_synthesis"

    if iteration >= max_iterations:
        return "research_synthesis"

    return "hypothesis_generator"


# -----------------------------------------
# Agent 5: Research Synthesis
# -----------------------------------------

def research_synthesis(state: ResearchState):
    print("\n[Research Synthesis] Preparing final report...")

    history = state.get("experiment_history", [])

    report = [
        f"Research Question: {state.get('research_query', '')}",
        "",
        "Experiment History:"
    ]

    for attempt in history:
        report.append(f"\nAttempt: {attempt['attempt']}")
        report.append(f"Hypothesis: {attempt['hypothesis']}")
        report.append(f"Result: {attempt['result']}")
        report.append(f"Feedback: {attempt['critic_feedback']}")
        report.append(f"Evaluation: {attempt['evaluation_status']}")

    report.append("\nFinal Evaluation:")
    report.append(state.get("evaluation_status", "not evaluated"))

    report.append("\nFinal Critic Feedback:")
    report.append(state.get("critic_feedback", ""))

    return {
        "final_report": "\n".join(report),
        "current_step": "completed"
    }


# -----------------------------------------
# Build LangGraph Workflow
# -----------------------------------------

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
