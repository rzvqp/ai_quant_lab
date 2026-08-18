# STATISTICIAN — PROTOCOL PRE-ÎNREGISTRAT: CONTROL NEGATIV NOU ȘI FIXAREA `w_atr`

**Document ID:** STAT-RANGE-V2-PREREG-PROTOCOL-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Decizie CEO consumată:** OPȚIUNEA A.
**★ ACEST DOCUMENT SE COMITE ÎNAINTE DE A ATINGE ORICE DATĂ PENTRU NOUL EPISOD. Commit-ul lui e dovada de precedență cerută la livrabilul 2. Orice rezultat publicat ulterior se raportează la ACEASTĂ versiune.**

---

# PARTEA 0 — VERIFICARE GIT ȘI CONFIRMĂRI

```
7c0987d  document Statistician (w_atr BLOCKED, s_max derivat)                    ✔
4fd6bdc  manifest v2.7.79                                                        ✔
fingerprint content_hash v2.7.79 = 55c08b32204e8a4345ba577c59be20e8b2b6a580b37c84a6b728404af95c61e3  ✔ MATCH
d307aec  VE 0.3.0 build · 22e1496 delivery                                       ✔
wheel 0.3.0 SHA-256 34603375… verificat prin re-hash la mandatul anterior        ✔
defaulturi VE NERATIFICATE: w_atr = 0.25 · s_max = 0.15                          ✔
n_generated_total = 363                                                          ✔
```

**CONFIRM: RC-07 și RC-08 NU au fost accesate — nici intervalele lor canonice nu au fost rezolvate vreodată. CONFIRM: RC-06 NU mai e tratat ca blind independent, fiindcă `RC-06 ⊂ RC-05` și RC-05 e în construcție.**

---

# 1 — POPULAȚIA ELIGIBILĂ

```
simbol / timeframe   XAUUSD / M15
bare                 CANONICE, cele 197.094 livrate de loaderul pre-holdout (4 blocuri oficiale)
excluse (SEALED/OOS) tot ce e în afara celor 4 blocuri; 2025-11+ ; range1.pdf ; range2.pdf
excluse (corpus)     intervalele canonice ale RC-03, RC-04, RC-05 și RC-06:
                       RC-03  2016-12-20 → 2016-12-27
                       RC-04  2016-09-21 → 2016-10-31
                       RC-05  2022-12-16 → 2022-12-30
                       RC-06  ⊂ RC-05, deci acoperit de excluderea lui RC-05
                     plus o BANDĂ TAMPON de 96 bare de fiecare parte a fiecărui interval exclus,
                     ca fereastra selectată să nu partajeze nicio bară cu ele.
```

## RC-07 / RC-08 — cum se garantează non-suprapunerea fără a le atinge

> **Nu le cunosc intervalele și NU le rezolv, fiindcă rezolvarea ar însemna atingerea lor. Rezolvarea e procedurală, nu probabilistică: regula de selecție de la §2 e DETERMINISTĂ și INDEPENDENTĂ de orice cunoaștere a poziției lor — ieșirea ei nu s-ar schimba nici dacă le-aș ști. Verificarea de non-suprapunere se DELEGĂ Red Team, care deține intervalele.**

```
CLAUZĂ DE REZERVĂ, PRE-DECLARATĂ ACUM: dacă Red Team constată că fereastra selectată se
suprapune cu RC-07 sau RC-08 (fie și o singură bară), se ia URMĂTOAREA fereastră în ACEEAȘI
ordine deterministă, fără nicio altă schimbare. Se repetă până la prima fereastră fără
suprapunere. Nicio discreție nu intră: ordinea e fixată aici.
```

---

# 2 — REGULA DETERMINISTĂ DE ALEGERE A UNUI SINGUR EPISOD

```
LUNGIME       L = 96 bare M15 (clasa MULTIDAY_RANGE, constanta deja derivată)
FERESTRE      NESUPRAPUSE, aliniate pe indexul barei canonice: [0,96), [96,192), …
              Alinierea pe index — nu pe calendar — ca reproducerea să fie exactă.
ORDINE        CRONOLOGICĂ STRICTĂ, crescătoare după indexul primei bare.
SELECȚIE      PRIMA fereastră, în această ordine, care satisface criteriul de canal (§3).
              NU „cea mai bună". NU „cea mai clară". PRIMA.
```

**Regula e reproductibilă de o altă echipă din același corpus fără nicio informație suplimentară de la mine.**

---

# 3 — DEFINIȚIA INDEPENDENTĂ A UNUI CANAL

**Nu folosește `RANGE_STATE`, nu folosește producătorul, nu folosește niciun output al detectorului. Geometrie pură pe bare închise.**

```
DERIVA        slope = OLS pe `close`, x = 0..L−1 (INDICI DE BARĂ)
              S = |slope| × L / ATR_ref                       [adimensional]
              ATR_ref = ATR(14) M15 la ULTIMA bară a ferestrei (index L−1 în fereastră), CAUZAL
OSCILAȚIA     r_j = close_j − (a + b·x_j)   (rezidualele față de dreapta OLS)
              n_cross = numărul de SCHIMBĂRI DE SEMN ale seriei r
CANAL  ⟺  S >= 2,0   ȘI   n_cross >= 4
```

## De ce `S >= 2,0` e DERIVAT, nu ales

> **`s_max ≡ 2·w_atr`, iar `w_atr < 0,495` (limita de disjuncție stabilită la v2.7.79) ⇒ `s_max < 0,99`. Cerând `S >= 2,0`, controlul negativ stă la un factor >2 DEASUPRA oricărui `s_max` admisibil. Deci verdictul lui — „nu e range" — e INSENSIBIL la valoarea finală a lui `w_atr`. Pragul nu e o alegere: e consecința intervalului deja publicat.**

**`n_cross >= 4` e PARAMETRIC LIBER: numără schimbări de semn, fără niciun prag numeric. Distinge un CANAL (oscilează în jurul unei drepte înclinate) de un TREND PUR (nu revine peste dreaptă).**

```
SENS   slope > 0 → CHANNEL_UP        slope < 0 → CHANNEL_DOWN
LUNGIME ADMISĂ   exact L = 96 bare. Minim = maxim = 96. O fereastră unică, nu un interval elastic.
```

---

# 4 — REGULA NUMERICĂ EXACTĂ CARE FIXEAZĂ `w_atr`

**Intervalul rămâne `0,10 <= w_atr < 0,495`. `1,00×ATR` e INTERZIS (degenerare de zone sub geometria V2). Punctul se obține dintr-o MĂSURĂTOARE plus o REGULĂ, nu dintr-o alegere.**

## 4.1 Limita INFERIOARĂ — din validitatea atingerii prin fitil

```
Pe POZITIVELE de construcție (RC-03, RC-04, RC-05), pe ferestre de L = 96:
  anchor_up = MEDIANA high-urilor swing-urilor high confirmate din fereastră
  BARĂ DE RESPINGERE SUS := high_j > anchor_up  ȘI  close_j < anchor_up
  overshoot_j := (high_j − anchor_up) / ATR_ref
  simetric jos: low_j < anchor_dn ȘI close_j > anchor_dn ; overshoot := (anchor_dn − low_j)/ATR_ref

w_lower := MEDIANA overshoot-urilor, peste ambele laturi și toate cele trei episoade, pooled.
```

> **De ce MEDIANA și nu o altă cuantilă: e ACEEAȘI convenție deja ratificată pentru ancoră, aleasă acolo pentru non-monotonicitate. Reutilizez convenția existentă în loc să introduc o cuantilă nouă. „Respingerea tipică prin fitil trebuie să se înregistreze ca atingere" e cerința; mediana e definiția lui „tipică".**

## 4.2 Limita SUPERIOARĂ

```
w_upper := min( 0,495 ,  S_channel / 2 )
   0,495     din disjuncția zonelor (v2.7.79, separarea ancorelor p05 = 0,99 ATR)
   S_ch / 2  din cerința ca noul control să NU fie clasificat range: respingerea pe axa pantei
             cere S_channel > s_max = 2·w_atr  ⟺  w_atr < S_channel / 2
```

## 4.3 REGULA DE FIXARE — un singur punct, reproductibil

```
LATTICE    L05 = {0,10 · 0,15 · 0,20 · 0,25 · 0,30 · 0,35 · 0,40 · 0,45}   (pas 0,05, declarat)
w_atr  :=  cel mai MIC element din L05 care este >= w_lower
```

> **Direcția e conservatoare și e argumentată, nu preferată: `w` mai MARE ⇒ `s_max = 2w` mai mare ⇒ un canal e MAI UȘOR admis ca range. Deci `w` mic e direcția SIGURĂ față de misclasificarea canalelor. Iau cea mai mică valoare din rețea care satisface totuși cerința de fitil — adică minimul admisibil, nu mijlocul unui interval. Asta evită exact eroarea pe care am comis-o de două ori: „alegerea atentă a mijlocului".**

## 4.4 CONDIȚIA DE BLOCARE, pre-declarată

```
BLOCKED  `RANGE_V2_W_ATR_STILL_NOT_IDENTIFIED`  dacă ORICARE:
  (a) niciun element din L05 nu satisface  w_lower <= w < w_upper   (interval vid pe rețea);
  (b) w_lower nu e calculabil (zero bare de respingere pe pozitivele de construcție);
  (c) nicio fereastră din populația eligibilă nu satisface criteriul de canal (§3);
  (d) valoarea rezultată NU e stabilă: dacă `w_atr` calculat pe fiecare episod pozitiv SEPARAT
      diferă de valoarea pooled cu mai mult de un pas de rețea (0,05), rezultatul depinde de
      un singur episod și NU se publică.
NU adaug episoade suplimentare până apare o valoare convenabilă. O singură rulare, o singură
selecție, verdictul care iese.
```

---

# 5 — CE SE ÎNREGISTREAZĂ PENTRU NOUL CONTROL

```
episode_id     RC-CONSTRUCTION-CHANNEL-NEW-01
rol            CONTROL NEGATIV DE CONSTRUCȚIE
               NU blind · NU ipoteză · NU produce p-value · NU intră în Alpha · NU pentru PnL
               NU modifică `m_inference` (26) și NU modifică `n_generated_total` (363)
de fixat ÎNAINTE de sweep-ul lui `w_atr`:
   intervalul EXACT de bare (index canonic + epoci UTC) · sensul canalului · S · n_cross
   structural_start_ts · confirm_ts · limitele episodului · motivul canal-nu-range
   hash-ul datelor consumate · regula independentă care l-a selectat
```

---

# 6 — INTERDICȚII, REAFIRMATE

```
zero acces RC-07 · zero acces RC-08 · RC-06 NU se folosește ca blind ·
range1.pdf și range2.pdf NEATINSE · zero SEALED/OOS · zero PnL · zero strategie ·
zero cost gate · zero p-value · zero Alpha · zero AI Trader · zero LIVE_SHADOW
INVARIANTE: n_generated_total = 363 · m_inference = 26 · tombstones · registrul Alpha ·
verdictele existente · F1-F6 și cele 44 `BLOCKED_PENDING_RANGE_SEMANTIC_FIX` · F7 `SAFETY_GUARD`
```

---

# 7 — ORDINEA DE EXECUȚIE, OBLIGATORIE

```
1. ACEST document se comite și se împinge.                     ← dovada de precedență
2. Abia apoi se rulează selecția (§2-§3) pe populația eligibilă.
3. Abia apoi se calculează `w_lower`, `w_upper` și `w_atr` (§4).
4. Rezultatul se publică într-un commit SEPARAT, care citează commit-ul acestui protocol.
Dacă pasul 3 nimerește condiția de blocare (§4.4), se publică BLOCKED. Nu se revine la §2.
```

---

**Manifest:** acest protocol se înregistrează în `config/split_manifest.json` v2.7.80 împreună cu rezultatul, dar commit-ul lui în `ai_quant_lab` PRECEDE orice execuție.
