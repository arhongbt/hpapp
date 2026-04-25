"""Resumable step-3 runner: build taxonomy ONE delprov per invocation.

Step 3 (the unified version) takes >45s because it inputs 138 clusters and
outputs a full hierarchical taxonomy in one go. This splits it per-delprov:
each delprov becomes a self-contained subtree (level 1 = delprov,
level 2 = areas, level 3 = micro-skills). Cross-delprov prerequisites are
not built — they can be added in a later step or by hand if needed.

Run repeatedly until "ALL DELPROV DONE", then we merge into step3_taxonomy.json.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE_DIR))

from src.config import MAX_TOKENS_TAXONOMY
from src.utils import call_claude, extract_json
from prompts.step3_taxonomy import SYSTEM_PROMPT_STEP3, USER_PROMPT_STEP3

OUTPUT_DIR = PIPELINE_DIR / "output" / "full"
CLUSTERS = OUTPUT_DIR / "step2_clusters.json"
PARTIAL = OUTPUT_DIR / "step3_partial.json"
FINAL = OUTPUT_DIR / "step3_taxonomy.json"


def build_for_delprov(delprov: str, clusters: list[dict]) -> dict:
    """Build a sub-taxonomy for one delprov."""
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
    return extract_json(response)


def main():
    from concurrent.futures import ThreadPoolExecutor, as_completed

    with open(CLUSTERS, "r", encoding="utf-8") as f:
        all_clusters = json.load(f)

    by_delprov = defaultdict(list)
    for c in all_clusters:
        by_delprov[c["delprov"]].append(c)
    delprov_list = sorted(by_delprov.keys())

    partial = {}
    if PARTIAL.exists():
        partial = json.loads(PARTIAL.read_text(encoding="utf-8"))

    todo = [dp for dp in delprov_list if dp not in partial]
    print(f"Delprov: {delprov_list}")
    print(f"Already done: {sorted(partial.keys())}")
    print(f"Todo this run: {todo}")

    if not todo:
        # Merge into final step3_taxonomy.json
        all_nodes = []
        for dp in delprov_list:
            all_nodes.extend(partial[dp]["nodes"])
        FINAL.write_text(
            json.dumps({"nodes": all_nodes}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nALL DELPROV DONE. {len(all_nodes)} taxonomy nodes written to {FINAL}")
        return

    # Process up to 4 concurrently per invocation
    CONCURRENCY = 4
    chunk = todo[:CONCURRENCY]
    print(f"\nRunning {len(chunk)} delprov with concurrency={CONCURRENCY}...")

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {ex.submit(build_for_delprov, dp, by_delprov[dp]): dp for dp in chunk}
        for fut in as_completed(futures):
            dp = futures[fut]
            try:
                tax = fut.result()
                partial[dp] = tax
                PARTIAL.write_text(
                    json.dumps(partial, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                n_nodes = len(tax.get("nodes", []))
                print(f"  ✓ {dp}: {n_nodes} nodes")
            except Exception as e:
                print(f"  ✗ {dp} failed: {e}")

    remaining = [dp for dp in delprov_list if dp not in partial]
    print(f"\n  Done this run: {len(chunk)}. Remaining: {remaining}")

    if not remaining:
        all_nodes = []
        for dp in delprov_list:
            all_nodes.extend(partial[dp]["nodes"])
        FINAL.write_text(
            json.dumps({"nodes": all_nodes}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nALL DELPROV DONE. {len(all_nodes)} taxonomy nodes written to {FINAL}")


if __name__ == "__main__":
    main()
