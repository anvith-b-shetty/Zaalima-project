from scientific_discovery.execution.executor import CodeExecutor
from scientific_discovery.execution.model import ExecutionRequest
from langgraph.graph import StateGraph, START, END

from scientific_discovery.orchestration.state import ResearchState
from scientific_discovery.agents.hypothesis_generator.generator import (
    generate_hypothesis
)
from scientific_discovery.agents.experiment_designer.code_generator import (
    generate_experiment_code
)


MAX_ITERATIONS = 3
docker_executor = CodeExecutor()

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
# Agent 3: Experiment Code Generator
# -----------------------------------------

def experiment_designer(state: ResearchState):
    print("\n[Experiment Designer] Generating experiment using Gemma...")

    hypothesis_details = state.get(
        "selected_hypothesis_details", {}
    )

    findings = state.get("research_findings", [])
    feedback = state.get("critic_feedback", "")
    previous_code = (
        state.get("experiment_code", "")
        if feedback else ""
    )

    experiment = generate_experiment_code(
        hypothesis_details=hypothesis_details,
        research_findings=findings,
        critic_feedback=feedback,
        previous_code=previous_code
    )

    print("\nExperiment Title:")
    print(experiment["title"])

    print("\nExperiment Explanation:")
    print(experiment["explanation"])

    print("\nGenerated Experiment Code:")
    print(experiment["code"])

    return {
        "experiment_code": experiment["code"],
        "experiment_design": experiment,
        "current_step": "code_execution"
    }

def code_executor(state: ResearchState):
    print("\n[Code Executor] Running experiment inside Docker...")

    iteration = state.get("iteration_count", 0) + 1
    errors = list(state.get("errors", []))
    history = list(state.get("experiment_history", []))

    experiment_code = state.get("experiment_code", "")

    try:
        if not experiment_code.strip():
            raise ValueError(
                "No experiment code provided in ResearchState."
            )

        # Execute Python code inside Docker.
        request = ExecutionRequest(
            code=experiment_code,
            timeout_seconds=10
        )

        response = docker_executor.execute(request)

        # Convert Pydantic response into a dictionary.
        result = response.model_dump()

        if result["status"] != "success":
            errors.append(
                result.get("stderr") or
                f"Execution failed: {result['status']}"
            )

        print(f"\nExecution Status: {result['status']}")
        print(f"Execution Output: {result['stdout']}")
        print(f"Execution Error: {result['stderr']}")
        print(f"Execution Time: {result['execution_time_ms']} ms")

    except Exception as exc:
        error_message = str(exc)
        errors.append(error_message)

        result = {
            "status": "error",
            "stdout": "",
            "stderr": error_message,
            "exit_code": None,
            "execution_time_ms": 0,
            "truncated_output": False
        }

        print(f"\nExecution Error: {error_message}")

    history.append({
        "attempt": iteration,
        "hypothesis": state.get("selected_hypothesis", ""),
        "experiment_code": experiment_code,
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
    experiment_code = state.get("experiment_code", "")

    if result.get("status") != "success":
        status = "needs_improvement"
        feedback = (
            "Experiment execution failed. Review the execution error "
            "and generate a corrected experiment."
        )

    elif not result.get("stdout", "").strip():
        status = "needs_improvement"
        feedback = (
            "The experiment produced no output. Add meaningful "
            "observations and printed results."
        )

    elif "Average glucose reading:" not in result.get("stdout", ""):
        status = "needs_improvement"
        feedback = (
            "The expected average glucose calculation was not found. "
            "Review the experiment calculations."
        )

    else:
        status = "passed"
        feedback = (
            "The demonstration experiment executed successfully and "
            "produced the expected output. This does not validate "
            "the scientific hypothesis."
        )

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

    return "experiment_designer"

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
    workflow.add_node("experiment_designer", experiment_designer)
    workflow.add_node("code_executor", code_executor)
    workflow.add_node("critic_agent", critic_agent)
    workflow.add_node("research_synthesis", research_synthesis)

    workflow.add_edge(START, "literature_reviewer")
    workflow.add_edge("literature_reviewer", "hypothesis_generator")
    workflow.add_edge("hypothesis_generator", "experiment_designer")
    workflow.add_edge("experiment_designer", "code_executor")
    workflow.add_edge("code_executor", "critic_agent")

    workflow.add_conditional_edges(
        "critic_agent",
        route_after_critic,
        {
            "experiment_designer": "experiment_designer",
            "research_synthesis": "research_synthesis"
        }
    )

    workflow.add_edge("research_synthesis", END)

    return workflow.compile()
