"""Resumable, parallel step-4 classifier.

Classifies up to N tasks per invocation with concurrency=K. Already-completed
tasks (in step4_classified.jsonl) are skipped. Append-after-each so partial
progress survives interrupt.
"""
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PIPELINE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPELINE_DIR))

from src.models import Task, Taxonomy
from src.step4_classify import classify_task
from src.utils import read_jsonl, append_jsonl, read_completed_ids

OUTPUT_DIR = PIPELINE_DIR / "output" / "full"
TASKS = PIPELINE_DIR / "data" / "uppgifter.jsonl"
TAXONOMY = OUTPUT_DIR / "step3_taxonomy.json"
CLASSIFIED = OUTPUT_DIR / "step4_classified.jsonl"


def main():
    import time

    CONCURRENCY = 20
    BATCH_SIZE = 20  # tasks per concurrent wave
    BUDGET_S = 35.0  # seconds — exit cleanly before bash timeout

    with open(TAXONOMY, "r", encoding="utf-8") as f:
        taxonomy = Taxonomy(**json.load(f))

    completed = read_completed_ids(CLASSIFIED, id_field="task_id")
    tasks = list(read_jsonl(TASKS))
    pending = [t for t in tasks if t["id"] not in completed]

    print(f"Total: {len(tasks)}, completed: {len(completed)}, pending: {len(pending)}")

    if not pending:
        print("\nALL TASKS DONE.")
        return

    started = time.monotonic()
    total_done = 0
    total_failed = 0
    run_idx = 0

    while pending:
        elapsed = time.monotonic() - started
        if elapsed > BUDGET_S:
            print(f"\n  Budget reached ({elapsed:.1f}s). Stopping.")
            break

        chunk = pending[:BATCH_SIZE]
        pending = pending[BATCH_SIZE:]
        run_idx += 1
        print(f"\n  Wave {run_idx}: {len(chunk)} tasks (elapsed {elapsed:.1f}s)")

        with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
            futures = {}
            for t_dict in chunk:
                task = Task(**t_dict)
                futures[ex.submit(classify_task, task, taxonomy)] = t_dict["id"]
            for fut in as_completed(futures):
                tid = futures[fut]
                try:
                    cls = fut.result()
                    append_jsonl(CLASSIFIED, cls.model_dump())
                    total_done += 1
                except Exception as e:
                    print(f"    ✗ {tid}: {e}")
                    total_failed += 1

    print(f"\n  Done this run: {total_done}, failed: {total_failed}")
    remaining = len(pending)
    completed_after = read_completed_ids(CLASSIFIED, id_field="task_id")
    overall_remaining = len(tasks) - len(completed_after)
    print(f"  Overall remaining: {overall_remaining}")
    if overall_remaining == 0:
        print("\nALL TASKS DONE.")


if __name__ == "__main__":
    main()
