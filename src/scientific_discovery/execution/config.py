
"""
Configuration for the Code Execution Engine.
"""

# Docker configuration
DOCKER_IMAGE = "python:3.12-slim"

# Execution limits
DEFAULT_TIMEOUT_SECONDS = 10
MAX_TIMEOUT_SECONDS = 20

# Resource restrictions
DOCKER_MEMORY_LIMIT = "128m"
DOCKER_CPU_LIMIT = "0.5"
DOCKER_PIDS_LIMIT = 64

# Input and output restrictions
MAX_CODE_SIZE_BYTES = 50_000
MAX_OUTPUT_SIZE_BYTES = 10_000

# Security settings
DOCKER_NETWORK_MODE = "none"
DOCKER_READ_ONLY = True
DOCKER_TMPFS_SIZE = "16m"
