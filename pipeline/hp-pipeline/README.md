# HP Classification Pipeline

En Python-pipeline som läser HP-uppgifter och bygger en taxonomi automatiskt med hjälp av Claude (Anthropic API).

## Vad detta är

Detta är **alternativ 2** från vår diskussion: en LLM-driven klassificering som bygger taxonomin från grunden utan manuellt arbete från dig.

Pipelinen kör i fyra steg:
1. **Råextraktion** — Claude beskriver vad varje uppgift testar i fri text
2. **Klustring** — Claude grupperar liknande beskrivningar
3. **Hierarkisering** — Claude bygger en taxonomi från klustren
4. **Reklassificering** — Claude taggar om alla uppgifter mot den slutliga taxonomin

Sen finns det tre kvalitetscheckar för att verifiera att taxonomin håller.

## Vad du behöver innan du kör

1. **Python 3.10 eller högre** installerat
2. **Anthropic API-nyckel** — hämtas på console.anthropic.com (kreditkort krävs, räkna med ~50 USD totalkostnad)
3. **Råa HP-uppgifter** i textformat — se sektion "Förbered datan" nedan
4. **2–3 timmar** för en första körning på 50 uppgifter (för att validera att det fungerar)
5. **6–8 timmar bakgrundskörning** för full körning på alla ~6000 uppgifter

## Hur du faktiskt kör detta (för någon icke-teknisk)

Om du inte är van vid Python: **be en utvecklare följa instruktionerna nedan**. Det här är inte rocket science men det innebär kommandoraden, miljövariabler, och felsökning. En genomsnittlig juniorutvecklare gör detta på en eftermiddag.

Om du vill prova själv: börja med [Replit](https://replit.com) — då slipper du installera något lokalt. Skapa en ny Python-replit, klistra in koden, och kör.

## Förbered datan

Du behöver HP-uppgifter i en `data/uppgifter.jsonl` fil med följande format (en rad per uppgift):

```json
{"id": "2024-vt-pass2-uppg14", "delprov": "XYZ", "year": 2024, "term": "vt", "pass_number": 2, "task_number": 14, "uppgift_text": "Vad är 35% av 280?", "answer_options": {"A": "98", "B": "84", "C": "112", "D": "70"}, "correct_answer": "A"}
```

**Hur du får den datan:**

1. Ladda ner gamla prov (PDF) från https://www.studera.nu/hogskoleprov/om/forbereda/tidigare/
2. Konvertera PDF → text. Använd `scripts/pdf_to_jsonl.py` (se nedan) eller låt en utvecklare göra det.
3. Granska 5–10 rader manuellt för att kontrollera att texten ser korrekt ut.

**Viktigt:** Pipeline-koden för PDF-konvertering är *inte* inkluderad i denna första leverans, eftersom HP-PDF:erna har olika format över åren och kräver case-by-case-justering. Detta är ett separat arbete (säkert 1 dag för en utvecklare) som jag rekommenderar att du gör efter att du sett första pipelinen fungera på handgjorda exempel.

## Steg-för-steg installation

```bash
# 1. Klona eller ladda ner detta projekt
cd hp-pipeline

# 2. Skapa en virtuell Python-miljö
python3 -m venv venv
source venv/bin/activate   # på Mac/Linux
# venv\Scripts\activate    # på Windows

# 3. Installera dependencies
pip install -r requirements.txt

# 4. Sätt din API-nyckel
export ANTHROPIC_API_KEY="sk-ant-din-nyckel-här"

# 5. Verifiera att allt funkar med en mini-körning
python src/run_pipeline.py --input data/uppgifter_sample.jsonl --output output/sample/ --limit 10

# 6. Kör hela pipelinen
python src/run_pipeline.py --input data/uppgifter.jsonl --output output/full/
```

## Output

Efter en lyckad körning får du:

- `output/full/step1_descriptions.jsonl` — fri-text-beskrivningar per uppgift
- `output/full/step2_clusters.json` — kluster med medlems-uppgifter
- `output/full/step3_taxonomy.json` — hierarkisk taxonomi
- `output/full/step4_classified.jsonl` — alla uppgifter taggade mot taxonomin
- `output/full/quality_report.md` — resultat av kvalitetschecker

## Vad du gör efter körningen

1. **Läs `quality_report.md`** — den säger om taxonomin är pålitlig nog att använda
2. **Granska 20 slumpmässiga rader** i `step4_classified.jsonl` — gör de pedagogiskt sett ut att vara korrekt klassificerade?
3. **Om kvaliteten ser bra ut:** vi har vårt fundament. Bygg appen ovanpå.
4. **Om kvaliteten är dålig:** vi byter till alternativ 3 (anställ pedagog). Förlorad investering: ~50 USD och en helg.

## Kostnadsuppskattning

Med Claude Sonnet 4 (current pris ~3 USD per miljon input-tokens, ~15 USD per miljon output-tokens):

- ~6000 uppgifter × 4 steg × ~1500 tokens snitt = ~36 miljoner tokens totalt
- Uppskattad kostnad: **40–80 USD**

För säkerhets skull, sätt en hard limit i ditt Anthropic-konto på 100 USD så det inte skenar.

## Frågor

Om något kraschar, kopiera felmeddelandet och fråga Claude i chatten. Det här är ganska standardiserade Python-fel.
