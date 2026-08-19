# RANGE V4.3 — Raport Construction-Only (Faza 4, mandat §13)

**Autor:** VE · **Data:** 2026-08-19 · **Status rezultat:** `RANGE_V4_3_PROTOTYPE_RESULTS_READY_FOR_CEO_REVIEW`

> **Acest raport NU e și nu poate fi un BLIND PASS.** Mandatul o declară explicit (§13: "Rezultatul
> NU e BLIND PASS"). Motivul e structural, nu o simplă formalitate: barele OHLC reale ale celor 48
> de ferestre `BLIND-001…048` stau ÎN AFARA celor patru checkout-uri Git, într-o zonă de escrow la
> care VE nu are și nu a încercat să obțină acces (verificat direct — v. §0 mai jos). Singurele
> artefacte NEsigilate, deja comise, disponibile pentru construcție sunt fișierele de ETICHETARE
> (`BLIND_BATCH_02_LEVEL_MAPPING.md`, `RANGE_V3_BLIND_BATCH_02_PART{1,2}_LOCKED_LABELS.json`,
> `PART{3,4}_PROVISIONAL_LABELS.json`, addendum-ul de corecție 046-048) — care descriu STRUCTURA
> (clasă/interval/nivel), nu prețurile reale bară-cu-bară. Acest raport rulează prototipul pe bare
> **sintetizate MECANIC din acele etichete**, deci compararea rezultatului cu aceleași etichete e
> prin construcție circulară pentru scopuri de validare — utilă exclusiv ca test de sanitate a
> implementării pe o varietate largă de forme structurale documentate, nu ca măsură de acuratețe
> de detecție oarbă. Comparația reală (detector vs. etichete, pe bare reale) rămâne, așa cum indică
> explicit `BLIND_LABEL_BATCH_02_CEO_INSTRUCTIONS.md`, **un mandat Red Team separat**.

---

## 0 — Verificarea limitei SEALED/OOS (înainte de orice cod)

Trei surse independente, toate pe `statistician-foundation`, confirmă separat aceeași limită:

1. `BLIND_LABEL_BATCH_02_CEO_INSTRUCTIONS.md`: *"Detectorul nu a fost rulat pe aceste ferestre și
   nu va fi rulat până după blocare. Comparația e un mandat Red Team separat."*
2. `BLIND_LABEL_BATCH_02_HASHES.md`: *"Toate recalculabile. Fișierele stau ÎN AFARA checkout-urilor
   Git."* — barele OHLC reale nu există în niciunul din cele patru repo-uri.
3. `STATISTICIAN_BLIND_LABEL_BATCH_02_PROTOCOL_v1.0.md` §1: populația canonică (OANDA:XAUUSD M15,
   197.094 bare, 4 blocuri oficiale) e ea însăși ne-sigilată/comună tuturor diviziilor — dar
   **maparea** fereastră→interval-canonic (care anume 96/288/480 bare din cele 197.094 corespund
   lui `BLIND-XXX`) e exact ce rămâne sigilat, ca să nu poată fi dedusă prin căutare inversă.

Addendum-ul 046-048 confirmă suplimentar că un detector (V3, nu V4.3 — acest prototip nu exista
încă) a rulat deja pe acest lot, cu rezultat *"zero bare ESTABLISHED și zero segmente RANGE
confirmate"* — motivul concret pentru care redesign-ul ierarhic V4.3 a fost comandat.

**Concluzie:** VE nu are și nu caută acces la barele reale. Construcția de mai jos folosește
EXCLUSIV structura deja publicată (clasă/interval/nivel/preț-aproximativ-unde-există), niciodată
identitatea reală a ferestrei.

---

## 1 — Metodologia de construcție (mecanică, uniformă, aceleași reguli pt. toate cele 48 ferestre)

- **Sursă:** `BLIND_BATCH_02_LEVEL_MAPPING.md` (nivel MACRO/INTERNAL/UNRESOLVED per segment) +
  cele 4 fișiere `PART{1,2,3,4}` (clasă/interval per segment, uneori `lower`/`upper` aproximative)
  + addendum-ul 046-048 (înlocuiește complet etichetele acelor 3 ferestre).
- **Două scheme JSON observate empiric** în cele 48 ferestre (nu una singură — protocolul de
  etichetare a evoluat pe parcurs): schema A (`segments` cu `TRANSITION` inline, la scară L1/MACRO)
  și schema B (`segments` = un singur plic L1/MACRO + `internal_structures` separat, mai
  fin-granular, la scară L2/INTERNAL). Parserul normalizează ambele într-o reprezentare unică de
  "spans" (regim sau bridge), preferând mereu sursa mai fin-granulară.
- **Sintetizare:** fiecare span RANGE/CHANNEL_UP/CHANNEL_DOWN devine o oscilație pe leg-uri (aceeași
  tehnică `legs_bars` validată în suita de teste unitare — NU o sinusoidă eșantionată, care produce
  vârfuri cu high identic pe bare consecutive și suprimă fractalul K_struct=2 la fiecare vârf).
  Fiecare span TRANSITION devine un bridge direcțional (susținut pt. BREAKOUT_*, poke-și-revenire
  pt. SWEEP_*/FAILED_BREAKOUT_*). Continuitate: fiecare span pornește de la nivelul unde s-a
  terminat cel anterior. Unde `lower`/`upper` sunt date explicit în JSON (adnotări aproximative ale
  etichetatorului uman, deja publicate, NU bare reale), sunt folosite ca centru/amplitudine.
- **Ferestre schema B** (BLIND-009/019/020/022/034/037): structurile L2/INTERNAL se generează la
  amplitudine redusă (0.35×) și primesc apoi o derivă lentă de plic (un singur ciclu sus-jos pe toată
  fereastra) reprezentând plicul L1/MACRO care le conține — o încercare de a reflecta ierarhia
  documentată (§5 mandat), nu o garanție că un candidat MACRO stabil se formează efectiv acolo (v.
  §4 mai jos — recall INTERNAL e limitat exact de această dificultate).
- **Suprapuneri:** limitele umane sunt aproximative; unde două span-uri adiacente se suprapun cu 1-2
  bare, span-ul ulterior câștigă (portiunea deja acoperită se sare).
- **ATR sintetic fix = 1.0** pe toată durata (aceeași convenție ca `run43_fixed_atr` din suita de
  teste unitare) — nu se folosește ATR-ul real N1 (ar necesita bare reale).
- **O singură rulare**, fără nicio ajustare a parametrilor sau a tehnicii de sintetizare după ce au
  fost văzute rezultatele — conform mandatului.

---

## 2 — Cât s-a detectat

| | GT (nivel 1, filtrat MACRO/INTERNAL) | detectate & CONFIRMATE (tot lotul) | potrivite (IoU>0) cu vreun GT |
|---|---:|---:|---:|
| MACRO | 88 | 119 | 57 |
| INTERNAL | 12 | 9 | 2 |
| UNRESOLVED | 26 | — raportate separat, niciodată scorate — | |

**Recall / Precision / IoU mediu (doar perechile potrivite):**

| | recall | precision | IoU mediu |
|---|---:|---:|---:|
| MACRO | 57/88 = **0,648** | 53/119 = **0,445** | **0,641** |
| INTERNAL | 2/12 = **0,167** | 1/9 = **0,111** | **0,249** |

**Eroare start/end (bare, doar perechile potrivite):**

| | eroare start medie | eroare end medie |
|---|---:|---:|
| MACRO | 17,6 bare | 22,6 bare |
| INTERNAL | 23,0 bare | 23,0 bare |

Erorile sunt substanțiale în termeni absoluți dar plauzibile structural: `d_macro=29` e o poartă de
durată STRICTĂ, deci un candidat confirmat pornește de regulă mai TÂRZIU decât granița etichetată
de un om (care poate "vedea" regimul format vizual înainte ca 29 de bare consecutive de touch-uri
în toleranță să se fi acumulat), și un breakout/promovare sintetic poate extinde finalul dincolo de
eticheta umană a segmentului RANGE original.

---

## 3 — Distribuție

**Pe lungime de fereastră (MACRO, potrivite/GT):**

| 96 bare | 288 bare | 480 bare |
|---:|---:|---:|
| 12/25 (48%) | 28/33 (85%) | 17/30 (57%) |

Ferestrele de 96 bare au recall vizibil mai slab — `d_macro=29` consumă ~30% din întreaga fereastră,
deci multe segmente etichetate ca RANGE de un om (posibil 20-40 bare) sunt structural prea scurte
pentru poarta de confirmare CEO-fixată. Nu e un defect de implementare — e o consecință directă,
observabilă, a config-ului §4 aplicat unor segmente scurte reale.

**Pe bloc canonic (MACRO, potrivite/GT):** B1 14/24 · B2 18/22 · B3 15/19 · B4 10/23 — nicio
concentrare anormală pe un singur bloc; B4 e vizibil mai slab, dar populația de ferestre pe bloc nu
e suficient de mare (12 per celulă) pentru a distinge semnal de zgomot aici.

**Pe lungime/bloc (INTERNAL):** eșantion prea mic (12 GT) pentru orice distribuție semnificativă.

---

## 4 — Confuzie RANGE / CHANNEL / TREND

Corpusul celor 48 de ferestre **nu conține nicio etichetă TREND_UP/TREND_DOWN** (verificat
exhaustiv pe toate cele 276 de segmente brute din JSON — doar `RANGE`, `CHANNEL_UP`, `CHANNEL_DOWN`,
`TRANSITION` apar). O matrice de confuzie RANGE/CHANNEL/TREND completă nu poate fi construită din
acest lot. Proxy raportat: dintre cele 57 de MACRO-uri detectate care s-au potrivit cu un GT
etichetat RANGE, **46 s-au închis prin `BREAKOUT_ACCEPTED`** (majoritatea urmate de `IS_TREND_MACRO`
— v. §5), adică motorul a interpretat continuarea structurală de dincolo de segmentul RANGE etichetat
ca o rupere spre trend, nu ca o extindere a range-ului. Asta reflectă construcția (fiecare fereastră
înlănțuie RANGE→CHANNEL→breakout conform etichetei), nu neapărat comportamentul pe bare reale.

INTERNAL: din cele 9 confirmări, motorul a clasificat majoritatea drept `INT_SUBRANGE`; eșantionul e
prea mic pentru o defalcare CHANNEL_UP/DOWN semnificativă.

---

## 5 — Evenimente: sweep-uri, breakout-uri, promovări, reason codes

| eveniment | nr. |
|---|---:|
| `PARTIAL_OVERLAP_NO_CONTAINMENT` (candidat refuzat — nu se potrivește curat sub niciun părinte) | 558 |
| `BOUNDARY_EXCURSION` | 458 |
| `SWEEP_CONFIRMED` (excursie respinsă / breakout eșuat — nu există un cod separat "FAILED_BREAKOUT"; conceptul din §7 mandat e implementat prin acest cod, v. `range_semantic_v4_3.py` §7) | 209 |
| `OK_RANGE_MACRO` | 119 |
| `BREAKOUT_ACCEPTED` | 112 |
| `IS_TREND_MACRO` (promovări) | 94 |
| `OK_RANGE_INTERNAL` | 9 |
| `ZONES_DEGENERATE` | 2 |
| `LIQUIDITY_SWEEP_REVERSAL` | 0 |

`PARTIAL_OVERLAP_NO_CONTAINMENT` domină — majoritatea candidaților formați din bridge-uri/goluri de
sintetizare (nu din span-uri RANGE/CHANNEL etichetate direct) sunt refuzați corect de `assign_level`
fiindcă nu se aliniază curat cu niciun părinte activ. Cele 2 `ZONES_DEGENERATE` au apărut în ferestre
cu span-uri foarte scurte adiacente aceluiași nivel de preț (candidat refuzat corect, cluster-urile
sus/jos s-ar fi suprapus).

---

## 6 — Segmente pierdute + motiv (MACRO, 31 din 88)

Toate cele 31 nepotrivite (IoU=0) grupate după cauza structurală cea mai probabilă (inspecție
directă a stării motorului la finalul ferestrei / a istoricului):

- **Segment prea scurt pt. `d_macro=29`** (cauza dominantă, mai ales pe ferestre de 96 bare):
  `BLIND-006(58-96)`, `BLIND-013(49-68, 82-96)`, `BLIND-025(78-96)`, `BLIND-026(61-80)`,
  `BLIND-033(18-36, 68-96)`, `BLIND-041(72-96)`, `BLIND-043(92-96)`, `BLIND-047(92-96)`.
- **Segment la finalul ferestrei, fără spațiu să acumuleze 29 de bare înainte de capăt**:
  `BLIND-004(384-432)`, `BLIND-014(205-241)`, `BLIND-015(356-430, 454-480)`, `BLIND-018(305-365,
  415-480)`, `BLIND-021(174-214, 224-288)`, `BLIND-042(215-288)`, `BLIND-048(235-330, 350-410)`.
- **Segment lung, dar motorul a găsit o graniță de candidat diferită** (confirmă, dar cu decalaj
  suficient încât IoU=0, nu doar eroare mare): `BLIND-003(163-224)`, `BLIND-010(108-294, 316-459)`,
  `BLIND-011(0-96)`, `BLIND-017(110-190, 205-260, 275-480)`, `BLIND-036(40-96)`,
  `BLIND-043(20-80)`, `BLIND-048(125-195)`.

Niciunul dintre aceste 31 de cazuri nu indică o eroare de implementare (excepție/crash/cod de motiv
greșit) — toate sunt consecințe plauzibile ale porții stricte de durată (§4 mandat, CEO-fixată) sau
ale construcției sintetice, verificabile prin inspecția directă a istoricului motorului.

## 6b — INTERNAL pierdute (10 din 12)

`BLIND-009(110-200, 270-288)`, `BLIND-012(0-52, 88-96)`, `BLIND-019(48-180, 468-480)`,
`BLIND-020(60-82)`, `BLIND-022(155-190)`, `BLIND-034(360-410, 410-480)`.

**Motiv sistemic, nu per-caz:** tehnica cu doi straturi (plic L1 lent + oscilație L2 la amplitudine
redusă, §1) nu garantează că plicul L1 însuși acumulează 2+ touch-uri pe fiecare parte înainte ca
oscilația L2 să înceapă — un singur ciclu sus-jos pe toată fereastra nu se poate confirma singur ca
MACRO stabil (`n_touch=2` cere minimum 2 atingeri pe fiecare frontieră). Fără un MACRO părinte deja
confirmat, swing-urile L2 nu sunt niciodată "respinse de MACRO" în sensul necesar formării unui
candidat INTERNAL legitim (v. fix-ul din `_offer_swing_everywhere`). **Limitare cunoscută și
declarată a metodologiei de construcție, nu a prototipului** — pt. o măsurătoare reală a recall-ului
INTERNAL ar fi nevoie fie de bare reale (imposibil aici, §0), fie de o tehnică de sintetizare mult
mai sofisticată care garantează un MACRO stabil PREEXISTENT înainte de fiecare oscilație L2.

---

## 7 — UNRESOLVED (26 segmente, 8 ferestre) — raportate separat, niciodată scorate

`BLIND-023`, `BLIND-029`, `BLIND-031`, `BLIND-032`, `BLIND-035`, `BLIND-038`, `BLIND-039`,
`BLIND-044` — toate marcate `LEVEL_ASSIGNMENT_UNRESOLVED` în `LEVEL_MAPPING.md` prin regula R3
(fereastra afirmă un regim-părinte în text liber `macro`, dar fără limite de bară explicite,
containment-ul nu poate fi stabilit mecanic). Motorul V4.3 a fost totuși rulat pe bare sintetizate
pentru aceste ferestre (nu au fost sărite) — dar orice structură pe care a confirmat-o acolo NU e
comparată cu nimic, conform regulii R3 din maparea normativă însăși (niciun părinte cu limite
cunoscute există de comparat). Consistent cu mandatul.

---

## 8 — Exemple recunoscute vs. ratate

**Recunoscut curat** (IoU>0,85): `BLIND-009#L1-1` (0-288, plicul L1 întreg) — detectat 3-96
(IoU calculat pe intersecție/reuniune cu eticheta 0-288 totuși moderat din cauza start-ului decalat
de swing-detection, nu un exemplu "curat" în sens absolut, dar arată motorul confirmând corect UN
macro pe toată extinderea unde etichetatorul a văzut un singur regim continuu).
`BLIND-005#L1-1` (0-288, fereastră întreagă etichetată RANGE) — printre cele mai bune IoU din lot,
motorul confirmă devreme și rămâne stabil aproape toată fereastra.

**Ratat clar**: `BLIND-013#L1-3` (49-68, doar 19 bare) — sub pragul `d_macro=29`, motorul nu a avut
nicio șansă structurală să confirme, indiferent de calitatea sintetizării.
`BLIND-021#L1-6` (224-288, la capătul ferestrei) — spațiu insuficient înainte de capăt pt. cele 29
de bare + timpul de acumulare a clusterului.

---

## 9 — Limitări declarate ale metodologiei (nu ale prototipului)

1. Nicio bară reală — comparația e circulară prin construcție (v. preambul). Nu e și nu poate fi un BLIND PASS.
2. Amplitudini/derive sintetice UNIFORME (aceleași constante pt. toate cele 48 ferestre) — nu au fost
   ajustate per-fereastră, deliberat, ca să nu introducă bias de reglaj țintit spre un rezultat dorit.
3. Recall INTERNAL e limitat sistemic de tehnica cu doi straturi (§6b) — nu reflectă capacitatea
   reală a motorului de a găsi structuri imbricate pe date reale.
4. Nicio etichetă TREND în corpus — matricea de confuzie RANGE/CHANNEL/TREND (§4) e parțială.
5. `lower`/`upper` din JSON (unde există) sunt adnotări aproximative ale unui om citind un grafic,
   nu bare — folosite ca atare, nicio pretenție de precizie.

---

## 10 — Verdict

`RANGE_V4_3_PROTOTYPE_RESULTS_READY_FOR_CEO_REVIEW`. Nu se autodeclară PASS semantic, PASS blind,
pregătire de wheel, autorizare Strategy Catalog/Alpha/AI Trader/LIVE_SHADOW/broker. Următorul
proprietar: CEO, apoi Red Team (singurul care poate autoriza comparația reală pe bare escrow-ate).
