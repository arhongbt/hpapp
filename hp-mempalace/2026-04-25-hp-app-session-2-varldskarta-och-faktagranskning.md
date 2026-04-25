# HP-app — Session 2: Världskarta + faktagranskning

**Datum:** 2026-04-25 (samma dag som session 1, men senare)
**Sammanhang:** Första försöket att rita kompetenskartan för HP. Hong krävde faktagranskning av Claudes påståenden. Många claims visade sig vara ogrundade gissningar — denna fil dokumenterar både kartan och vad som faktiskt är verifierat.

---

## ⚠️ Status på denna fils innehåll

**Verifierat fakta** = bekräftat av minst en oberoende publicerad källa
**Arbetshypotes** = Claudes pedagogiska intuition, ej empiriskt verifierat
**Korrigerat** = något Claude tidigare påstod som visade sig vara fel

Framtida sessioner ska inte ta arbetshypoteser som fakta. Den verkliga kartan föds först när klassificeringspipelinen körts mot riktiga prov.

---

## ✅ Verifierad fakta om HP-strukturen

### Övergripande struktur (per provdag)
- 5 provpass × 55 minuter
- 200 uppgifter totalt, varav 160 räknas (40 är utprövning)
- Två kvantitativa pass + två verbala pass + ett utprövningspass

### Antal uppgifter per delprov, per provpass
| Delprov | Per pass | Totalt över provet |
|---|---|---|
| XYZ | 12 | 24 |
| KVA | 10 | 20 |
| NOG | 6 | 12 |
| DTK | 12 | 24 |
| ORD | 10 | 20 |
| LÄS | 10 | 20 |
| MEK | 10 | 20 |
| ELF | 10 | 20 |

Källor: Studera.nu, allakando.se, hpguiden.se, hpappen.se, allarätt.nu

### Ämnesområden i kvantitativa delar
- **XYZ**: aritmetik, algebra, geometri, funktionslära, statistik. Bygger på gymnasiets Matte 1b (vissa källor säger Matte 1–2). Matte 3 och uppåt behövs INTE — inga derivator, integraler, komplexa tal, avancerad trigonometri.
- **KVA**: samma områden som XYZ, men formatet är jämförelse mellan två kvantiteter. Fyra fasta svarsalternativ.
- **NOG**: logiska/kvantitativa resonemang. Bedöma om information räcker för att lösa.
- **DTK**: avläsning och tolkning av diagram, tabeller, kartor. Kräver grundläggande procenträkning, addition, subtraktion, ibland medelvärde.

### Verbala delar
- **ORD**: ordförståelse, fyra svarsalternativ
- **LÄS**: svensk läsförståelse, 10 uppgifter per pass
- **MEK**: meningskomplettering, 1–3 ord saknas
- **ELF**: engelsk läsförståelse

### Tidsrekommendationer per delprov (per pass)
- XYZ: ~12 min (1 min/uppg)
- KVA: ~10 min (1 min/uppg)
- NOG: ~10 min
- DTK: ~23 min (en källa säger 20 min, hpkungen säger 46 min för båda passen tillsammans = 23 min/pass)
- Totalt 55 min per kvantitativt pass

### Hjälpmedel på provet
- Endast tillåtet: rak linjal
- Inte tillåtet: miniräknare
- Inget formelblad
- Tillåtet att kladda i provhäftet

### Poäng och normering
- Alla uppgifter värda 1 poäng
- Inget avdrag för fel svar (gissa alltid)
- Resultat normeras till 0.00–2.00
- Två tillfällen per år (vår + höst)

### Specifika fakta om uppgiftstyper
- **NOG-deltyper enligt Eddler**: ordningsproblem, fyrfältsproblem, antal okända, antal samband
- **KVA fjärde alternativ (D)**: betyder "informationen otillräcklig", inte "vet ej". Ovanligaste alternativet (~18%). B vanligast (~30%).
- **Procent som tvärgående färdighet**: HP-spelet rapporterar att 8–12 av 40 kvantitativa uppgifter helt eller delvis involverar procent
- **Procentfällan**: -25% följt av +25% ger inte tillbaka ursprungspriset (klassisk återkommande typuppgift)
- **Linjal-tekniken på DTK**: används främst för (a) avläsning av diagrampositioner, (b) skalmätning på kartor

### Statistiska mönster i svarsalternativ (allarätt.nu, baserat på alla prov sedan 2011)
- XYZ: C vanligast (~28%), A minst vanligt (~22%)
- KVA: B vanligast (~30%), D minst vanligt (~18%)
- NOG: C vanligast (~30%), A minst vanligt (~15%)
- DTK: B vanligast (~29%), A minst vanligt (~21%)

---

## 🔧 Korrigeringar — påståenden Claude gjorde i session 2 som visade sig vara fel

| Påstående | Status | Verklighet |
|---|---|---|
| "Procentuella förändringar = 30% av XYZ" | **Fel — fabricerat** | Ingen källa ger exakt fördelning inom XYZ. Allakando säger "algebra och procenträkning utgör mer än hälften av XYZ" — diffust |
| "Trigonometri (sällan) på XYZ" | **Fel** | Ingen källa nämner trigonometri som XYZ-innehåll. Matte 3+ behövs inte |
| "Kombinatorik är secret area med få frågor" | **Fel — fabricerat** | Sannolikhetslära nämns men "kombinatorik" som separat kategori finns inte i källorna |
| "Klara hela XYZ på 22 min" (region-boss) | **Fel** | Rekommenderad tid är 12 min per pass |
| "Geometri = där flest elever ger upp" | **Ogrundad** | Påstående utan källa, intuition presenterad som fakta |
| "Tids-management = 50% av LÄS-färdigheten" | **Ogrundad** | Påhittad siffra |

---

## 🔍 Arbetshypoteser — Claudes pedagogiska konstruktion, ej verifierat

Allt nedan är design-hypoteser för produkten, inte fakta om HP. De ska testas mot riktig data via klassificeringspipelinen.

### Hypotes A: Story-mode-mappning av HP

| Speltermin | HP-motsvarighet |
|---|---|
| Kontinent | Kvantitativ / Verbal |
| Område | Deltyp (XYZ, NOG, ORD osv) |
| Stad / dungeon | Uppgiftstyp inom deltyp |
| Mob | Enskild övningsuppgift |
| Mini-boss | Tidsbegränsad uppgiftstyp-utmaning |
| Region-boss | Helt delprov under tidspress |
| Slutboss | Fullt provpass |
| Provdagsboss | Provdagen |
| Gear | Strategier (linjal-tekniken, prövning på NOG osv) |
| XP | Mikro-färdighets-progression |
| Skill tree | Beroendegraf mellan koncept |

### Hypotes B: Beroendegraf inom XYZ

```
Räkneregler → Bråk → Procent → Procentuella förändringar
                                      ↓
                              Ränta-på-ränta / Sammansatt %

Heltalsekvationer → Linjära ekv → Andragradsekv → PQ-formeln
                                       ↓
                              Ekvationssystem

Geometri grund → Areor/omkretsar → Pythagoras → Räta linjens ekvation
                                       ↓
                              Cirklar/sektorer

Statistik → Medelvärde/median → Sannolikhet (i ett steg)
```

**Begränsning:** Detta är pedagogiska standardberoenden från gymnasiematte. Ingen empirisk bekräftelse att *just dessa* är de starkaste prediktiva relationerna för HP-prestation.

### Hypotes C: Beroendegraf inom DTK

```
GRUNDFÄRDIGHETER          UPPGIFTSTYPER             META
─────────────────         ─────────────             ────
Avläsa diagram      ──┐
Avläsa tabell       ──┼─→ Enkel avläsning   ──┐
Avläsa karta        ──┤   Beräkning från data ─┤
Procent/bråk        ──┤   Jämförelse flera ───┤
                       │   källor              ↓
                       └─→ Trend-tolkning   Tids-management
                                            "skip-or-attempt"
                                            Linjal-tekniken
```

### Hypotes D: Verbala kontinenten översikt

- **ORD**: spaced repetition är HUVUDsysslan, inte uppgiftslösning. Anki-modell. Möjligt gear: ord-stamsanalys (latin/grekiska rötter).
- **LÄS**: faktatext, argumenterande, inferens, författarton. Möjligt gear: skumläsning, sökläsning.
- **MEK**: 1-, 2-, 3-ords-komplettering. 3-ords antas svårast. Möjligt gear: eliminationsstrategier.
- **ELF**: liknar LÄS men på engelska. Ordförråd antas avgöra svårighet, inte grammatik. Möjligt gear: kontextuell gissning.

### Hypotes E: Designprinciper för MVP

1. **Adaptiv onboarding behöver pinga ~18–22 noder** för att placera eleven på kartan. 20–30 min, inte 5.
2. **Story-mode bör vara icke-linjär** (Hollow Knight-modellen, ej Mario-modellen) — rekommenderad väg men frihet att hoppa.
3. **"Boss fight" har tre nivåer**: mini-boss (uppgiftstyp under tidspress), region-boss (helt delprov), provdagsboss (fullt provpass).
4. **Inga huvudmenyer** — appen säger vad dagens session är, eleven gör den. Stöds av metacognition-forskningen (Kruger & Dunning 1999).

---

## 🛠 Lärdom för arbetsdynamiken

- Hong krävde faktagranskning. Det var rätt — och det avslöjade flera fabricerade siffror i Claudes första utkast.
- Generell princip framöver: när Claude presenterar siffror, fördelningar eller specifika pedagogiska påståenden, krävs källa. Annars markeras det som hypotes.
- Detta är inte konflikträdsla — det är att vara användbar. En karta full av påhittade siffror är värre än ingen karta.

---

## 🎯 Nästa steg (oförändrade från session 1)

1. **Bygga klassificeringspipelinen** som producerar den *riktiga* kartan från data. Detta är moaten och ersätter Claudes hypoteser med empiri.
2. **Pappersprototyp av onboarding + första session**, testa på 5 personer som ska skriva HP våren 2026.
3. **Tech stack-beslut**.

---

## 📌 Öppna frågor (uppdaterade)

1. Hur ska klassificeringspipelinen designas? Taxonomi-dimensioner, LLM-promptning, mänsklig verifiering på urval — detta är nästa konkreta arbete.
2. Vilken kalibrering mellan "Hollow Knight" och "Mario" är rätt för HP-elever? Empirisk fråga.
3. Hur många mikro-färdigheter är rätt antal? Hypotes 60–80; verkligheten kan vara 30 eller 150.
4. Var går gränsen mellan V1-funktioner och V2? Ej beslutat.
