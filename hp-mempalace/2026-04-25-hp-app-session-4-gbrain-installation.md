# HP-app — Session 4: GBrain installation och brain-bygge

**Datum:** 2026-04-25 (kvällen, samma dag som session 1-3)
**Sammanhang:** Pipelinen från session 3 körd klart, 280/280 klassificerade, facit verifierat 100% match. Nu integration mot GBrain enligt session 3:s graf-mappnings-skiss.
**Status:** ✅ Brain installerad, 426 pages indexerade, 1245 typed-länkar, queryable via CLI.

---

## TL;DR

GBrain installerad via `~/Desktop/gbrain` (npm fallback efter bun-hängning), brain-data skapad i `~/Desktop/hp-app/brain/` (7 delprov + 138 mikrofärdigheter + 280 uppgifter = 426 markdown-pages). Auto-link extraherade 1245 typed-länkar mellan task → microskill → delprov utan en enda LLM-anrop. Path A (Anthropic-only, ingen OpenRouter, ingen vector embedding-runtime) valdes efter att vector-ranking visade noise vs keyword-search precision på vår data. Final state: 1 orphan (readme), 100% embed coverage, brain score 85/100.

---

## Hongs explicita requests denna session

> "ja fixa det snälla"
> "nej jag vill att du tar över nu"
> "hoppa till gbrain"
> "openrouter"
> "den får köra på openrouter api med deepseek v4 som modell"
> "kör inuti hp-app/brain"
> "vi kan ta bort openrouter och endast köra på anthropic"
> "skapa mempalace för det vi gjort"

Hong-tonen kvar: action-oriented, korta beslut, accepterar väl-motiverade rekommendationer (Path A vann över DeepSeek-V4 efter ROI-analys: $1/månad besparing vs 30-min eng-jobb).

---

## Vad som faktiskt landade på disk

### GBrain-installation

| Steg | Status | Notering |
|---|---|---|
| `git clone ~/Desktop/gbrain` | ✅ | 14.86 MiB, 7432 objects |
| `bun install` | ❌ | Hängde efter 3 min på `@smithy/invalid-dependency` |
| `npm install` (fallback) | ✅ | 6s, 14 packages added |
| `bun link` | ✅ | gbrain 0.21.0 i PATH |
| `gbrain apply-migrations --yes` | ✅ | postinstall skippades pga gbrain inte i PATH när det kördes |
| `gbrain init` | ✅ | 25 schema-migrations, PGLite vid `/Users/benzinho/.gbrain/brain.pglite` |
| `gbrain doctor --fast` | ✅ | 90/100 (7 resolver-warnings i gbrain:s egna interna skills, irrelevant) |

**Lärdom:** `bun install` hängde på AWS SDK-deps, men `npm install` + `bun link` fungerade som fallback. Mönstret: när bun strular, npm-fallback är gratis (deps installeras på samma plats).

### Brain-data-bygge

`scripts/build_brain_repo.py` (179 rader) genererar:

```
~/Desktop/hp-app/brain/
├── README.md                                    (index)
├── concepts/
│   ├── xyz.md, kva.md, nog.md, dtk.md,
│   ├── ord.md, las.md, mek.md                  (7 delprov)
│   └── <delprov>_kluster_b<NN>_<NNN>.md        (138 mikrofärdigheter)
└── entities/
    └── 2026-vt-pass3-uppg01.md, ...            (280 uppgifter)
```

**Format per page:** gbrain compiled-truth + timeline med YAML frontmatter, body med beskrivning och `[Title](concepts/slug)` markdown-länkar. Auto-link-extraktorn fångar dessa via regex på `gbrain extract links --source db` — 0 LLM-anrop.

### Provider-resolution (Path A vald)

Tre alternativ utvärderades:

| Path | Setup | För vår data |
|---|---|---|
| A. Anthropic-only (Haiku query-expansion) + tsvector keyword-search | Bara `ANTHROPIC_API_KEY` | ✅ Vald |
| B. OpenRouter för embeddings + Anthropic för chat | Två keys, hybrid vector+keyword+RRF | Testad, vector noise > precision |
| C. OpenRouter routar både embeddings + chat (DeepSeek V4) | Skulle kräva patch av gbrain:s expansion.ts (Anthropic SDK med tools-schema → OpenAI tools) | Avvisad — 30 min eng-jobb sparar $1/mån |

**Path A vinst:** keyword search är extremt precis i 426-page-skala. Cluster-IDs är unika strängar, titlar är deskriptiva. Vector-modellen klustrade "procentuell förändring" så hårt att en NOG-kluster som *nämnde* frasen rankade högre än XYZ-klustret som *handlar om* den. Borttagning av vector-runtime löste detta automatiskt.

### Provider-config (lås in)

```bash
# I ~/.zshrc:
export PATH="$HOME/.bun/bin:$PATH"
# OPENAI_API_KEY och OPENAI_BASE_URL kommenterade ut
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

---

## Final state (verifierat)

```
gbrain stats:
  Pages:     426
  Chunks:    429
  Embedded:  429   (kvar från första embedding-runda via OpenRouter)
  Links:     1245
  Tags:      13
  Timeline:  0

By type:
  entity: 280
  concept: 146  (7 delprov + 138 microskills + 1 README)

gbrain doctor:
  Health score: 80/100
  ✓ 100% embed coverage
  ✓ Schema version 29 (latest)
  ✓ Brain score 85/100 (embed 35/35, links 25/25, orphans 15/15, dead-links 10/10, timeline 0/15)

gbrain orphans: 1 orphan (readme, intentionally isolated index page)
```

### Query-verifiering

Två queries testade:

**1. "FOIL-metoden binomialprodukter"** → Path A (keyword-search):
- Rank 1 (0.95): `entities/2025-ht-pass1-uppg03` ✓ — faktisk FOIL-uppgift
- Rank 2 (0.95): `entities/2026-vt-pass3-uppg01` ✓ — andra FOIL-uppgiften

**2. "procentuell förändring beräkna nytt värde"** → Path A (`gbrain search`):
- Rank 1 (1.00): `entities/2025-ht-pass4-uppg01` ✓ — "En vara kostar 250 kr..."
- Rank 2 (1.00): `entities/2026-vt-pass3-uppg10` ✓ — "Vad är 150% av 50..."
- Rank 3 (1.00): `concepts/dtk_kluster_b00_007` — Procentuell förändring från diagram (relevant)

Båda queries gav exakt rätt svar i topp 2-3. Moaten i action.

---

## ASCII-fällan (igen)

Step 2 genererade cluster-IDs med ä (`läs_kluster_b00_000`). Step 3:s deterministiska builder från session 3:s update 9 behöll dessa IDs. `build_brain_repo.py` skrev filer som `läs_*.md`. Men **gbrain slugifierar fil-paths till ASCII vid import**, så page-slugs blev `las_*` i DB:n. Markdown-länkarna i task-pages pekade på `concepts/läs_*` som inte resolvade → 16 LÄS-orphans.

**Fix:** lade till `normalize_id()` i `load_taxonomy()` och `load_classifications()` så både fil-namn och länkar använder ASCII från start.

```python
def normalize_id(s: str) -> str:
    return s.replace("ä", "a").replace("å", "a").replace("ö", "o").lower()
```

Resultat efter re-import: **17 orphans → 1** (bara README kvar, intentionellt).

**Lärdom #11 (lägg till i framtida sessioners ASCII-fälla-listan):** Normalisera slugs/IDs *vid genereringen i alla pipeline-steg*, inte bara vid query-tid. Step 4:s ASCII-fix räddade klassificeringen men step 3:s deterministiska build behöll ä-versionen som spreds till brain-byggets fil-namn.

---

## Tekniska beslut + motivering

### Varför markdown-filer istället för direkt API-anrop till gbrain?

GBrain:s ingest-modell är "git-repo med markdown är source of truth". Auto-link-extraktion är regex-baserad (zero LLM cost). Att skriva markdown-filer ger:
- Människa-läsbar fallback (kan öppna i Obsidian eller text-editor)
- Versions-kontrollerad data (`git diff`, `git blame`)
- Frikoppling pipeline-output → brain (kan re-bygga brain från andra källor)

Alternativ: använda gbrain:s MCP-API och skriva entities/edges direkt. Skulle vara snabbare ingestion men förlora mänsklig fallback.

### Varför "concepts" + "entities" som directories?

`DIR_PATTERN` i gbrain:s `link-extraction.ts` matchar bara vissa directory-namn för auto-link-extraktion: `people, companies, meetings, concepts, deal, civic, project, projects, source, media, yc, tech, finance, personal, openclaw, entities`. Om vi använt `delprov/`, `microskills/`, `tasks/` hade auto-link inte fungerat — ingen typed-länk i DB:n.

**Mappning:**
- delprov + microskills → `concepts/` (de är abstrakta begrepp/färdigheter)
- tasks → `entities/` (de är konkreta instanser)

### Varför Path A (Anthropic-only) vann över Path B (hybrid)?

Vector search noiseade på "procentuell förändring":
- Top 3 rankade EN korrekt XYZ-kluster på rank 3 (score 0.94)
- Ranks 1-2 var false positives som *nämnde* frasen i sin description men inte handlade om den
- Embedding-modellen klustrar fraser hårdare än kontext

Keyword search via tsvector matchade entities (faktiska procent-uppgifter) på rank 1-2 med score 1.00 — *det* är vad användaren vill se vid pedagogisk sökning.

**Insikt:** vector embeddings är verktyg för att hitta semantisk likhet i opaque corpus (typ blogposts, transcripts). För strukturerad data med tydliga termer (cluster_ids, titlar) är keyword search precisare. 426 pages är väl under skalan där vector blir nödvändig.

---

## Vad som finns på disk efter denna session

### På `main`-branch (committat?)

Pending. Hong behöver göra:

```bash
cd ~/Desktop/hp-app
git add pipeline/hp-pipeline/scripts/build_brain_repo.py \
        hp-mempalace/2026-04-25-hp-app-session-4-gbrain-installation.md
git commit -m "feat(gbrain): brain-repo builder + session 4 mempalace doc"
git push
```

Brain-data (`brain/` directory) är gitignored — den är *output*, inte *kod*. Om vi vill ha brain som versions-kontrollerad: separat git-repo `cd brain && git init`.

### Lokalt (ej committat)

- `~/Desktop/hp-app/brain/` — 426 markdown-filer (gitignored)
- `~/Desktop/gbrain/` — själva gbrain CLI-installationen
- `~/.gbrain/brain.pglite` — PGLite-databasen
- `~/.zshrc` med ANTHROPIC_API_KEY exporterad

---

## Vägen framåt — när Hong är redo

**Imorgon eller nästa session (low-stakes):**
1. **Commita session 4-doc + build_brain_repo.py**
2. **Spot-check brain via fler queries** — testa edge cases ("vilka uppgifter är svårast?", "vilka mikrofärdigheter har bara 1 uppgift?")
3. **Gör brain-repo till sin egen git-repo** om du vill versionera datan separat: `cd ~/Desktop/hp-app/brain && git init && git add . && git commit -m "init: 426 pages, 1245 links from HP pipeline"`

**När appen ska byggas:**
- Tunn frontend (Next.js, t.ex.) som queries gbrain via MCP eller `gbrain serve` HTTP-endpoint
- Use cases:
  - "5 procent-uppgifter med stigande svårighet" → query + filter på `estimated_difficulty`
  - "Vilka mikrofärdigheter har jag aldrig sett?" → graph-query mot user-progression
  - "Quiz mig på FOIL" → graph-traversal från FOIL microskill till alla 2 entities

**När brain ska kompoundera:**
- `gbrain dream` nattligt cron — entity sweep, citation fixes, memory consolidation. Brain läser sig själv smartare över tid.
- `gbrain extract timeline --source db` om vi lägger till timestampade events (t.ex. "elev X klarade uppgift Y 2026-05-01")

---

## Lärdomar (cumulatively, alla sessioner)

1. Token-limits skalar med data — testa med produktionsstorlek
2. Svenska tecken i id-fält är ASCII-fälla (igen i session 4)
3. Anthropic SDK kräver streaming över ~21K tokens, men streaming har egen instabilitet
4. Lower batch + lower max_tokens + non-streaming är robust för moderate workloads
5. Resumable steps räddar bort tid
6. Modell-bumpen Sonnet 4 → Sonnet 4.6 löste flera saker samtidigt
7. Aldrig kopiera secret-värden in i mempalace-anteckningar (GitHub secret scanning)
8. Cowork-sandboxen har 45s bash-timeout + bwrap die-with-parent — chunked execution-pattern krävs
9. Concurrency mot Anthropic API: 16-20 parallella OK
10. Pragmatiska shortcuts ofta vinner (deterministisk step 3 över LLM-step 3)
11. **NEW:** ASCII-normalisera slugs/IDs vid *genereringen i varje pipeline-steg*, inte bara query-tid
12. **NEW:** `bun install` strular ibland — `npm install` + `bun link` är gratis fallback
13. **NEW:** Vector embeddings är inte universellt bättre — för strukturerad data (cluster_ids, titlar) är keyword search precisare
14. **NEW:** GBrain:s DIR_PATTERN är hårdkodad — `concepts/` och `entities/` ger auto-link, custom directories gör det inte

---

## Avslutande noteringar

Det här är moaten session 1 specade. Empirisk taxonomi från riktiga uppgifter, ingen manuell kategorisering, varje fråga kopplad till mikrofärdighet med common traps + lösningsstrategier, allt sökbart genom typed graph + en CLI. På disk. Verifierat. Klar för app-bygge.

Hong-tonen denna session var samma som session 3: korta, action-oriented beslut, accepterar väl-motiverade pushbacks (DeepSeek V4 → Path A var ett pushback Hong accepterade snabbt). Pattern: ge tydlig rekommendation med substans → snabbt ja/nej.
