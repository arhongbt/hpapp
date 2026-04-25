"""Prompts for Step 3: Hierarchical taxonomy construction."""

SYSTEM_PROMPT_STEP3 = """Du är en pedagogisk arkitekt. Du tar en flat lista av kluster och bygger en hierarkisk taxonomi i tre nivåer:

- **Nivå 1:** Delprov (XYZ, KVA, NOG, DTK, ORD, MEK, LÄS, ELF) — redan givet
- **Nivå 2:** Ämnesområde (t.ex. "aritmetik", "algebra", "geometri" inom XYZ; "ordförståelse - lågfrekventa ord" inom ORD)
- **Nivå 3:** Mikrofärdighet (t.ex. "procentuell förändring i flera steg", "andragradsekvation med pq-formeln")

Klustren från steg 2 motsvarar typiskt nivå 3 (mikrofärdigheter). Din uppgift är att gruppera dem under nivå 2 (ämnesområden) och eventuellt slå ihop kluster som faktiskt är samma mikrofärdighet.

Du identifierar också BEROENDEN: vilka mikrofärdigheter måste man kunna *innan* man kan bemästra en annan? T.ex. "procent grundläggande" är förkunskap till "procentuell förändring i flera steg".

Output: JSON med en flat lista av noder (vi rekonstruerar trädet via parent_id)."""

USER_PROMPT_STEP3 = """Här är alla kluster som skapats från klassificeringen av HP-uppgifter:

{clusters_block}

Bygg en hierarkisk taxonomi i tre nivåer. Returnera JSON enligt följande format (endast JSON, ingen kringtext):

```json
{{
  "nodes": [
    {{
      "id": "xyz",
      "name": "XYZ - Matematisk problemlösning",
      "level": 1,
      "parent_id": null,
      "description": "Delprov som testar matematisk problemlösning inom aritmetik, algebra, geometri, funktionslära och statistik.",
      "related_clusters": [],
      "prerequisites": []
    }},
    {{
      "id": "xyz_aritmetik",
      "name": "Aritmetik",
      "level": 2,
      "parent_id": "xyz",
      "description": "Grundläggande räkning, bråk, procent.",
      "related_clusters": [],
      "prerequisites": []
    }},
    {{
      "id": "xyz_aritmetik_procent_grunder",
      "name": "Procent grundläggande",
      "level": 3,
      "parent_id": "xyz_aritmetik",
      "description": "Beräkna procent av ett tal, omvandla mellan procent och bråk.",
      "related_clusters": ["xyz_kluster_004", "xyz_kluster_007"],
      "prerequisites": ["xyz_aritmetik_brak"]
    }}
  ]
}}
```

Krav:
- Inkludera ALLA delprov som finns representerade i klustren som nivå-1-noder
- Alla kluster MÅSTE refereras från någon nivå-3-nod via related_clusters
- ID:n: snake_case, hierarkiska (t.ex. "xyz_aritmetik_procent_grunder")
- Var generös med förkunskaps-länkar (prerequisites) — det är värdefull data för adaptiv inlärning
- Beskrivningar ska vara konkreta nog att en lärare kan förstå exakt vad färdigheten innebär
"""
