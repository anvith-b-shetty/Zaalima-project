
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

    print("\n========== GENERATED HYPOTHESIS ==========")
    print(result)


if __name__ == "__main__":
    main()
