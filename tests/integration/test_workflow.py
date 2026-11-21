
from scientific_discovery.orchestration.graph import build_research_graph


def main():

    research_graph = build_research_graph()

    initial_state = {
        "research_query": "Can machine learning improve early diabetes prediction?",
        "retrieved_papers": [],
        "research_findings": [],
        "generated_hypotheses": [],
        "selected_hypothesis": "",
        "selected_hypothesis_details": {},
        "critic_feedback": "",
        "evaluation_status": "",
        "experiment_code": "",
        "experiment_design": {},
        "execution_result": {},
        "experiment_history": [],
        "final_report": "",
        "current_step": "start",
        "iteration_count": 0,
        "max_iterations": 3,
        "errors": []
    }

    print("\nStarting Scientific Discovery Workflow...")

    final_state = research_graph.invoke(initial_state)

    print("\n========== FINAL RESEARCH REPORT ==========")
    print(final_state["final_report"])

    print("\n========== HYPOTHESIS HISTORY ==========")

    for index, hypothesis in enumerate(
        final_state["generated_hypotheses"], start=1
    ):
        print(f"\nHypothesis {index}:")
        print(hypothesis["hypothesis"])
        print("Reasoning:", hypothesis["reasoning"])
        print("Variables:", hypothesis["variables"])
        print("Expected Relationship:", hypothesis["expected_relationship"])

    print("\n========== EXPERIMENT HISTORY ==========")

    for attempt in final_state["experiment_history"]:
        print(f"\nAttempt: {attempt['attempt']}")
        print(f"Hypothesis: {attempt['hypothesis']}")
        print(f"Result: {attempt['result']}")
        print(f"Feedback: {attempt['critic_feedback']}")
        print(f"Evaluation: {attempt['evaluation_status']}")

    print("\n========== WORKFLOW SUMMARY ==========")
    print("Status:", final_state["current_step"])
    print("Iterations:", final_state["iteration_count"])
    print("Evaluation:", final_state["evaluation_status"])
    print("Errors:", final_state["errors"])


if __name__ == "__main__":
    main()
