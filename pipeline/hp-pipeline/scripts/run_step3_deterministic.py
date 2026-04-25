"""Build step 3 taxonomy deterministically (no LLM call).

Rationale: under chunked-execution constraints, the LLM-based hierarchical
merge in step3_taxonomy.py exceeds our per-call time budget. We build a
flat 2-level taxonomy directly from clusters:

- Level 1 = delprov (one node per delprov)
- Level 3 = clusters as micro-skills (each cluster_id becomes a node)

(Level 2 is skipped — step 4's `format_skills()` only uses ancestry to find
level-3 nodes under a delprov root, so a flat L1→L3 structure works.)

This loses LLM-based cluster-merging and prerequisite inference, but
preserves the 138 cluster granularity for classification. A proper
hierarchical pass can be added later as a separate enrichment step.
"""
import json
from collections import defaultdict
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PIPELINE_DIR / "output" / "full"
CLUSTERS = OUTPUT_DIR / "step2_clusters.json"
FINAL = OUTPUT_DIR / "step3_taxonomy.json"


def normalize_delprov_id(delprov: str) -> str:
    """Step 4 uses ASCII-normalized delprov as taxonomy root id (LÄS → 'las')."""
    return delprov.lower().replace("ä", "a").replace("å", "a").replace("ö", "o")


DELPROV_NAMES = {
    "XYZ": "Matematisk problemlösning (XYZ)",
    "KVA": "Kvantitativa jämförelser (KVA)",
    "NOG": "Kvantitativa resonemang (NOG)",  # Hong's session-2 fact: NOG = Kvantitativa resonemang
    "DTK": "Diagram, tabeller och kartor (DTK)",
    "ORD": "Ordförståelse (ORD)",
    "LÄS": "Svensk läsförståelse (LÄS)",
    "MEK": "Meningskomplettering (MEK)",
    "ELF": "Engelsk läsförståelse (ELF)",
}

DELPROV_DESCRIPTIONS = {
    "XYZ": "Matematisk problemlösning inom aritmetik, algebra, geometri, funktionslära och statistik.",
    "KVA": "Jämförelse av två kvantitativa storheter givet villkor — testar talförståelse och algebraisk variationsanalys.",
    "NOG": "Bedömning av om given information är tillräcklig för att besvara en kvantitativ fråga — kräver matematisk resonemang om informationsvärdering.",
    "DTK": "Avläsning och tolkning av diagram, tabeller, kartor och annan visuell kvantitativ information.",
    "ORD": "Förståelse av enskilda ords betydelse, inklusive lågfrekventa ord och idiomatiska uttryck.",
    "LÄS": "Förståelse av längre sammanhängande svenska texter — huvudtes, detaljer, retorisk funktion, implikationer.",
    "MEK": "Meningskomplettering — fyll i ord/uttryck som passar i kontext, fackterminologi och nyansering.",
    "ELF": "Engelsk läsförståelse.",
}


def main():
    with open(CLUSTERS, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    # Group clusters by delprov
    by_delprov = defaultdict(list)
    for c in clusters:
        by_delprov[c["delprov"]].append(c)

    nodes = []

    # Level 1: delprov roots
    for delprov in sorted(by_delprov.keys()):
        root_id = normalize_delprov_id(delprov)
        nodes.append({
            "id": root_id,
            "name": DELPROV_NAMES.get(delprov, delprov),
            "level": 1,
            "parent_id": None,
            "description": DELPROV_DESCRIPTIONS.get(delprov, f"Delprov {delprov}."),
            "related_clusters": [],
            "prerequisites": [],
        })

    # Level 3: clusters as micro-skills
    for delprov in sorted(by_delprov.keys()):
        root_id = normalize_delprov_id(delprov)
        for c in by_delprov[delprov]:
            nodes.append({
                "id": c["cluster_id"],
                "name": c["title"],
                "level": 3,
                "parent_id": root_id,
                "description": c["description"],
                "related_clusters": [c["cluster_id"]],
                "prerequisites": [],
            })

    FINAL.write_text(
        json.dumps({"nodes": nodes}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    n_l1 = sum(1 for n in nodes if n["level"] == 1)
    n_l3 = sum(1 for n in nodes if n["level"] == 3)
    print(f"Wrote {FINAL}")
    print(f"  Level 1 (delprov):       {n_l1}")
    print(f"  Level 2 (ämnesområden):  0  (skipped — see script docstring)")
    print(f"  Level 3 (mikrofärdighet): {n_l3}")
    print(f"  Total nodes:             {len(nodes)}")


if __name__ == "__main__":
    main()
