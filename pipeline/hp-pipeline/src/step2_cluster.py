"""Step 2: Clustering — group similar descriptions per delprov.

Clusters within each delprov separately (XYZ tasks don't cluster with ORD tasks).
"""
import json
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

from .config import MAX_TOKENS_CLUSTER, CLUSTERING_BATCH_SIZE
from .models import Cluster
from .utils import read_jsonl, call_claude, extract_json
from prompts.step2_cluster import SYSTEM_PROMPT_STEP2, USER_PROMPT_STEP2


def cluster_descriptions(descriptions: list[dict], delprov: str) -> list[Cluster]:
    """Cluster all descriptions for a single delprov."""
    if not descriptions:
        return []
    
    # Build descriptions block
    blocks = []
    for d in descriptions:
        blocks.append(
            f"- ID: {d['task_id']}\n"
            f"  Beskrivning: {d['description']}\n"
            f"  Initial gissning: {d.get('primary_skill_guess', 'okänd')}"
        )
    descriptions_block = "\n\n".join(blocks)
    
    user_prompt = USER_PROMPT_STEP2.format(
        n=len(descriptions),
        delprov=delprov,
        delprov_lower=delprov.lower(),
        descriptions_block=descriptions_block,
    )
    
    response = call_claude(
        system_prompt=SYSTEM_PROMPT_STEP2,
        user_prompt=user_prompt,
        max_tokens=MAX_TOKENS_CLUSTER,
    )
    
    parsed = extract_json(response)
    
    clusters = []
    for c in parsed:
        clusters.append(Cluster(
            cluster_id=c["cluster_id"],
            title=c["title"],
            description=c["description"],
            delprov=delprov,
            member_task_ids=c["member_task_ids"],
        ))
    
    return clusters


def run_step2(descriptions_path: Path, output_path: Path) -> None:
    """Cluster descriptions per delprov, save unified cluster list."""
    print(f"\n=== Step 2: Clustering descriptions ===")
    print(f"Input:  {descriptions_path}")
    print(f"Output: {output_path}")
    
    # Group by delprov
    by_delprov = defaultdict(list)
    for d in read_jsonl(descriptions_path):
        by_delprov[d["delprov"]].append(d)
    
    print(f"Found delprov: {sorted(by_delprov.keys())}")
    
    all_clusters = []
    for delprov, descriptions in tqdm(by_delprov.items(), desc="Clustering delprov"):
        print(f"\n  {delprov}: {len(descriptions)} descriptions")
        
        # If too many descriptions, batch within delprov
        if len(descriptions) > CLUSTERING_BATCH_SIZE * 2:
            print(f"    Splitting into batches of {CLUSTERING_BATCH_SIZE}")
            batched_clusters = []
            for i in range(0, len(descriptions), CLUSTERING_BATCH_SIZE):
                batch = descriptions[i:i + CLUSTERING_BATCH_SIZE]
                clusters = cluster_descriptions(batch, delprov)
                # Renumber cluster IDs to avoid collisions across batches
                for j, c in enumerate(clusters):
                    c.cluster_id = f"{delprov.lower()}_kluster_b{i//CLUSTERING_BATCH_SIZE:02d}_{j:03d}"
                batched_clusters.extend(clusters)
            all_clusters.extend(batched_clusters)
        else:
            clusters = cluster_descriptions(descriptions, delprov)
            all_clusters.extend(clusters)
    
    # Write unified cluster file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            [c.model_dump() for c in all_clusters],
            f,
            ensure_ascii=False,
            indent=2,
        )
    
    print(f"\nStep 2 complete. {len(all_clusters)} clusters created.")
