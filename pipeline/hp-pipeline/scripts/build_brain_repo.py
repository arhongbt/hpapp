"""Build a gbrain-compatible markdown brain repo from pipeline outputs.

Generates ~/Desktop/hp-app/brain/ with:
  concepts/<delprov>.md          — 7 delprov pages (XYZ, KVA, NOG, DTK, ORD, LÄS, MEK)
  concepts/<cluster_id>.md       — 138 microskill pages
  entities/<task_id>.md          — 280 task pages

Each page uses gbrain's compiled-truth + timeline format. Cross-references use
markdown link form `[Title](concepts/slug)` so gbrain's auto-link extraction
(regex-based, zero LLM) captures the typed graph automatically on `gbrain import`.

Directories chosen to match gbrain's DIR_PATTERN:
  - concepts/  — delprov + microskills (taxonomy nodes)
  - entities/  — tasks (specific instances)

Run: python3 scripts/build_brain_repo.py
"""
import json
import re
from collections import defaultdict
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent.parent
BRAIN_DIR = PIPELINE_DIR.parent.parent / "brain"
OUTPUT_DIR = PIPELINE_DIR / "output" / "full"

DELPROV_NAMES = {
    "XYZ": "Matematisk problemlösning (XYZ)",
    "KVA": "Kvantitativa jämförelser (KVA)",
    "NOG": "Kvantitativa resonemang (NOG)",
    "DTK": "Diagram, tabeller och kartor (DTK)",
    "ORD": "Ordförståelse (ORD)",
    "LÄS": "Svensk läsförståelse (LÄS)",
    "MEK": "Meningskomplettering (MEK)",
}

DELPROV_DESCRIPTIONS = {
    "XYZ": "Testar matematisk problemlösning inom aritmetik, algebra, geometri, funktionslära och statistik. Varje uppgift har fyra svarsalternativ.",
    "KVA": "Testar förmågan att jämföra två kvantitativa storheter givet villkor. Fem svarsalternativ inklusive 'ej tillräcklig information'. Kräver talförståelse och algebraisk variationsanalys.",
    "NOG": "Testar förmågan att avgöra om given information är tillräcklig för att besvara en kvantitativ fråga. Kräver matematisk resonemang om informationsvärdering snarare än räkning.",
    "DTK": "Testar avläsning och tolkning av diagram, tabeller, kartor och annan visuell kvantitativ information. Kombinerar visuell analys med beräkning och jämförelse.",
    "ORD": "Testar förståelse av enskilda ords betydelse, inklusive lågfrekventa ord, fackord och idiomatiska uttryck. Synonym/parafrasidentifiering med fem alternativ.",
    "LÄS": "Testar förståelse av längre sammanhängande svenska texter — huvudtes, detaljer, retorisk funktion, implicit ståndpunkt och orsakssamband.",
    "MEK": "Testar meningskomplettering — fyll i ord/uttryck som passar i kontext. Kräver fackterminologi, semantisk koherens och stilistisk nyansering.",
}

# Filename-safe slug (gbrain expects lowercase, no special chars)
def slugify(s: str) -> str:
    s = s.lower()
    s = s.replace("ä", "a").replace("å", "a").replace("ö", "o")
    s = re.sub(r"[^a-z0-9_-]", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def normalize_id(s: str) -> str:
    """Normalize cluster IDs to ASCII (gbrain slugifies on import; we must match)."""
    return s.replace("ä", "a").replace("å", "a").replace("ö", "o").lower()


def load_taxonomy():
    with open(OUTPUT_DIR / "step3_taxonomy.json") as f:
        tax = json.load(f)
    # Normalize all node IDs + parent_ids to ASCII
    for node in tax["nodes"]:
        node["id"] = normalize_id(node["id"])
        if node.get("parent_id"):
            node["parent_id"] = normalize_id(node["parent_id"])
    return tax


def load_tasks():
    """Returns {task_id: task_dict}."""
    tasks = {}
    with open(PIPELINE_DIR / "data" / "uppgifter.jsonl") as f:
        for line in f:
            t = json.loads(line)
            tasks[t["id"]] = t
    return tasks


def load_classifications():
    """Returns {task_id: classification_dict}. Normalizes skill IDs to ASCII."""
    cls = {}
    with open(OUTPUT_DIR / "step4_classified.jsonl") as f:
        for line in f:
            c = json.loads(line)
            c["primary_skill_id"] = normalize_id(c["primary_skill_id"])
            c["secondary_skill_ids"] = [normalize_id(s) for s in c.get("secondary_skill_ids", [])]
            cls[c["task_id"]] = c
    return cls


def write_delprov_pages(taxonomy, tasks_by_microskill_count):
    """Write 7 delprov pages."""
    out_dir = BRAIN_DIR / "concepts"
    out_dir.mkdir(parents=True, exist_ok=True)

    delprov_nodes = [n for n in taxonomy["nodes"] if n["level"] == 1]
    for node in delprov_nodes:
        delprov = next(k for k in DELPROV_NAMES if slugify(k) == node["id"])
        title = DELPROV_NAMES[delprov]
        desc = DELPROV_DESCRIPTIONS[delprov]
        slug = node["id"]

        # Find microskills under this delprov
        microskills = [n for n in taxonomy["nodes"] if n["level"] == 3 and n["parent_id"] == slug]
        n_tasks = sum(tasks_by_microskill_count.get(m["id"], 0) for m in microskills)

        # Microskill list as markdown links
        ms_lines = []
        for ms in sorted(microskills, key=lambda m: -tasks_by_microskill_count.get(m["id"], 0)):
            n = tasks_by_microskill_count.get(ms["id"], 0)
            ms_lines.append(f"- [{ms['name']}](concepts/{ms['id']}) — {n} uppgifter")

        body = f"""---
type: concept
title: "{title.replace('"', "'")}"
tags: [hp, delprov, kvantitativ]
delprov: {delprov}
---

{desc}

## Mikrofärdigheter ({len(microskills)} totalt, {n_tasks} klassificerade uppgifter)

{chr(10).join(ms_lines)}

---

- 2026-04-25: Pipeline-klassificering — {len(microskills)} mikrofärdigheter identifierade från {n_tasks} uppgifter över HP 2025-10-19 och 2026-04-18.
"""
        (out_dir / f"{slug}.md").write_text(body, encoding="utf-8")
    print(f"  Wrote {len(delprov_nodes)} delprov pages to concepts/")


def write_microskill_pages(taxonomy, classifications, tasks):
    """Write 138 microskill pages."""
    out_dir = BRAIN_DIR / "concepts"
    out_dir.mkdir(parents=True, exist_ok=True)

    microskill_nodes = [n for n in taxonomy["nodes"] if n["level"] == 3]

    # Group tasks by primary skill
    tasks_by_skill = defaultdict(list)
    for c in classifications.values():
        tasks_by_skill[c["primary_skill_id"]].append(c["task_id"])

    for ms in microskill_nodes:
        slug = ms["id"]
        title = ms["name"]
        desc = ms["description"]
        parent_id = ms["parent_id"]
        parent_title = next((n["name"] for n in taxonomy["nodes"] if n["id"] == parent_id), parent_id)

        # Tasks classified to this microskill
        task_ids = tasks_by_skill.get(slug, [])
        task_lines = []
        for tid in sorted(task_ids):
            task_year = tasks.get(tid, {}).get("year", "?")
            task_lines.append(f"- [{tid}](entities/{tid}) ({task_year})")

        # Common traps + strategies aggregated across tasks (sample first 3)
        sample_traps = []
        sample_strats = []
        for tid in task_ids[:3]:
            c = classifications.get(tid, {})
            sample_traps.extend(c.get("common_traps", [])[:1])
            sample_strats.extend(c.get("solution_strategies", [])[:1])

        traps_block = "\n".join(f"- {t}" for t in sample_traps[:3]) if sample_traps else "_(inga ännu)_"
        strats_block = "\n".join(f"- {s}" for s in sample_strats[:3]) if sample_strats else "_(inga ännu)_"

        body = f"""---
type: concept
title: "{title.replace('"', "'")}"
tags: [hp, microskill, {parent_id}]
delprov_root: {parent_id}
parent: {parent_id}
---

Mikrofärdighet inom delprov [{parent_title}](concepts/{parent_id}).

{desc}

## Vanliga fällor (urval från klassificerade uppgifter)

{traps_block}

## Lösningsstrategier (urval)

{strats_block}

## Klassificerade uppgifter ({len(task_ids)})

{chr(10).join(task_lines) if task_lines else "_(inga ännu)_"}

---

- 2026-04-25: Identifierad i step 2-klustring av {len(task_ids)} HP-uppgifter, etablerad som mikrofärdighet i step 3-taxonomi.
"""
        (out_dir / f"{slug}.md").write_text(body, encoding="utf-8")
    print(f"  Wrote {len(microskill_nodes)} microskill pages to concepts/")


def write_task_pages(tasks, classifications, taxonomy):
    """Write 280 task pages."""
    out_dir = BRAIN_DIR / "entities"
    out_dir.mkdir(parents=True, exist_ok=True)

    skill_titles = {n["id"]: n["name"] for n in taxonomy["nodes"]}

    for tid, task in tasks.items():
        c = classifications.get(tid)
        if not c:
            continue

        primary_id = c["primary_skill_id"]
        primary_title = skill_titles.get(primary_id, primary_id)

        secondary_links = []
        for sid in c.get("secondary_skill_ids", []):
            title = skill_titles.get(sid, sid)
            secondary_links.append(f"- [{title}](concepts/{sid})")

        # Format options
        opts = task.get("answer_options", {})
        opts_lines = "\n".join(f"- **{k}:** {v}" for k, v in sorted(opts.items()))

        # Common traps
        traps_lines = "\n".join(f"- {t}" for t in c.get("common_traps", []))
        strats_lines = "\n".join(f"- {s}" for s in c.get("solution_strategies", []))

        # Year/term metadata
        year = task.get("year", "?")
        term = task.get("term", "?")
        pass_n = task.get("pass_number", "?")
        task_n = task.get("task_number", "?")
        delprov = task.get("delprov", "?")
        delprov_root = slugify(delprov)
        date_iso = "2026-04-18" if (year == 2026 and term == "vt") else "2025-10-19"

        body = f"""---
type: entity
title: HP {tid}
tags: [hp, task, {delprov_root}]
year: {year}
term: {term}
pass_number: {pass_n}
task_number: {task_n}
delprov: {delprov}
correct_answer: {task.get("correct_answer", "?")}
difficulty: {c.get("estimated_difficulty", "?")}
estimated_time_seconds: {c.get("estimated_time_seconds", "?")}
classifier_confidence: {c.get("classifier_confidence", "?")}
---

Uppgift från Högskoleprovet {date_iso}, provpass {pass_n} ({delprov}), uppgift {task_n}.

## Frågan

{task.get("uppgift_text", "_(saknas)_")}

## Svarsalternativ

{opts_lines}

**Rätt svar:** {task.get("correct_answer", "?")}

## Testar primärt

[{primary_title}](concepts/{primary_id})

{f"## Testar också{chr(10)}{chr(10)}{chr(10).join(secondary_links)}" if secondary_links else ""}

## Vanliga fällor

{traps_lines or "_(inga dokumenterade)_"}

## Lösningsstrategier

{strats_lines or "_(inga dokumenterade)_"}

## Klassificerare-noter

{c.get("classifier_notes", "_(inga)_")}

---

- {date_iso}: Provuppgift på Högskoleprovet
- 2026-04-25: Klassificerad mot [{primary_title}](concepts/{primary_id}) med konfidens {c.get("classifier_confidence", "?")}
"""
        (out_dir / f"{tid}.md").write_text(body, encoding="utf-8")
    print(f"  Wrote {len(tasks)} task pages to entities/")


def write_index_page():
    """Write a top-level README/index for the brain."""
    body = """---
type: concept
title: HP-app Brain
tags: [hp, index]
---

# HP-app Brain

Detta brain innehåller kunskapsmodellen för Högskoleprovet:

- **7 delprov** (`concepts/xyz.md`, `kva.md`, `nog.md`, `dtk.md`, `ord.md`, `las.md`, `mek.md`)
- **138 mikrofärdigheter** (`concepts/<delprov>_kluster_*.md`) — empiriskt identifierade från klassificering av 280 uppgifter
- **280 uppgifter** (`entities/<task_id>.md`) — varje uppgift med klassificering, vanliga fällor och lösningsstrategier

## Snabblänkar

### Delprov

- [Matematisk problemlösning (XYZ)](concepts/xyz)
- [Kvantitativa jämförelser (KVA)](concepts/kva)
- [Kvantitativa resonemang (NOG)](concepts/nog)
- [Diagram, tabeller och kartor (DTK)](concepts/dtk)
- [Ordförståelse (ORD)](concepts/ord)
- [Svensk läsförståelse (LÄS)](concepts/las)
- [Meningskomplettering (MEK)](concepts/mek)

## Datakällor

- HP 2025-10-19 (140 uppgifter)
- HP 2026-04-18 (140 uppgifter)
- ELF (engelsk läsförståelse) ej inkluderat

## Pipeline

Genererat från `pipeline/hp-pipeline/output/full/{step3_taxonomy.json, step4_classified.jsonl}`. Klassificering verifierad mot officiella facit (100% match, 280/280).

---

- 2026-04-25: Brain-repon byggd från pipeline-klassificering
"""
    (BRAIN_DIR / "README.md").write_text(body, encoding="utf-8")


def main():
    print(f"Building brain at {BRAIN_DIR}")
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)

    taxonomy = load_taxonomy()
    tasks = load_tasks()
    classifications = load_classifications()

    print(f"Loaded: {len(taxonomy['nodes'])} taxonomy nodes, {len(tasks)} tasks, {len(classifications)} classifications")

    # Count tasks per microskill (for delprov pages)
    tasks_by_microskill_count = defaultdict(int)
    for c in classifications.values():
        tasks_by_microskill_count[c["primary_skill_id"]] += 1

    write_delprov_pages(taxonomy, tasks_by_microskill_count)
    write_microskill_pages(taxonomy, classifications, tasks)
    write_task_pages(tasks, classifications, taxonomy)
    write_index_page()

    # Stats
    n_concepts = len(list((BRAIN_DIR / "concepts").glob("*.md")))
    n_entities = len(list((BRAIN_DIR / "entities").glob("*.md")))
    print(f"\nDone. Brain at {BRAIN_DIR}:")
    print(f"  concepts/  {n_concepts} files")
    print(f"  entities/  {n_entities} files")
    print(f"  README.md  index")


if __name__ == "__main__":
    main()
