# HP-app — Session Handoff

**Datum:** 2026-04-25 (uppdaterad efter full körning)
**Branch:** `chore/dotenv-fix` (lokala ändringar ej committade — git index.lock blockerar i sandboxen, lös manuellt: `rm .git/index.lock`)
**PR-länk att skapa manuellt:** https://github.com/arhongbt/hpapp/pull/new/chore/dotenv-fix

---

## TL;DR

**✅ Full pipeline kördes klart.** 280/280 uppgifter klassificerade mot 138-mikrofärdighets-taxonomi. Avg confidence 0.863. Quality report: "Taxonomin verkar pålitlig." Streaming-buggen löst genom revert till `messages.create()` + chunked execution-pattern för sandbox-begränsningar.

**Vad som faktiskt finns på disk efter denna session:** `output/full/{step1_descriptions, step2_clusters, step3_taxonomy, step4_classified, quality_report}` — alla 5 artifakter klara.

---

## Resultat (denna session)

| Mått | Värde |
|---|---|
| Klassificerade | 280/280 (100%) |
| Avg confidence | 0.863 (spridning 0.55–0.99) |
| Tasks med konf < 0.7 | 3 |
| Taxonomi | 145 noder (7 L1 + 0 L2 + 138 L3) |
| Mikrofärdigheter | 138 definierade, 128 använda, 10 aldrig använda |
| Difficulty-fördelning | 1: 13, 2: 156, 3: 99, 4: 12 |
| Per delprov-classified | XYZ 48, KVA 40, NOG 24, DTK 48, ORD 40, LÄS 40, MEK 40 |

Quality report: ✅ "Taxonomin verkar pålitlig. Inga större röda flaggor."

---

## Vad som ändrades denna session

### Kodfixar (på disk, ej committade)

1. **`pipeline/hp-pipeline/src/utils.py`** — `call_claude` revertad från `messages.stream()` till `messages.create()`. Dokumenterad varför (streaming-implementation visade sig vara instabil, text_stream-iteration avslutar tyst för vissa batches).
2. **`pipeline/hp-pipeline/src/config.py`** — `MAX_TOKENS_CLUSTER`: 32768 → 16384 (slutligt värde — först 8192, men LÄS#1 trunkerades). `MAX_TOKENS_CLASSIFICATION`: 1024 → 2048 (en KVA-task hade JSON truncated mitt i common_traps).

### Nya scripts (`pipeline/hp-pipeline/scripts/`)

Alla tre är resumable och säkra mot interrupt — partial state sparas efter varje API-call:

- **`run_step2_chunked.py`** — kör step 2 en batch (15 descriptions) per invocation. Concurrency=4. Skriver `step2_partial.json` löpande, slår ihop till `step2_clusters.json` när allt klart.
- **`run_step3_deterministic.py`** — bygger taxonomy utan LLM (level 1 = delprov, level 3 = clusters direkt). Pragmatiskt val pga 45s-budget per anrop. Förlorar level-2-aggregering och prerequisite-inferens — kan läggas till senare som enrichment-pass.
- **`run_step4_chunked.py`** — concurrency=20, 20-task wave/budget=35s. Använder befintlig `append_jsonl` så step 4-resumability bevaras.
- **`debug_step2_las.py`** (oförändrat — committat tidigare av föregående session) — det script som bevisade streaming-buggen.

### Varför chunked execution-pattern behövdes

Sandbox-bash-callen i den här sessionen har en hård 45-sekunders-timeout, och bwrap kör med `--die-with-parent` så bakgrundsprocesser kan inte överleva mellan anrop. Originalpipelinen körde sequentiellt med ~60 min totaltid — passar inte. Chunked-runners delar upp arbetet i batches som hinner färdigt inom 45s, och sparar progress efter varje batch så ingen tid förloras vid avbrott.

---

## Vad som måste göras nästa session

### 1. Commita ändringarna manuellt

`.git/index.lock` blockerade alla `git add`-anrop från min sandbox (Operation not permitted). Lös:

```bash
cd ~/Desktop/hp-app
rm -f .git/index.lock
git add pipeline/hp-pipeline/src/utils.py \
        pipeline/hp-pipeline/src/config.py \
        pipeline/hp-pipeline/scripts/run_step2_chunked.py \
        pipeline/hp-pipeline/scripts/run_step3_deterministic.py \
        pipeline/hp-pipeline/scripts/run_step4_chunked.py \
        pipeline/hp-pipeline/scripts/debug_step2_las.py \
        hp-mempalace/SESSION_HANDOFF.md \
        hp-mempalace/2026-04-25-hp-app-session-3-tooling-integration.md
git commit -m "fix(pipeline): revert streaming + chunked execution + 280-task full run

- utils.py: revert messages.stream() → messages.create()
- config.py: MAX_TOKENS_CLUSTER 32768 → 16384, MAX_TOKENS_CLASSIFICATION 1024 → 2048
- scripts/: chunked runners for step 2/3/4 (sandbox constraint workaround)
- step3: deterministic L1+L3 taxonomy from clusters (no LLM, see script docstring)

Result: 280/280 classified, avg conf 0.863, 138 micro-skills."
git push
```

PR: https://github.com/arhongbt/hpapp/pull/new/chore/dotenv-fix

### 2. Manuell stickprovsgranskning (~15 min)

Quality report har 20 slumpvalda klassificeringar i `output/full/quality_report.md` — läs dem och bedöm pedagogiskt om majoriteten ser rimliga ut. Om ja → grönt ljus för GBrain-mappning.

### 3. Designa GBrain-skrivning från `step4_classified.jsonl` + `step3_taxonomy.json`

Mappning från session 3:s schema:
- 7 delprov → 7 `Delprov`-noder
- 138 clusters → 138 `MicroSkill`-noder, parent=delprov
- 280 tasks → 280 `Task`-noder
- Per task: `(Task) –[tests_primarily]→ (MicroSkill)`, `(Task) –[has_trap]→ (Trap)`, `(Task) –[solved_by]→ (Strategy)`

### 4. (Valfritt) LLM-enrichment

Med chunked-pattern fungerar nu nedanstående om vi vill (post-MVP):
- Bygga level-2 områden via per-delprov LLM-call (kör `run_step3_per_delprov`-variant)
- Inferera prerequisites mellan mikrofärdigheter

---

## Det ursprungliga "next action"-bloket (för historikens skull, redan utfört)

Gör dessa fyra ändringar i ordning, sen kör pipelinen från step 2:

### 1. Revertera streaming i `pipeline/hp-pipeline/src/utils.py`

Ersätt nuvarande `call_claude` (rader ~80–102) med non-streaming-versionen:

```python
@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=INITIAL_RETRY_DELAY, max=60),
    retry=retry_if_exception_type((APIError, RateLimitError, APIConnectionError)),
    reraise=True,
)
def call_claude(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.0,
) -> str:
    """Call Claude with retry logic. Returns the text response."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text
```

### 2. Sänk `MAX_TOKENS_CLUSTER` i `pipeline/hp-pipeline/src/config.py`

```python
MAX_TOKENS_CLUSTER = 8192   # var 32768 — under 21K-streaming-tröskeln
```

### 3. Behåll `CLUSTERING_BATCH_SIZE = 15` (redan satt — ändra inget)

### 4. Re-run från step 2

```bash
cd /Users/benzinho/Desktop/hp-app/pipeline/hp-pipeline
unset ANTHROPIC_API_KEY  # zsh-arvet — annars kraschar load_dotenv
./venv/bin/python -m src.run_pipeline \
  --input data/uppgifter.jsonl \
  --output output/full/ \
  --skip-step1
```

**Förväntat:** ~60 min, ~$3–4. Step 1 hoppas över (280 descriptions redan på disk).

### 5. Commit fix till `chore/dotenv-fix`

```bash
git add src/utils.py src/config.py
git commit -m "fix(utils): revert streaming, drop max_tokens under 21K-tröskel"
git push
```

Sen skapa PR på https://github.com/arhongbt/hpapp/pull/new/chore/dotenv-fix.

---

## State (verifierad mot repo)

### Repo

| Branch | Commits ahead | Status |
|---|---|---|
| `main` | – | `3c877fd docs: session 3 update` |
| `chore/dotenv-fix` | +5 | Pushad, PR ej skapad |

### Senaste commits på `chore/dotenv-fix`

```
a0b5df8 fix(pipeline): streaming + högre token-limits + lägre batch-size  ← det HÄR är buggen
323f092 fix: token-trunkering i step 3 + ASCII-mismatch i step 4
f063781 chore: bump model claude-sonnet-4-20250514 → claude-sonnet-4-6
cfe2b24 feat(scripts): PDF→JSONL extractor via Anthropic document API
b78295e fix(config): load_dotenv(override=True) + gitignore hp-prov/
```

### Lokala filer (gitignored, finns inte i remote)

- `hp-prov/` — 10 HP-PDFs, 14MB, copyright
- `data/uppgifter.jsonl` — 280 extraherade uppgifter, 0 saknade facit
- `output/full/step1_descriptions.jsonl` — 280 beskrivningar klara
- `output/pilot50/` — komplett, validerad (53-noders taxonomi)
- `.env` — API-nyckel (rotera efter projekt)

### Pending lokala ändringar

```
modified:   hp-mempalace/2026-04-25-hp-app-session-3-tooling-integration.md
untracked:  pipeline/hp-pipeline/scripts/debug_step2_las.py
```

`debug_step2_las.py` är scriptet som bevisade streaming-buggen. Värt att committa till `chore/dotenv-fix` som regression-test.

---

## Root cause: streaming-buggen

Hypotes innan debug: LÄS-batches genererar för mycket text och trunkeras.

Verklighet, bevisad med isolerat script: `messages.create()` (utan streaming) körd på *exakt samma* LÄS-batch:

- `stop_reason: end_turn`
- `usage: input=4643, output=1057`
- 5 clusters, ren JSON, parses korrekt

Streaming-loopen i `utils.py:call_claude` (`text_stream`-iterationen) avslutar tyst efter ~500 chars för vissa LÄS-batches. Inte LÄS-specifikt — det är streaming-implementationen som är instabil för moderate workloads.

Fixen är inte att fixa streamen. Fixen är att inte streama: med `MAX_TOKENS_CLUSTER = 8192` (under SDK:s 21K-streaming-tröskel) och faktisk output ~2–3K tokens per batch, är streaming överflödig och `messages.create()` är robustare.

---

## Lessons (för framtida pipelines)

1. **Token-limits skalar med data — testa med produktionsstorlek.** 4096 räckte för 5-task sample, brast på 50-task pilot, brast igen på 280. Pilot 50 räckte inte för att hitta detta.
2. **Svenska tecken i id-fält är en ASCII-fälla.** Taxonomy-id är ASCII (`las`, `lases`), input är Unicode (`LÄS`). Normalisera tidigt — `delprov.lower().replace("ä","a").replace("å","a").replace("ö","o")`.
3. **Anthropic SDK kräver streaming över ~21K tokens — men streaming har egen instabilitet.** Default-pattern: håll max_tokens under tröskeln när det går, streama bara när du måste.
4. **Lower batch + lower max_tokens + non-streaming är robustare än streaming för moderate workloads.** Streaming är ett tool för verkligt långa svar, inte en generisk "säkrare" default.
5. **Resumable steps räddar bort tid.** Step 4-resume gjorde att vi bara behövde 7 retries efter ASCII-fixen, inte 50. Bygg in `--skip-stepN` + per-task append från start.
6. **Modell-bumpen Sonnet 4 → Sonnet 4.6 löste flera saker samtidigt** (NOG-namn, mer realistisk confidence-spridning, bättre common traps). När en modellbump är trivial och kvalitet är pending — bumpa.
7. **Aldrig kopiera secret-värden in i mempalace-anteckningar**, även för "verbatim quote"-doktrinen. GitHub secret scanning rejekterar pushen.

---

## Vad kommer ut när det är klart

- 280 uppgifter klassificerade mot empirisk taxonomi
- ~80–100 mikrofärdigheter förväntat (skalat från pilot 25 / 50)
- Common traps + solution strategies per uppgift (verifierat pedagogiskt skarpa i pilot)
- Quality report (auto-genererad, säger om taxonomin är pålitlig)
- Det session 1 specade som "moaten" — på disk

Sen: GBrain-mappning per session 3:s schema (`Task → tests_primarily → MicroSkill`, etc).
