"""Step 1: Raw extraction — free-text description per task.

Resumable: skips tasks already in output file.
"""
from pathlib import Path
from tqdm import tqdm

from .config import MAX_TOKENS_DESCRIPTION
from .models import Task, TaskDescription
from .utils import read_jsonl, append_jsonl, read_completed_ids, call_claude, extract_json
from prompts.step1_describe import SYSTEM_PROMPT_STEP1, USER_PROMPT_STEP1


def format_options(options: dict[str, str]) -> str:
    return "\n".join(f"  {k}: {v}" for k, v in options.items())


def describe_task(task: Task) -> TaskDescription:
    user_prompt = USER_PROMPT_STEP1.format(
        delprov=task.delprov,
        year=task.year,
        term=task.term,
        uppgift_text=task.uppgift_text,
        answer_options=format_options(task.answer_options),
        correct_answer=task.correct_answer,
    )
    
    response = call_claude(
        system_prompt=SYSTEM_PROMPT_STEP1,
        user_prompt=user_prompt,
        max_tokens=MAX_TOKENS_DESCRIPTION,
    )
    
    parsed = extract_json(response)
    
    return TaskDescription(
        task_id=task.id,
        delprov=task.delprov,
        description=parsed["description"],
        primary_skill_guess=parsed.get("primary_skill_guess", "okänd"),
        requires_image=parsed.get("requires_image", False),
        notes=parsed.get("notes", ""),
    )


def run_step1(input_path: Path, output_path: Path, limit: int | None = None) -> None:
    """Run step 1 on all tasks in input_path. Resumable."""
    print(f"\n=== Step 1: Generating descriptions ===")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    
    completed_ids = read_completed_ids(output_path, id_field="task_id")
    if completed_ids:
        print(f"Resuming: {len(completed_ids)} tasks already processed.")
    
    tasks = list(read_jsonl(input_path))
    if limit:
        tasks = tasks[:limit]
    
    pending = [t for t in tasks if t["id"] not in completed_ids]
    print(f"Processing {len(pending)} tasks...")
    
    failed = []
    for task_dict in tqdm(pending, desc="Step 1"):
        try:
            task = Task(**task_dict)
            description = describe_task(task)
            append_jsonl(output_path, description.model_dump())
        except Exception as e:
            print(f"\n  ERROR on task {task_dict.get('id')}: {e}")
            failed.append(task_dict.get("id"))
    
    print(f"Step 1 complete. Failed: {len(failed)}")
    if failed:
        print(f"  Failed IDs: {failed[:10]}{'...' if len(failed) > 10 else ''}")
