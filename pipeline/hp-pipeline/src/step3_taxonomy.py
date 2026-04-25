"""Step 3: Hierarchical taxonomy construction from clusters."""
import json
from pathlib import Path

from .config import MAX_TOKENS_TAXONOMY
from .models import Taxonomy, TaxonomyNode
from .utils import call_claude, extract_json
from prompts.step3_taxonomy import SYSTEM_PROMPT_STEP3, USER_PROMPT_STEP3


def build_taxonomy(clusters: list[dict]) -> Taxonomy:
    """Build hierarchical taxonomy from flat list of clusters."""
    blocks = []
    for c in clusters:
        blocks.append(
            f"- {c['cluster_id']} ({c['delprov']})\n"
            f"  Titel: {c['title']}\n"
            f"  Beskrivning: {c['description']}\n"
            f"  Antal uppgifter: {len(c['member_task_ids'])}"
        )
    clusters_block = "\n\n".join(blocks)
    
    user_prompt = USER_PROMPT_STEP3.format(clusters_block=clusters_block)
    
    response = call_claude(
        system_prompt=SYSTEM_PROMPT_STEP3,
        user_prompt=user_prompt,
        max_tokens=MAX_TOKENS_TAXONOMY,
    )
    
    parsed = extract_json(response)
    
    nodes = [TaxonomyNode(**n) for n in parsed["nodes"]]
    return Taxonomy(nodes=nodes)


def run_step3(clusters_path: Path, output_path: Path) -> None:
    """Build taxonomy from clusters."""
    print(f"\n=== Step 3: Building taxonomy ===")
    print(f"Input:  {clusters_path}")
    print(f"Output: {output_path}")
    
    with open(clusters_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)
    
    print(f"Building taxonomy from {len(clusters)} clusters...")
    
    taxonomy = build_taxonomy(clusters)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy.model_dump(), f, ensure_ascii=False, indent=2)
    
    by_level = {1: 0, 2: 0, 3: 0}
    for n in taxonomy.nodes:
        by_level[n.level] = by_level.get(n.level, 0) + 1
    
    print(f"Step 3 complete.")
    print(f"  Level 1 (delprov):       {by_level.get(1, 0)}")
    print(f"  Level 2 (ämnesområden):  {by_level.get(2, 0)}")
    print(f"  Level 3 (mikrofärdighet): {by_level.get(3, 0)}")
