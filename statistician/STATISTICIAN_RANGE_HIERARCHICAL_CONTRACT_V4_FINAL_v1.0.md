# STATISTICIAN — CONTRACT FINAL: RANGE IERARHIC V4

**Document ID:** STAT-RANGE-HIERARCHICAL-CONTRACT-V4-FINAL-v1.0 · **Data:** 2026-08-19
**Status:** `RANGE_HIERARCHICAL_SEMANTIC_SPEC_V4_FINAL_READY_FOR_VE_PROTOTYPE_MANDATE`
**Contract:** `range-hierarchical-v4.1` (înlocuiește `v4.0` @`5c29582`) · **următorul proprietar:** CEO, pentru mandatul de prototip VE

> **Acest status autorizează DOAR pregătirea următorului mandat. NU autorizează: implementare directă fără mandat separat · wheel final · Red Team PASS · Strategy Catalog · Alpha · AI Trader integration · LIVE_SHADOW cutover · brokerul · tranzacții.**

```
verificat   spec V4 5c29582 (2026-08-19 15:46:29 +0300) · manifest v2.7.88 fcea167 ·
            fingerprint efc03b6a42e9672e15c5416644f19c1e4789f0cb0a28ee5d7d5057d2a504d3fe   ✔
detectorul NU a fost rerulat · SEALED/OOS_ACCESS = 0
```

**Cele patru decizii CEO sunt NORMATIVE.** Fiecare apare mai jos ca regulă executabilă, cu condiție, ceas și cod de refuz — nu ca observație. Unde o decizie contrazice `v4.0`, `v4.0` cade.

---

# 1 — CE SE SCHIMBĂ FAȚĂ DE `v4.0`

```
D2  DOUĂ niveluri → TREI: MACRO · MESO · MICRO. `INTERNAL` din v4.0 se DESFACE în MESO și MICRO.
D4  ACCUMULATION și DISTRIBUTION IES din enumerarea stărilor vii. Devin ROLURI ISTORICE.
    În timp real, starea neutră e BALANCE. `NEUTRAL_INTERNAL_STRUCTURE` din v4.0 se elimină —
    era exact locul unde s-ar fi strecurat o previziune.
D1  Promovarea canal → trend macro devine o TRANZIȚIE cu patru precondiții cauzale, nu o comparație de pantă.
D3  Protocolul în șapte pași devine parte din contract, cu o poartă de îngheț care blochează
    modificarea valorilor după deschiderea blindului.
```

> **Observație care mi se cuvine mie, nu CEO-ului: în `v4.0` pusesem `ACCUMULATION` și `DISTRIBUTION` printre stările interne VII. Era o greșeală de model — un detector care declară „acumulare" înainte să știe direcția ieșirii face o PREVIZIUNE, nu o observație. Decizia 4 o repară, iar eu o consemnez ca defect al meu, nu ca îmbunătățire venită din afară.**

---

# 2 — DECIZIA 1, NORMATIVĂ: PROMOVAREA CANALULUI LA TREND MACRO

## 2.1 Regula

```
Cât timp CHANNEL_UP/CHANNEL_DOWN rămâne între limitele unui RANGE_MACRO activ,
E STRUCTURĂ MESO. NU înlocuiește macro-ul. Panta singură NU promovează niciodată.
```

**Promovarea la `TREND_UP` / `TREND_DOWN` macro cere TOATE cele patru, în ordine cauzală:**

```
P1  prețul PĂRĂSEȘTE limita range-ului macro
P2  evenimentul e confirmat BREAKOUT_ACCEPTED — nu sweep, nu excursie nerezolvată
P3  STRUCTURA CONTINUĂ în exteriorul range-ului           ← definită la 2.2
P4  episodul RANGE anterior e ÎNCHIS (end_ts scris) dar PĂSTRAT INTEGRAL în istoric
```

```
INTERZIS   reclasificarea retroactivă a range-ului drept „nu a existat"
           promovarea pe baza pantei fără P1-P4
           promovarea în timpul unei excursii nerezolvate (BREAKOUT_PENDING)
cod refuz  PROMOTION_REFUSED_PRECONDITION_<P1|P2|P3|P4>
```

## 2.2 Ce confirmă „continuarea structurii" — definiție STRUCTURALĂ, fără valori numerice

**P3 e satisfăcută când, ÎNTREG în afara limitei rupte, se formează o secvență de extreme structurale în direcția ruperii, confirmate cu ACELAȘI detector de swing folosit peste tot în contract:**

```
pentru TREND_UP    un swing high NOU peste maximul ruperii
                   ȘI un swing low NOU peste limita superioară a range-ului închis
                   (higher high urmat de higher low, ambele CONFIRMATE, ambele în afară)
pentru TREND_DOWN  simetric: lower low sub minimul ruperii ȘI lower high sub limita inferioară

confirm_ts(P3) = bara la care se confirmă AL DOILEA dintre cele două extreme.
                 Nu la primul. Un singur extrem nu e o structură, e un impuls.
```

```
NU pretinde nicio valoare numerică. Cere DOUĂ extreme confirmate, nu „x bare" sau „y×ATR".
Singurul parametru latent e `n_continuation` = câte perechi extrem-extrem se cer.
   Valoare implicită STRUCTURALĂ: 1 pereche (adică 2 extreme).
   Orice valoare > 1 e NEIDENTIFICATĂ și se alege prin protocolul de la §6.
```

> **Nu aleg această valoare din rezultatul blind, fiindcă nu există rezultat blind — și nici din corpusul de construcție, fiindcă `n_continuation` se poate fixa structural: „o structură are nevoie de cel puțin două puncte" e o afirmație despre ce înseamnă structură, nu despre datele astea. Marchez totuși pragul ca revizuibil, ca să nu pară derivat empiric.**

## 2.3 Drumul invers

```
TREND_MACRO → RANGE_MACRO se face prin ACELAȘI mecanism, nu prin scăderea pantei:
   trendul se încheie când apare un RANGE_MACRO nou care satisface propriile precondiții,
   cu predecessor_id = trendul închis. Un trend NU „devine" range prin plictiseală.
```

---

# 3 — DECIZIA 2, NORMATIVĂ: TREI NIVELURI

## 3.1 Nivelurile

```
depth 0  MACRO   RANGE_MACRO · TREND_UP · TREND_DOWN · TRANSITION_MACRO
depth 1  MESO    canalul sau sub-range-ul PRINCIPAL din interiorul macro-ului:
                 MESO_SUBRANGE · MESO_CHANNEL_UP · MESO_CHANNEL_DOWN · MESO_BALANCE
depth 2  MICRO   structura LOCALĂ, utilizabilă ulterior pentru execuție:
                 MICRO_SUBRANGE · MICRO_CHANNEL_UP · MICRO_CHANNEL_DOWN · MICRO_BALANCE
```

```
O bară poate aparține SIMULTAN unui obiect MACRO, unuia MESO și unuia MICRO.
Cel mult UN obiect activ pe fiecare nivel, la orice bară.
Ieșirea la bara i e un TRIPLET (macro, meso, micro), oricare putând fi null pe nivelurile 1-2.
```

## 3.2 Evenimentele sunt ORTOGONALE, nu al patrulea nivel

```
SWEEP_UP · SWEEP_DOWN · FAILED_BREAKOUT_UP · FAILED_BREAKOUT_DOWN ·
BREAKOUT_PENDING · BREAKOUT_ACCEPTED_UP · BREAKOUT_ACCEPTED_DOWN ·
REENTRY_CONFIRMED · STRUCTURE_BREAK_UP · STRUCTURE_BREAK_DOWN

Fiecare eveniment poartă `applies_to_structure_id` — NU are depth propriu.
Un eveniment poate viza orice nivel; se înregistrează cui i se aplică.
```

> **RECURSIVITATEA NEMĂRGINITĂ E INTERZISĂ PRIN TIP. `depth > 2` trebuie să fie NEREPREZENTABIL, nu doar respins la rulare. Un al patrulea nivel structural cere o schimbare de contract și o versiune nouă.**

## 3.3 Schema obligatorie a fiecărui obiect structural

```
structure_id          int, monoton, unic pe rulare
parent_structure_id   id-ul obiectului de pe nivelul imediat superior; NULL doar la depth 0
depth                 0 | 1 | 2 — enumerare închisă, nu int liber
start_ts              începutul, retrospectiv
confirm_ts            când s-a putut ȘTI. Nicio decizie la start_ts.
end_ts                NULL cât e activ
boundary_lower        limita inferioară + banda ei
boundary_upper        limita superioară + banda ei
state                 starea curentă din enumerarea nivelului
reason_codes          motivele stării
not_yet_available     ce NU se putea ști la bara curentă — OBLIGATORIU
identity_fingerprint  hash peste (contract_version, depth, start_ts, limite, config_id)
predecessor_id        obiectul ÎNCHIS de pe ACELAȘI nivel din care descinde
role                  NULL în timp real; vezi §4
role_known_ts         NULL până când rolul devine cunoscut
```

**Invarianți de integritate, verificați prin tip:**

```
I1  depth(copil) = depth(părinte) + 1
I2  [start_ts, end_ts] al copilului ⊆ [start_ts, end_ts] al părintelui
I3  închiderea părintelui închide copiii, cu end_ts = end_ts al părintelui
I4  cel mult un obiect activ pe nivel
I5  parent_structure_id NULL ⟺ depth = 0
```

---

# 4 — DECIZIA 4, NORMATIVĂ: ROLURI CONFIRMATE, NU PREVIZIUNI

## 4.1 În timp real, starea e NEUTRĂ

```
BALANCE   consolidare fără direcție de ieșire cunoscută. Starea NEUTRĂ implicită
          pe orice nivel, la orice obiect care nu e canal sau trend.
```

> **`ACCUMULATION` și `DISTRIBUTION` NU EXISTĂ ca stări vii. Emiterea lor înainte de confirmare e o VIOLARE DE CONTRACT, cu cod `ROLE_ASSERTED_BEFORE_CONFIRMATION`, tratată fail-closed. Diferența nu e de vocabular: „acumulare" afirmă cine cumpără și de ce, iar asta nu e observabil dintr-o bară închisă.**

## 4.2 După confirmare — rol ISTORIC, adăugat retrospectiv

```
ieșire BULLISH acceptată (P2) ȘI continuare structurală (P3)  → role = ACCUMULATION_CONFIRMED
ieșire BEARISH acceptată (P2) ȘI continuare structurală (P3)  → role = DISTRIBUTION_CONFIRMED
```

**Adăugarea retrospectivă e permisă DOAR cu toate patru câmpurile păstrate:**

```
role_known_ts                 bara la care rolul a devenit cunoscut  ← NICIODATĂ = start_ts
confirm_ts                    confirmarea originală a episodului, NEMODIFICATĂ
not_yet_available_at_the_time  ce nu se putea ști atunci — se păstrează, nu se șterge
structure_id                   identitatea episodului original, NESCHIMBATĂ
```

```
INTERZIS   rescrierea lui state · rescrierea lui confirm_ts · reemiterea episodului cu id nou ·
           orice interogare care returnează rolul ca și cum ar fi fost cunoscut la start_ts
CERUT      orice consumator care citește `role` trebuie să citească ȘI `role_known_ts`.
           Un jurnal care păstrează rolul și pierde momentul cunoașterii e o falsificare
           de istorie — aceeași regulă de PERECHE ca la reason codes în v2.1.
```

## 4.3 Tiparul HBL-20, scris cauzal

```
BALANCE ─────────────────► SWEEP_DOWN ──► REENTRY_CONFIRMED ──► BULLISH_STRUCTURE_BREAK ──► MARKUP
   ▲                          bara 52          bara 56                                        bara 63
   │                     not_yet_available = SWEEP_VS_BREAKOUT
   │                     ★ pe bara 52 NU se pretinde că acumularea era cunoscută
   └──────────────── role = ACCUMULATION_CONFIRMED, role_known_ts = bara de confirmare a P3
                     atribuit RETROSPECTIV episodului BALANCE original
```

**Rămâne obiect semantic. Zero PnL, zero semnal, zero Strategy Catalog.**

---

# 5 — TRUTH TABLE ȘI TRANZIȚII

## 5.1 MACRO la bara `i`

| swings ≥2/latură | durată ≥ `d_macro` | zone disjuncte | ATR | excursie | P1-P4 îndeplinite | → MACRO |
|---|---|---|---|---|---|---|
| — | — | — | **nu** | — | — | `Unavailable(ATR_UNAVAILABLE)` |
| nu | — | — | da | nu | — | `TRANSITION_MACRO` |
| da | nu | da | da | nu | — | `RANGE_FORMING` |
| da | da | da | da | nu | — | `RANGE_CONFIRMED` |
| da | da | **nu** | da | nu | — | `Unavailable(ZONES_DEGENERATE)` |
| da | da | da | da | **da** | — | `BOUNDARY_EXCURSION` → 5.2 |
| — | — | — | da | — | **toate 4** | `TREND_UP` / `TREND_DOWN` |
| — | — | — | da | — | parțial | `PROMOTION_REFUSED_PRECONDITION_<Pk>` — macro NESCHIMBAT |

## 5.2 Rezolvarea excursiei

| reintrare ≤ `K_reentry` | `N_accept` închideri în afară | continuare structurală (P3) | → rezultat |
|---|---|---|---|
| nu încă | nu | — | `BREAKOUT_PENDING` + `not_yet_available = SWEEP_VS_BREAKOUT` |
| **da** | nu | — | `SWEEP_CONFIRMED` — macro RĂMÂNE deschis |
| **da** | nu | ruptură opusă ≤ `K_struct` | `SWEEP_CONFIRMED` + `LIQUIDITY_SWEEP_REVERSAL` |
| nu | **da** | nu (încă) | `BREAKOUT_ACCEPTED` — macro se ÎNCHIDE; **fără promovare** |
| nu | **da** | **da** | `BREAKOUT_ACCEPTED` + promovare la TREND + rol istoric (§4.2) |

## 5.3 MESO și MICRO

| macro | precondiție de nivel | → stare |
|---|---|---|
| `RANGE_CONFIRMED` sau `TREND_*` | swings suficiente + durată ≥ `d_meso` | `MESO_*` conform geometriei |
| macro absent sau `Unavailable` | — | MESO și MICRO **null** — nu există structură fără părinte |
| MESO activ | durată ≥ `d_micro` + swings | `MICRO_*` |
| pantă mare la nivel MESO | — | `MESO_CHANNEL_*` — **NU promovează macro-ul** (D1) |

## 5.4 Tranziții permise și interzise

```
PERMISE     FORMING → CONFIRMED → {INTERNAL_MOVE, BOUNDARY_EXCURSION}
            BOUNDARY_EXCURSION → {SWEEP_CONFIRMED, BREAKOUT_PENDING, BREAKOUT_ACCEPTED}
            SWEEP_CONFIRMED → CONFIRMED                      (range-ul supraviețuiește)
            BREAKOUT_ACCEPTED → EPISODE_CLOSED → {RANGE_MACRO nou, TREND_* dacă P3}
            orice → Unavailable la lipsă de input
            atribuirea unui `role` unui episod ÎNCHIS, cu role_known_ts (§4.2)

INTERZISE   ★ CONFIRMED → FORMING fără eveniment
            ★ EPISODE_CLOSED → orice stare vie
            ★ reclasificarea retroactivă a unui episod închis
            ★ CHANNEL (MESO) → TREND (MACRO) fără P1-P4
            ★ ACCUMULATION / DISTRIBUTION ca stare vie
            ★ depth > 2 sub orice formă
            ★ copil fără părinte activ
            ★ două obiecte active pe același nivel
            ★ orice tranziție care folosește o bară cu index > i
```

## 5.5 Precedența

```
1  Unavailable bate tot
2  MACRO se evaluează ÎNAINTEA lui MESO, MESO înaintea lui MICRO. Niciodată invers.
3  Un nivel inferior NU poate schimba unul superior. Singura cale în sus e promovarea (D1).
4  la egalitate între candidați pe același nivel, câștigă cel cu start_ts mai VECHI
```

---

# 6 — DECIZIA 3, NORMATIVĂ: PROTOCOLUL ÎN ȘAPTE PAȘI

```
1  se PREÎNREGISTREAZĂ regula de alegere a fiecărui parametru (măsurătoare + regulă, nu căutare)
2  se folosește corpusul actual — 48 ferestre, 114 segmente — EXCLUSIV pentru construcție
3  se FIXEAZĂ valorile
4  se ÎNGHEAȚĂ codul, configurația și fingerprint-ul
5  se generează un lot NOU, nevăzut de detector
6  DOAR acel lot poate susține validarea blind finală
7  după deschiderea blindului, valorile NU se mai schimbă fără reluarea completă a validării
```

```
POARTA DE ÎNGHEȚ, executabilă:
   config_frozen_at   commit-ul înghețării
   config_id          hash peste TOȚI parametrii + contract_version
   după pasul 4, orice rulare cu alt config_id ≠ config_frozen e MARCATĂ
      POST_FREEZE_CONFIG_DRIFT și NU poate purta un verdict blind
```

```
CORPUSUL ACTUAL: CEO_ASSISTED_CONSTRUCTION_ONLY
   permis      semantică · intervale de parametri · alegere deterministă a configurației ·
               testul de nevacuitate · măsurarea erorilor prototipului
   INTERZIS    BLIND_PASS sub orice formă
```

**Ocuparea nu e țintă.** „Piața stă 70% în range" rămâne ipoteză de măsurat. Orice reglaj către un procent prestabilit e o violare a pasului 1.

---

# 7 — TESTELE DE NEVACUITATE

**Nicio condiție nu intră în contract fără să se demonstreze că poate ȘI să treacă, ȘI să eșueze:**

```
pentru fiecare condiție c:
    n_pass(c) = câte obiecte/bare o satisfac      n_fail(c) = câte o încalcă
    n_pass = 0  → CONDIȚIE MOARTĂ    → REFUZ, cod CONDITION_DEAD_BY_CONSTRUCTION
    n_fail = 0  → CONDIȚIE VACUĂ     → REFUZ, cod CONDITION_VACUOUS_BY_CONSTRUCTION
se raportează pentru FIECARE condiție, inclusiv cele care trec
```

**Condițiile care TREBUIE testate explicit, fiindcă exact ele au eșuat istoric:**

```
T1  durata macro          la V2 nu putea eșua · la V3 nu putea reuși. AMBELE trebuie posibile.
T2  fereastra de reintrare la V3 plafonată la 2 bare de cuplarea K<=N, acum ELIMINATĂ
T3  zone degenerate       trebuie să se declanșeze uneori și să nu se declanșeze alteori
T4  promovarea la trend   trebuie să existe cazuri promovate ȘI refuzate pe fiecare precondiție
T5  atribuirea de rol     trebuie să existe episoade cu rol ȘI episoade rămase BALANCE pentru totdeauna
T6  MESO și MICRO         fiecare nivel trebuie să fie NEVID pe corpus, altfel ierarhia e decorativă
```

> **T6 e testul care ar fi trebuit să existe de la V2: dacă un nivel nu se populează niciodată, el nu există, oricât de frumos e scris în contract.**

---

# 8 — SNAPSHOT ȘI IDENTITATE

```
contract_version         range-hierarchical-v4.1
structure_schema_version range-structure-v4.1
snapshot_schema_version  range-snapshot-v4.1
identity_version         range-identity-v4.1
config_id                hash peste toți parametrii + contract_version
```

```
SNAPSHOT
   macro_active + macro_history (mărginit)
   meso_active  + meso_history  (mărginit, fiecare cu parent_structure_id)
   micro_active + micro_history (mărginit, fiecare cu parent_structure_id)
   excursion_state {open_bar, direction, closes_outside, reentry_seen, expires_at, applies_to}
   swing_buffer cu fereastra de reținere DECLARATĂ
   id_counters monotone
   roles_assigned [(structure_id, role, role_known_ts)]
   contract_version + config_id   OBLIGATORII
```

> **Restaurarea unui snapshot cu altă `contract_version` SAU alt `config_id` trebuie să EȘUEZE ÎNCHIS, prin tip. Restaurarea tăcută a snapshot-urilor V1-V3 sau `v4.0` e INTERZISĂ. Cod: `SNAPSHOT_CONTRACT_MISMATCH`.**

```
INCOMPATIBILITĂȚI
V1 ancoră max+close · V2 ancoră fixă 512 · V3 un singur segment · V3 K<=N ·
V3 IS_CHANNEL = respingere · v4.0 două niveluri · v4.0 ACCUMULATION ca stare vie
   → toate INCOMPATIBILE. Fingerprint RECALCULAT; rezultatele anterioare NECOMPARABILE PRIN TIP.
```

---

# 9 — CERINȚELE EXACTE PENTRU PROTOTIPUL VE

```
1   trei niveluri, cu depth enumerare ÎNCHISĂ {0,1,2} — depth 3 NEREPREZENTABIL prin tip
2   ieșirea la fiecare bară e un TRIPLET (macro, meso, micro) + evenimente ortogonale
3   invarianții I1-I5 verificați prin tip sau assert, nu prin convenție
4   ACCUMULATION/DISTRIBUTION IMPOSIBIL de emis ca stare vie — doar ca `role` pe episod închis
5   role_known_ts obligatoriu ori de câte ori role e nenul
6   promovarea canal→trend DOAR prin P1-P4, cu cod de refuz pe precondiția care a picat
7   K_reentry și N_accept parametri INDEPENDENȚI — fără constrângerea K<=N
8   fiecare obiect poartă not_yet_available; între breșă și rezolvare = SWEEP_VS_BREAKOUT
9   snapshot/restore BIT-IDENTIC; refuz fail-closed la contract_version sau config_id străin
10  raportul de nevacuitate T1-T6 livrat ODATĂ cu prototipul, nu după
11  zero lookahead verificabil prin construcție: nicio ieșire la bara i nu citește index > i
12  config_id calculat și înregistrat la fiecare rulare
13  N1 rămâne byte-neatins
14  0.4.1 NU se suprascrie — se păstrează pentru audit
```

---

# 10 — VALORILE CARE RĂMÂN NEIDENTIFICATE NUMERIC

| parametru | nivel | ce spune corpusul, MĂSURAT | stare |
|---|---|---|---|
| `d_macro` | MACRO | durate observate [4, 480], mediană 55, n=114 | **NEIDENTIFICAT** |
| `d_meso` | MESO | sub-range-uri [8, 132] n=12; canale [11, 110] n=22 | **NEIDENTIFICAT** |
| `d_micro` | MICRO | neobservabil separat — CEO nu a etichetat trei niveluri consecvent | **NEIDENTIFICAT** |
| `K_reentry` | eveniment | sweep-uri observate [4, 22], mediană 10, n=65 | **NEIDENTIFICAT** |
| `N_accept` | eveniment | **NEOBSERVABIL** — omul marchează sweep-ul prin reintrare, nu numărând închideri | **NEIDENTIFICAT** |
| `K_struct` | eveniment | neobservabil separat de `K_reentry` în etichete | **NEIDENTIFICAT** |
| `w_atr` | toate | ratificat 0,30 sub ancora VECHE — invalid sub cea nouă | **DE REDERIVAT** |
| `s_max` | MACRO | cuplarea `2·w_atr` se păstrează; valoarea urmează `w_atr` | **DERIVAT** |
| `tol_touch` | toate | neidentificat; constrângere `<= w_atr` | **NEIDENTIFICAT** |
| `n_continuation` | promovare | fixat STRUCTURAL la 1 pereche (2 extreme); > 1 ar fi empiric | **STRUCTURAL, revizuibil** |
| `swing_k` | toate | moștenit 2 | **MOȘTENIT, neratificat sub V4** |
| `atr_window` | toate | moștenit 14 | **MOȘTENIT, neratificat sub V4** |

```
Constrângeri structurale obligatorii prin tip:
   d_micro < d_meso < d_macro          fereastra ancorei unui obiect <= durata acelui obiect
   d_event << d_micro                  K_reentry ⊥ N_accept (independenți)
```

> **Zece valori nu au număr ratificat sub V4, iar compoziția e verificabilă din tabel: ȘAPTE marcate `NEIDENTIFICAT` (`d_macro`, `d_meso`, `d_micro`, `K_reentry`, `N_accept`, `K_struct`, `tol_touch`) + `w_atr` DE REDERIVAT sub ancora nouă + DOUĂ moștenite dar neratificate sub V4 (`swing_k`, `atr_window`). Celelalte două rânduri NU intră în număr: `s_max` e DERIVAT prin cuplare, iar `n_continuation` e fixat STRUCTURAL. Niciuna nu se alege în acest document. Coloana din mijloc e DISTRIBUȚIA observată, nu pragul — corpusul dă compromisul, nu punctul, iar punctul cere protocolul din §6 executat în ordinea lui.**

---

# 11 — CE RĂMÂNE DESCHIS

```
MATERIAL   `d_micro` nu e observabil din corpusul actual: CEO a etichetat trei niveluri doar
           sporadic. Nivelul MICRO e specificat, dar corpusul nu-l poate încă identifica —
           iar T6 va spune dacă e viu sau decorativ.
MATERIAL   `N_accept` și `K_struct` nu se pot deriva din etichete sub NICIO regulă: omul nu
           numără închideri. Ele cer fie o convenție declarată de CEO, fie un corpus adnotat altfel.
LIMITARE   `n_continuation = 1 pereche` e o alegere STRUCTURALĂ, nu empirică. Am marcat-o
           revizuibilă ca să nu pară derivată din date.
LIMITARE   Corpusul e CEO_ASSISTED. Poate arăta doar că stările sunt VII, niciodată că sunt CORECTE.
```

---

**Invariante verificate neatinse:** `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 · F7 `SAFETY_GUARD` · LIVE_SHADOW · broker gate. Detectorul NU a fost rerulat. Zero PnL, zero strategie, `SEALED/OOS_ACCESS = 0`.

**Manifest:** v2.7.89.
