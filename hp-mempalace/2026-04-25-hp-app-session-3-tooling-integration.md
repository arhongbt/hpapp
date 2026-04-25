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
