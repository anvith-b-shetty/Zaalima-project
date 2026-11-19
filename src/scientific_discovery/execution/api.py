
"""
FastAPI interface for the Code Execution Engine.
"""

from fastapi import APIRouter, FastAPI

from .executor import CodeExecutor
from .model import ExecutionRequest, ExecutionResponse


# Initialize the executor
code_executor = CodeExecutor()

# Create the API router
router = APIRouter(
    prefix="/execution",
    tags=["Code Execution"]
)


@router.post(
    "/execute",
    response_model=ExecutionResponse
)
def execute_code(
    request: ExecutionRequest
) -> ExecutionResponse:
    """Execute submitted Python code using Docker."""
    return code_executor.execute(request)


# Create the FastAPI application
app = FastAPI(
    title="Scientific Discovery Code Executor",
    description="API for isolated Python code execution",
    version="1.0.0"
)


# Register the execution router
app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Code Executor"
    }
