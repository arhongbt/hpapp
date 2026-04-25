# HP-app — Session 3: Tooling-integration (fyra repos utvärderade)

**Datum:** 2026-04-25 (samma dag som session 1+2, ännu senare)
**Sammanhang:** Innan vi börjar arbeta i `hp-pipeline.zip` ville Hong att fyra externa repos skulle integreras. Claude utvärderade var och en mot pipelinens faktiska behov och pushade tillbaka på två av dem.
**Status:** Bedömning levererad, väntar på Hongs godkännande av integrationsplan.

---

## Hongs request (verbatim)

> "ja men innan det integrera dessa https://github.com/ruvnet/ruflo https://github.com/forrestchang/andrej-karpathy-skills https://github.com/zilliztech/claude-context https://github.com/garrytan/gbrain"

Det föregicks av: *"läs vad vi gör på pipeline, det finns mempalace filer med minne så du förstår vad vi gör"* — Hong ville att Claude först skulle ladda kontext från session 1+2 innan integration bedömdes.

---

## De fyra reposen (kort sammanfattning från README)

### 1. ruflo (ruvnet)
Multi-agent AI-orkestreringsplattform för Claude Code. 16 specialiserade agentroller + custom types i koordinerade swarms. WASM/Rust-kärna, enterprise-grade säkerhet, self-learning. Bygger på `claude-flow` (6000+ commits, v3.5).

### 2. karpathy-skills (forrestchang)
En enkel `CLAUDE.md`-fil baserad på Karpathys observationer om LLM-kodning. Fyra principer:
- **Think Before Coding** (mot wrong assumptions, hidden confusion)
- **Simplicity First** (mot overcomplication, bloated abstractions)
- **Surgical Changes** (mot orthogonal edits)
- **Goal-Driven Execution** (tests-first, verifiable success)

Karpathy-citat (från README):
> "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications... They really like to overcomplicate code and APIs, bloat abstractions... implement a bloated construction over 1000 lines when 100 would do."

### 3. claude-context (zilliztech)
MCP-plugin som ger Claude Code semantisk kodsökning via vector database. "Your entire codebase as Claude's context" — eliminerar multi-round discovery i stora repos. Kräver Zilliz Cloud eller egen vector-DB.

### 4. gbrain (garrytan, YC President/CEO)
Själv-trådande knowledge graph + agentminne. 29 skills, hybrid search, typade länker (`attended`, `works_at`, `invested_in`, `founded`, `advises`), backlink-boosted ranking, zero-LLM entity extraction från sidskrivningar. Benchmarkat mot kategorin: **P@5 49.1%, R@5 97.9%** på BrainBench (240-page Opus-genererat korpus). PGLite (ingen separat server, redo på 2 sekunder). Designad för agent-installation (~30 min).

Bygger för Garrys egna OpenClaw + Hermes-deployments: 17 888 sidor, 4 383 personer, 723 företag, 21 cron-jobb autonomt.

---

## Claudes bedömning

### ✅ Integrera — load-bearing

**karpathy-skills** → trivial drop, ingen risk. Pipelinen är 21KB Python; Karpathys *Simplicity First + Surgical Changes* är exakt disciplinen som behövs när vi börjar editera prompts och klassificeringskod. Drop `CLAUDE.md` i `hp-pipeline/`-roten.

**gbrain** → *inte ett verktyg för pipelinen, utan arkitekturen för moaten*. Session 1 specade:
- Mikro-färdighets-taxonomi (60–80 noder)
- Skill tree = beroendegraf mellan koncept
- Mental modell av varje elev över sessioner

GBrains datamodell `(entity) –[typed_link]→ (entity)` mappar 1:1 på:
- `(uppgift) –[testar]→ (mikro-färdighet)`
- `(mikro-färdighet) –[förutsätter]→ (mikro-färdighet)`
- `(elev) –[bemästrat]→ (mikro-färdighet)`
- `(elev) –[kämpat-med]→ (uppgiftstyp)`

Pipelinen ska alltså skriva *till en GBrain-graf*, inte bara JSONL. Det levererar världskartan + skill tree gratis från klassificeringen.

### 🤷 Vänta — marginell

**claude-context** → semantisk kodsökning är overkill för 21KB Python (4 filer). Värdefull när vi senare jobbar i hela HP-app-kodbasen eller dodsbo (55+ routes). Skjut till efter MVP-pipelinen körts.

### ❌ Skippa (för nu) — fel verktyg

**ruflo** → 16-agent-swarm för fyra sekventiella LLM-anrop är "bloated construction over 1000 lines when 100 would do" — exakt det karpathy-skills varnar för. Pipelinen är inbyggt enkel: describe → cluster → taxonomy → classify. Möjligt återbesök om vi senare behöver agent-per-delprov (XYZ-agent, NOG-agent...) men först bevisa att enkel pipeline fungerar.

---

## Föreslagen integrationsplan

1. Packa upp `hp-pipeline.zip` → `hp-app/pipeline/hp-pipeline/`
2. Lägg karpathy-skills `CLAUDE.md` i pipeline-roten
3. Skissa hur step3 (taxonomy) + step4 (classify) skriver till GBrain — inte bara JSONL — så skill-grafen byggs av klassificeringen
4. Läs GBrains `INSTALL_FOR_AGENTS.md` för att bedöma installationskrav innan vi rör pipeline-kod
5. claude-context + ruflo → backlog

---

## Tonregister-anteckning

Claude pushade tillbaka mot "integrera alla fyra" trots Hongs explicit request. Motivering: substans, inte realism-coach. *Två av fyra var fel verktyg för uppgiften*, och föregående sessioner etablerade att Claude ska pusha tillbaka när det finns vetenskaplig/teknisk grund (som "metoder från åtta länder" → blev accepterat). Avgörande: Hong sa själv tidigare *"konkurrenter ska inte stoppa visionen från att tas på allvar"* — på samma sätt ska tooling-katalog inte få fördröja moaten. ruflo och claude-context är inte fel verktyg, de är fel verktyg *för pipelinen just nu*.

Beslut hos Hong.

---

## Öppna frågor

1. Godkänner Hong planen (1–5)? Eller ska vi köra alla fyra ändå?
2. Om GBrain → behöver Hong en agent-plattform (OpenClaw/Hermes) eller går det köra "naked" mot vår existerande Claude Code-setup? Måste verifieras i `INSTALL_FOR_AGENTS.md`.
3. Ska gbrain-grafen vara den *enda* persistensen, eller dual-write JSONL + graf under utveckling?

---

## Update — efter Hongs godkännande

Hong svarade kort: **"ja"** — godkände hela planen.

### Vad som faktiskt hamnade på disk

| Steg | Status | Plats |
|---|---|---|
| 1. Packa upp `hp-pipeline.zip` | ✅ | `hp-app/pipeline/hp-pipeline/` |
| 2. Karpathy `CLAUDE.md` i pipeline-roten | ✅ | `hp-app/pipeline/hp-pipeline/CLAUDE.md` (med HP-projekt-specifik addendum) |
| 3. Skissa GBrain-skrivning från step3+step4 | 🟡 påbörjad | Inläst `step3_taxonomy.py`, `step4_classify.py`, `models.py` — själva designen ej skriven än |
| 4. GBrain `INSTALL_FOR_AGENTS.md` läst | ✅ | Krav: `git clone ~/gbrain`, `bun install && bun link`, `OPENAI_API_KEY` (kritisk), `ANTHROPIC_API_KEY` (optional) |
| 5. claude-context + ruflo → backlog | ✅ | Bara README-fetched, inte klonade |

### Repo-status (verbatim klargörande till Hong)

> "På disk finns just nu: `pipeline/hp-pipeline/CLAUDE.md` (karpathy — färdig). Inget av de tre andra repos lokalt."

- **karpathy-skills** — fullt integrerat (en CLAUDE.md-fil, inget mer i repot vi behöver)
- **gbrain** — läst men ej klonat eller installerat
- **claude-context** — bara README
- **ruflo** — bara README

---

## Pipelinens datamodeller (för GBrain-mappning)

Lästa från `src/models.py`. Fem Pydantic-modeller flödar genom pipelinen:

| Modell | Steg | Relevant fält för GBrain |
|---|---|---|
| `Task` | input | `id, delprov, uppgift_text, answer_options, correct_answer` |
| `TaskDescription` | step 1 | `task_id, description, primary_skill_guess, requires_image` |
| `Cluster` | step 2 | `cluster_id, title, description, delprov, member_task_ids` |
| `TaxonomyNode` | step 3 | `id, name, level (1=delprov, 2=area, 3=micro-skill), parent_id, prerequisites: list[str]` |
| `Classification` | step 4 | `task_id, primary_skill_id, secondary_skill_ids, estimated_difficulty (1–5), estimated_time_seconds, common_traps, solution_strategies` |

**Naturlig graf-mappning till GBrain:**

```
TaxonomyNode (level=1) → entity: Delprov
TaxonomyNode (level=2) → entity: Area
TaxonomyNode (level=3) → entity: MicroSkill

(Area) –[part_of]→ (Delprov)
(MicroSkill) –[belongs_to]→ (Area)
(MicroSkill) –[prerequisite_for]→ (MicroSkill)   # från TaxonomyNode.prerequisites

Task → entity: Task
(Task) –[tests_primarily]→ (MicroSkill)          # primary_skill_id
(Task) –[tests_also]→ (MicroSkill)               # secondary_skill_ids
(Task) –[has_trap]→ (Trap)                       # common_traps som entiteter
(Task) –[solved_by]→ (Strategy)                  # solution_strategies som entiteter

Cluster → entity: Cluster
(Task) –[member_of]→ (Cluster)
```

Det här är förslaget, ej beslutat. Klargörs vid nästa session.

---

## Versionshantering — ny situation

Vid `/create-pr`-försök upptäcktes:
- **dodsbo-repot**: bara `.claude/settings.local.json` ändrad (tooling-brus från code-review-toggle, inte sessionsarbete)
- **hp-app/**: var **inte** ett git-repo

Hong valde **alt 1**: init `hp-app/` som git-repo, pusha till nytt remote `arhongbt/hp-app`.

### Status på init

✅ `git init -b main` körd i `hp-app/`
✅ `.gitignore` skriven (Python, OS, pipeline output, node_modules)
✅ Filer **stagade**: `.gitignore`, `hp-mempalace/*`, `pipeline/*`
🟡 **Inte committat ännu**
❌ **Blockerare**: `gh` CLI inte installerat — kan inte skapa remote `arhongbt/hp-app` automatiskt

### Push-procedur när Hong är redo

```bash
# Slutföra commit lokalt
cd /Users/benzinho/Desktop/hp-app
git commit -m "init: HP-app vision, pipeline, mempalace"

# Skapa repot manuellt på github.com (privat) → arhongbt/hp-app
# Eller installera gh: brew install gh && gh auth login

# Sedan:
git remote add origin https://github.com/arhongbt/hp-app.git
git push -u origin main
```

---

## Tonregister-anteckning (uppdaterad)

Claude pushade tillbaka tre gånger denna session, alla med substans:
1. Mot "integrera alla fyra repos" → två var fel verktyg, två var rätt
2. Mot `/create-pr` mot dodsbo → sessionens arbete låg inte där
3. Mot att överskatta vad som var "klart" → klargjorde att bara karpathy faktiskt landat på disk, inte de andra tre

Hong accepterade alla tre. Mönstret som etablerades i session 1 håller: när substansen finns ska Claude pusha tillbaka, inte lista risker som redan övervägts.

---

## Öppna frågor (uppdaterade)

1. Ska `git clone https://github.com/garrytan/gbrain.git ~/gbrain` köras nu eller vänta?
2. Ska `gh` CLI installeras (`brew install gh`) eller skapar Hong repot manuellt på github.com?
3. Privat eller publikt repo för `arhongbt/hp-app`? *Default-rekommendation: privat — det här är moaten, ska inte exponeras till konkurrenter.*
4. Den föreslagna graf-mappningen ovan — granska och justera innan vi skriver kod för step3/step4 → GBrain.

---

## Update 2 — repo live + pipeline kartlagd

### Repo etablerat

Hong skapade repot manuellt på github.com och gav push-kommandona verbatim:

> "git remote add origin https://github.com/arhongbt/hpapp.git
> git branch -M main
> git push -u origin main"

**Notering:** Repo-namnet blev `hpapp` (ett ord), inte `hp-app` med bindestreck.

**Commits:**
- `63f3c1c` — init: HP-app vision, pipeline, mempalace
- `3c877fd` — docs: session 3 update — push status, gbrain graph mapping draft

Live på: https://github.com/arhongbt/hpapp

**Lärdom:** `rtk` filterhook svalde stderr när `git push -u origin main` faktiskt misslyckades första gången ("Everything up-to-date" + "no upstream configured"). `rtk proxy git push` gav rå output och pushen gick igenom. Spara: när git-output ser "för ren" ut, verifiera med `rtk proxy`.

### Pipelinens fulla struktur (kartlagd)

```
hp-pipeline/
├── src/
│   ├── run_pipeline.py     # CLI, --limit för test, --skip-stepN för rerun
│   ├── step1_describe.py   # per-task fri-text (resumable via append_jsonl)
│   ├── step2_cluster.py    # per-delprov klustring (batch 50)
│   ├── step3_taxonomy.py   # 1 LLM-anrop, hierarkisk taxonomi från kluster
│   ├── step4_classify.py   # per-task klassificering (resumable, low_confidence flagg)
│   ├── quality_check.py    # genererar quality_report.md
│   ├── utils.py            # call_claude med retry, JSONL helpers, extract_json
│   ├── config.py           # MODEL, batch-storlekar
│   └── models.py           # Pydantic: Task, TaskDescription, Cluster, TaxonomyNode, Classification
├── prompts/                # SYSTEM/USER PROMPT per steg
├── data/uppgifter_sample.jsonl  # 5 uppgifter (XYZ × 2, KVA × 1, NOG × 1, ORD × 1)
└── requirements.txt        # anthropic, pydantic, tqdm, tenacity, dotenv
```

### Sakliga observationer (efter genomläsning)

1. **Modellen är gammal**: `claude-sonnet-4-20250514` (Sonnet 4 från maj 2025). Dagens latest är Sonnet 4.6 / Opus 4.7. *Beslut*: lämna ifred för smoke-test (surgical changes), bumpa senare om kvaliteten brister.
2. **Sample är minimal**: 5 uppgifter över 4 delprov → step 2 får 1–2 uppgifter per kluster. Räcker för "kör pipelinen utan crash"-verify, inte för "taxonomin är bra"-verify.
3. **Saknad API-nyckel**: `config.py:11` kraschar vid import om `ANTHROPIC_API_KEY` inte är satt. Pending från Hong.
4. **Kostnad**: sample (5 task) ≈ $0.05. Full körning (6000 task) ≈ $50 enligt README.
5. **Sample data har KEY trap-uppgift**: `sample-001` är klassiska "−25% sedan +25% är inte 0%"-fällan — exakt samma som session 2:s verifierade fakta om procentfällan i XYZ.

### Föreslaget success-kriterium ("börja jobba")

Per Karpathy's *Goal-Driven Execution*:

```
1. Smoke-test pipelinen mot sample (5 task)  → verify: alla 4 output-filer skapas utan crash
2. Läs output (taxonomy.json + classified.jsonl) → verify: ser pedagogiskt rimligt ut
3. Bestäm GBrain-mappning baserat på faktisk output → verify: skissen committad
```

**Pending:** Hongs API-nyckel innan smoke-test kan köras.

### Karpathy-disciplin redan tillämpad i denna session

- *Surgical Changes*: bestämde att INTE bumpa modellen som del av "börja jobba". En sak i taget.
- *Think Before Coding*: pushade tillbaka på `/create-pr` mot dodsbo (fel target). Pushade tillbaka på "integrera alla fyra repos" (två fel verktyg).
- *Goal-Driven Execution*: definierade tre verifierbara steg innan kod körs.

Om vi följer den här disciplinen säger karpathy-skills att det syns som: "fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes."

---

## Update 3 — smoke-test genomförd

### Setup-flödet

Hong delade `ANTHROPIC_API_KEY` i chatten. Skrev till `.env` (gitignored). Säkerhetsnotis lämnad: rotera nyckeln efter projektet.

*(Nyckelvärde redacted — GitHub secret scanning rejekterade tidigare commit som innehöll den verbatim. Lärdom: aldrig kopiera secret-värden in i mempalace-anteckningar, även för "verbatim quote"-doktrinen.)*

### dotenv-bug upptäckt

`load_dotenv()` i `config.py:7` laddar **inte** från `.env` om env-varianten redan är satt till **tom sträng** i shellet. Hongs zsh hade `ANTHROPIC_API_KEY=''` exporterad någonstans. Manifesterade som krasch trots att `.env` fanns och innehöll rätt nyckel.

**Workaround som fungerade:** `unset ANTHROPIC_API_KEY && python -m src.run_pipeline ...`

**Permanent fix (föreslagen, ej committad än):** ändra `load_dotenv()` → `load_dotenv(override=True)` i `config.py`. En keyword arg. Surgical change-godkänd: gör beteendet robust.

### Smoke-test-resultat

```bash
# Från hp-pipeline/, efter unset:
./venv/bin/python -m src.run_pipeline --input data/uppgifter_sample.jsonl --output output/sample/
```

| Steg | Resultat | Tid |
|---|---|---|
| Step 1 (describe) | 5/5 ✅ | ~32s |
| Step 2 (cluster) | 5 kluster över 4 delprov | ~13s |
| Step 3 (taxonomy) | 14 noder (4 L1, 5 L2, 5 L3) | ~5s |
| Step 4 (classify) | 5/5, avg confidence 0.95 | ~32s |
| Quality | ✅ "Taxonomin verkar pålitlig" | – |

**Total tid:** ~76s. **Kostnad:** ~$0.05.

### Kvalitetsanalys av output

#### ✅ Genuint bra

- **`xyz_aritmetik_procent_sammansatt`** ("Sammansatt procentuell förändring") — fångar **exakt** procentfällan från session 2:s verifierade fakta. Modellen skiljer mellan `procent_grunder`, `procent_forandring`, `procent_sammansatt`. Pedagogiskt rätt nivå.
- **`kva_talforstaelse_kvadrering_brak`** — "Kvadrering av tal mellan 0 och 1". Specifik insight (x² < x när 0 < x < 1), inte generisk "talförståelse". Exakt den nivå av mikro-färdighet session 1 efterfrågade.
- **Common traps är pedagogiskt korrekta.** För sample-001: modellen listade "Tror att +25% och -25% tar ut varandra och svarar 400 kr" — *exakt* vad fel-alternativ B är. Modellen förstår fällan.
- **Prerequisites byggs in** i `TaxonomyNode.prerequisites: list[str]`. Dependency-grafen finns.
- **Solution strategies pedagogiskt rimliga** (multiplikativ metod, konkret exempel-testning, etc).

#### ⚠️ Problem

1. **NOG-namnet är hallucinerat.** Taxonomin kallar NOG för **"Noggrannhet"** (id=`nog`, name=`"NOG - Noggrannhet"`). Det är **fel**. NOG = "Kvantitativa resonemang" / informationstillräcklighet (session 2 verifierad). Modellen gissade på akronymen.
   - **Fix:** hårdkoda delprov-namn i `prompts/step3_taxonomy.py` SYSTEM_PROMPT.
   - **Skjuts:** löses bättre när vi har mer data att iterera mot. Surgical-principen.

2. **Prerequisites refererar till noder som inte existerar** i taxonomin (t.ex. `xyz_aritmetik_procent_grunder`, `xyz_aritmetik_brak_decimal`). För 5 uppgifter kan taxonomin bara skapa noder för det den ser. *Inte ett bug — löses med större dataset.*

3. **Alla confidence = 0.95.** Misstänkt — antingen är alla 5 sample genuinely tydliga matches eller modellen "spelar säkert". Validering kräver riktig dataset.

### Föreslagna nästa steg (rangordnade)

1. **Fix dotenv-bug** (en kw-arg, commit nu)
2. **Skaffa riktigt data**: ladda ner PDF-prov från `https://www.studera.nu/hogskoleprov/om/forbereda/tidigare/`, konvertera → JSONL, kör mot 50–100 uppgifter.
3. **Iterera prompts** baserat på vad som syns med riktig data (t.ex. NOG-bug)
4. **Design GBrain-skrivning** mot output-formatet — vi har det nu, schema-mappningen från session 3 håller
5. **Modell-bump** (sonnet 4 → sonnet 4.6) endast om kvalitet brister

### Anchor-citat från Hong (för framtida sessioner)

Hong-tonen den här sessionen var kort, action-oriented:
> "ja"
> "okej ska vi köra på med add zippa up pipeline filen och börja jobba"
> "okej gör såhär jag har filerna i pdf i hp mappen konvertera dem till jsonl så att allt blir tydligt och läsbart för dig, efter det går vi vidare"

Det matchar tonregister-anteckningen: sparring, inte realism-coach. Jag ska inte fråga sju gånger.

---

## Update 4 — riktigt data + PDF-extraktor

### GitHub secret scanning blockerade fix-commit

Andra `git push` (med `fix(config): override=True` + session 3-uppdatering) **rejekterades** av GitHub:
```
[remote rejected] main -> main (push declined due to repository rule violations)
```
Orsak: jag hade kopierat in API-nyckeln verbatim i session 3-filen som "verbatim Hong"-citat. GitHub secret scanning fångade det.

**Fix-flöde:**
1. `git reset --soft HEAD~1` — undo commit, behöll filer
2. Edit session 3 → redacta nyckelvärdet
3. Skapade ny branch `chore/dotenv-fix`
4. Commit + push lyckades → branch `chore/dotenv-fix` skapad

**Lärdom (sparad ovan):** aldrig kopiera secret-värden in i mempalace-anteckningar, även för "verbatim quote"-doktrinen.

PR att skapa manuellt: https://github.com/arhongbt/hpapp/pull/new/chore/dotenv-fix

### Hongs PDF-data

Hong delade två sätt att leverera HP-prov:

1. **SmallPDF-konverterade JSON** i `Downloads/smallpdffree-PDF_to_Json/` (10 filer)
2. **Original-PDFs** i `hp-app/hp-prov/` (10 filer, gitignored, 14MB)

#### SmallPDF-kvalitetsanalys (efter genomläsning)

| Filtyp | Kvalitet | Användbar för |
|---|---|---|
| Facit (`hogskoleprovet-facit-26a.json`, `hp-25b.json`) | ✅ Perfekt | Direkt regex-parsa eller LLM |
| Verbal (`provpass-*-verb-utan-elf.json`) | ✅ ~95% | Med LLM-städning |
| Kvant XYZ/KVA/NOG | ⚠️ ~70% | Matematiska formler trasiga |
| Kvant DTK | ❌ ~10% | Bokstav-för-bokstav fragmenterad text, diagram saknas |

**Notera:** ELF (engelsk läsförståelse) saknas helt i alla verbal-filer ("utan-elf").

#### Prov-mappning (verifierad från SmallPDF-JSON-datum)

- **HP 2026-04-18 (vt 2026, "26a")**: pass 1=utprövning (skip), pass 2=verb, pass 3=kvant, pass 4=verb, pass 5=kvant
- **HP 2025-10-19 (ht 2025, "25b")**: pass 1=kvant, pass 2=utprövning (skip), pass 3=verb, pass 4=kvant, pass 5=verb

Total räknad volym: 2 prov × 4 pass × 40 uppgifter = 320 uppgifter.

### Beslut: använd Anthropic PDF document API

Eftersom SmallPDF-JSON är för trasig för DTK och formler valde vi att skicka original-PDFs direkt till Claude (med vision för diagram + formler). Cost-estimat: ~$0.20 per provpass × 8 + ~$0.05 × 2 facits = **~$1.70 total**.

### Skapad: `pipeline/hp-pipeline/scripts/extract_corpus.py`

Script-arkitektur:
- `EXAM_META`: dict mappar PDF-filnamn → `{date, year, term, kind, pass}`
- `extract_facit()`: skickar facit-PDF till Claude → `{pass_number: [40 svar]}`
- `extract_provpass()`: skickar prov-PDF → JSONL med `task_number, delprov, uppgift_text, answer_options`
- `main()`: kör båda, mergar med facit, skriver `data/uppgifter.jsonl`
- CLI-flagga `--only <fil>` för smoke-test (skriver till `data/_test_<stem>.jsonl`)

**Kärnfunktion:**
```python
client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": [
        {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
        {"type": "text", "text": prompt},
    ]}],
)
```

### Smoke-test resultat: 30 uppgifter, hög kvalitet

Kört på `provpass-2-verb-utan-elf.pdf`:

| Delprov | Antal | Kvalitet |
|---|---|---|
| ORD (1-10) | 10 | ✅ Perfekt — ord + 5 alternativ A-E |
| LÄS (11-20) | 10 | ✅ Bra — Claude markerar text-referens + frågan |
| MEK (21-30) | 10 | ✅ Antagen bra (ej manuellt verifierad än) |
| ELF (31-40) | 0 | ✅ Korrekt utesluten (utan-elf-fil) |

Exempel ORD: `{"task_number": 1, "delprov": "ORD", "uppgift_text": "prognos", "answer_options": {"A": "besked", "B": "utvärdering", "C": "sammanfattning", "D": "förutsägelse", "E": "redovisning"}}`

Exempel LÄS: `"uppgift_text": "Text om medborgarkompetens och skolreform. Vilket är det huvudsakliga målet med den studie som presenteras i texten?"`

`correct_answer: "?"` i smoke-test eftersom facit inte processades med `--only` flag.

### Sakliga observationer

1. **`claude-sonnet-4-20250514` är deprecerad** (EOL 2026-06-15). Bumpa till `claude-sonnet-4-6` efter validering. Surgical-principen: fix en sak i taget.
2. **LÄS-fulltexter saknas i extraktionen** — Claude komprimerar till en text-referens. Räcker för klassificering, inte för app-UX. V2-arbete.
3. **Kostnadsmodell verifierad:** smoke-test på 0.4MB PDF tog ~30s, ger oss konfidens att 14MB total körning ligger på ~$1.70 / 5 min.

### Status (vid senaste auto-save)

- ✅ `extract_corpus.py` skriven (ej committad än — väntar på full validering)
- ✅ Smoke-test klar (30 uppgifter, hög kvalitet)
- 🟡 **Full extraktion startad i bakgrund** (alla 10 PDFs) — task ID `bt8bzc3i6`
- ⏰ Schemalagd poll om 90s för att kolla resultat
- 📋 Pending: commit script + commit `data/uppgifter.jsonl` (sista är gitignored så bara script committas)

### Föreslagna nästa steg efter extraktion

1. Granska `data/uppgifter.jsonl` — verifiera 320 uppgifter, korrekta facit-svar (inga "?")
2. Commit `extract_corpus.py` till `chore/dotenv-fix`-branchen
3. Köra hela klassificeringspipelinen mot riktiga 320 uppgifter (~$50, ~2 timmar)
4. Iterera prompts om kvalitet brister (NOG-namn-bug etc)
5. Sedan: GBrain-mappning

---

## Update 5 — extraktion klar + pilot startad

### Faktisk extraktion: 280 uppgifter, inte 320

Förväntat var 320 (4 pass × 40 × 2 prov), men vi fick **280**. Orsak: alla verb-PDFs är `*-utan-elf.pdf` — ELF-delprovet (uppgift 31-40) saknas i alla 4 verb-pass = 4 × 10 = 40 uppgifter saknas. **280 är rätt** givet datakällan.

```
Per delprov: XYZ 48, KVA 40, NOG 24, DTK 48, ORD 40, LÄS 40, MEK 40, ELF 0
Saknar facit (?): 0
```

### Kvalitet på extraktion (verifierad spot-check)

- **XYZ formel**: `x + 1/4 = 1/8` korrekt återskapad (SmallPDF gav fragmenterade glyfer `"+", "x", "1", "4", "1", "=", "8"`)
- **KVA**: `25 procent av √16` vs `√4` — kvadratrot-symbol bevarad
- **NOG**: 5-alternativ A-E komplett
- **DTK**: ✅ vision funkar — "Tabell visar antal pensionärer i december 2017 redovisat utifrån kön, uttagsandel och typ av pension..."

### Commits efter senaste auto-save

| Commit | Branch | Beskrivning |
|---|---|---|
| `cfe2b24` | chore/dotenv-fix | feat(scripts): PDF→JSONL extractor via Anthropic document API |
| `f063781` | chore/dotenv-fix | chore: bump model claude-sonnet-4-20250514 → claude-sonnet-4-6 |

Branch `chore/dotenv-fix` har nu 3 commits ahead of main. PR pending manuell skapelse: https://github.com/arhongbt/hpapp/pull/new/chore/dotenv-fix

### Hongs nya kommandon

> "what happend you need to brief me what you are doing"

— Hong bytte språk till engelska och bad om briefing. Levererade kort sammanfattning av all dagens arbete.

> "yes do de recommendation"

— Godkände min rekommendation: kör pilot på 50 uppgifter innan vi spenderar $2 på 280.

### Pilot 50: stratifierad subset

```python
# Per delprov: 7-8 task, total 50
# Seed=42 för reproducerbarhet
random.seed(42)
for delprov in ['XYZ', 'KVA', 'NOG', 'DTK', 'ORD', 'LÄS', 'MEK']:
    pilot.extend(random_sample(by_delprov[delprov], 7))
pilot.append(by_delprov['XYZ'][7])  # +1 = 50

# Resultat:
# {'XYZ': 8, 'KVA': 7, 'NOG': 7, 'DTK': 7, 'ORD': 7, 'LÄS': 7, 'MEK': 7}
```

Skriven till `data/uppgifter_pilot50.jsonl` (gitignored).

### Pilot-körning startad i bakgrund

- **Task ID**: `bu6x391v7`
- **Model**: claude-sonnet-4-6 (bumpad)
- **Output**: `output/pilot50/`
- **ETA**: ~12 min
- **Cost**: ~$0.65
- **Schemalagd poll**: 600s (efter starttiden)

### Vad jag kommer kolla när pilot är klar

1. **NOG-namnet** — fortfarande "Noggrannhet" (hallucinerat) eller fixat? Canary-bug.
2. **DTK-klassificering** — fungerar visuellt-baserade beskrivningar i text-only pipeline-step?
3. **Confidence-spridning** — alla 0.95 igen (misstänkt) eller varierar?
4. **Taxonomins storlek** — antal mikrofärdigheter (förväntat ~30-50)
5. **Faktisk kostnad** vs $0.65-estimatet

### Anchor för framtida sessioner

Hong är action-oriented och accepterar väl-motiverade rekommendationer snabbt:
- "yes do de recommendation"

Pattern: ge en tydlig rekommendation med substans → Hong svarar kort med ja/nej. Inte bra att bara lista 5 alternativ utan riktning.

---

## Update 6 — pilot körd, 2 buggar fixade

### Pilot 50: 3 körningar, 2 strukturella buggar fixade

**Försök 1**: Step 3 kraschade mid-JSON. Orsak: `MAX_TOKENS_TAXONOMY = 4096` för litet för 25 kluster. Pydantic kunde inte parsa avhugget JSON.

**Försök 2** (efter `MAX_TOKENS_TAXONOMY = 16384`, --skip-step1 --skip-step2): Step 3 lyckades, men step 4 hade 7/50 failures. **ALLA 7 var LÄS-uppgifter**, dessutom 3/3 LÄS-mikrofärdigheter "Aldrig använda" i quality report.

**Root cause** (verifierad): `step4_classify.format_skills()` jämförde `delprov.lower()` ("läs" med ä) mot taxonomi-id ("las" utan ä). Resultat: tom `skills_block` för LÄS-uppgifter, Claude fick "(inga mikrofärdigheter hittades)" och returnerade `null` på `primary_skill_id`. Pydantic-modellen kräver `str` → krasch.

**Försök 3** (efter ASCII-fix, --skip-step1 --skip-step2 --skip-step3, step 4 resumable): 50/50 klart, 0 failures.

### Buggfixar (commit `323f092` på `chore/dotenv-fix`)

1. `src/config.py`: `MAX_TOKENS_TAXONOMY` 4096 → 16384
2. `src/step4_classify.py`:
```python
delprov_root_id = delprov.lower().replace("ä", "a").replace("å", "a").replace("ö", "o")
```

### NOG-canary-buggen FIXAD med Sonnet 4.6

Session 1+2 noterade att Sonnet 4 hallucinerade `"NOG - Noggrannhet"` (fel — NOG = Kvantitativa resonemang). Med Sonnet 4.6:

> `"NOG - Matematisk problemlösning med informationsvärdering"`

Inte perfekt frasering men **inte längre fel akronym-tolkning**. Modell-bumpen löste det utan prompt-iteration.

### Pilot-stats

| Mått | Värde |
|---|---|
| Klassificerade | 50/50 (100%) |
| Avg confidence | 0.908 (spridning 0.82–0.99) |
| Taxonomi | 53 noder (7 L1 + 21 L2 + 25 L3) |
| Mikrofärdigheter | 25 definierade, 22 använda |
| Faktisk kostnad | ~$1 (3 körningar inkl misslyckade) |

### Klassificeringskvalitet (verifierat med 5 spot-checks)

Alla 5 var pedagogiskt skarpa. Common traps är konkreta, inte generiska:

- **NOG (tomtar-uppgift)**: `nog_ekvationssystem_frihetsgrader` → trap: "5 = 25% av ursprungligt antal ger direkt"
- **KVA (jämna/udda heltal)**: `kva_algebraisk_variationsanalys` → trap: "beräknar bara ett specifikt exempel"
- **DTK (utrikeshandel)**: `dtk_diagram_kvot_andel` → trap: "läser av fel stapel" (DTK fungerar trots att step 4 är text-only — den description Claude gav i extract_corpus räcker)
- **MEK (psykospatienter)**: `mek_fackterminologi_amnesspecifik` → trap: "tillstånden saknar specifik medicinsk innebörd"
- **XYZ (tärningssannolikhet)**: `xyz_sannolikhet_sammansatt` → trap: "räknar bara utfall där tiotalssiffran är 5 eller 6"

Varje uppgift har: mikrofärdighet, svårighet (1-5), tid (s), 2-3 common traps, 1-3 solution strategies.

### Nästa steg

Pilot ger grönt ljus för full körning. Min rekommendation: **kör alla 280 nu**, ~$4, ~70 min. Båda strukturella buggar fixade. Output: `output/full/{step1...step4, quality_report}.

Pending: Hongs godkännande för full körning.

### Lärdomar för framtida sessioner

1. **Verifiera token-limits proportionellt mot data-storlek**. 4096 räcker för 5-task sample men inte för 50-task pilot. För 280 är 16384 troligen OK men bör monitor.
2. **Svenska tecken i id-fält är en ASCII-fälla**. Taxonomy-id är ASCII (las, lases), input är Unicode (LÄS). Normalisera tidigt.
3. **Resumable steps räddar bort tid**. Att step 4 är resumable per task gjorde att vi bara behövde köra 7 retries efter ASCII-fixen, inte 50.
4. **Modell-bumpen Sonnet 4 → Sonnet 4.6 löste flera saker samtidigt** (NOG-namn, mer realistisk confidence-spridning, bättre common traps). Bra ROI för 5 min jobb.

---

## Update 7 — full körning, 3 nya buggar, streaming-fix

### Försök full pipeline 280 task — 4 körningar krävdes

| Försök | Resultat | Orsak |
|---|---|---|
| 1 (`big08tn9b`) | ❌ Step 2 trunkerade | `MAX_TOKENS_CLUSTER = 4096` för litet för 40 ORD desc |
| 2 (`bmj9smm12`) | ❌ Step 2 trunkerade DTK | 16384 räckte för XYZ/KVA/NOG men inte DTK (48 desc med rik vision-kontext) |
| 3 (`b7h9znull`) | ❌ SDK-fel | `MAX_TOKENS_CLUSTER = 32768` → "Streaming is required for operations that may take longer than 10 minutes" (Anthropic SDK kräver `messages.stream()` när max_tokens > ~21K) |
| 4 (`bv6gxh173`) | 🟡 Kör nu | Streaming-fix i `utils.py` löste root cause |

### Nya buggfixar (ej committade än)

```python
# config.py
MAX_TOKENS_CLUSTER = 32768  # var 16384, nu 32768

# utils.py — call_claude() nu med streaming
with client.messages.stream(
    model=MODEL, max_tokens=max_tokens, ...
) as stream:
    for chunk in stream.text_stream:
        text_parts.append(chunk)
return "".join(text_parts)
```

Streaming löser strukturellt: vi behöver aldrig oroa oss för 10-min non-streaming-gräns igen, oavsett max_tokens.

### Hongs Cowork-fråga (verbatim)

> "kan vi istället låta cowork ta över?"

**Svar: nej, passar inte här.** Tre konkreta hinder:
1. PDFs i `hp-prov/` är gitignored (copyright-skyddat HP-material) → Cowork klonar bara repo
2. `data/uppgifter.jsonl` är gitignored → Cowork får inte input-datat
3. `ANTHROPIC_API_KEY` ligger i lokal `.env` → måste konfigureras manuellt i Cowork-miljön

Cowork passar för: schedule-driven backlog-tasks, parallellt arbete med isolerat scope, async-jobb som inte kräver lokal data. Inte för: kärnpipeline med privat dataset.

### Status vid auto-save

- Pipelinen kör (`bv6gxh173`)
- Step 1: ✅ 280/280 klara
- Step 2: 🟡 3/7 delprov klara, ingen krasch
- ETA: ~60 min kvar
- Pollas: schemalagd om 60 min (`big08tn9b`-poll, men troligen redan klar)

### Lärdom för framtida sessioner

5. **Anthropic SDK har en "10-min non-streaming-gräns"**: när `max_tokens` är högt (~>21K för Sonnet 4.6) MÅSTE vi använda `messages.stream()` istället för `messages.create()`. Lägg till streaming i alla utility-funktioner som default-pattern.
6. **Whack-a-mole-buggar med token-limits beror på underestimering av output**. Ett delprov kan generera 10x mer output än ett annat samma storlek (DTK > XYZ pga vision-kontext). Sätt token-limits konservativt högt och använd streaming från början.
7. **Cowork är värt att fundera på, men inte för pipelines med lokal data + secrets**. Beslutskriterium: kan jobbet repliceras helt från git-repo + offentliga deps? Om ja → cowork ok. Om nej → lokalt.

---

## Update 8 — Streaming-buggen identifierad via isolerad debug

### Hongs request (verbatim)

> "gör en sammanfattning på vad vi gjort ska föra det vidare"

Hong bad om summary för att föra det vidare. Levererade inline-summary + skapade handoff-dokument.

### Critical finding: Streaming är boven, inte LÄS

Misstänkte LÄS-specifik bugg efter 6 misslyckade pipeline-körningar där bara LÄS step 2 trunkerade. Byggde isolerat debug-script (`scripts/debug_step2_las.py`) som körde **exakt samma LÄS-batch utan streaming**:

**Resultat: fungerade perfekt.**
- `stop_reason: end_turn`
- `usage: input=4643, output=1057`
- 5 clusters, ren JSON, parses korrekt

**Slutsats**: `messages.stream()` i `utils.py:call_claude` har en bugg där `text_stream`-iterationen avslutar tyst för vissa LÄS-batches efter ~500 chars. Inte LÄS-specifikt.

### Konkret fix (5-min-jobb, ej genomfört än)

1. Revertera `utils.py` `call_claude` till `messages.create()` (ingen streaming)
2. Sänk `MAX_TOKENS_CLUSTER` 32768 → 8192 (under 21K streaming-tröskeln)
3. Behåll `CLUSTERING_BATCH_SIZE = 15`
4. Re-run med `--skip-step1`

Med dessa: ingen streaming krävs (8K << 21K), ingen 10-min-timeout, batches genererar bara ~2-3K tokens output (5 clusters × 500 tokens). Inte i närheten av token-gränser.

### Pending state vid auto-save

- 6 misslyckade körningar gjorda, inga lokala output sparade efter step 2-misslyckandet
- `output/full/step1_descriptions.jsonl` är intakt (280 descriptions klara)
- Streaming-koden i `utils.py` är committad men skadlig — måste revertas
- `MAX_TOKENS_CLUSTER = 32768` i config.py — måste sänkas

### Resultat av kvällens session

**Vad vi har på disk (lokal):**
- 280 extraherade uppgifter med facit (`data/uppgifter.jsonl`)
- 280 step1-descriptions klara (`output/full/step1_descriptions.jsonl`)
- Pilot-resultat på 50 task (`output/pilot50/`) — komplett, validerad kvalitet

**Vad som saknas:**
- Step 2 → 4 för full 280-task-körning. Blockerat av streaming-bug.

**Vad som krävs för att avsluta:**
- Reverta streaming + sänk max_tokens + re-run step 2-4. Estimerad tid efter fix: 60 min, $3-4.

### Vägen framåt nästa session

Se `hp-mempalace/SESSION_HANDOFF.md` för action-orienterad startguide.

---

## Update 9 — full körning slutförd via chunked execution

### Hongs request (verbatim)

> "nej jag vill att du tar över nu"

Hong överlämnade efter Update 8:s handoff-doc — istället för att vänta på nästa session skulle Claude direkt göra fixen och köra pipelinen färdigt.

### Sandbox-realiteten

Cowork-sandboxen där Claude kör har två hårda begränsningar som bröt den ursprungliga "5-min revert + re-run"-planen:

1. **45-sekunders timeout per bash-anrop.** Step 2 ensam tar ~5 min, step 4 ~28 min. Synkron körning omöjlig.
2. **bwrap `--die-with-parent`.** Bakgrundsprocesser dör när bash-anropet slutar. `nohup` och `setsid` båda meningslösa. Filsystemet persisterar mellan anrop, men inga processer.

Lösning: chunked execution-pattern. Varje step fick en custom runner som:
- Sparar partial state till disk efter varje API-batch
- Vid nästa invocation läser partial state och fortsätter där den slutade
- Concurrent API-anrop (4–20 parallella) för att maxa nytta inom 45s-fönstret

### Kodfixar (på disk denna session)

| Fil | Ändring | Motiv |
|---|---|---|
| `src/utils.py` | `messages.stream()` → `messages.create()` | Streaming-buggen som identifierades i Update 8 |
| `src/config.py` | `MAX_TOKENS_CLUSTER`: 32768 → 16384 | LÄS#1-batch trunkerades vid 8192, 16384 räcker |
| `src/config.py` | `MAX_TOKENS_CLASSIFICATION`: 1024 → 2048 | En KVA-task hade truncated common_traps |

Varför inte 8192 för CLUSTER (som SESSION_HANDOFF v1 föreslog)? För att Sonnet 4.6 ibland behöver mer headroom för LÄS-batches med rik kontext. 16384 är fortfarande under 21K-streaming-tröskeln så `messages.create()` håller.

### Nya scripts

`pipeline/hp-pipeline/scripts/`:

| Script | Syfte | Concurrency |
|---|---|---|
| `run_step2_chunked.py` | One batch (15 descs) per call, 4 parallella | 4 |
| `run_step3_deterministic.py` | Bygg taxonomy utan LLM (L1+L3 från clusters) | 0 |
| `run_step4_chunked.py` | Per-task classify, 20-task wave, save-after-each | 20 |

### Step 3-kompromissen

Step 3 (taxonomy-building) tar ~45-90s med en LLM-call på alla 138 clusters. Per-delprov med concurrency=4 fortfarande 45-60s per call, vilket inte fick plats i 45s-budget.

**Beslut:** kör step 3 deterministiskt — level 1 = 7 delprov-noder, level 3 = 138 cluster-noder direkt. Skippa level 2. `format_skills()` i step 4 använder bara ancestry för att hitta L3-noder under en delprov-root, så denna struktur fungerar.

**Vad vi tappar:** LLM-aggregering av semantiskt liknande clusters, prerequisite-inferens, level-2-områden. Allt kan läggas till i ett separate enrichment-pass senare. Inte blockerande för MVP.

### Resultat

```
Total: 280/280 klassificerade (100%)
Avg confidence: 0.863 (spridning 0.55–0.99)
Tasks med konf < 0.7: 3
Taxonomi: 145 noder (7 L1 + 138 L3)
Mikrofärdigheter använda: 128/138 (93%)
Aldrig använda: 10
Difficulty-fördelning: 1: 13, 2: 156, 3: 99, 4: 12
Per delprov: XYZ 48, KVA 40, NOG 24, DTK 48, ORD 40, LÄS 40, MEK 40
Quality verdict: ✅ "Taxonomin verkar pålitlig"
```

### Aldrig använda mikrofärdigheter (10/138)

Mest dubblettkluster där step 4 valde en annan av en överlappande grupp:

- 3 DTK-clusters om diagram/tabell-avläsning (täcks av andra DTK-kluster)
- 1 KVA-cluster om informationstillräcklighet (handlade om jämförelse)
- 4 MEK-clusters om semantisk koherens (täcks av andra MEK-kluster)
- 2 ORD-clusters om synonym-precision (täcks av andra ORD-kluster)

Inte bug — tydligt symptom på att step 2 skapade fler clusters än step 4 behövde, vilket är OK. En level-2-aggregeringsfas skulle förmodligen slå ihop dessa.

### Pending: git commit blockerad

`.git/index.lock` blockerar alla git-operationer från sandboxen (Operation not permitted vid `rm`). Användaren behöver lokalt:

```bash
cd ~/Desktop/hp-app
rm -f .git/index.lock
git add pipeline/hp-pipeline/src/{utils,config}.py \
        pipeline/hp-pipeline/scripts/run_step{2,3,4}_*.py \
        pipeline/hp-pipeline/scripts/debug_step2_las.py \
        hp-mempalace/{SESSION_HANDOFF.md,2026-04-25-hp-app-session-3-tooling-integration.md}
git commit -m "fix(pipeline): revert streaming + chunked execution + 280-task full run"
git push
```

Sen skapa PR manuellt: https://github.com/arhongbt/hpapp/pull/new/chore/dotenv-fix

### Lärdomar (sandboxe-cooking)

8. **Cowork-sandboxen kan inte köra bakgrundsprocesser längre än 45s.** För långsamma jobb: chunked execution + persistent state. Mönstret: en runner som processar ETT batch per invocation, sparar partial state, exiterar — anropas upprepade gånger.
9. **Concurrency mot Anthropic API:** 16-20 parallella requests fungerar. Higher trippar rate limits utan tydligt felmeddelande (bara långsammare progress).
10. **Pragmatiska shortcuts ofta vinner.** Det deterministiska step 3 levererar 90% av värdet utan LLM-runtime — och kan alltid LLM-förbättras senare. Bygg sämre version som funkar, snyggare version sen.
11. **Token-trunkering i LLM-output:** alltid sätt `extract_json` att fånga truncated och retry med högre max_tokens, eller bygg in en "is_truncated"-detektor. En enda task med truncated `common_traps` kostade 30s av runtime denna körning.
