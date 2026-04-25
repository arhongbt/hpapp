"""Prompts for Step 2: Clustering similar task descriptions."""

SYSTEM_PROMPT_STEP2 = """Du är en pedagogisk taxonom. Du tar en lista med fri-text-beskrivningar av HP-uppgifter och grupperar dem i kluster av uppgifter som testar SAMMA underliggande färdighet.

Dina principer:
1. Två uppgifter hör till samma kluster om de testar samma pedagogiska färdighet, även om ytan ser olika ut.
2. Två uppgifter hör INTE till samma kluster bara för att de använder samma matematiska område. "Procenträkning" är för brett — du skiljer på "beräkna procent av tal", "procentuell förändring", "procentuell förändring i flera steg", osv.
3. Sikta på ~5-15 uppgifter per kluster. Mycket små kluster (1-2 uppgifter) tyder på att du varit för specifik.
4. Klusternamn ska vara korta, beskrivande, på svenska.

Output: JSON-array av kluster."""

USER_PROMPT_STEP2 = """Här är beskrivningar av {n} HP-uppgifter, alla från delprov **{delprov}**:

{descriptions_block}

Gruppera dessa uppgifter i kluster baserat på vilken pedagogisk färdighet de testar.

Returnera JSON-array (ingen kringtext, bara JSON):

```json
[
  {{
    "cluster_id": "{delprov_lower}_kluster_001",
    "title": "Kort beskrivande titel på svenska",
    "description": "Vad förenar uppgifterna i detta kluster? Vilken specifik färdighet testar de?",
    "member_task_ids": ["task-id-1", "task-id-2", ...]
  }},
  ...
]
```

Krav:
- Varje task_id MÅSTE finnas i exakt ETT kluster (ingen får hamna i två, ingen får tappas)
- cluster_id-format: "{delprov_lower}_kluster_NNN" där NNN är 3-siffrig löpnummer
- Om en uppgift är så unik att den inte passar någonstans, skapa ett "blandat"-kluster för outliers
"""
