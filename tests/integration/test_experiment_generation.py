
from scientific_discovery.agents.experiment_designer.code_generator import (
    generate_experiment_code,
    validate_experiment_code
)


def test_gemma_generates_valid_experiment():
    hypothesis = {
        "hypothesis": (
            "Higher daily physical activity may be associated "
            "with lower average blood glucose levels."
        ),
        "reasoning": "Physical activity may influence glucose regulation.",
        "variables": [
            "daily physical activity",
            "average blood glucose level"
        ],
        "expected_relationship": (
            "An increase in physical activity may be associated "
            "with lower average blood glucose."
        )
    }

    research_findings = [
        "Physical activity is relevant to glucose regulation.",
        "A real patient dataset has not yet been connected."
    ]

    result = generate_experiment_code(
        hypothesis_details=hypothesis,
        research_findings=research_findings
    )

    assert result["code"]
    assert result["explanation"]
    assert isinstance(result["assumptions"], list)

    validate_experiment_code(result["code"])

    print("\nGenerated experiment:")
    print(result["code"])
