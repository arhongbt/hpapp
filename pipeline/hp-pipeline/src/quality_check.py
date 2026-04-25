"""Quality checks that determine whether the taxonomy is reliable enough to use."""
import json
import random
from pathlib import Path
from collections import Counter

from .models import Taxonomy
from .utils import read_jsonl


def write_quality_report(
    classifications_path: Path,
    taxonomy_path: Path,
    descriptions_path: Path,
    output_path: Path,
) -> None:
    """Compute quality metrics and write markdown report."""
    classifications = list(read_jsonl(classifications_path))
    descriptions = {d["task_id"]: d for d in read_jsonl(descriptions_path)}
    
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        taxonomy = Taxonomy(**json.load(f))
    
    micro_skills = taxonomy.get_micro_skills()
    skill_ids = {s.id for s in micro_skills}
    
    # Metric 1: How many classifications have valid skill IDs?
    invalid_primary = [c for c in classifications if c["primary_skill_id"] not in skill_ids]
    
    # Metric 2: Confidence distribution
    confidences = [c["classifier_confidence"] for c in classifications]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0
    low_conf = [c for c in classifications if c["classifier_confidence"] < 0.7]
    
    # Metric 3: Coverage — how many micro-skills are actually used?
    used_skills = Counter(c["primary_skill_id"] for c in classifications)
    unused_skills = [s for s in micro_skills if s.id not in used_skills]
    
    # Metric 4: Skill distribution — any skills with too few or too many tasks?
    underused = [(sid, count) for sid, count in used_skills.items() if count < 3]
    overused = [(sid, count) for sid, count in used_skills.items() if count > 50]
    
    # Metric 5: Random sample for human review
    sample_size = min(20, len(classifications))
    sample = random.sample(classifications, sample_size)
    
    # Build report
    report = []
    report.append("# Quality Report — HP Classification Pipeline\n")
    report.append(f"Total classified tasks: **{len(classifications)}**\n")
    report.append(f"Taxonomy size: {len(taxonomy.nodes)} noder ({len(micro_skills)} mikrofärdigheter)\n")
    
    report.append("\n## Verdict\n")
    issues = []
    if invalid_primary:
        issues.append(f"❌ {len(invalid_primary)} klassificeringar har ogiltiga skill-ID")
    if avg_conf < 0.7:
        issues.append(f"⚠️ Genomsnittlig konfidens är {avg_conf:.2f} (under 0.70)")
    if len(low_conf) > len(classifications) * 0.3:
        issues.append(f"⚠️ {len(low_conf)} ({100*len(low_conf)/len(classifications):.0f}%) tasks har konfidens < 0.7")
    if len(unused_skills) > len(micro_skills) * 0.3:
        issues.append(f"⚠️ {len(unused_skills)} mikrofärdigheter används inte alls")
    
    if not issues:
        report.append("✅ **Taxonomin verkar pålitlig.** Inga större röda flaggor.\n")
    else:
        report.append("⚠️ **Taxonomin har problem som behöver granskas:**\n")
        for issue in issues:
            report.append(f"- {issue}\n")
    
    report.append("\n## Detaljerad statistik\n")
    
    report.append("### Konfidens\n")
    report.append(f"- Genomsnitt: {avg_conf:.3f}\n")
    report.append(f"- Lägsta: {min(confidences):.3f}\n")
    report.append(f"- Högsta: {max(confidences):.3f}\n")
    report.append(f"- Tasks med konf < 0.7: {len(low_conf)}\n")
    
    report.append("\n### Mikrofärdigheter\n")
    report.append(f"- Totalt definierade: {len(micro_skills)}\n")
    report.append(f"- Använda i klassificering: {len(used_skills)}\n")
    report.append(f"- Aldrig använda: {len(unused_skills)}\n")
    report.append(f"- Underanvända (<3 tasks): {len(underused)}\n")
    report.append(f"- Överanvända (>50 tasks): {len(overused)}\n")
    
    if unused_skills:
        report.append("\n#### Aldrig använda mikrofärdigheter:\n")
        for s in unused_skills[:20]:
            report.append(f"- `{s.id}`: {s.name}\n")
    
    if overused:
        report.append("\n#### Överanvända mikrofärdigheter (kanske för bred kategori):\n")
        for sid, count in sorted(overused, key=lambda x: -x[1])[:10]:
            report.append(f"- `{sid}`: {count} tasks\n")
    
    report.append("\n### Topp 10 mest använda mikrofärdigheter\n")
    for sid, count in used_skills.most_common(10):
        skill = next((s for s in micro_skills if s.id == sid), None)
        name = skill.name if skill else "(okänd)"
        report.append(f"- `{sid}` ({name}): {count} tasks\n")
    
    report.append("\n## Slumpmässigt urval för manuell granskning\n")
    report.append(f"_Granska följande {sample_size} klassificeringar manuellt. Om majoriteten ser pedagogiskt rimliga ut, är taxonomin OK att gå vidare med._\n")
    
    for c in sample:
        skill = next((s for s in micro_skills if s.id == c["primary_skill_id"]), None)
        skill_name = skill.name if skill else "(ogiltigt id)"
        desc = descriptions.get(c["task_id"], {}).get("description", "(beskrivning saknas)")
        report.append(f"\n### {c['task_id']}\n")
        report.append(f"- **Tilldelad färdighet:** `{c['primary_skill_id']}` ({skill_name})\n")
        report.append(f"- **Konfidens:** {c['classifier_confidence']:.2f}\n")
        report.append(f"- **Svårighet:** {c['estimated_difficulty']}/5\n")
        report.append(f"- **Beskrivning:** {desc}\n")
        if c.get("classifier_notes"):
            report.append(f"- **Notes:** {c['classifier_notes']}\n")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(report)
    
    print(f"\nQuality report written to {output_path}")
    print(f"Average confidence: {avg_conf:.3f}")
    print(f"Issues flagged: {len(issues)}")
