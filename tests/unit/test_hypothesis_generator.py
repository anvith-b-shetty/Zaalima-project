
from scientific_discovery.agents.hypothesis_generator.generator import (
    generate_hypothesis
)


def main():
    result = generate_hypothesis(
        research_query=(
            "Can machine learning improve early diabetes prediction?"
        ),
        research_findings=[
            "Blood glucose levels are important predictors.",
            "BMI and age may contribute to diabetes risk."
        ]
    )

    print("\n========== STRUCTURED HYPOTHESIS ==========")

    print("\nHypothesis:")
    print(result["hypothesis"])

    print("\nScientific Reasoning:")
    print(result["reasoning"])

    print("\nVariables:")
    for variable in result["variables"]:
        print("-", variable)

    print("\nExpected Relationship:")
    print(result["expected_relationship"])

    print("\n========== JSON OUTPUT ==========")
    print(result)


if __name__ == "__main__":
    main()
