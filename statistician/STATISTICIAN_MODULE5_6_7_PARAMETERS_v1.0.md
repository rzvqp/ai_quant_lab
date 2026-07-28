# STATISTICIAN — PARAMETRII MODULELOR 5, 6 ȘI 7 (Mandat 3.21)

**Document ID:** STAT-MODULE-5-6-7-PARAMETERS-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician

**Verificare de sursă:** confirmat direct în `EDGE_DISCOVERY_REGISTRY_v1.md`/`EDGE_DISCOVERY_ROADMAP.md` — coloana `volume` e "of unconfirmed provenance (likely OTC tick-count proxy, not verified exchange volume)"; E022/E031 sunt în Tier 3 „testabil azi, dar orice Verdict Final trebuie să menționeze proxy-ul"; E020 e ținut integral pe motivul ăsta. Confirmat `edge_research/_profile.py:11-13` — `HORIZONS=(1,3,5,10,20,50)`, `ATR_THRESHOLDS=(0.25,0.5,1.0,1.5,2.0)`, `REACTION_THRESHOLD=1.0` (disclosed, not tuned). Confirmat `code/mtf.py:38` — exact patru sesiuni, `asia/london/ny/late`, nicio a cincea.

---

## PROBLEMA 1 — filtrul de volum: ELIMINAT din primitiva de bază

**Decizie: se elimină, nu se include cu proveniență declarată.**

Motiv: diferența dintre E022/E031 (ipoteze STANDALONE, fiecare cu propriul caveat individual, deja acceptat de lab pentru testare) și un filtru de volum bagat în **Order Block ca primitivă FUNDAMENTALĂ, persistentă** (Modulul 5) e reală. E022/E031 poartă caveatul o singură dată, la nivelul propriei ipoteze. Un filtru de volum în primitiva de bază ar fi MOȘTENIT TĂCUT de orice ipoteză viitoare care folosește Order Block — riscul de proveniență s-ar propaga fără ca fiecare consumator să-l re-declare, exact opusul disciplinei deja aplicate (E019-E023/E031 fiecare cu propriul caveat explicit, niciodată implicit).

Definiția geometrică de bază a Order Block (corp înghițit de bara opusă următoare, cf. Mandatul 3.20) e deja COMPLETĂ fără volum — eliminarea nu rupe primitivă, doar o păstrează curată de o dependență de date pe care lab-ul o tratează cu precauție peste tot în altă parte. Dacă o variantă AUGMENTATĂ cu volum e dorită vreodată pentru o ipoteză specifică, aceea e o adăugire separată, cu propriul caveat explicit (ca E022/E031), nu o componentă tacită a primitivei fundamentale. **Nu derivez o fereastră SMA, pentru că nu inclu filtrul.**

## PROBLEMA 2 — pragul de expansiune: REUTILIZAT din E010, nu 2,5 și nu REACTION_THRESHOLD

**2,5 respins — nu are nicio derivare.** **REACTION_THRESHOLD=1,0 respins ca înlocuitor direct — măsoară altceva** (magnitudinea reacției pe orizont FORWARD, cf. `movement_profile`, nu mărimea unei singure bare).

**Decizie: se reutilizează verbatim criteriul de „bară de deplasare" deja înghețat la E010** (V0 deja frozen, folosit deja de mai multe ori ca precedent pentru mecanica Order Block/Breaker): `range[i] = high[i]-low[i] > 1,5 × ATR14[i-1]` (ATR-ul bării PRECEDENTE, ca deplasarea proprie a barei să nu-și infleze propriul reper) **ȘI** corp direcțional puternic, `|close-open| ≥ 0,5 × range[i]`. Aceeași categorie conceptuală exactă („o bară semnalează forță decisivă de piață") — nu invenție, reutilizare a unei decizii deja luate, deja folosită ca sursă pentru criteriul de inversare Breaker (E010/E012). Consecvent: dacă Breaker-ul Order Block-ului reutilizează deja E010, expansiunea care FORMEAZĂ Order Block-ul trebuie să reutilizeze aceeași sursă, nu una nouă.

## PROBLEMA 3 — compresia: fereastră RULANTĂ derivată (460 bare), strict cauzală

**Confirmat riscul de lookahead — percentila pe tot istoricul ar fi exact asta.** Fereastră rulantă, strict trailing (bara curentă + cele 459 anterioare, NICIODATĂ bare viitoare) — aceeași disciplină cauzală ca orice indicator deja folosit în cod (ATR14, EMA20 etc., niciodată centrate).

**Lungimea, derivată, nu aleasă:** **460 bare** — media empirică de săptămână, deja derivată direct din date la Mandatele 3.18/3.19 (regula de gol-de-weekend pe `derive_week_index`), reutilizată aici verbatim, nu re-calculată. Motivul alegerii tocmai a acestei surse (dintre orizonturile deja existente — 1,3,5,10,20,50,480,960): regimurile de volatilitate/compresie se discută la scară de zile-săptămâni, nu de ore — o fereastră de „o săptămână" e suficient de lungă pentru o percentilă stabilă, suficient de scurtă ca să rămână locală regimului curent (nu amestecă ere de piață complet diferite, cum ar face tot istoricul). **Aceeași derivare acoperă și pragul de volatilitate/extindere de la S4/S8** (Mandatul 3.19, unde măsura fusese definită dar pragul lăsat deschis) — o singură fereastră, două utilizări.

**Nivelul de percentilă (10) rămâne cel din specificație** — nu-l re-derivez, e tratat ca prag implicit declarat (aceeași convenție ca `ATR_THRESHOLDS`/`REACTION_THRESHOLD`, „disclosed, not tuned"). Ce trebuia rezolvat era FEREASTRA (sursa de lookahead), nu nivelul.

## PROBLEMA 4 — sesiunile: numele reale, nicio a cincea sesiune

Confirmat: patru sesiuni, exact, `code/mtf.py:38` — `asia (hh<8)`, `london (hh<13)`, `ny (hh<21)`, `late (implicit)`. **„Cash" nu există — nu se introduce.** Pentru un instrument XAUUSD tranzacționat aproape 24/5, distincția cash-vs-futures (relevantă pentru acțiuni/indici cu ore de piață închise) nu se mapează natural — cel mai apropiat echivalent deja stabilit e pur și simplu `london` și `ny`. **Se folosesc exact aceste două etichete, fără redenumire, fără sesiune nouă implicită.**

## PROBLEMA 5 — Modulul 7: LOCATOR GENERIC parametrizabil, NU o ipoteză

**Decizie: Modulul 7 e un locator generic de intersecții, care NU fixează nicio combinație anume.**

Exemplul din specificație (OB validat + bazin extern activ + sesiuni london/ny) e o ipoteză completă de tranzacționare — intrare (next-open), condiție (atingere OB), fereastră (sesiuni) — și, tratată ca ipoteză, îi lipsesc toate cele cinci criterii pe care le-am impus celor 40 de V0 și pe care le-am aplicat la LM-001: populație, orizont, criteriu de succes, familie de corecție. Nu o formalizez ca ipoteză acum — asta ar cere pre-înregistrare completă, neautorizată aici.

**În schimb:** Modulul 7 se implementează ca funcție generică — primește un SET de condiții primitive (ex. „OB validat", „bazin extern activ", „sesiune ∈ {X}") ca PARAMETRI, verifică dacă toate se întâlnesc la aceeași bară/fereastră, și returnează evenimentele calificate — analog `count_bpr` (D-BPR), care e parametrizat pe toleranță, nu hardcodat pe o singură valoare. Combinația SPECIFICĂ din exemplu (OB+bazin+london/ny) rămâne un EXEMPLU DE UTILIZARE posibil, nu implementarea implicită. **Dacă acea combinație specifică se dorește testată vreodată ca ipoteză proprie, trece prin pre-înregistrare completă separată** (populație/orizont/succes/familie), ca oricare din cele 20 SMC_S*, nu se strecoară ca „primitivă".

## ÎNTREBAREA DE FOND — ancorarea: parțială, verificată pe fiecare piesă, nu răspuns unic

Am verificat fiecare din primitivele Modulelor 5/6/7 individual, față de cele 20 familii SMC_S*, nu am dat un răspuns global:

**Ancorate deja, la familii blocate concrete (Mandatul 3.19):** `Trend`/MTF-Trend (SMC_S9/S20), `Volatility`/`Expansion` (SMC_S4/S8, măsura Parkinson + acum pragul de fereastră din Problema 3), `Session`-OHLC (SMC_S5/S6/S19). Nu sunt definiții abstracte — au un consumator concret deja numit.

**Deja definite prin reutilizare, NU definiții noi abstracte:** din cele patru primitive numite ale Modulului 5 (Order Block, Breaker, Mitigation, Rejection), **trei sunt deja complete prin reutilizare a mecanicilor deja ratificate**, nu invenții noi: `Breaker` = criteriul de inversare E010/E012 deja înghețat în `order_block_void.py`; `Mitigation` = exact evenimentul (a) din fereastra de valabilitate OB (atingere de fitil = consumare D7), deja specificat la Mandatul 3.20, are nevoie doar de un NUME formal, nu de o derivare nouă; `Rejection` = mecanica D6 wick-sweep-reject deja folosită peste tot (LM-001, PDH/PDL) — la fel, nume nu derivare. **Rămâne genuin nou doar `Order Block` însuși** — zona (Mandatul 3.20), și acum filtrul de volum (eliminat) și pragul de expansiune (Problema 2, reutilizat din E010).

**Rămân genuin neancorate, definiție în abstract, risc declarat:** `Compression` (Modulul 6) — nicio familie SMC_S* n-o cere, e cea mai puțin constrânsă dintre toate (deși fereastra ei de percentilă e acum derivată, Problema 3, ceea ce reduce, nu elimină, riscul de „zece variante plauzibile"). **Criteriul de FORMARE al Order Block** (care lumânare devine candidat OB, dincolo de zonă) rămâne de asemenea deschis, cf. Mandatul 3.20 — încă neancorat.

**Concluzie:** nu accept definirea în abstract fără rezerve pentru TOATE cele șapte primitive — majoritatea (Trend, Volatility, Expansion, Session, Breaker, Mitigation, Rejection) au fie un consumator concret, fie o reutilizare directă a unei decizii deja luate. Rămân cu adevărat „în abstract, risc declarat" doar **`Compression`** și **criteriul de formare OB** — pentru acestea două, accept definirea abstractă acum (poziția CTO — biblioteca completă înainte de simulare — e defensabilă), dar consemnez explicit riscul, nu-l ascund.

---

**LM-001 rămâne blocat prin decizia CTO** (biblioteca completă înainte de orice simulare) — nu prin vreo problemă statistică; oracolul rămâne ratificat, execuția rămâne asignată VE, doar secvențierea se amână. **Holdout SEALED, neatins.**

**VE implementează după publicare. Manifestul incrementat la v2.6.1 (commit `2fb948f`, `alpha-automation-v1`).**
