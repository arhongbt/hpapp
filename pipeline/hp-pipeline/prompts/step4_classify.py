"""Prompts for Step 4: Re-classification against final taxonomy."""

SYSTEM_PROMPT_STEP4 = """Du är en HP-pedagog som klassificerar uppgifter mot en fastställd taxonomi av mikrofärdigheter. För varje uppgift identifierar du:

1. **Primär färdighet** — den ENDA mikrofärdigheten som är centralt i uppgiften
2. **Sekundära färdigheter** — andra mikrofärdigheter som behövs men inte är huvudfokus
3. **Svårighetsgrad** — 1 (lätt) till 5 (mycket svår), kalibrerat mot HP:s genomsnittliga svårighet
4. **Tid** — uppskattad lösningstid i sekunder för en genomsnittlig elev som tränat
5. **Vanliga fällor** — typiska felsvar och deras orsaker
6. **Lösningsstrategier** — effektiva angreppssätt
7. **Konfidens** — hur säker är du på primär färdighet (0.0-1.0)

Var ÄRLIG med konfidens. Om uppgiften är gränsfall mellan två färdigheter, sätt konfidens till 0.6-0.7 så vi vet att den behöver mänsklig granskning."""

USER_PROMPT_STEP4 = """**Uppgift:**
ID: {task_id}
Delprov: {delprov}

Text: {uppgift_text}

Svarsalternativ:
{answer_options}

Rätt svar: {correct_answer}

**Tillgängliga mikrofärdigheter (välj från denna lista):**

{skills_block}

Klassificera uppgiften. Returnera JSON (endast JSON, ingen kringtext):

```json
{{
  "primary_skill_id": "id_från_listan_ovan",
  "secondary_skill_ids": ["id_1", "id_2"],
  "estimated_difficulty": 3,
  "estimated_time_seconds": 90,
  "common_traps": [
    "Beskrivning av en typisk fälla",
    "Annan fälla"
  ],
  "solution_strategies": [
    "Mest effektiv strategi",
    "Alternativ strategi"
  ],
  "classifier_confidence": 0.85,
  "classifier_notes": "Eventuella kommentarer, t.ex. om uppgiften är gränsfall eller ovanlig"
}}
```
"""
