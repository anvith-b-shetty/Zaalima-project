
import json
from typing import Any

import ollama


MODEL_NAME = "gemma3:1b"

# Enforce the expected response structure.
HYPOTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "hypothesis": {"type": "string"},
        "reasoning": {"type": "string"},
        "variables": {
            "type": "array",
            "items": {"type": "string"}
        },
        "expected_relationship": {"type": "string"}
    },
    "required": [
        "hypothesis",
        "reasoning",
        "variables",
        "expected_relationship"
    ],
    "additionalProperties": False
}


def generate_hypothesis(
    research_query: str,
    research_findings: list[str],
    critic_feedback: str = ""
) -> dict[str, Any]:

    findings_text = "\n".join(
        f"- {finding}" for finding in research_findings
    ) or "No literature findings available."

    if critic_feedback:
        task = f"""
    Revise the previous scientific hypothesis using this feedback:

    {critic_feedback}

    IMPORTANT:
    - Do not copy the critic feedback as the hypothesis.
    - Treat the feedback as instructions for improvement.
    - Write a NEW, complete, testable scientific hypothesis.
    - Include the independent and dependent variables.
    - Explain the expected relationship between them.
    """
    else:
        task = "Generate an initial scientific hypothesis."

    prompt = f"""
You are a scientific hypothesis generation agent.

Research question:
{research_query}

Research findings:
{findings_text}

Task:
{task}

Generate ONE concise, testable scientific hypothesis.

Return these four fields:
1. hypothesis: The testable hypothesis.
2. reasoning: Brief scientific explanation.
3. variables: List of relevant variables.
4. expected_relationship: Expected relationship between variables.

Do not invent results or claim the hypothesis is proven.
Return only the requested structured data.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format=HYPOTHESIS_SCHEMA,
        options={
            "temperature": 0.2,
            "num_predict": 450
        }
    )

    raw_response = response.message.content

    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemma returned invalid JSON: {raw_response}"
        ) from exc

    required_fields = [
        "hypothesis",
        "reasoning",
        "variables",
        "expected_relationship"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")

    for field in [
        "hypothesis",
        "reasoning",
        "expected_relationship"
    ]:
        if not isinstance(result[field], str) or not result[field].strip():
            raise ValueError(f"Invalid or empty field: {field}")

    if (
        not isinstance(result["variables"], list)
        or not all(
            isinstance(item, str) and item.strip()
            for item in result["variables"]
        )
    ):
        raise ValueError("Variables must be a list of non-empty strings.")

    return result
