
import json

import pytest

from scientific_discovery.agents.experiment_designer import code_generator


def make_response(data):
    return {
        "message": {
            "content": json.dumps(data)
        }
    }


def valid_experiment_response():
    return {
        "title": "Activity and glucose demonstration",
        "explanation": "A synthetic demonstration experiment.",
        "observations": [
            {"activity_level": 20, "glucose_reading": 150},
            {"activity_level": 40, "glucose_reading": 130},
            {"activity_level": 60, "glucose_reading": 120}
        ],
        "assumptions": [
            "All observations are synthetic."
        ]
    }


def test_generator_builds_valid_code(monkeypatch):
    data = valid_experiment_response()

    monkeypatch.setattr(
        code_generator.ollama,
        "chat",
        lambda **kwargs: make_response(data)
    )

    result = code_generator.generate_experiment_code(
        hypothesis_details={"hypothesis": "Test hypothesis"},
        research_findings=["Test finding"]
    )

    assert result["code"]
    assert result["title"] == data["title"]
    assert result["assumptions"] == data["assumptions"]

    code_generator.validate_experiment_code(result["code"])


def test_generator_rejects_invalid_json(monkeypatch):
    monkeypatch.setattr(
        code_generator.ollama,
        "chat",
        lambda **kwargs: {"message": {"content": "not valid JSON"}}
    )

    with pytest.raises(ValueError, match="invalid experiment JSON"):
        code_generator.generate_experiment_code(
            hypothesis_details={"hypothesis": "Test"},
            research_findings=[]
        )


def test_generator_rejects_too_few_observations(monkeypatch):
    data = valid_experiment_response()
    data["observations"] = [
        {"activity_level": 20, "glucose_reading": 150}
    ]

    monkeypatch.setattr(
        code_generator.ollama,
        "chat",
        lambda **kwargs: make_response(data)
    )

    with pytest.raises(ValueError, match="between 3 and 5"):
        code_generator.generate_experiment_code(
            hypothesis_details={"hypothesis": "Test"},
            research_findings=[]
        )


def test_generator_rejects_out_of_range_observations(monkeypatch):
    data = valid_experiment_response()
    data["observations"][0]["activity_level"] = 150

    monkeypatch.setattr(
        code_generator.ollama,
        "chat",
        lambda **kwargs: make_response(data)
    )

    with pytest.raises(ValueError, match="outside the allowed range"):
        code_generator.generate_experiment_code(
            hypothesis_details={"hypothesis": "Test"},
            research_findings=[]
        )
