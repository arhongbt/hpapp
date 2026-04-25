"""Utility functions used across the pipeline."""
import json
import re
from pathlib import Path
from typing import Iterator
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from anthropic import APIError, RateLimitError, APIConnectionError

from .config import client, MODEL, MAX_RETRIES, INITIAL_RETRY_DELAY


def read_jsonl(path: Path) -> Iterator[dict]:
    """Stream JSONL file as dicts."""
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {line_num} of {path}: {e}")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    """Write list of dicts as JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, row: dict) -> None:
    """Append a single dict as JSONL line. Used for resumable runs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_completed_ids(path: Path, id_field: str = "task_id") -> set[str]:
    """Read JSONL and return set of IDs already processed (for resume)."""
    if not path.exists():
        return set()
    completed = set()
    for row in read_jsonl(path):
        if id_field in row:
            completed.add(row[id_field])
    return completed


def extract_json(text: str) -> dict | list:
    """Extract JSON from LLM output, handling code fences and surrounding text."""
    # Strip markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```\s*$", "", text.strip())
    
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON object/array in text
    for pattern in [r"\{.*\}", r"\[.*\]"]:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue
    
    raise ValueError(f"Could not extract JSON from: {text[:500]}")


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=INITIAL_RETRY_DELAY, max=60),
    retry=retry_if_exception_type((APIError, RateLimitError, APIConnectionError)),
    reraise=True,
)
def call_claude(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> str:
    """Call Claude with retry logic. Returns the text response.

    Använder streaming — krävs av SDK när max_tokens >~21k och säkrare för
    långa svar. Lägre max_tokens funkar också via stream().
    """
    text_parts: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            text_parts.append(chunk)
    return "".join(text_parts)
