# STATISTICIAN — Q1 WP-5' (PRIORITAR), CELE PATRU DEFINIȚII, PRIMITIVELE LIPSĂ (Mandat 3.19)

**Document ID:** STAT-WP5-Q1-DEFINITIONS-PRIMITIVES-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician

**Verificare de sursă:** citit integral `code/wp5_null_generator.py` (commit `db249ee`) și verificat `mypy --strict` direct — curat. Verificat direct în cod: `detect_sweeps` (Definiția 1) confirmă exact formula citată; `detect_level_touches` (Definiția 4, deja citit la Mandatul 3.14/3.17). Recalculat independent statisticile Definiției 3 pe setul de date REAL folosit (`data/market/OANDA_XAUUSD_M15__SUPERSEDED_v1_2022-12-16_to_2026-07-13_R03terminal.csv`, 84.152 bare — nu fișierul curent `M15.csv`, care are 355.696) — cifrele tale ies IDENTICE: 48.321 (57,4%), mediană 0,02, p90 0,095, p99 0,55, >1,00 = 377, >5,00 = 123.

---

## Q1 (PRIORITAR) — invariantul de suprapunere: DISTRIBUȚIA COMPLETĂ, nu doar media

**Decizie: `sample_event_positions` reproduce distribuția EMPIRICĂ completă a spațierii/gradului (histograma deja măsurată de VE), nu doar media 7,64.**

Nu e o alegere între „media" și „distribuția" ca alternative separate — media e o proprietate a distribuției. Reproducând distribuția completă, media rezultă automat, corectă. Alegerea reală era: parametric (ex. proces Poisson cu rată medie 1/6,2, care ar reproduce media dar nu forma/varianța reală) versus empiric (re-eșantionare directă din histograma de grad reală). **Aleg empiric** — motivul e exact același ca la refuzul mapării densitate→φ de la Mandatul 3.17: bateria originală AR(1) a eșuat parțial pentru că un rezumat (φ unic) a ascuns comportament regim-dependent (φ=0,4 trece, φ=0,6 pică) — un null construit doar pe medie ar risca EXACT aceeași ascundere, de data asta pe coada distribuției de grad (evenimente cu 15-26 suprapuneri, nu doar cele tipice de 5-10). `spacing_histogram` există deja ca și câmp în `OverlapNullConfig` — folosește-l direct ca țintă de re-eșantionare, nu doar `target_avg_concurrent`.

**Mecanic:** re-eșantionează pozițiile evenimentelor prin bootstrap direct pe secvența REALĂ de spațieri observate (sau tragere i.i.d. din histograma empirică a spațierii) — nu dintr-un proces parametric cu rată constantă.

Aceasta deblochează `sample_event_positions`.

---

## Q2-Q6 (parțiale/clarificări) — rezolvate

**Q2 — alocare pe segment + graniță:** numărul de evenimente per segment de descoperire (bear/bull/correction) se FIXEAZĂ la cifrele empirice (9.254/7.186/4.614, Mandatul 3.17) — nu se re-eșantionează, pentru consecvență cu auditul deja stratificat pe regim. Fereastra `[c, c+H]` care ar depăși capătul segmentului: **EXCLUSĂ**, nu trunchiată — regula identică celei deja folosite la auditul real (6 evenimente excluse la graniță de orizont, Mandatul 3.17), pentru comparație corectă măr-cu-măr.

**Q3 — structura de sesiune:** **stratificată, nu doar agregat.** Precedent direct în acest lab: bateria AR(1) originală a arătat comportament REGIM-DEPENDENT (φ=0,4 trece, φ=0,6 pică) — un rezumat agregat ar fi ascuns exact acest tip de eterogenitate. Reproduce densitatea per sesiune (london 9,85/ny 9,36 vs asia 6,92/late 6,27) și raportează FPR atât agregat CÂT ȘI per-sesiune, ca să nu se ascundă un buzunar anti-conservator regional.

**Q4 — 69% orizont partajat:** **CONSECINȚĂ DERIVATĂ, nu invariant impus separat.** E algebric, `(H−spațiere)/H` — o dată ce spațierea empirică (Q1) și H=20 sunt reproduse corect, 69% rezultă automat. Impunerea lui separată ar fi redundantă sau, mai rău, ar putea crea un sistem supra-constrâns dacă nu se potrivește exact cu ce produce mecanic spațierea re-eșantionată. Tratează-l ca verificare DUPĂ generare (confirmă că Q1 a fost implementat corect), nu ca țintă de intrare.

**Q5 — distribuția șocurilor:** **empirică, nu normală.** Cozile grele sunt deja un fapt documentat repetat în acest lab (concentrare NET, colaps la cea mai bună tranzacție, distribuții fragile — Mandatele anterioare). Un șoc normal ar SUBESTIMA riscul de coadă, direcția periculoasă (exact avertismentul deja scris în raportul de calibrare original: „supra-declară semnificația"). Aleg reeșantionare bootstrap directă a randamentelor reale per-bară M15 (din barele de descoperire) — fără nicio formă distribuțională presupusă, cea mai puțin arbitrară alegere posibilă.

**Q6 — agregarea pe orizont:** **sumă de șocuri, consistentă cu Q5.** Sub un șoc reeșantionat din randamente reale (nu un proxy artificial), suma șocurilor pe fereastră ESTE reproducerea fidelă a mișcării de preț pe fereastră (`close[c+H]−open[c+1]` e literal suma randamentelor intermediare) — deci nu există o tensiune reală între „sumă" și „reproducere fidelă", odată ce Q5 e rezolvat empiric. **Scop explicit, ca să nu fie extins tacit:** asta calibrează STRUCTURA DE DEPENDENȚĂ pentru FPR, nu reproduce pipeline-ul complet `net_R` (normalizare pe R geometric, cost, direcție) — acela rămâne obiectul testului statistic propriu-zis LM-001, nu al acestei calibrări.

**L rămâne variabil** `{10,20,28,40}` în aval, cum a specificat VE — nu fixez aici.

---

## PRIORITATEA 2 — cele patru definiții

### Definiția 1 — LiquiditySweep: RATIFICATĂ, confirmare nu noutate

Verificat direct în `liquidity_mechanics.py:detect_sweeps` — formula citată e identică, verbatim: `low[c]<p AND close[c]>p` (BELOW), simetric ABOVE. Parametrul `require_close_back_inside=False` există deja exact pentru distincția „dacă închiderea trece dincolo, eticheta se mută la BOS." **Nimic lipsește. RATIFICATĂ ca reconfirmare a D6, nu ca definiție nouă.**

### Definiția 4 — PDH/PDL/Weekly ca repere fixe: RATIFICATĂ

Consistentă exact cu `detect_level_touches` (Mandatul 3.14/3.17): consumare la prima atingere prin fitil, în fereastra de disponibilitate a zilei/săptămânii curente, fără re-armare. **RATIFICATĂ, neschimbată.**

### Definiția 3 — Liquidity Void: PRAG DERIVAT, criteriu HIBRID (nu doar mărime, nu doar timp)

Confirmat empiric (verificat independent, cifre identice): inegalitatea strictă `Open[c+1]≠Close[c]` prinde 57,4% din tranziții, mediană 2 cenți — zgomot de spread, nu discontinuitate. **Nu aleg un prag de mărime izolat — deriv unul, ȘI arăt de ce mărimea singură nu ajunge.**

**Pragul de mărime, derivat:** reutilizez convenția deja stabilită de stres de cost 3× (`3 × 0,40$ = 1,20$`, aceeași logică folosită la podeaua de 10,1 pips a lui LM-001) — un salt sub acest nivel e explicabil prin variabilitatea normală a costului de execuție; peste el, nu. La acest prag: **344 bare** (vs 377 la 1,00$ ales de tine — apropiat, dar derivat, nu ochit).

**De ce mărimea singură nu ajunge — verificat, nu presupus:** am descompus cele două criterii posibile pe același set de 84.152 bare:

| | N |
|---|---|
| doar mărime (>1,20$, FĂRĂ discontinuitate temporală) | **248** |
| doar timp (gol >900s sau weekend, FĂRĂ salt mare) | **119** |
| ambele | 96 |

248 de bare sunt salturi mari FĂRĂ nicio pauză de tranzacționare — exact tiparul „slippage la CPI" pe care l-ai numit, care ar fi INVIZIBIL unui criteriu bazat doar pe timp. 119 sunt pauze reale de tranzacționare (redeschideri de weekend, întreruperi) cu salt mic — INVIZIBILE unui criteriu bazat doar pe mărime. **Niciunul singur nu acoperă conceptul intenționat complet.**

**Definiție finală: `LiquidityVoid` = discontinuitate TEMPORALĂ SAU discontinuitate de MĂRIME (oricare, nu ambele obligatoriu):**
```
temporal:  time[c+1] − time[c] > 900s, EXCLUZÂND fereastra deja documentată de
           mentenanță zilnică (~20:00-21:59 UTC, ≤75 min) — regula EXACTĂ deja
           existentă în code/gapfind.py, reutilizată verbatim
mărime:    |Open[c+1] − Close[c]| > 1,20$ — derivat din stresul de cost 3×
```
O tranziție calificată dacă ORICARE din cele două se aplică — 215 (temporal) + 344 (mărime) − 96 (ambele) = **463 evenimente calificate** pe cele 84.152 bare, verificat direct pe același set de date.

### Definiția 2 — Order Block/Breaker: DOUĂ PROBLEME REZOLVATE

**Problema 1 — contradicția de zonă, decisă:** pentru un OB bearish, corpul e `[Close, Open]` (Open>Close). Formula propusă `[Open, Low]` acoperă corpul PLUS fitilul inferior — o zonă mult mai mare, nu corpul. **Decid: zona activă = CORPUL, `[Close_Bdown, Open_Bdown]`** — textul are dreptate, formula e greșită, se corectează formula. Motiv: fitilul are deja un rol semantic separat, stabilit, în acest laborator (D6: fitil=penetrare/atingere, închidere=confirmare) — dacă zona OB ar include fitilul, „atingerea OB-ului" ar deveni ambiguă (atingere de fitil vs atingere de corp ar însemna lucruri diferite). Păstrarea fitilului EXCLUSIV ca mecanică de atingere (nu ca parte din zonă) menține disciplina deja aplicată la Q4/Q6 MK-03.

**Problema 2 — riscul de circularitate E010, rezolvat prin separare structurală explicită, ÎNAINTE de implementare:**

E010 a picat pentru că fereastra de SELECȚIE („OB nerupt până la orizont") și fereastra de MĂSURARE („a continuat în același orizont") erau IDENTICE (`min(idx+1+480,n)` ambele). Specific acum, separat, ca VE să implementeze din start:

1. **Fereastra de VALIDITATE** (cât rămâne OB-ul activ candidat) — de la formare până la ORICARE din: (a) atingere prin fitil în zonă → consumare D7-analog (folosit o dată, fără re-armare) SAU (b) rupere decisivă prin ÎNCHIDERE dincolo de zonă → devine „breaker" (reutilizat verbatim din criteriul de inversare E010/E012, deja ratificat la Mandatul 3.14: prima închidere ulterioară dincolo de margine). Aceste DOUĂ evenimente sunt DIFERITE — (a) nu implică (b).
2. **Fereastra de MĂSURARE** — începe DOAR la bara evenimentului CALIFICATOR (fie (a), fie (b)), niciodată la formarea OB-ului însuși, și rulează orizontul GRUPA A (20 bare) ÎNAINTE din acel punct.

**Prin construcție, cele două ferestre nu se pot suprapune identic** — validitatea se termină exact quando începe măsurarea, nu sunt aceeași fereastră recalculată de două ori pentru scopuri diferite, cum a fost cazul la E010. Specificat înainte de orice cod, cum ai cerut.

## PRIORITATEA 3 — primitivele lipsă, DOAR cele cerute efectiv

Verificat exact ce cere fiecare familie blocată, din Modulul 5 (Order Flow) și Modulul 6 (Market State) — nu construiesc ce nu e cerut.

**Nu e cerut de nicio familie blocată — NU construiesc:** Order Block, Breaker, Mitigation, Rejection (Modulul 5, deja tratate separat mai sus la Definiția 2, pentru propriile motive, nu pentru vreo familie SMC blocată). Compression (Modulul 6, nicio familie n-o numește).

**Rezolvat integral prin recompunere, fără primitivă nouă (corecție a propriei mele analize de la Mandatul 3.18):**
- **SMC_S12 (Range Rotation)** — NU mai e gol parțial. `Range` se definește precis din primitivele deja ratificate: o pereche de bazine (un suport, o rezistență) din swing-uri CLASIFICATE în ACELAȘI bloc (D4), AMBELE neconsumate (D7), și fără niciun alt swing clasificat de extremitate mai mare între formarea lor și bara curentă (garantează că sunt granița curentă, nu niveluri depășite). Reformalizat, **S12 devine complet formalizabil**, aceeași disciplină ca cele 9 din Mandatul 3.18.
- **SMC_S9, SMC_S20 (MTF-Trend)** — `Trend` multi-timeframe NU cere o primitivă nouă de la zero: aplică `market_structure`-ul deja ratificat (clasificare HH/HL/LH/LL) la fiecare rezoluție, folosind context-ul deja VALIDAT (`H1_from_M15_v2`/`H4_from_M15_v2`/`D1_from_M15_v2`, deja `CONTEXT_DERIVED_VALIDATED` în manifest) — cere ALINIERE (aceeași direcție) pe ≥2 rezoluții. Compoziție din piese deja ratificate, nu o primitivă nouă de cercetare.

**Primitivă nouă, MĂSURA definită acum, pragul specific rămas de derivat separat (nu inventat):**
- **Volatility / Expansion (Modulul 6), cerute de SMC_S4 și SMC_S8:** măsura = standardul OFICIAL deja existent în lab (E000): Parkinson log-range `ln(H/L)`, primar. „Regim de expansiune" (S4) = volatilitatea curentă în percentila superioară a distribuției proprii trailing; „extindere" (S8) = distanță de la un reper normalizată la aceeași măsură. **Pragul exact de percentilă rămâne o derivare separată, propria ei — nu îl inventez acum**, exact disciplina deja aplicată la filtrul LM-001 (nu se alege, se derivă printr-un audit dedicat).

**Rămân genuin negăsibile, chiar și după Modulele 5-6 — nu apar în niciuna din listele date:**
- **SMC_S14 (Momentum Exhaustion)** — cere un indicator tip ROC/RSI. Nu apare nici în Modulul 5, nici în Modulul 6.
- **SMC_S15 (Trend Acceleration)** — cere o rată de schimbare swing-la-swing. Nici `Trend` (Modulul 6) singur nu o acoperă — `Trend` clasifică direcția, nu accelerația ei.

**Gol ieftin, confirmat, extensie a tiparului deja existent (nu Modulul 5/6, ci Modulul 4 la granularitate de sesiune):**
- **SMC_S5, SMC_S6, SMC_S19** — au nevoie de OHLC la nivel de sesiune (deschidere/închidere/maxim/minim per sesiune), nu de o primitivă nouă de cercetare — exact tiparul deja implementat de `institutional_levels` pentru zi/săptămână, aplicat la granițele de sesiune deja stabilite (`mtf.py`). Extensie mecanică, nu Modulul 5/6.

---

**O corecție a S18 primită, nu re-discutată aici:** reclasificarea S18 ca stratificare (nu familie) rămâne cum a fost decisă la Mandatul 3.18 — semnalezi corect că schimbă cum trebuie citit unicul supraviețuitor FDR; nu redeschid acea decizie acum, doar o confirm neschimbată.

**Toate familiile rămân `AWAITING_VALIDATION_ENGINE_CODE`. Holdout SEALED, neatins. Niciun backtest rulat.**

Publicat pe `statistician-foundation`; manifestul se incrementează după publicare.
