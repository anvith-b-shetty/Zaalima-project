
import ollama


MODEL_NAME = "gemma3:1b"


def generate_hypothesis(
    research_query: str,
    research_findings: list[str],
    critic_feedback: str = ""
) -> str:
    """
    Generate or revise a scientific research hypothesis
    using the locally hosted Gemma model.
    """

    findings_text = "\n".join(
        f"- {finding}" for finding in research_findings
    ) or "No literature findings available yet."

    if critic_feedback:
        task = f"""
Revise the previous hypothesis using this critic feedback:
{critic_feedback}
"""
    else:
        task = "Generate an initial research hypothesis."

    prompt = f"""
You are a scientific research hypothesis generation agent.

Research question:
{research_query}

Available research findings:
{findings_text}

Task:
{task}

Requirements:
1. Produce ONE clear and testable scientific hypothesis.
2. Explain the expected relationship between variables.
3. Keep it concise and scientifically reasonable.
4. Do not invent experimental results or claim the hypothesis is proven.

Return:
Hypothesis:
Scientific reasoning:
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.3,
            "num_predict": 200
        }
    )

    return response.message.content.strip()
