"""Step 4: Re-classify all tasks against the final taxonomy.

Resumable. Per-task call for accuracy.
"""
import json
from pathlib import Path
from tqdm import tqdm

from .config import MAX_TOKENS_CLASSIFICATION
from .models import Task, Classification, Taxonomy
from .utils import read_jsonl, append_jsonl, read_completed_ids, call_claude, extract_json
from prompts.step4_classify import SYSTEM_PROMPT_STEP4, USER_PROMPT_STEP4


def format_skills(taxonomy: Taxonomy, delprov: str) -> str:
    """Format only the micro-skills relevant for this delprov."""
    lines = []
    # Normalisera svenska tecken: taxonomy-id är ASCII (LÄS → "las", inte "läs")
    delprov_root_id = delprov.lower().replace("ä", "a").replace("å", "a").replace("ö", "o")
    
    # Find all level-3 nodes whose ancestor is this delprov
    parent_map = {n.id: n.parent_id for n in taxonomy.nodes}
    
    def is_descendant_of(node_id: str, ancestor_id: str) -> bool:
        current = node_id
        while current is not None:
            if current == ancestor_id:
                return True
            current = parent_map.get(current)
        return False
    
    for node in taxonomy.nodes:
        if node.level == 3 and is_descendant_of(node.id, delprov_root_id):
            lines.append(f"- **{node.id}**: {node.name} — {node.description}")
    
    return "\n".join(lines) if lines else "(inga mikrofärdigheter hittades för detta delprov)"


def classify_task(task: Task, taxonomy: Taxonomy) -> Classification:
    skills_block = format_skills(taxonomy, task.delprov)
    
    options = "\n".join(f"  {k}: {v}" for k, v in task.answer_options.items())
    
    user_prompt = USER_PROMPT_STEP4.format(
        task_id=task.id,
        delprov=task.delprov,
        uppgift_text=task.uppgift_text,
        answer_options=options,
        correct_answer=task.correct_answer,
        skills_block=skills_block,
    )
    
    response = call_claude(
        system_prompt=SYSTEM_PROMPT_STEP4,
        user_prompt=user_prompt,
        max_tokens=MAX_TOKENS_CLASSIFICATION,
    )
    
    parsed = extract_json(response)
    
    return Classification(
        task_id=task.id,
        primary_skill_id=parsed["primary_skill_id"],
        secondary_skill_ids=parsed.get("secondary_skill_ids", []),
        estimated_difficulty=parsed["estimated_difficulty"],
        estimated_time_seconds=parsed["estimated_time_seconds"],
        common_traps=parsed.get("common_traps", []),
        solution_strategies=parsed.get("solution_strategies", []),
        classifier_confidence=parsed.get("classifier_confidence", 0.5),
        classifier_notes=parsed.get("classifier_notes", ""),
    )


def run_step4(tasks_path: Path, taxonomy_path: Path, output_path: Path) -> None:
    """Re-classify all tasks against final taxonomy."""
    print(f"\n=== Step 4: Re-classification ===")
    print(f"Tasks:    {tasks_path}")
    print(f"Taxonomy: {taxonomy_path}")
    print(f"Output:   {output_path}")
    
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        taxonomy = Taxonomy(**json.load(f))
    
    completed_ids = read_completed_ids(output_path, id_field="task_id")
    if completed_ids:
        print(f"Resuming: {len(completed_ids)} tasks already classified.")
    
    tasks = list(read_jsonl(tasks_path))
    pending = [t for t in tasks if t["id"] not in completed_ids]
    print(f"Classifying {len(pending)} tasks...")
    
    failed = []
    low_confidence = []
    for task_dict in tqdm(pending, desc="Step 4"):
        try:
            task = Task(**task_dict)
            classification = classify_task(task, taxonomy)
            append_jsonl(output_path, classification.model_dump())
            if classification.classifier_confidence < 0.7:
                low_confidence.append(classification.task_id)
        except Exception as e:
            print(f"\n  ERROR on task {task_dict.get('id')}: {e}")
            failed.append(task_dict.get("id"))
    
    print(f"\nStep 4 complete.")
    print(f"  Failed: {len(failed)}")
    print(f"  Low confidence (<0.7): {len(low_confidence)} (these need manual review)")
