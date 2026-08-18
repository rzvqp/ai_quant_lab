# STATISTICIAN — REPARAREA ESCROW-ULUI BLIND RC-07/RC-08 ȘI RULING FINAL PE REASON CODES

**Document ID:** STAT-RANGE-V2-BLIND-ESCROW-RULING-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Declanșat de:** Red Team `RT-RANGE-0003` @`0e1a385` (LEDGER E78) — `RANGE_V2_BLIND_PROTOCOL_COMPROMISED` + `RANGE_V2_CONTRACT_AMBIGUITY_REASON_CODES`

---

## STATUSURI TERMINALE

```
ESCROW BLIND     RANGE_V2_BLIND_ESCROW_REPAIR_BLOCKED_NO_INDEPENDENT_SEMANTIC_GROUND_TRUTH_REMAINS
REASON CODES     RANGE_V2_REASON_CODE_CONTRACT_FINAL_READY_FOR_VE_0_3_2
RC-07            SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE        (0 bare canonice, MĂSURAT)
RC-08            SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE        (0 bare canonice, MĂSURAT)
ÎNLOCUIRE        NEEXECUTABILĂ cu materialul existent — regula e preînregistrată aici și devine
                 mecanică în clipa în care CEO livrează episoade etichetate vizual
0.3.1 vs 0.3.2   0.3.2 NECESAR — dar NU din cauza denumirilor: lipsește o gardă RATIFICATĂ
URMĂTORUL        VE_RANGE_0.3.2_PINNED_REDELIVERY
```

**`BLIND_OUTPUT_NOT_ACCESSED` · `SEALED/OOS_ACCESS = 0` · zero Alpha · zero PnL · zero cost gate · zero p-value · zero AI Trader · zero LIVE_SHADOW · zero broker · zero `order_send`.**

---

# 1 — VERIFICARE GIT (toate confirmate din repo, nu din mandat)

```
STATISTICIAN   4e69e22  protocol pre-înregistrat        2026-08-18 20:24:20 +0300   ✔
               c29ac98  rezultat w_atr                  2026-08-18 20:29:41 +0300   ✔
               2dde05a  addendum                        2026-08-18 20:41:58 +0300   ✔
MANIFEST       84a1a98  v2.7.80                         2026-08-18 20:29:21 +0300   ✔
               2611d22  v2.7.81                         2026-08-18 20:41:26 +0300   ✔
               fingerprint 432170ff5b6d0d20e125ea318d0293053f10ff0da8df9948bb470dde6d6501f6  ✔ recalculat
VE             aa01f41  build 0.3.1                     2026-08-18 21:17:59 +0300   ✔
               18d1aa1  delivery 0.3.1                  2026-08-18 21:18:15 +0300   ✔
               wheel SHA-256 048ee2b495112c9f90b39d65a7d6bd851764a46f1e32b0eda7c6ad2a42686cca  ✔ re-hash direct
RED TEAM       0e1a385  RT-RANGE-0003 (E78)             2026-08-18 21:43:54 +0300   ✔
```

## Confirmările cerute înainte de lucru

```
Red Team NU a rulat 0.3.1 pe RC-07/RC-08     ✔  raportul propriu o declară; §4-§6 marcate NOT EXECUTABLE
VE NU a accesat RC-07/RC-08                  ✔  docstring-ul buildului declară calibrare DOAR pe
                                                RC-CONSTRUCTION-CHANNEL-NEW-01; testele folosesc fixture sintetice
Niciun output de detector pe aceste episoade ✔  căutare pe disc: zero fișiere `*rc07*`/`*rc-07*`/`*blind*`;
                                                singurele apariții „RC-07" sunt DECLARAȚII în documente
SEALED/OOS_ACCESS = 0                        ✔
```

> **`RANGE_V2_BLIND_DATA_ALREADY_EXPOSED` NU se aplică.** Nu există output anterior. Reconstrucția era permisă.

---

# 2 — REZOLVAREA RC-07 ȘI RC-08

## 2.1 Ce sunt de fapt fișierele

Ambele PDF-uri **nu au niciun strat de text** — zero fonturi, un singur XObject imagine RGB comprimat Flate. Deci nicio dată nu e extractibilă altfel decât din pixeli:

```
channel bullish si range.pdf   2361 x 1350 px   RGB   0 fonturi
range si trend bearish.pdf     2397 x 1356 px   RGB   0 fonturi
```

Citite din imagine: **`Gold Spot / U.S. Dollar · 15 · OANDA`**, mod **Replay**, fusul graficului **UTC+3** (bara de stare). Simbolul și rezoluția sunt exact cele cerute.

## 2.2 Ancorele temporale sunt redate de TradingView, nu deduse de mine

Etichetele de pe axă sunt randate de platformă din chiar timestamp-urile barelor — cel mai autoritar datum din imagine:

```
RC-07   crosshair „08 Dec '22 22:00"                       → 2022-12-08 19:00 UTC
        repere zilnice vizibile: 30 · Dec · 2 · 5 · 6 · 7 · 8 · 12 · 13 · 14 · 15
RC-08   crosshair „15 Nov '22 04:30"
        DOUĂ etichete albastre de capăt ale desenului SELECTAT (canalul):
        „18 Nov '22 04:00" și „21 Nov '22 19:45"          → 2022-11-18 01:00 și 2022-11-21 16:45 UTC
```

**Capetele canalului RC-08 sunt EXACTE** — sunt etichetele proprii ale desenului. Restul segmentelor sunt derivate prin interpolare de pixeli între ancore, cu **maparea liniară în INDEX DE BARĂ, nu în timp**: prima încercare, liniară în timp, a produs un capăt de canal **sâmbătă**, ceea ce e imposibil. Corectat cu un mapaj care sare weekendul (piața închisă vineri 21:00 UTC → duminică 22:00 UTC — convenție citită din chiar corpusul canonic, ale cărui blocuri se termină la `…21:45` și reiau la `…22:00`).

```
RC-07   segment RANGE      2022-12-05 13:15 → 2022-12-07 13:45 UTC   (±6 bare)
        segment CANAL      2022-12-07 14:30 → 2022-12-12 07:30 UTC   (±6 bare)
RC-08   segment RANGE      2022-11-16 17:45 → 2022-11-17 05:15 UTC   (±4 bare)
        segment CANAL      2022-11-18 01:00 → 2022-11-21 16:45 UTC   (EXACT)
```

## 2.3 Nu m-am oprit la etichete — am căutat episoadele în tot corpusul

Etichetele pot fi citite greșit. Am pus întrebarea independent de ele: **există undeva în populația canonică o fereastră care reproduce forma din captură?** Am extras, din pixeli, anvelopa maxim/minim a lumânărilor (mască pe culorile lumânărilor, coloană cu coloană, binuită la 128 de intervale) și am corelat-o, invariant la scară, cu fiecare fereastră canonică, pe șapte rezoluții de bare-per-bin.

**Un rezultat nul nu valorează nimic dacă instrumentul nu poate găsi o potrivire când ea există. Așa că am construit întâi controlul pozitiv:** am randat o fereastră canonică (index 150.000, 1.280 bare) în același stil vizual și am trecut-o prin **exact același** extractor de pixeli și aceeași căutare.

```
CONTROL POZITIV   adevăr: index 150000, N=1280
                  găsit:  index 150000, N=1280,  r = 0.9999,  eroare 0 bare
                  al 50-lea candidat: 0.9270  → potrivirea adevărată iese clar din câmp

RC-07             cel mai bun r = 0.5009   (al 50-lea 0.4341)
RC-08             cel mai bun r = 0.5343   (al 50-lea 0.4657)
```

> **Instrumentul recuperează o potrivire reală cu `r = 0,9999` și eroare zero. Pentru ambele capturi, cel mai bun candidat din tot corpusul stă la `r ≈ 0,5` și e practic nediferențiabil de alte câteva sute. Aceasta nu e o potrivire ambiguă — e ABSENȚA oricărei potriviri.**

```
unique_match_count(RC-07) = 0
unique_match_count(RC-08) = 0
```

`RANGE_V2_BLIND_INTERVAL_AMBIGUOUS_<RC_ID>` **nu se aplică**: condiția lui e *mai multe* potriviri plauzibile. Aici nu e niciuna.

---

# 3 — VERIFICAREA POPULAȚIEI: CAUZA

Populația canonică M15_v2 (pre-holdout, 197.094 bare) are **PATRU** blocuri oficiale:

```
1   2011-07-26 16:30  →  2013-09-27 16:45
2   2016-01-11 09:00  →  2018-04-06 11:52
3   2020-08-11 06:45  →  2021-09-05 12:15
4   2022-12-16 10:45  →  2025-10-12 23:15
```

**Între blocul 3 și blocul 4 se întinde un gol de aproape cincisprezece luni.** Noiembrie 2022 și prima jumătate a lui decembrie 2022 cad integral în el:

```
bare canonice în 2022-12-05 → 2022-12-13   (fereastra RC-07):   0
bare canonice în 2022-11-16 → 2022-11-22   (fereastra RC-08):   0
```

Nu e o trunchiere la marginea unui bloc și nu e o sigilare. Sunt date **nelivrate niciodată**. Indiciile CEO (RC-07 ≈ 5-12 decembrie, RC-08 ≈ 16-21 noiembrie) s-au dovedit corecte ca lună și an — și exact de aceea episoadele sunt inutilizabile.

```
RC-07  →  SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE
RC-08  →  SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE
```

Nu le forțez, nu le relochetez, nu le mut.

---

# 4 — CONSTATAREA CARE BLOCHEAZĂ ÎNLOCUIREA

Am recitit tot corpusul vizual, nu doar cele două capturi. **Toate cele opt episoade etichetate uman sunt epuizate:**

| ID | sursă | perioadă | stare |
|---|---|---|---|
| RC-01 | `range3.pdf` | 2015-12-10 → 12-18 | **0 bare canonice** (golul blocurilor 1-2) |
| RC-02 | `range4.pdf` | 2015-12-21 → 12-30 | **0 bare canonice** |
| RC-03 | `range5.pdf` | 2016-12-20 → 12-27 | **construcție** — VE le-a văzut |
| RC-04 | `range6.pdf` | 2016-09-21 → 10-31 | **construcție** — VE le-a văzut |
| RC-05 | `range7.pdf` | 2022-12-16 → 12-30 | **construcție** — VE le-a văzut |
| RC-06 | `range8.pdf` | 2022-12-16 → 12-29 | `RC-06 ⊂ RC-05` ⇒ **nu e blind** |
| RC-07 | `channel bullish si range.pdf` | 2022-12 | **0 bare canonice** (măsurat aici) |
| RC-08 | `range si trend bearish.pdf` | 2022-11 | **0 bare canonice** (măsurat aici) |

> **Nu mai există NICIUN episod etichetat uman care să fie simultan (a) în populația canonică și (b) nevăzut de VE. Sursa de semantică independentă s-a epuizat — nu s-a compromis, s-a terminat.**

## De ce nu fabric o înlocuire

§8 îmi cere să preînregistrez o regulă deterministă și să selectez un episod nou. Pot face asta procedural. **Nu produce însă o validare blind, și diferența nu e una de formă.**

Singura statistică de pantă independentă de detector pe care o am este `S = |slope| · d_min / ATR` — **exact statistica pe care detectorul o pragează**. Un control de canal selectat prin `S ≥ 2,0` e respins ca range prin **aritmetică**, nu prin semantică: `S = 3,38 > s_max = 0,60` era adevărat înainte să ruleze orice cod. Asta e deja limitarea recunoscută a lui `RC-CONSTRUCTION-CHANNEL-NEW-01`, iar Red Team ar avea dreptate să o numească circulară dacă aș ridica-o la rang de dovadă blind.

Simetric pentru un pozitiv selectat prin regulă: aș testa dacă implementarea respectă specificația mea, nu dacă detectorul vede piața corect. **Acesta e testul pe care Red Team îl face deja prin suita de conformitate. Nu e testul semantic.**

> **A eticheta o comparație regulă-contra-regulă drept „validare blind" ar fi exact genul de certificare falsă pe care Red Team a refuzat-o. Refuz și eu.**

```
RANGE_V2_BLIND_ESCROW_REPAIR_BLOCKED_NO_INDEPENDENT_SEMANTIC_GROUND_TRUTH_REMAINS
```

---

# 5 — REGULA DE ÎNLOCUIRE, PREÎNREGISTRATĂ ACUM (înainte de orice dată nouă)

Se execută **mecanic**, fără nicio discreție, în clipa în care CEO livrează capturi noi. Se comite ÎNAINTE de a fi văzute, exact ca protocolul `4e69e22`.

## 5.1 Ce trebuie să livreze CEO

```
DOUĂ capturi minim: un POZITIV (range clar) și un NEGATIV (canal clar, ascendent sau descendent)
Etichetare VIZUALĂ, făcută de om, nu de regulă
Perioada OBLIGATORIU în una din ferestrele ELIGIBILE de mai jos
Aceleași cerințe de captură ca RC-07/RC-08: simbol + rezoluție + fus vizibile, axă temporală lizibilă,
   iar dacă desenul e SELECTAT, etichetele de capăt devin ancore EXACTE — de preferat
```

## 5.2 Ferestrele eligibile — populația canonică minus tot ce e deja consumat

```
2016-01-11 09:00 → 2016-09-20              (înainte de RC-04)
2016-11-01      → 2016-12-19               (între RC-04 și RC-03)
2016-12-28      → 2018-04-06 11:52         (după RC-03)
2020-08-11 06:45 → 2021-09-05 12:15        (bloc întreg, neatins)
2022-12-31      → 2025-10-12 23:15         (după RC-05/RC-06)
EXCLUS suplimentar: [192, 288) în index canonic — RC-CONSTRUCTION-CHANNEL-NEW-01, plus tampon 96 bare
EXCLUS: orice după 2025-10-12 23:15 (embargo/SEALED/OOS)
```

## 5.3 Regula deterministă, dacă ambiguitatea persistă

```
Dacă o captură livrată se rezolvă la MAI MULTE ferestre canonice plauzibile (r > 0,90 pentru
   cel puțin două ferestre disjuncte): RANGE_V2_BLIND_INTERVAL_AMBIGUOUS_<RC_ID>, nu se alege manual.
Dacă se rezolvă la ZERO ferestre (r_max < 0,90 peste tot): episodul e în afara populației,
   SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE, se cere altul. Pragul 0,90 e fixat AICI, derivat din
   controlul pozitiv de la §2.3: potrivirea adevărată dă 0,9999, iar al 50-lea candidat 0,9270 —
   deci 0,90 stă sub potrivirea reală și deasupra câmpului de zgomot de la RC-07/RC-08 (≈0,50).
Se ia câte UN singur episod de fiecare rol. NU se adaugă episoade până iese rezultatul dorit.
Matricea per-bară se scrie ÎNAINTE de orice rulare a detectorului, după schema din escrow.
```

---

# 6 — ESCROW-UL: MECANISMUL EXISTĂ ȘI E VERIFICAT

Payloadul **nu locuiește în niciunul din cele patru repo-uri** consumate de VE/Alpha. Stă în afara oricărui checkout git, exact ca `tools/notify.py`:

```
C:\Users\MEDION GAMING\escrow_red_team\
   escrow_tool.py                 sigilare/deschidere/verificare, zero dependințe terțe
   payload-2dcfbeeab5794d5f.bin   content-addressed: numele = primii 16 hex din SHA-256 al cifrului
   escrow_key.bin                 cheia, separat de payload
```

```
payload SHA-256      2dcfbeeab5794d5fd5a4921374aaae44a986ab8752caf7b8e8aada9bdaceb362
plaintext SHA-256    95dc4f8ea7870dbae86e0ce8945e38ab8a810c15c09444ebccb73605dfd1b39a
contract             range-blind-escrow-v1.0
```

**Verificat înainte de predare, nu presupus:**

```
1  Red Team poate deschide                          DA — escrow_id RT-BLIND-ESCROW-RANGE-V2-001
2  cheie greșită                                    RESPINS, fail-closed (tag invalid)
3  un singur bit modificat în payload               RESPINS, fail-closed
4  hash-ul payloadului e recomputabil               DA, identic
5  e în afara oricărui repo git                     DA — `git rev-parse` eșuează în director
6  îl poate consuma accidental VE/Alpha             NU — 0 potriviri în `git status --ignored`
                                                    în toate cele trei repo-uri
```

**Ce conține payloadul, onest:** rezolvarea RC-07/RC-08, segmentele lor calendaristice, semantica vizuală citită din capturi, verdictul de eligibilitate, schema matricei per-bară și criteriile PASS/FAIL — totul marcat `blind_eligible: false`, `SEMANTIC_ONLY`. **Zero episoade blind-eligibile, fiindcă zero există.** Conținutul e totuși informație de etichetă despre conceptul-țintă și nu are ce căuta la VE; de aceea e sigilat, iar mecanismul e astfel probat cap-coadă înainte să sosească payloadul real.

**Ce NU pretinde mecanismul:** nu e o afirmație de securitate criptografică — cheia stă pe același disc. Asigură **separare custodială** față de suprafața git citită de VE/Alpha și **detectarea oricărei modificări**. Exact proprietățile de care depinde testul blind.

## Manifestul public (fără intervale, fără etichete)

```json
{
  "escrow_id": "RT-BLIND-ESCROW-RANGE-V2-001",
  "contract_version": "range-blind-escrow-v1.0",
  "data_source_identity": "OANDA:XAUUSD M15, populatia canonica pre-holdout (4 blocuri, 197094 bare)",
  "payload_sha256": "2dcfbeeab5794d5fd5a4921374aaae44a986ab8752caf7b8e8aada9bdaceb362",
  "plaintext_sha256": "95dc4f8ea7870dbae86e0ce8945e38ab8a810c15c09444ebccb73605dfd1b39a",
  "episodes_declared": 2,
  "episodes_blind_eligible": 0,
  "eligibility": {"RC-07": "SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE", "RC-08": "SEMANTIC_ONLY_NOT_BLIND_ELIGIBLE"},
  "bars_count_canonical": {"RC-07": 0, "RC-08": 0},
  "precedence_proof": "sigilat inaintea oricarei rulari Red Team pe 0.3.1; RT-RANGE-0003 declara §4-§6 NEEXECUTATE",
  "intervals_visible_here": false,
  "expected_labels_visible_here": false
}
```

---

# 7 — RULING PE REASON CODES

**Am citit codul, nu documentația.** Verdictul pe fiecare pereche:

| spec Statistician | emis de 0.3.1 | verdict | dovada |
|---|---|---|---|
| `NO_ENTRY_BY_CONSTRUCTION` | `RANGE_MID_NO_ENTRY` | **MAPARE AUTORIZATĂ** — redenumire pură | aceeași gardă F7, `SAFETY_GUARDS_REGISTER` conține exact un element; semantica neschimbată față de 0.2.0 |
| `CHANNEL_UP_SLOPE` / `CHANNEL_DOWN_SLOPE` | `IS_CHANNEL` + `structure_class` | **MAPARE AUTORIZATĂ, BIJECTIVĂ — cu o condiție verificată** | vezi 7.1 |
| `ATR_UNAVAILABLE` | `INPUT_UNAVAILABLE` | **MAPARE AUTORIZATĂ** — ATR e SINGURA intrare care poate lipsi | vezi 7.2 |
| `SLOPE_UNAVAILABLE` | *nimic* | **INACCESIBIL PRIN CONSTRUCȚIE — eroarea mea** | vezi 7.2 |
| `ZONES_DEGENERATE` | *nimic* | **NU E O PROBLEMĂ DE DENUMIRE: GARDA LIPSEȘTE** | vezi 7.3 |
| — | `LEGACY_S_MAX_REJECTED` | **RATIFICAT ca ADĂUGIRE** | vezi 7.4 |

## 7.1 `IS_CHANNEL` singur **nu** e echivalent cu două coduri direcționale — dar nu e niciodată singur

Mandatul cere exact această verificare. Am făcut-o în cod, nu prin impresie:

```
range_state_v2.py:620-621   IS_CHANNEL se adaugă DOAR când structure_class ∈ {CHANNEL_UP, CHANNEL_DOWN}
range_state_v2.py:621       e singura apariție a lui IS_CHANNEL în tot pachetul (grep exhaustiv)
range_state_v2.py:643-644   ACELAȘI obiect returnat poartă `structure_class` ȘI `slope`, obligatoriu, nenul
```

> **Direcția e prezentă OBLIGATORIU în același output, deci maparea e bijectivă: `(IS_CHANNEL, structure_class=CHANNEL_UP) ↔ CHANNEL_UP_SLOPE`. Condiția de care atârnă bijecția, și care devine normativă: reprezentarea de audit trebuie să înregistreze PERECHEA. Un jurnal care păstrează `IS_CHANNEL` și pierde `structure_class` distruge bijecția și colapsează două stări în una. Asta se interzice explicit prin contract.**

`slope > 0 → CHANNEL_UP, altfel CHANNEL_DOWN` tratează `slope == 0` ca descendent — asimetric în aparență, dar ramura se atinge doar când `|slope| · d_min > s_max · ATR ≥ 0`, deci `slope == 0` e inaccesibil acolo. **Non-material**, consemnat ca să nu fie redescoperit ca defect.

## 7.2 `INPUT_UNAVAILABLE` nu colapsează două stări — a doua nu există

```
range_state_v2.py:378-383   singurul drum spre INPUT_UNAVAILABLE este `if atr is None`
range_state_v2.py:349-357   `_slope()` se calculează din close-uri; cu ≥2 close-uri nu poate eșua
```

Panta e mereu calculabilă când producătorul ajunge să o ceară; doar **pragul** ei folosește ATR. Deci ATR e singura intrare care poate lipsi, iar `INPUT_UNAVAILABLE ≡ ATR_UNAVAILABLE` e o **redenumire**, nu o pierdere de informație.

> **`SLOPE_UNAVAILABLE` numește o stare în care mașina nu poate intra. Am scris-o în specificație fără să verific accesibilitatea ei. Se RETRAGE din contract, nu se mapează — a mapa un cod inaccesibil ar sugera că cineva ar trebui să-l aștepte vreodată. E a NOUA eroare a mea prinsă de mine în acest dosar și e din aceeași familie cu `R10`: *o cerință care nu poate fi produsă de output-ul oficial nu e o cerință, ci o bucată de text.***

## 7.3 `ZONES_DEGENERATE` — aici nu e ambiguitate de contract, e o cerință ratificată neimplementată

Manifestul v2.7.80, secțiunea `canonical_config.new_guard`, ratificat:

> `2*w_atr*ATR_ref >= (anchor_up - anchor_dn) → Unavailable, reason ZONES_DEGENERATE (fail-closed by type)`

```
grep exhaustiv „ZONES_DEGENERATE" / „degener" în tot ve_n1_replay, inclusiv teste:   ZERO potriviri
grep după gardă sub ORICE nume (comparație lățime-zonă vs separare-ancore):          ZERO potriviri
```

**Garda nu există.** Nici Red Team nu a semnalat-o, fiindcă atenția lui a fost pe escrow și pe denumiri.

Consecința e cuantificată, nu ipotetică: la `w_atr = 0,30`, degenerarea măsurată pe pozitivele de construcție a fost **0,00% / 0,74% / 0,26%** — mică, dar **nenulă**. Pe acele bare cele două zone de frontieră se SUPRAPUN, deci o singură bară poate „atinge" ambele frontiere simultan, iar range-ul e geometric lipsit de sens. Garda a fost ratificată exact ca să eșueze închis acolo. Fără ea, producătorul emite un range peste geometrie degenerată, **tăcut**.

> **Aceasta, și nu denumirile, e ceea ce impune 0.3.2.**

## 7.4 `LEGACY_S_MAX_REJECTED` — adăugire, ratificată

Nu e în specificația mea fiindcă e un cod la nivel de **parser**: `from_dict()` refuză explicit un câmp `s_max` primit din exterior. E chiar mecanismul care face cuplarea `s_max ≡ 2·w_atr` nereprezentabilă ca doi parametri liberi — cerință ratificată la v2.7.80. **Se ratifică drept adăugire la contract**, cu regula: e o eroare de configurație, niciodată un reason code de stare de piață, și nu apare niciodată în `reason_codes` ale unui rezultat.

## 7.5 Contractul normativ

```
contract_version   range-reason-codes-v2.1     (v2.0 = textul specificației mele; v2.1 = acesta)

COD EMIS              ÎNSOȚITOR OBLIGATORIU     COD SPEC ECHIVALENT        CONDIȚIA EXACTĂ
RANGE_MID_NO_ENTRY    guard field               NO_ENTRY_BY_CONSTRUCTION   eveniment RANGE_MID
IS_CHANNEL            structure_class (nenul)   CHANNEL_UP_SLOPE           structure_class = CHANNEL_UP
IS_CHANNEL            structure_class (nenul)   CHANNEL_DOWN_SLOPE         structure_class = CHANNEL_DOWN
INPUT_UNAVAILABLE     data_readiness=DEGRADED   ATR_UNAVAILABLE            atr is None, după warmup
ZONES_DEGENERATE      —                         ZONES_DEGENERATE           DE IMPLEMENTAT în 0.3.2
LEGACY_S_MAX_REJECTED excepție, nu reason_codes —                          s_max primit din exterior
(retras)              —                         SLOPE_UNAVAILABLE          INACCESIBIL — se șterge din spec

REGULĂ DE COMPATIBILITATE   audit-ul păstrează PERECHEA (cod, însoțitor). Pierderea însoțitorului
                            colapsează informație și INVALIDEAZĂ maparea.
REGULĂ DE VERSIONARE        orice consumator care citește reason codes declară contract_version;
                            nepotrivirea REFUZĂ, nu comentează.
```

---

# 8 — CE TREBUIE SĂ FACĂ VE ÎN 0.3.2

```
1  IMPLEMENTEAZĂ garda ZONES_DEGENERATE, fail-closed prin tip, exact ca la v2.7.80:
     2*w_atr*ATR_ref >= (anchor_up - anchor_dn)  →  Unavailable(reason=ZONES_DEGENERATE)
2  Expune contract_version = "range-reason-codes-v2.1" în output și în manifestul sidecar
3  Garantează în TIP, nu prin convenție, că `structure_class` e nenul ori de câte ori
   reason_codes conține IS_CHANNEL — bijecția trebuie să fie nereprezentabil-încălcabilă
4  ȘTERGE orice referință la SLOPE_UNAVAILABLE, dacă există
5  range_spec_id RECALCULAT → rezultatele 0.3.1 devin NECOMPARABILE PRIN TIP
6  0.3.1 NU se suprascrie, se păstrează pentru audit
7  Restul logicii BYTE-IDENTIC; N1 rămâne byte-identic
8  Citează ACEST commit ca sursă normativă
9  Red Team primește DOAR 0.3.2 pinuit — NU e autorizat pe 0.3.0 și nici pe 0.3.1
```

---

# 9 — ELEMENTE DESCHISE

```
BLOCANT     Nu mai există sursă de semantică independentă în populația canonică. Doar CEO poate
            debloca, livrând capturi noi etichetate vizual din ferestrele eligibile de la §5.2.
            Fără ele, „validare blind" nu e realizabilă — nici de mine, nici de Red Team.
BLOCANT     Garda ZONES_DEGENERATE lipsește din 0.3.1. Impune 0.3.2.
MATERIAL    RC-CONSTRUCTION-CHANNEL-NEW-01 rămâne un control slab: fiind selectat prin chiar
            statistica pe care detectorul o pragează, respingerea lui e aritmetică, nu semantică.
            Nu poate purta singur o concluzie de validare.
MATERIAL    Segmentele RC-07/RC-08 derivate prin pixeli au ±4-6 bare. Irelevant cât timp episoadele
            sunt semantic-only; ar deveni relevant dacă vreodată ar apărea date pentru ele.
LIMITARE    Căutarea de formă compară anvelopa maxim/minim, nu fiecare lumânare. Controlul pozitiv
            arată că e suficientă pentru identificare (r=0,9999, eroare 0 bare) la această scară.
NON-MATERIAL slope == 0 ar fi clasificat CHANNEL_DOWN, dar ramura e inaccesibilă.
```

---

# 10 — INVARIANTE, VERIFICATE NEATINSE

```
n_generated_total = 363 · m_inference = 26 · tombstones · registrul Alpha · verdictele existente
F1-F6 și cele 44: BLOCKED_PENDING_RANGE_SEMANTIC_FIX · F7: SAFETY_GUARD
Alpha NU e autorizat. ALPHA_RANGE_CANONICAL_LEDGER_RERUN NU e autorizat.
Red Team NU e autorizat pe 0.3.0 și nici pe 0.3.1.
BLIND_OUTPUT_NOT_ACCESSED · SEALED/OOS_ACCESS = 0
```

**Manifest:** v2.7.82.
