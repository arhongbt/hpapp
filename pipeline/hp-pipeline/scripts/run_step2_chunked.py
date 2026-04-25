"""Resumable step-2 runner: processes ONE BATCH per invocation.

Used when wall-clock-time per call is constrained. Each invocation:
1. Reads `output/full/step2_partial.json` for already-done batches
2. Picks the next undone (delprov, batch_idx) and clusters it
3. Writes the per-batch result to `step2_partial.json`
4. When all batches done, also writes the unified `step2_clusters.json`
   (matching the format the rest of the pipeline expects).

Run repeatedly until you see "ALL BATCHES DONE".
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE_DIR))

from src.config import CLUSTERING_BATCH_SIZE
from src.step2_cluster import cluster_descriptions
from src.utils import read_jsonl

OUTPUT_DIR = PIPELINE_DIR / "output" / "full"
DESCRIPTIONS = OUTPUT_DIR / "step1_descriptions.jsonl"
PARTIAL = OUTPUT_DIR / "step2_partial.json"
FINAL = OUTPUT_DIR / "step2_clusters.json"


def load_partial() -> dict:
    """Returns {batch_key: [cluster_dicts]} where batch_key = 'XYZ#0', 'XYZ#1', etc."""
    if PARTIAL.exists():
        return json.loads(PARTIAL.read_text(encoding="utf-8"))
    return {}


def save_partial(data: dict) -> None:
    PARTIAL.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def all_batches(by_delprov: dict) -> list[tuple[str, int, list[dict], bool]]:
    """Returns list of (delprov, batch_idx, batch_descs, is_batched)."""
    out = []
    for delprov in sorted(by_delprov.keys()):
        descs = by_delprov[delprov]
        if len(descs) > CLUSTERING_BATCH_SIZE * 2:
            for i in range(0, len(descs), CLUSTERING_BATCH_SIZE):
                out.append((delprov, i // CLUSTERING_BATCH_SIZE, descs[i:i + CLUSTERING_BATCH_SIZE], True))
        else:
            out.append((delprov, 0, descs, False))
    return out


def cluster_one_batch(delprov: str, batch_idx: int, batch_descs: list[dict], is_batched: bool) -> list[dict]:
    """Run clustering for one batch, returning list of cluster dicts."""
    clusters = cluster_descriptions(batch_descs, delprov)
    if is_batched:
        for j, c in enumerate(clusters):
            c.cluster_id = f"{delprov.lower()}_kluster_b{batch_idx:02d}_{j:03d}"
    return [c.model_dump() for c in clusters]


def main():
    """Process up to N batches concurrently per invocation."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    CONCURRENCY = 4   # parallel API calls — each batch is independent
    MAX_BATCHES_PER_RUN = 8  # safety cap per invocation

    by_delprov = defaultdict(list)
    for d in read_jsonl(DESCRIPTIONS):
        by_delprov[d["delprov"]].append(d)

    batches = all_batches(by_delprov)
    partial = load_partial()
    keys = [f"{dp}#{idx}" for (dp, idx, _, _) in batches]

    print(f"Total batches: {len(batches)}, done: {len(partial)}/{len(batches)}")

    todo = [(i, batches[i]) for i, k in enumerate(keys) if k not in partial][:MAX_BATCHES_PER_RUN]
    if not todo:
        flat = []
        for k in keys:
            flat.extend(partial[k])
        FINAL.write_text(
            json.dumps(flat, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nALL BATCHES DONE. {len(flat)} clusters written to {FINAL}")
        return

    print(f"Running {len(todo)} batches with concurrency={CONCURRENCY}...")
    results = {}
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {}
        for i, b in todo:
            delprov, batch_idx, batch_descs, is_batched = b
            key = f"{delprov}#{batch_idx}"
            futures[ex.submit(cluster_one_batch, delprov, batch_idx, batch_descs, is_batched)] = key
        for fut in as_completed(futures):
            key = futures[fut]
            try:
                clusters = fut.result()
                results[key] = clusters
                # Save after each finish so partial progress survives interrupt
                partial[key] = clusters
                save_partial(partial)
                print(f"  ✓ {key}: {len(clusters)} clusters")
            except Exception as e:
                print(f"  ✗ {key} failed: {e}")

    remaining = [k for k in keys if k not in partial]
    print(f"\n  Done this run: {len(results)}. Remaining: {len(remaining)}")

    if not remaining:
        flat = []
        for k in keys:
            flat.extend(partial[k])
        FINAL.write_text(
            json.dumps(flat, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nALL BATCHES DONE. {len(flat)} clusters written to {FINAL}")


if __name__ == "__main__":
    main()
