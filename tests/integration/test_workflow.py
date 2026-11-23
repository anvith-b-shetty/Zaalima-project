
from scientific_discovery.orchestration.graph import build_research_graph


def test_research_workflow():
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

    final_state = research_graph.invoke(initial_state)

    # Verify workflow completion
    assert final_state["current_step"] == "completed"

    # Verify hypothesis generation
    assert len(final_state["generated_hypotheses"]) > 0

    # Verify experiment execution was attempted
    assert final_state["iteration_count"] >= 1

    # Verify final report generation
    assert final_state["final_report"]

    print("\nWorkflow completed successfully!")
    print("Final status:", final_state["current_step"])
    print("Iterations:", final_state["iteration_count"])
    # Verify successful Docker execution
    assert final_state["execution_result"]["status"] == "success"

    # Verify Critic Agent evaluation
    assert final_state["evaluation_status"] == "passed"

    # Verify experiment history
    assert len(final_state["experiment_history"]) >= 1

    assert (
        final_state["experiment_history"][-1]["result"]["status"]
        == "success"
    )

    print("Docker execution: SUCCESS")
    print("Critic evaluation: PASSED")