
from scientific_discovery.orchestration.graph import build_research_graph


def main():
    # Create the research workflow
    research_graph = build_research_graph()

    # Initial input from the user
    initial_state = {
        "research_query": "Can machine learning improve early diabetes prediction?",
        "retrieved_papers": [],
        "research_findings": [],
        "generated_hypotheses": [],
        "selected_hypothesis": "",
        "experiment_code": "",
        "execution_result": {},
        "critic_feedback": "",
        "evaluation_status": "",
        "final_report": "",
        "current_step": "start",
        "iteration_count": 0,
        "errors": []
    }

    # Execute the workflow
    final_state = research_graph.invoke(initial_state)

    # Display results
    print("\n========== FINAL RESEARCH REPORT ==========")
    print(final_state["final_report"])

    print("\n========== WORKFLOW STATUS ==========")
    print(final_state["current_step"])

    print("\n========== GENERATED HYPOTHESES ==========")
    for hypothesis in final_state["generated_hypotheses"]:
        print("-", hypothesis)


if __name__ == "__main__":
    main()
