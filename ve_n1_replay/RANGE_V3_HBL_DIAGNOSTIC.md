# RANGE V3 — Diagnostic construction-only pe `RANGE_HUMAN_LABEL_BATCH_01`

**Versiune artefact:** `ve_n1_replay 0.4.0` · **Detector:** `RangeSemanticProducerV3` (`range-semantic-v3.0`)
**Sursă normativă:** Statistician `STAT-RANGE-SEMANTIC-SPEC-V3-v1.0` @`bf9f780`, manifest v2.7.84 @`db098ed`,
fingerprint `cddaab381f0132eac025e9fcad3454d54fca78dc1abab6bc8b3cea05e5951233` (verificat exact din manifest).
**Lot etichete:** `RANGE_HUMAN_LABEL_BATCH_01_CEO_ASSISTED_RESULTS` — proveniență **`CEO_ASSISTED`**,
**construction-only PERMANENT**.

## 0. Ce ESTE și ce NU e acest document

- **ESTE** un diagnostic de construcție: rulează detectorul 0.4.0 pe **analoage sintetice** ale celor 24
  ferestre, construite din **secvența calitativă de faze declarată explicit** în eticheta CEO_ASSISTED, și
  compară structural comportamentul cu baseline-ul propriu al Statisticianului pe `ve_n1_replay 0.3.1`.
- **NU** e o validare blind, NU e o validare independentă, NU e OOS, NU calculează sau țintește o ocupație.
- **NU** folosește ferestrele reale — intervalele lor exacte (bare/timestamp-uri UTC) sunt **deliberat
  nepublicate**, ținute în afara oricărui checkout git (`config/split_manifest.json` @`db098ed`,
  secțiunea `human_label_batch_01_v2_7_83`: *"intervale exacte + hash OHLC per fereastră — NEPUBLICATE...
  în afara oricărui checkout git, fiindcă axa temporală dezvăluie intervalele"*). VE nu poate deci re-reda
  byte-identic cele 24 ferestre reale.
- **Excepția**: `HBL-20` e reprodus **numeric exact** (nu doar calitativ) dintr-un fixture sintetic construit
  direct din verificarea proprie, deja publicată, a Statisticianului (bara 52/56/63) — vezi §3.
- Aceste etichete nu au fost și nu vor fi folosite pentru alegerea parametrilor K/N/w_atr și apoi validarea
  acelorași parametri pe același lot (regula CEO, respectată).

## 1. Baseline citat VERBATIM — `ve_n1_replay 0.3.1` (Statistician, `HUMAN_LABEL_BATCH_01_SEGMENT_TABLE.md` @`bf9f780`)

> Detector: `ve_n1_replay 0.3.1`, config pinuit `w_atr = 0,30` / `s_max = 0,60`, fingerprint `432170ff…`,
> 480 bare de încălzire înainte de fiecare fereastră. Rulat exclusiv pentru DIAGNOSTIC.
>
> Segmentele CEO nu au timestamp-uri, deci potrivirea e la nivel de **fereastră** — „detectorul a produs
> vreodată starea X aici" — nu la nivel de bară. „Început prea târziu" și „închis prea devreme" NU se pot
> măsura fără granițe de segment; sunt raportate ca element deschis, nu estimate.
>
> ```
> 66 segmente etichetate · 37 OMISE (56%) · 18 parțiale · restul tranziții/sweep-uri fără stare
> ```

**Eșantion reprezentativ, 7 din 66 rânduri** (NU tabelul complet — tabelul integral, cu toate cele 66 de
rânduri, rămâne NEMODIFICAT la sursă, în `statistician/HUMAN_LABEL_BATCH_01_SEGMENT_TABLE.md` @`bf9f780`;
citește acolo pentru fiecare rând):

| HBL_ID | segment | eticheta CEO | ieșire detector 0.3.1 (bare) | potrivire | defect semantic |
|---|---|---|---|---|---|
| `HBL-01` | S1 | `RANGE` | RANGE 0 · CANAL 0 · INDISP 89/96 | NU | SEGMENT OMIS — zero bare RANGE_STATE |
| `HBL-02` | S1 | `CHANNEL_DOWN` | RANGE 0 · CANAL 0 · INDISP 73/96 | NU | SEGMENT OMIS — nici canalul nu se clasifică |
| `HBL-05` | S3 | `BREAKOUT_DOWN` | ^ | - | 36 ruperi ACCEPTATE într-o fereastră unde CEO vede UNA |
| `HBL-15` | S2 | `SWEEP_FAILED_BREAKOUT_UP` | ^ | - | eveniment emis de 4 ori, dar NU există stare de sweep |
| `HBL-20` | S1 | `RANGE_ACUMULARE` | RANGE 0 · CANAL 8 · INDISP 62/96 | NU | SEGMENT OMIS — zero bare RANGE_STATE |
| `HBL-20` | S2 | `SWEEP_DOWN` | ^ | - | eveniment emis o dată, dar NU există stare de sweep |
| `HBL-24` | S1 | `RANGE` | RANGE 12 · CANAL 73 · INDISP 322/480 | partial | doar 12 bare RANGE_STATE în toată fereastra |

Acesta e „ÎNAINTE" — motivul complet pentru care mandatul 0.4.0 există: absența segmentării longitudinale
(o singură etichetă globală per fereastră, niciodată o secvență), acceptarea care distruge episodul (36-38
„ruperi" numărate ca evenimente disjuncte în ferestre unde CEO vede O SINGURĂ tranziție), și sweep emis ca
eveniment fără nicio stare care să-l consume.

## 2. Metodologie — analoage sintetice (NU ferestrele reale)

Pentru fiecare fereastră HBL cu o secvență calitativă declarată explicit în etichetă (ex. `HBL-05`:
`CHANNEL_UP → RANGE → BREAKOUT_DOWN → CHANNEL_UP`), am construit un fixture sintetic compus din faze
generate programatic (`range_phase`/`channel_phase`/`breakout_phase`/`sweep_phase`), alocând bare
proporțional din totalul REAL al ferestrei (96/288/480, confirmat direct din coloana „ieșire detector" a
tabelului 0.3.1 de mai sus) împărțit egal între fazele etichetate.

**Ferestre EXCLUSE din sinteza calitativă** (2/24):
- `HBL-03` — eticheta CEO însăși declară `AMBIGUOUS/MULTI-REGIME` **fără o secvență dominantă** de raportat;
  nu s-a inventat o structură pe care CEO nu a afirmat-o.
- `HBL-20` — tratat SEPARAT, cu reproducere **numerică exactă** (nu analog calitativ) — vezi §3.

**Configurație folosită pt. acest diagnostic** — explicit `UNRATIFICATĂ/CONSTRUCTION_ONLY`, aleasă pentru
reachability, NU calibrare (același principiu ca în suita decisivă): `K=4, N=8, w_atr=1.5, d_min_bars=24,
n_touch=2, swing_k=2`. Nu s-a țintit nicio ocupație; parametrii NU au fost aleși prin încercare-eroare pe
verdictele de mai jos.

**Limitări cunoscute, declarate explicit** (nu ascunse):
1. **Fără timestamp-uri CEO** ⇒ „delta start"/„delta end" NU sunt calculabile — **aceeași limitare pe care
   Statisticianul însuși o declară** pentru diagnosticul 0.3.1 (§1, citat mai sus: „potrivirea e la nivel de
   fereastră... nu se pot măsura fără granițe de segment"). Coloanele sunt marcate `N/A` uniform.
2. **Bugetul de bare per fază**: ferestrele de 96 bare împărțite în 3-4 faze etichetate lasă ~24-32 bare per
   fază — aproape de `d_min_bars=24`, insuficient pentru ca unele faze să atingă pragul de durată înainte ca
   fereastra sintetică să se termine. Efectul observat: unele faze RANGE/CHANNEL scurte nu apucă să se
   confirme structural — un artefact al ALOCĂRII de bare a fixture-ului, nu al semanticii detectorului
   (verificat separat, izolat de zgomotul fixture-ului, în suita decisivă `test_range_semantic_v3.py`).
3. **Sensibilitate a generatorului sintetic la aliasing** — un pattern periodic (triunghi 8-bare) poate
   produce o pantă OLS trailing ne-nulă în funcție de alinierea fazei față de `d_min_bars` (clasă de
   capcană deja documentată și rezolvată separat, prin teste white-box, pentru logica de DECIZIE însăși).
4. Rezultatul „potrivire" de mai jos e deci un semnal **calitativ/structural** (a apărut vreodată clasa
   respectivă în istoricul segmentelor ferestrei?), NU o măsură de acuratețe bar-cu-bar.

**Dovada structurală primară** (motivul real al acestui mandat) nu e tabelul de mai jos — e faptul
verificabil direct: **0 din cele 22 ferestre sintetizate au istoric complet gol** (`n_history == 0`,
echivalentul sintetic al „RANGE 0 · CANAL 0" din 0.3.1). La 0.3.1, majoritatea covârșitoare a ferestrelor
arătau exact acest tipar (omitere completă). La 0.4.0, fiecare fereastră sintetizată produce cel puțin UN
segment cu o clasificare reală (RANGE_ESTABLISHED, CHANNEL_UP/DOWN, sau o rupere confirmată).

## 3. `HBL-20` — reproducere NUMERICĂ EXACTĂ (nu analog calitativ)

Fixture sintetic construit direct din verificarea PROPRIE, deja publicată, a Statisticianului — ancoră
exactă 3333,06 / 3346,10, breach bara 52 (low 3330,25), reintrare bara 56 (close 3334,94), markup bara 63
(close 3346,99). Verificat bar-exact în `tests/test_range_semantic_v3.py::test_hbl20_exact_reproduction_sweep_confirms_at_reentry_not_breach`:

| Bară | Eveniment 0.4.0 | `confirm_ts` | Comentariu |
|---|---|---|---|
| 52 | breach deschide `BREACH_PENDING` (pe LOW, nu pe close) | — | „informația 'e sweep' nu există încă" (spec, citat) |
| 53–55 | rămâne AMBIGUU (`TRANSITION`) | — | nici sweep, nici breakout — exact ca la spec |
| **56** | **`LIQUIDITY_SWEEP_DOWN` CONFIRMAT** | **bara 56** | NU bara 52 — regula cauzală S3 verificată exact |
| 63 | breach deschide pe SUS (markup) — NU confirmă singur breakout | — | o singură închidere nu ajunge; necesită N consecutive |
| >63 | `BREAKOUT_ACCEPTANCE_UP` eventual confirmat | — | expansiunea se rezolvă STRICT după bara 63 |

Comparativ, baseline-ul 0.3.1 pe `HBL-20` (§1): `RANGE 0 · CANAL 8 · INDISP 62/96` — zero bare RANGE_STATE,
sweep emis o dată fără nicio stare care să-l consume, segment OMIS. 0.4.0 reproduce bar-exact secvența
cauzală completă pe care 0.3.1 nu putea nici măcar să o reprezinte.

## 4. Tabel complet — analoage sintetice (22/24 ferestre; `HBL-03`/`HBL-20` excluse, vezi §2/§3)

`potrivire`: DA = toate clasele din eticheta CEO au apărut în istoricul segmentelor ferestrei sintetice ·
PARTIAL = unele au apărut · NU = niciuna · start/end delta = N/A (fără timestamp-uri CEO, §2.1).

| HBL_ID | segment(e) CEO | segment(e) detector 0.4.0 | Δstart | Δend | potrivire | tranziție omisă | motiv |
|---|---|---|---|---|---|---|---|
| `HBL-01` | RANGE (breakout DOWN/SWEEP) | 1 segment: ESTABLISHED→SWEEP_DOWN→BREAKOUT_DOWN | N/A | N/A | **DA** | — | secvență completă reprodusă |
| `HBL-02` | CHANNEL_DOWN | 6 segmente, 5 BREAKOUT_ACCEPTANCE_DOWN, 0 CHANNEL_DOWN | N/A | N/A | NU | CHANNEL_DOWN | trend puternic clasificat ca rupturi succesive, nu ca stare de canal — a se vedea §2.2/2.3 |
| `HBL-03` | AMBIGUOUS (fără secvență) | — | — | — | NESINTETIZAT | — | CEO însuși declină o clasă dominantă |
| `HBL-04` | RANGE (breakout DOWN) | 1 segment: ESTABLISHED→BREAKOUT_DOWN | N/A | N/A | **DA** | — | secvență completă reprodusă |
| `HBL-05` | CHANNEL_UP→RANGE→BREAKOUT_DOWN→CHANNEL_UP | 20 segmente: 5 CHANNEL, 15 rupturi, 0 ESTABLISHED | N/A | N/A | PARTIAL | RANGE | faza RANGE (120 bare alocate) nu s-a confirmat — buget de bare/aliasing, §2.2 |
| `HBL-06` | RANGE succesive→CHANNEL_UP | 21 segmente, 12 CHANNEL, 0 ESTABLISHED | N/A | N/A | PARTIAL | RANGE | idem |
| `HBL-07` | RANGE (breakout DOWN) | 2 segmente, 2 CHANNEL_DOWN, 0 ESTABLISHED | N/A | N/A | NU | RANGE | fază unică RANGE (48 bare) a aliasat spre canal |
| `HBL-08` | RANGE (breakout DOWN) | 2 segmente, 2 CHANNEL_DOWN, 0 ESTABLISHED | N/A | N/A | NU | RANGE | idem HBL-07 |
| `HBL-09` | RANGE→CHANNEL_UP→RANGE | 13 segmente, 7 CHANNEL, 0 ESTABLISHED | N/A | N/A | PARTIAL | RANGE | fazele RANGE (96 bare/fază) nu s-au confirmat |
| `HBL-10` | RANGE→CHANNEL_UP | 14 segmente, 5 CHANNEL, 0 ESTABLISHED | N/A | N/A | PARTIAL | RANGE | idem |
| `HBL-11` | CHANNEL_UP→CHANNEL_DOWN→BREAKOUT_UP→RANGE | 19 segmente, 5 CHANNEL (ambele sensuri), 14 rupturi | N/A | N/A | PARTIAL | RANGE | canal+breakout reproduse, faza finală RANGE nu |
| `HBL-12` | CHANNEL_UP→RANGE→CHANNEL_DOWN | 20 segmente, 1 ESTABLISHED, 0 CHANNEL | N/A | N/A | PARTIAL | CHANNEL_UP, CHANNEL_DOWN | RANGE reprodus, fazele de canal (160 bare fiecare) dominate de rupturi frecvente |
| `HBL-13` | CHANNEL_UP | 6 segmente, 6 BREAKOUT_ACCEPTANCE_UP, 0 CHANNEL | N/A | N/A | NU | CHANNEL_UP | trend puternic clasificat ca rupturi succesive |
| `HBL-14` | CHANNEL_UP→CHANNEL_DOWN→RANGE | 5 segmente, 0 ESTABLISHED, 0 CHANNEL | N/A | N/A | NU | toate 3 | 96 bare/3 faze = 32 bare/fază, sub bugetul necesar (§2.2) |
| `HBL-15` | RANGE→SWEEP/FAILED_BREAKOUT_UP→BREAKOUT_DOWN→CHANNEL_DOWN | 6 segmente: 1 ESTABLISHED, sweep UP, 1 CHANNEL_DOWN, rupturi DOWN | N/A | N/A | **DA** | — | toate clasele etichetate au apărut |
| `HBL-16` | RANGE→BREAKOUT_DOWN→CHANNEL_DOWN→RANGE | 8 segmente: 1 ESTABLISHED, 2 CHANNEL_DOWN, rupturi | N/A | N/A | **DA** | — | toate clasele etichetate au apărut |
| `HBL-17` | RANGE larg, breakout NONE | 17 segmente, 17 CHANNEL, 0 ESTABLISHED | N/A | N/A | NU | RANGE | amplitudinea largă a etichetei + zonă îngustă => cicluri repetate breach/reintrare, nu un ESTABLISHED stabil |
| `HBL-18` | CHANNEL_UP→RANGE→CHANNEL_DOWN→RANGE→BREAKOUT_UP→RANGE | 19 segmente, 8 CHANNEL, 10 rupturi, 0 ESTABLISHED | N/A | N/A | PARTIAL | RANGE (×3 apariții) | canal+breakout reproduse, fazele RANGE nu |
| `HBL-19` | CHANNEL_UP→BREAKDOWN_DOWN→CHANNEL_UP→RANGE | 4 segmente: 1 CHANNEL, rupturi, sweep DOWN | N/A | N/A | PARTIAL | RANGE, un CHANNEL_UP | breakdown reprodus, restul nu (96 bare/4 faze = 24 bare/fază, la limita d_min) |
| `HBL-20` | RANGE→SWEEP_DOWN→MARKUP_UP→RANGE nou | reprodus NUMERIC EXACT — vezi §3 | — | — | — | — | tratat separat |
| `HBL-21` | BREAKDOWN_DOWN→RANGE→BREAKOUT_UP/CHANNEL_UP | 1 segment: ESTABLISHED→sweep→BREAKOUT_UP | N/A | N/A | PARTIAL | CHANNEL_UP | breakdown+range+breakout reproduse într-un singur segment coerent, canalul final nu s-a mai clasificat separat |
| `HBL-22` | CHANNEL_UP→RANGE→CHANNEL_UP | 15 segmente, 3 CHANNEL, 0 ESTABLISHED | N/A | N/A | PARTIAL | RANGE | canalul reprodus, faza RANGE de corecție nu |
| `HBL-23` | CHANNEL_DOWN→CHANNEL_UP→RANGE larg | 20 segmente, 0 CHANNEL, 19 rupturi | N/A | N/A | PARTIAL | CHANNEL_UP, CHANNEL_DOWN | RANGE reprodus, canalele dominate de rupturi frecvente (aceeași cauză ca HBL-12) |
| `HBL-24` | RANGE→BREAKOUT_UP→CHANNEL_UP→CHANNEL_DOWN→CHANNEL_UP | 18 segmente, 1 ESTABLISHED, 18 rupturi, 0 CHANNEL | N/A | N/A | PARTIAL | CHANNEL_UP, CHANNEL_DOWN | RANGE+breakout reproduse, fazele de canal dominate de rupturi |

**Sumar verdict:** DA=4 · PARTIAL=12 · NU=6 · nesintetizat=2 (din 24). **Omitere completă (istoric gol,
echivalentul „RANGE 0 · CANAL 0" din 0.3.1): 0/22 sintetizate** — vs. majoritatea ferestrelor la 0.3.1.

## 5. Raportare pe clasă (mandat §9)

- **RANGE pur** (`HBL-17`): NU (canal dominat de cicluri breach/reintrare pe zonă îngustă) — vezi limitarea §2.2.
- **CHANNEL pur** (`HBL-02`, `HBL-13`): NU (trend puternic clasificat repetat ca rupturi, nu ca stare de
  canal continuă) — comportament DIFERIT de defectul 0.3.1 (care nu clasifica NIMIC), dar nu identic cu
  eticheta CEO; notabil pentru rafinare viitoare a pragului canal-vs-breakout.
- **Multi-regim** (17/24 ferestre din lot, per eticheta CEO): PARTIAL în marea majoritate — segmentarea
  longitudinală FUNCȚIONEAZĂ (multiple segmente distincte, cu `predecessor_id` înlănțuit — defectul D1
  închis structural), dar bugetul de bare per fază al fixture-ului sintetic limitează câte faze individuale
  ating pragul de confirmare `d_min_bars`.
- **Sweep/manipulare** (`HBL-01`, `HBL-15`, `HBL-19`, `HBL-20`, `HBL-21`): reprodus consistent — inclusiv
  cazul numeric exact `HBL-20` (§3) și cazul explicit `SWEEP/FAILED_BREAKOUT_UP` din `HBL-15` (0.3.1 îl
  emitea ca eveniment fără nicio stare care să-l consume; 0.4.0 îl reprezintă ca `LIQUIDITY_SWEEP_UP`
  confirmat contra unei stări reale).
- **Breakout** (aproape toate ferestrele multi-regim): reprodus consistent — și, spre deosebire de 0.3.1
  (unde o rupere acceptată ȘTERGEA episodul, 36-38 „ruperi" per fereastră fără nicio memorie a ce a precedat),
  la 0.4.0 fiecare rupere confirmată apare în `history` cu `reached_established`/`predecessor_id` intacte
  (D4 închis structural — verificat direct în suita decisivă, nu doar aici).
- **Tranziții**: fiecare capăt de segment (canal, breakout, breach expirat) poartă `predecessor_id` +
  `transition_reason` explicit către segmentul următor — proprietate STRUCTURALĂ, verificată direct în
  `test_predecessor_chain_links_successive_segments` și `test_terminated_segment_survives_in_history_not_erased`,
  nu doar observată aici.

## 6. Ce NU afirmă acest document

- NU afirmă că detectorul 0.4.0 e „corect" pe piața reală — asta necesită validare Red Team pe un lot BLIND,
  nepublicat aici, cu escrow adecvat (spre deosebire de eșecul `RANGE_V2_BLIND_PROTOCOL_COMPROMISED`).
  Acest document e diagnostic de CONSTRUCȚIE, o cross-verificare calitativă, NU o validare.
- NU calculează și NU țintește nicio ocupație (procent de bare RANGE_STATE) — interzis explicit de mandat.
- NU folosește etichetele pentru a alege K/N/w_atr — configurația de mai sus a fost aleasă înainte de a privi
  verdictele finale, pentru reachability, la fel ca `loose = cfg(w_atr=2.0, ...)` din suita decisivă.
- Dovada de CORECTITUDINE a logicii de decizie stă în `tests/test_range_semantic_v3.py` (75 teste,
  white-box, izolate de zgomotul de fixture) — acest document e un supliment calitativ, NU înlocuiește suita
  decisivă.

**Verdict permis:** conform mandatului, acest document contribuie la `READY_FOR_RANGE_V3_SEMANTIC_REVALIDATION`
— NU e o auto-declarare PASS. Verdictul final revine Red Team.
