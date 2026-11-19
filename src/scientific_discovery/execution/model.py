
"""
Data models for the Code Execution Engine.

Defines the request received from the AI agent
and the response returned by the executor.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .config import (
    DEFAULT_TIMEOUT_SECONDS,
    MAX_TIMEOUT_SECONDS,
    MAX_CODE_SIZE_BYTES,
)


class ExecutionRequest(BaseModel):
    """Request containing code submitted for execution."""

    code: str = Field(..., description="Python source code")

    language: Literal["python"] = Field(
        default="python",
        description="Supported programming language",
    )

    timeout_seconds: int = Field(
        default=DEFAULT_TIMEOUT_SECONDS,
        ge=1,
        le=MAX_TIMEOUT_SECONDS,
        description="Maximum execution time in seconds",
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Code cannot be empty")

        if len(value.encode("utf-8")) > MAX_CODE_SIZE_BYTES:
            raise ValueError("Code exceeds the maximum allowed size")

        return value


class ExecutionResponse(BaseModel):
    """Structured result returned by the executor."""

    status: Literal["success", "error", "timeout"]

    stdout: str = ""

    stderr: str = ""

    exit_code: int | None = None

    execution_time_ms: int = Field(default=0, ge=0)

    truncated_output: bool = False
