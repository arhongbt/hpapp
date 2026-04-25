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
