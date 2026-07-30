# STATISTICIAN — DOUĂ CALCULATOARE DE PROBABILITATE: REGIM 4H ȘI BIAS 1H (SPECIFICAȚIE, NU EXECUȚIE)

**Document ID:** STAT-HTF-PROBABILISTIC-CONTEXT-DESCRIPTORS-SPEC-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă înainte de a specifica orice:** citit direct `code/market_state.py` — confirmă exact `expansion()` (E010 verbatim: `range>1,5×ATR14[i-1]` ȘI `corp>=0,5×range`) și `compression()` (fereastră STRICT CAUZALĂ de 460 bare, percentila 10, măsura = log-range Parkinson `ln(high/low)`, ambele deja înghețate, Mandatul 3.20-3.21). Citit `code/mtf.py` — confirmă `trend_up=(ema20>ema50).astype(float)`, exact binarul citat. Verificat `HORIZON_GROUP_C_DAY=92` (mediană empirică zilnică, bare M15, Mandatul 3.18) — folosit mai jos ca ancoră pentru orizontul H4.

**Acest document e SPECIFICAȚIE, nu execuție** — exact cum s-a cerut. Nimic din ce urmează nu e autorizat pentru rulare aici.

---

## CONFIRM: niciunul dintre cele două calculatoare nu consumă familia

**Motiv, nu doar afirmație:** ambele sunt descrieri ale STĂRII PIEȚEI (regim de volatilitate/direcție, bias de trend) — NU ating niciodată `net_R`, SL/TP, execuție de tranzacție sau profitabilitate. Nu calculează niciun p-value, nu compară nimic împotriva unui H0, nu emit niciun verdict. **Sunt cu un pas mai departe de un test de ipoteză decât fișele medicale de la mandatul anterior** (care măcar calculau P&L, fără p-value) — aici nu există nici măcar P&L, doar frecvențe empirice ale unor stări de piață deja definite (compresie/expansiune, trend_up). Exact aceeași logică care a scutit deja survey-ul MFE/MAE și fișele medicale de familie se aplică aici, cu și mai puțină ambiguitate.

**Constrângere pe care o adaug explicit, cerută implicit de propria formulare a CTO ("nu sunt strategii, sunt descriptori de context"):** aceste calculatoare NU autorizează, prin simpla lor existență, ca vreo ipoteză VIITOARE să le folosească drept filtru de intrare (ex. "doar tranzacții cu P_LONG>70%") fără ca ACEA construcție specifică să treacă prin propria ei pre-înregistrare și propriul ei consum de familie — exact disciplina deja aplicată de fiecare dată când un lever de frecvență/bias a fost propus în acest track (H4-only bias, Varianta de confirmare, etc.). Descriptorii sunt liberi de consumat; UTILIZAREA lor într-o construcție tranzacționabilă nu e.

---

# CALCULATORUL 1 — REGIM 4H CU PROBABILITATE

## Stările — 3, derivate EXCLUSIV din primitivele deja înghețate, zero invenție nouă

```
Compresie        = is_compressed[i] = True   (compression(), fereastră 460 bare H4, P10, Parkinson)
Trend puternic    = is_compressed[i] = False  ȘI  expansion[i] = True   (E010 verbatim)
Range             = is_compressed[i] = False  ȘI  expansion[i] = False
```

**Regulă de prioritate, declarată explicit (nu ascunsă):** e posibil, matematic, ca o bară să fie SIMULTAN `is_compressed=True` (în coada de 10% a distribuției proprii de 460 de bare) ȘI `expansion=True` (range>1,5×ATR14[i-1], dacă ATR-ul recent era el însuși scăzut, dintr-o perioadă liniștită anterioară). **Compresia are prioritate** — motivul: e criteriul mai strict statistic (o coadă de percentilă fixă, 10%), față de expansiune (un multiplu de ATR, mai puțin rar). Convenție declarată, nu re-derivată, analog altor rezoluții de suprapunere deja acceptate în acest proiect (ex. `stop_before_target=True`).

**Delimitare de scop, explicită:** "Trend puternic" descrie o PROPRIETATE A BAREI CURENTE (o bară de deplasare, nu comprimată) — NU o afirmație despre persistența multi-bară a unui trend. Persistența e tocmai ce calculează probabilitatea de mai jos, separat.

## Probabilitatea — frecvență empirică de PERSISTENȚĂ înainte, nu un model estimat

**Ce înseamnă "82%":** nu e încrederea în clasificarea barei curente (asta e deja un fapt cauzal, determinist, odată ce bara s-a închis) — e probabilitatea empirică ca STAREA curentă să se mențină peste un orizont dat, estimată prin numărare directă pe istoric, nu printr-un model ajustat.

**Orizontul, derivat, nu ales arbitrar:** reutilizez `HORIZON_GROUP_C_DAY=92` (mediană empirică zilnică, bare M15, Mandatul 3.18) — pe H4 (16 bare M15/bară H4), 92/16=5,75 ≈ **6 bare H4 ≈ 1 zi de tranzacționare**. Derivat dintr-o constantă deja stabilită, nu inventat.

```
PENTRU fiecare bară i (fereastra de estimare, vezi split mai jos), cu starea S(i):
  verifică dacă bara i+6 are ACEEAȘI stare S(i) (verificare punctuală, nu majoritate pe fereastră —
    mai mecanic, fără o decizie suplimentară de agregare)
P(S | fereastra de estimare) = (numărul de bare cu starea S unde S se menține la i+6) / (numărul total
    de bare cu starea S în fereastra de estimare)
```

**Raportare, per stare, agregat ȘI per regim** (bear/bull/corecție — consecvent cu tot restul acestui track, chiar dacă nu cerut explicit aici — semnalez asta, nu o adaug tacit).

---

# CALCULATORUL 2 — BIAS 1H CU [P_LONG, P_SHORT]

## Stările — 2, identice cu binarul deja existent, doar reconvertite probabilistic

```
UP (bias long)   = h1_trend_up = True   (ema20 > ema50, neschimbat)
DOWN (bias short) = h1_trend_up = False
```

## Probabilitatea — frecvență CONDIȚIONATĂ de ordinul 1 (lanț Markov prin numărare directă)

**Aleg frecvența condiționată de ORDINUL 1** (condiționată doar de starea CURENTĂ, nu de un istoric mai lung) — motiv: cu doar 2 stări, ordinul 1 dă 2 celule de condiționare, robuste statistic; ordinul 2 ar da 4 celule, ordinul 3, 8 — subțiind rapid eșantionul per regim, fără un beneficiu clar declarat. Nu o alegere arbitrară — un compromis explicit între informativitate și robustețea eșantionului.

```
Orizont: 4-12 ore, raportat ca INTERVAL, nu colapsat la un singur punct fără motiv —
  punct primar = 8h (mijlocul intervalului cerut), plus 4h și 12h ca verificare de sensibilitate.

PENTRU fiecare bară i (fereastra de estimare) cu starea curentă S(i) ∈ {UP, DOWN}, orizont H ∈ {4,8,12}:
  verifică starea la bara i+H
P_LONG(S_curent, H) = (numărul de bare cu starea S_curent unde starea la i+H = UP)
                     / (numărul total de bare cu starea S_curent, în fereastra de estimare)
P_SHORT = 1 − P_LONG   (doar 2 stări, complementaritate exactă — verificare de consistență, nu asumpție)
```

**Raportare: per stare curentă (UP/DOWN) × orizont (4/8/12h) × regim + agregat.** Sesiunea NU se folosește ca stratificare aici — semnalez, nu decid tacit: NU e o omisiune, ci o alegere: bara H1 SE aliniază curat cu granițele de sesiune (spre deosebire de H4, care le traversează), deci o extindere pe sesiune ar fi FEZABILĂ dacă CTO o dorește — o las ca opțiune deschisă, nu o adaug neceută.

---

## Fereastra de estimare vs. fereastra de aplicare — splitul, pentru AMBELE calculatoare

**Reutilizez granițele de regim DEJA stabilite, nu invenția unui procent arbitrar:**

```
ESTIMARE   = bear + bull (2011-08 → 2020-07, ≈4,408 ani, ~80% din descoperire)
APLICARE   = corecție (2020-07 → 2022-10, ≈1,068 ani, ~20% din descoperire)
```

**Motiv:** graniță deja existentă, nu o fracțiune procentuală nouă — și corecția e regimul cel mai APROPIAT cronologic de holdout-ul real (sigilat, neatins), făcând testarea pe ea cea mai relevantă verificare de generalizare din descoperire disponibilă. **Holdout-ul rămâne complet neatins — acest split e intern descoperirii, nu îl afectează.**

**Distincție critică, de reținut:** graniță de regim aici e un DISPOZITIV METODOLOGIC pentru validarea generalizării (folosit O SINGURĂ DATĂ, la calibrare) — NU o variabilă de condiționare LIVE în formula de probabilitate. "Care regim istoric suntem" nu e ceva calculabil live, azi; NU intră în calculul lui P_LONG/P(regim) — doar STAREA curentă (compresie/expansiune, h1_trend_up), ambele calculabile live, intră în formule.

## Regula pentru celule mici — reutilizată, neschimbată

**N_MIN=25**, identic cu tot restul acestui track. Sub prag: SUPRIMĂ cifra (nu doar etichetează), raportează doar `n` și `INSUFFICIENT_N` — aceeași disciplină fixată la mandatul anterior, pentru același motiv (o cifră mică arată vizual la fel de convingătoare ca una reală).

---

## Ce NU se autorizează aici

Nicio rulare, nicio implementare. Acest document e specificația completă — implementarea (dacă și când e cerută) ar fi un pas separat, autorizat separat.

---

**Publicat pe `statistician-foundation`; manifestul se incrementează.**
