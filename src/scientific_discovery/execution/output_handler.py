
"""
Output Handler for the Code Execution Engine.

Processes captured stdout and stderr, determines
execution status, and creates structured responses.
"""

from .model import ExecutionResponse


class OutputHandler:
    """Format and classify Docker execution results."""

    @staticmethod
    def decode_output(data: bytes) -> str:
        """Convert captured bytes into readable text."""
        return data.decode("utf-8", errors="replace")

    def build_response(
        self,
        stdout: bytes,
        stderr: bytes,
        exit_code: int | None,
        execution_time_ms: int,
        timed_out: bool = False,
        output_limit_reached: bool = False,
    ) -> ExecutionResponse:
        """
        Create a structured execution response.

        Determines whether execution succeeded, failed,
        exceeded its time limit, or exceeded its output limit.
        """

        stdout_text = self.decode_output(stdout)
        stderr_text = self.decode_output(stderr)

        if timed_out:
            status = "timeout"
            stderr_text += "\nExecution time limit exceeded."

        elif output_limit_reached:
            status = "error"
            stderr_text += "\nMaximum output size exceeded."

        elif exit_code == 0:
            status = "success"

        else:
            status = "error"

        return ExecutionResponse(
            status=status,
            stdout=stdout_text,
            stderr=stderr_text,
            exit_code=exit_code,
            execution_time_ms=max(0, execution_time_ms),
            truncated_output=output_limit_reached,
        )
