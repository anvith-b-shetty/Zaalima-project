
"""
Unit tests for the Code Executor Output Handler.
"""

from src.scientific_discovery.execution.output_handler import OutputHandler


def test_successful_execution():
    handler = OutputHandler()

    result = handler.build_response(
        stdout=b"30\n",
        stderr=b"",
        exit_code=0,
        execution_time_ms=100,
    )

    assert result.status == "success"
    assert result.stdout == "30\n"
    assert result.stderr == ""
    assert result.exit_code == 0


def test_runtime_error():
    handler = OutputHandler()

    result = handler.build_response(
        stdout=b"",
        stderr=b"ZeroDivisionError",
        exit_code=1,
        execution_time_ms=100,
    )

    assert result.status == "error"
    assert "ZeroDivisionError" in result.stderr
    assert result.exit_code == 1


def test_timeout_handling():
    handler = OutputHandler()

    result = handler.build_response(
        stdout=b"",
        stderr=b"",
        exit_code=137,
        execution_time_ms=10000,
        timed_out=True,
    )

    assert result.status == "timeout"
    assert "Execution time limit exceeded" in result.stderr


def test_output_limit_handling():
    handler = OutputHandler()

    result = handler.build_response(
        stdout=b"A" * 10000,
        stderr=b"",
        exit_code=0,
        execution_time_ms=100,
        output_limit_reached=True,
    )

    assert result.status == "error"
    assert result.truncated_output is True
    assert len(result.stdout.encode("utf-8")) == 10000
    assert "Maximum output size exceeded" in result.stderr


def test_invalid_utf8_output():
    handler = OutputHandler()

    result = handler.build_response(
        stdout=b"Hello\xff",
        stderr=b"",
        exit_code=0,
        execution_time_ms=100,
    )

    assert result.status == "success"
    assert "\ufffd" in result.stdout


def test_negative_execution_time():
    handler = OutputHandler()

    result = handler.build_response(
        stdout=b"",
        stderr=b"",
        exit_code=0,
        execution_time_ms=-10,
    )

    assert result.execution_time_ms == 0
