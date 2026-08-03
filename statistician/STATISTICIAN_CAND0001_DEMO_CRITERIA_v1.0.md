# STATISTICIAN — CRITERII DEMO, CAND-0001 PDH-PDL v2.0 (DEMO_BASELINE)

**Document ID:** STAT-CAND0001-DEMO-CRITERIA-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `POLICY_PDH_PDL_v2.md` (comitul `1558397`, `alpha-automation-v1`), `red_team/policy_reviews/RT-OPS-B-0001_PDH_PDL_v2.md` (`ai_quant_lab`), și `docs/MIN_STOP_FLOOR_PREREG.md` — formula oficială, constantele pre-înregistrate (k_spread=2, k_tick=5, k_atr=0,10), regula INVALID EXECUTION, exact cum sunt citate, nu parafrazate din memorie.

**Constrângerea respectată:** NU proiectez metoda de risc (SL=extrema barei de atingere, țintă=nivelul opus, time-stop=închiderea zilei, sizing=1R — a lui Alpha, înghețată, comitul `1558397`). Definesc DOAR cum se măsoară și ce garduri trebuie să impună motorul de execuție.

---

## Controalele Part A — referite, nereluate

**W-sel, W-conf, W-ovl, W-e010 rămân exact cum au fost specificate în `STATISTICIAN_BATCH_A_0001_PROTOCOL_SPEC_v1.0.md`** — Part A (declanșatorul) e neschimbat față de v1.2, deci controalele asupra lui nu se re-derivă aici. Se aplică neschimbat, alături de gardurile Part B de mai jos.

---

## GARDUL 1 (S1) — coliziune intrabar, ca precondiție executabilă

**Ierarhie worst-case, DERIVATĂ din convenția deja stabilită (nu inventată azi):** acest laborator are deja convenția `stop_before_target=True` (implicit în `partial_exit.py`, Q-A) — stopul câștigă orice ambiguitate de aceeași bară. **Extind ACEEAȘI logică, consecvent, la toate trei coliziunile pe care Red Team le-a semnalat, nu doar la prima:**

```
IERARHIE (worst-case, aplicată în ORDINEA asta la orice bară cu coliziune):
  1. STOP        — dacă bara atinge atât stop-ul cât ȘI oricare altă condiție, STOP câștigă (pierdere).
  2. TIME-STOP   — dacă bara e granița de zi ȘI atinge ținta (dar NU stopul), rezultatul e TIME-STOP
                   (ieșire la închiderea barei), NU ținta — presupunerea optimistă ("ținta a fost atinsă
                   întâi") e exact ce Red Team a interzis.
  3. ȚINTA       — doar dacă nici stopul, nici granița de zi nu se aplică pe acea bară.
```

**INVALID EXECUTION rămâne rezervat EXACT cum spune convenția** (`MIN_STOP_FLOOR_PREREG.md`, linia 29-31) — pentru cazuri pe care ierarhia de mai sus NU le poate rezolva deloc (ex. un gap prin stop-ul podit la intrare, discutat la Gardul 2), NU pentru coliziunile obișnuite stop/țintă/time-stop, care SUNT rezolvate de ierarhie. **Motorul trebuie să arate, per tranzacție, câmpul `intrabar_ordering` aplicat exact conform ierarhiei de mai sus — altfel gardul nu e demonstrat impus.**

## GARDUL 2 (S2) — podeaua `min_executable_risk`, ca precondiție executabilă

**Formula oficială, aplicată exact, cifră cu cifră, din convenția deja pre-înregistrată** (nu recalculată azi):

```
min_executable_risk = max(k_spread × effective_spread, k_tick × tick_size, k_atr × ATR)
                     = max(2 × effective_spread, 5 × tick_size, 0,10 × ATR)
executable_stop_distance = max(strategy_stop_distance, min_executable_risk)
```

unde `strategy_stop_distance` = distanța structurală deja definită de Alpha (`entry − extrema barei de atingere`). **Sizing-ul 1R trebuie calculat pe `executable_stop_distance` (podit), NU pe `strategy_stop_distance` brut.** INVALID EXECUTION doar la: gap prin stopul podit la intrare, sau risc zero/negativ după podire — exact cum spune convenția, nu o excludere mai largă.

**Motorul trebuie să arate, per tranzacție: `strategy_stop_distance`, `min_executable_risk` calculat, `executable_stop_distance` final, și un flag `floored: bool`** — altfel gardul nu e demonstrat impus.

## GARDUL 3 (S3) — ținta deja vizitată mai devreme în zi

**Regulă derivată, nu o metodă nouă de risc — o precizare a FERESTREI DE MĂSURARE:** atingerea țintei se măsoară STRICT pe barele de la `entry_idx+1` înainte — orice atingere a ACELEIAȘI valori de nivel ÎNAINTE de intrare (fie că a declanșat consumarea D7 pe partea opusă, fie o simplă atingere-și-retragere mai devreme în zi) **e irelevantă pentru măsurarea țintei ACESTEI tranzacții.** Nivelul e o coordonată de preț fixă pentru toată ziua — consumarea D7 guvernează doar eligibilitatea de DECLANȘATOR, nu dacă acel preț mai poate fi "atins" ca țintă downstream. Garda deja existentă la intrare (nu se intră dacă next-open e deja dincolo de țintă) rămâne neschimbată — S3 adaugă precizia că FEREASTRA de măsurare a rezultatului pornește curat la intrare, nu accidental mai devreme.

**Motorul trebuie să arate, per tranzacție, că verificarea "țintă atinsă" a scanat DOAR de la `entry_idx+1`, ignorând orice atingere anterioară a nivelului.**

---

## Criterii DEMO — ce se măsoară, cum se raportează

**Per tranzacție (audit obligatoriu, nu opțional):** `intrabar_ordering` (Gardul 1), `strategy_stop_distance`/`min_executable_risk`/`executable_stop_distance`/`floored` (Gardul 2), fereastra de scanare a țintei (Gardul 3), motivul ieșirii (stop/țintă/time-stop/INVALID_EXECUTION).

**Agregat, per regim ȘI agregat total (N_MIN rezervat, vezi mai jos):** winrate, expectancy în R (sizing-invariant, exact apărarea proprie a Part B) ȘI în dolari (calculat pe `executable_stop_distance` podit, Gardul 2 — NU pe distanța brută), edge brut $, net total $, n, best/sumR (concentrare), wo1 (fără cel mai bun trade), fracția PDH vs PDL, **fracția INVALID_EXECUTION** (raportată explicit, niciodată ascunsă sau exclusă tăcut din numitor), fracția rezolvată prin time-stop vs stop vs țintă.

## Cele trei elemente deferite MIE de Alpha — fixate aici

**Verificat direct în `POLICY_PDH_PDL_v2.md`:** linia 50 (Part A), linia 69 (Part B) și linia 93 (handoff) deferă către Statistician `min_trades`, `regimes_permitted` ȘI convenția de cost. Le fixez pe toate trei, nu doar pe prima.

### min_trades = 25 — dar NU e un prag de putere, și precizarea contează

**Corecție de categorie, nu pedanterie:** Alpha îl numește "statistical-power floor". Puterea statistică e definită DOAR relativ la un test — iar DEMO nu rulează niciun test (vezi regula de raportare de mai jos). **Nu poate fi un prag de putere pentru că nu există nicio putere de calculat.** Ce e cu adevărat, mecanic: un **prag de SUPRIMARE a raportării**, identic ca funcție cu cel deja folosit la fișele medicale (v2.7.29).

```
N_MIN = 25, per celulă raportată (per regim, și agregat).
Sub 25: se raportează DOAR n și eticheta INSUFFICIENT_N. Cifrele agregate (winrate,
expectancy R și $, edge brut, best/sumR, wo1) NU se calculează și NU se afișează.
```

**Valoare reutilizată, declarată ca atare, nu re-derivată azi** — e convenția standard a acestui laborator de la Discovery Screen V1 încoace. Motivul suprimării (nu doar etichetării) e neschimbat: un winrate pe 3 tranzacții arată vizual identic cu unul real, oricâte avertismente ar sta lângă el.

**Atingerea lui n=25 NU conferă validitate** — deblochează doar afișarea cifrelor. Un DEMO cu n=200 rămâne exact la fel de neconcludent statistic ca unul cu n=25 (vezi regula de raportare).

### regimes_permitted = TOATE, fără filtru de regim

**Niciun filtru.** Motivul e specific DEMO-ului, nu o preferință generală: regimul istoric (bear/bull/corecție) e o etichetă derivată RETROSPECTIV din blocurile de descoperire — **nu e calculabilă live**, exact distincția pe care am fixat-o la v2.7.30 (regimul e un dispozitiv metodologic de split, niciodată o variabilă de condiționare live). Un cont DEMO rulează ÎNAINTE, în timp real, unde nimeni nu știe în ce regim se află. **A restricționa DEMO-ul pe regim ar fi imposibil de executat onest.** Regimul rămâne o STRATIFICARE DE RAPORTARE retrospectivă (dacă perioada DEMO se suprapune cu unul), nu o condiție de intrare.

### Convenția de cost — OBSERVATĂ, nu modelată (diferența față de backtest)

**Aceasta e distincția centrală a unui cont DEMO față de tot ce s-a măsurat până acum în acest laborator.** În backtest, costul e o constantă modelată (`cost_round_trip`, verificată la sursă la v2.7.8). **Pe DEMO cu fill-uri reale, costul NU se modelează — se OBSERVĂ.**

```
Per tranzacție, obligatoriu: spread-ul REALIZAT la intrare, spread-ul REALIZAT la ieșire,
  slippage-ul REALIZAT pe fiecare (diferența față de prețul cerut), costul total realizat în $.
Agregat, obligatoriu: costul realizat median și mediu, comparat EXPLICIT cu constanta modelată
  a laboratorului — o reconciliere raportată, nu o presupunere tăcută că cele două coincid.
```

**De ce contează dincolo de acest pilot:** dacă spread-ul realizat pe DEMO se abate sistematic de la constanta modelată, asta e o informație reală despre TOATE rezultatele de backtest ale acestui laborator, nu doar despre CAND-0001 — dar se consemnează ca observație, **nu invalidează retroactiv nimic** fără o verificare separată, proprie. Semnalez legătura; nu trag concluzia aici.

**Nota importantă asupra Gardului 2:** `effective_spread` din formula `min_executable_risk` devine, pe DEMO, spread-ul REAL observat, nu unul presupus — motorul trebuie să folosească valoarea realizată, altfel podeaua e calculată pe o presupunere într-un mediu unde adevărul e disponibil.

## Regula de raportare — obligatorie, nu opțională

**DEMO NU E VALIDARE STATISTICĂ. Niciun rezultat de aici nu promovează CAND-0001 (sau orice altă construcție) către producție, ratificare, sau vreun verdict statistic formal.** Nu se calculează niciun p-value, nu se aplică niciun H0/WP-5', nu se consumă familie — motivul e cu atât mai clar decât la fișele medicale sau caracterizarea de execuție anterioare: acesta e un cont DEMO real, un pilot autorizat explicit de CEO, nu o măsurătoare descriptivă și nici un test formal. Orice cifră pozitivă din DEMO **NU e un candidat care "cere pre-înregistrare"** — e literalmente neconcludentă prin design, indiferent cum arată.

---

## CONDIȚIA RED TEAM — păstrată verbatim, nu parafrazată

> **"Dacă motorul DEMO nu poate fi arătat ca impune cele trei garduri, politica NU tranzacționează."**

Aceasta rămâne condiția de poartă, literală, necondiționată de nimic altceva din acest document.

---

## HANDOFF

**Validation Engine** — pentru executabilitate ȘI verificarea mecanică a celor trei garduri (fiecare cu câmpurile de audit specificate mai sus). Dacă oricare gard nu poate fi demonstrat impus în motor, condiția Red Team se aplică direct: politica nu tranzacționează.

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
