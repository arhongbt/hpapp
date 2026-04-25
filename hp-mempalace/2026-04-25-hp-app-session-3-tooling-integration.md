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

Det matchar tonregister-anteckningen: sparring, inte realism-coach. Jag ska inte fråga sju gånger.
