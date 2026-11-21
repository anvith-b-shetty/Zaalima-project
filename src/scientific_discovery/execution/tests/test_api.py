
"""
Automated API tests for the Code Execution Interface.

Uses FastAPI TestClient and a mocked executor so
these tests do not require Docker to run.
"""

from fastapi.testclient import TestClient

from src.scientific_discovery.execution import api
from src.scientific_discovery.execution.model import ExecutionResponse


client = TestClient(api.app)


def test_successful_api_execution(monkeypatch):
    """Verify that the API returns a successful result."""

    def mock_execute(request):
        return ExecutionResponse(
            status="success",
            stdout="30\n",
            stderr="",
            exit_code=0,
            execution_time_ms=100,
            truncated_output=False,
        )

    monkeypatch.setattr(
        api.code_executor,
        "execute",
        mock_execute,
    )

    response = client.post(
        "/execution/execute",
        json={
            "code": "print(10 + 20)",
            "language": "python",
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["stdout"] == "30\n"
    assert response.json()["exit_code"] == 0


def test_runtime_error_api_response(monkeypatch):
    """Verify that runtime errors are returned correctly."""

    def mock_execute(request):
        return ExecutionResponse(
            status="error",
            stdout="",
            stderr="ZeroDivisionError: division by zero",
            exit_code=1,
            execution_time_ms=100,
            truncated_output=False,
        )

    monkeypatch.setattr(
        api.code_executor,
        "execute",
        mock_execute,
    )

    response = client.post(
        "/execution/execute",
        json={
            "code": "print(1 / 0)",
            "language": "python",
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "error"
    assert "ZeroDivisionError" in response.json()["stderr"]
    assert response.json()["exit_code"] == 1


def test_empty_code_validation():
    """Verify that empty code is rejected by the API."""

    response = client.post(
        "/execution/execute",
        json={
            "code": "",
            "language": "python",
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 422
    assert "Code cannot be empty" in response.json()["detail"][0]["msg"]


def test_timeout_validation():
    """Verify that timeout values above the limit are rejected."""

    response = client.post(
        "/execution/execute",
        json={
            "code": "print(10 + 20)",
            "language": "python",
            "timeout_seconds": 30,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == [
        "body",
        "timeout_seconds",
    ]


def test_unsupported_language_validation():
    """Verify that unsupported languages are rejected."""

    response = client.post(
        "/execution/execute",
        json={
            "code": "print(10 + 20)",
            "language": "javascript",
            "timeout_seconds": 10,
        },
    )

    assert response.status_code == 422
