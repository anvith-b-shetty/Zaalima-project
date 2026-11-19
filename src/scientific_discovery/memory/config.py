"""
Configuration for the Memory and Experiment Tracking Engine.
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
EXPERIMENTS_DATA_DIR = DATA_DIR / "experiments"
METRICS_DATA_DIR = DATA_DIR / "metrics"

# Ensure data directories exist
EXPERIMENTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Default storage paths
DEFAULT_EXPERIMENTS_FILE = EXPERIMENTS_DATA_DIR / "experiment_history.json"
DEFAULT_MEMORY_LOG_FILE = EXPERIMENTS_DATA_DIR / "session_memory.jsonl"

# Token pricing rates (USD per 1,000,000 tokens)
MODEL_PRICING = {
    "gemini-1.5-pro": {"prompt": 3.50, "completion": 10.50},
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gpt-4o": {"prompt": 5.00, "completion": 15.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
}
DEFAULT_MODEL = "gemini-1.5-flash"

# Context window limits (in tokens)
MAX_CONTEXT_WINDOW_TOKENS = 128_000
BUFFER_TRIGGER_THRESHOLD = 0.80  # Trigger compaction at 80% usage
