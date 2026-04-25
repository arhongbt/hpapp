# HP-app — Sessionssammanfattning

**Datum:** 2026-04-25
**Sammanhang:** Tidig produktvisionering. Hong utforskar att bygga en svensk högskoleprov-app som konkurrent till HPGuiden, Eddler, HP-appen, AllaRätt.nu m.fl.
**Status:** Kärnvision formulerad, MVP-scope ännu ej låst, inget byggt.

---

## Marknadslandskap (kartlagt under sessionen)

- **HPGuiden** (sedan 2004): 280k+ användare, bred VIP-utbildning, coach-modell. Etablerad auktoritet.
- **HP-appen**: 13 000 övningar, real-time normering, mobile-first, modernt UX. Närmast en seriös teknisk konkurrent.
- **Eddler**: drivs av Eddler AB (sedan 2010). HP är *en kurs* i ett bredare matte/fysik/programmering-ekosystem. Deras SEO-fördel kommer från domain authority över hela matte-nischen — de slår HPGuiden för att Google ser dem som auktoritära på matematik bredare, inte för att deras HP-content är bättre.
- **AllaRätt.nu**: gratis, ful, stagnerad, 18k uppgifter. No-frills.
- **Allakando, Läxhjälp.nu**: privatlärar-vinklat.

**Insikt:** Att försöka slå Eddler head-on på "högskoleprovet matte" är att slåss mot deras 15 år av domänauktoritet — inte mot deras content. SEO som primär strategi är inte vägen.

---

## Kärnvision (Hongs formulering, utvecklad genom sessionen)

> **"Vi ska vara den läraren."**

Hong observerade att svenska skolresultat varierar inte främst pga system, läroplan eller resurser — utan pga lärarkvalitet. Forskning bekräftar detta (se "Vetenskaplig grund" nedan). Existerande HP-appar är *uppgiftsbibliotek med polish*. De är inte lärare. Hypotesen: en app designad arkitektoniskt för att bete sig som den bästa privatläraren slår en app som är ett uppgiftsbibliotek med polish.

**Utvidgad formulering vid sessionens slut:**
> *HP-förberedelse fungerar idag som en lärobok som råkar vara digital — vi gör om den till en story-mode där eleven inte vet att hen pluggar förrän hen plötsligt klarar bossen.*

---

## Beslutade designprinciper

### 1. Story-mode-struktur (game design möter pedagogik)

HP är pedagogiskt *unikt lämpligt* för en story-mode-modell pga sin fasta struktur. Hela "spelvärlden" kan kartläggas på förhand.

- **Världen** = HP som helhet (slutbossen är provdagen, 2.0 är true ending)
- **Områden** = de åtta deltyperna (XYZ är skogen, NOG är grottan, DTK är slottet)
- **Sub-bossar** = specifika uppgiftstyper (procentuella förändringar är minibossen i XYZ-skogen)
- **Gear** = strategier och mentala verktyg (linjal-tekniken på DTK är ett bokstavligt "gear-pickup")
- **XP** = ackumulerade mikro-färdigheter
- **Skill tree** = beroendegrafen mellan koncept

Spelet *är* matten — inte runt matten. Bra spelmekanismer = spelandet är samma sak som lärandet (Mario-principen). Dåliga = spelandet är belöning *för* lärandet (Duolingo-kritiken).

### 2. Adaptiv onboarding som första-timme-upplevelse

Inte ett test — ett intro-level. 15–20 utvalda kalibreringsuppgifter som täcker kompetensgrafen. Under huven: diagnostik. För eleven: introduktion. Outputen är en personlig roadmap: "din väg till 1.5 är ungefär 8 veckor, här är planen".

### 3. Inga huvudmenyer

Eleven öppnar appen → skärmen säger direkt vad dagens session är: "Idag tränar vi NOG med två villkor. Du missade tre stycken igår. 12 min." Klart. Ingen valbörda.

**Pedagogisk grund:** *metacognition gap* (Kruger & Dunning 1999) — dåliga elever är systematiskt sämre på att bedöma sin egen förmåga. Den elev som mest behöver veta vad hen ska göra är minst kapabel att lista ut det. Appen fattar beslutet åt eleven, baserat på data eleven inte ser.

### 4. Synliga boss fights var 7–10 dag

Mini-provdel under tidspress på det eleven tränat på. Inte rapport-grafer. *Konkret upplevelse* av att bossen som dödade dig förra veckan dör i ett slag.

### 5. AI-tutor som "DEN bästa läraren" — inte "förklara uppgiften"-feature

Designad för att maximera Hatties tre dimensioner (clarity, feedback, relation). Konkreta förmågor:
- Detektera förvirring innan användaren säger något (mönster i fel-svar och paus-tider, proaktivt "vänta, du missförstår grundkonceptet")
- Förklara samma sak tre olika sätt (visuellt → algebraiskt → analogi → konkret)
- Veta när eleven är trött och säga "vi tar det imorgon" (mot streak-logik, för pedagogisk effekt)
- Vara ärlig om svagheter, inte gömma dem bakom uppmuntrande grafik
- Bygga upp mental modell av varje elev över sessioner (LLM-edge ingen svensk konkurrent har)

### 6. Mikro-färdighetsklassificering som moat

Klassificera varenda HP-uppgift på (a) deltyp, (b) underliggande mikro-färdighet (~60–80 stycken), (c) svårighet, (d) lösningstid. Detta är Hongs unika dataset — kan göras på några veckor med LLM-pipeline. Eddler/HPGuiden har gjort detta manuellt under 15 år; LLM-klassificering kan ikapphämta det utan licensiering.

### 7. Före/efter-jämförelse på samma uppgiftstyp

"Vecka 1: fel, 3:20. Idag: rätt, 1:40." Den enskilt mest underanvända mekaniken i edtech enligt vår analys. Gör abstrakt progress till konkret minneskänsla.

### 8. Studiegrupper byggda på cooperative learning-forskning (V2-tema, ej V1)

Inte "se varandras streaks" (det är observation, inte ömsesidigt beroende). Riktiga villkor enligt Johnson & Johnson:
- **Positivt ömsesidigt beroende**: gemensam pott av poäng som låses upp när alla tre nått dagens mål; eller rolltilldelning där "Jin förklarar NOG idag, du förklarar ORD imorgon".
- **Individuell ansvarighet**: varje person måste mätbart bidra. Annars *social loafing*.

---

## Vetenskaplig grund (allt jag hämtade fram under sessionen)

### Lärar-effekt (Hattie, 800+ studier)
- *Collective teacher efficacy*: effektstorlek 1.39 (enormt)
- *Teacher clarity*: 0.85
- *Feedback*: 0.70
- *Reciprocal teaching*: 0.74
- *Teacher-student relationships*: 0.62
- (Referens: klasstorlek 0.21, hemarbete 0.29, tekniska hjälpmedel utan pedagogik nära noll)

### Flow-state designvillkor (Csikszentmihalyi)
Tre direkt designbara i app:
- Tydligt mål per session (inte "plugga matte" — "bemästra procentuella förändringar")
- Omedelbar och kalibrerad feedback (inte bara rätt/fel)
- Utmaning som matchar förmåga (Vygotskijs ZPD; sweetspot 75–85% lösbarhet)

### Cognitive science-principer (välbelagda, ska byggas in)
- Spaced repetition (intervall 1d, 3d, 7d, 14d)
- Retrieval practice
- Interleaving (20–40% förbättrad retention över blocked practice i meta-analyser)
- Elaboration
- Dual coding

### Game design-principer som fungerar pedagogiskt
- Progressiv disclosure (Mario-design, studeras på pedagogikinstitutioner)
- Boss fights som integrationsövning = interleaved practice
- Visible mastery (skill trees, Khan Academy)
- Skill-matched difficulty (flow-fönstret)

### Game design-principer som *inte* fungerar (cargo-cult gamification)
- Punkt-system bara för engagemang → *gamification overjustification effect*
- Random rewards / loot boxes (etiska frågor)
- Streaks utan förståelse (30 sekunder/dag bara för att inte tappa streaken)

### Cooperative learning (Johnson & Johnson)
Gruppstudier slår individuell studie konsekvent men *bara under fem specifika villkor*. De två viktigaste för app-design: positivt ömsesidigt beroende, individuell ansvarighet.

### Metacognition gap (Kruger & Dunning 1999)
Dåliga elever systematiskt sämre på självbedömning. Argumenterar för att appen ska fatta beslut åt eleven där elevens egen bedömning skulle vara opålitlig.

---

## Avskrivna idéer / korrigeringar

- **"Metoder från åtta toppstuderande länder"** — Claude pushade tillbaka. Det finns ingen syntetisk "vetenskapligt bevisad metod från Kina+USA+Japan+Egypten+osv". Östasiatisk PISA-prestation drivs av kulturella/socioekonomiska faktorer som inte överförs. Finland och Sydkorea har motsatta modeller och båda fungerar. Det som är universellt är *cognitive science* (spaced repetition etc), inte nationell pedagogik. Hong accepterade pushbacken.
- **SEO som primär strategi** — avskriven. Eddlers fördel är 15 års domänauktoritet; kan inte slås head-on. SEO blir acquisition (long-tail som "DTK strategier", "ord på högskoleprovet 2026"), produkten är retention.
- **"Bara arcade-feed för TikTok-generation"** — för smal. Provdagen är 4 timmar; om appen bara tränar 3-min-format reproducerar den exakt det koncentrationsproblem målgruppen har. Lösning: snack-läge (daglig vana) *och* deep-work-läge (fullt provblock med tid).

---

## Hongs perspektiv som Claude underskattat (korrigerade i realtid)

- Hong har tid (är föräldraledig). Claude drog tids/scope-kortet flera gånger; Hong pushade tillbaka och hade rätt. Tonen ska vara sparring, inte bromskloss.
- Hong vill bygga något revolutionärt; konkurrenter ska inte stoppa visionen från att tas på allvar.
- När Hong presenterar en teori är Claudes uppgift att *gräva i den med fakta och vetenskap* — inte lista risker som redan övervägts.
- Hongs "vara läraren"-formulering är inte scope-creep. Det är en sammanhängande pedagogisk filosofi som råkar peka mot flera funktioner. Alla funktioner är uttryck för samma kärnprincip.

---

## Öppna frågor / ej beslutat

1. **Vilken funktion är "hjärtat" för V1?** Hong svarade i riktning av story-mode + roadmap-genererad onboarding, men slutligt MVP-scope ej låst.
2. **Världskartan / kompetensgrafen** — föreslagen som nästa konkret arbete. En eftermiddags arbete för att kartlägga: hur ser beroendegrafen mellan HP:s deltyper, mikrofärdigheter och bossar faktiskt ut?
3. **Tech stack** — ej diskuterat ännu.
4. **Affärsmodell** — freemium antagligen, men inte beslutat. Ska AI-tutor vara premium-feature eller ingå?
5. **Releasedatum** — Hong är föräldraledig, "extremt mycket tid på kort period". Inget specifikt datum bestämt.
6. **Klassificeringspipeline** — vilka mikro-färdigheter? 60–80 stycken? Lista att skapa.

---

## Föreslagna nästa steg (i prioritetsordning)

1. **Bygga världskartan**: kompetensgrafen med deltyper, mikro-färdigheter, beroenden, bossar. Fundament för allt annat.
2. **Klassificeringspipeline**: ladda ner alla gamla prov från studera.nu, LLM-pipeline för klassificering på alla dimensioner. Är moaten.
3. **Pappersprototyp av onboarding + första session**: testa på 5 personer som ska skriva HP våren 2026. Inte fråga "är detta bra" — fråga "när skulle du använda detta, hur länge, vad skulle få dig att sluta".
4. **Bestäm tech stack och bygg MVP**.

---

## Tonregister-anteckning för framtida sessioner

Hong vill ha sparring-partner, inte realism-coach. Pusha tillbaka *när det finns substans att pusha tillbaka på* (som Claude gjorde med "metoder från åtta länder" — det blev accepterat). Pusha *inte* tillbaka på Hongs bedömning av sin egen tid, motivation eller risk-tolerans. Den separationen är viktig och Hong gjorde rätt i att kalla ut Claude på det.
