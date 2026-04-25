"""Configuration and Anthropic client setup."""
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY='sk-ant-...'"
    )

# Model: Claude Sonnet 4.6 — good quality/cost balance for this task.
# If quality is insufficient on tricky cases, swap to Opus.
MODEL = "claude-sonnet-4-6"

# Token limits
MAX_TOKENS_DESCRIPTION = 1024
MAX_TOKENS_CLUSTER = 32768
MAX_TOKENS_TAXONOMY = 16384
MAX_TOKENS_CLASSIFICATION = 1024

# Batch sizes (tune based on token limits and rate limits)
CLUSTERING_BATCH_SIZE = 15  # descriptions per clustering call (mindre = mer reliable, mer cost)
CLASSIFICATION_BATCH_SIZE = 1  # one task at a time for accuracy

# Retry config
MAX_RETRIES = 5
INITIAL_RETRY_DELAY = 2.0

PROJECT_ROOT = Path(__file__).resolve().parent.parent

client = Anthropic(api_key=API_KEY)
