"""Debug-script: kör step 2 på första LÄS-batchen och logga allt."""
import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PIPELINE_DIR = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(PIPELINE_DIR))
from prompts.step2_cluster import SYSTEM_PROMPT_STEP2, USER_PROMPT_STEP2

# Läs första 15 LÄS-descriptions
descs = []
with open(PIPELINE_DIR / "output/full/step1_descriptions.jsonl") as f:
    for line in f:
        d = json.loads(line)
        if d["delprov"] == "LÄS":
            descs.append(d)
        if len(descs) == 15:
            break

blocks = []
for d in descs:
    blocks.append(
        f"- ID: {d['task_id']}\n"
        f"  Beskrivning: {d['description']}\n"
        f"  Initial gissning: {d.get('primary_skill_guess', 'okänd')}"
    )
descriptions_block = "\n\n".join(blocks)

user_prompt = USER_PROMPT_STEP2.format(
    n=len(descs),
    delprov="LÄS",
    delprov_lower="las",
    descriptions_block=descriptions_block,
)

print(f"Input prompt length: {len(user_prompt)} chars")
print(f"Calling Sonnet 4.6 (no streaming) with max_tokens=8192...")

# Försök 1: NON-streaming
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8192,
    temperature=0.0,
    system=SYSTEM_PROMPT_STEP2,
    messages=[{"role": "user", "content": user_prompt}],
)

print(f"\nstop_reason: {response.stop_reason}")
print(f"usage: input={response.usage.input_tokens}, output={response.usage.output_tokens}")

text = "\n".join(b.text for b in response.content if hasattr(b, "text"))
print(f"\nResponse length: {len(text)} chars")
print(f"First 200 chars: {text[:200]}")
print(f"Last 200 chars: {text[-200:]}")

# Försök parsea
try:
    parsed = json.loads(text.strip().lstrip("```json").rstrip("```").strip())
    print(f"\n✅ JSON parses, {len(parsed)} clusters")
except Exception as e:
    print(f"\n❌ JSON parse error: {e}")
    print(f"Text ends with: {text[-100:]!r}")
