# STATISTICIAN — VERDICTUL PE TESTUL PERECHE (OBDZ, MĂSURĂTOAREA ÎN TREI BRAȚE)

**Document ID:** STAT-OBDZ-PAIRED-TEST-VERDICT-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

Un singur lucru în acest document: verdictul. Am calculat testul pereche eu însumi — nu am cerut o nouă tură de măsurare. Am reutilizat codul deja ratificat (`obdz_three_arm_windows.py`, comitul `d869177`, neschimbat) pentru a extrage cele 654 de perechi A-C brute la ferestrele `[+2,+5]` și `[+2,+10]`, apoi am calculat testul pe care l-am specificat eu însumi la Mandatul 3.30 (bootstrap perechi, i.i.d. și în blocuri, pe diferența `d_i = MFE_A_i − MFE_C_i`). Script temporar, necomis, șters după utilizare.

**De acord cu constatarea CTO, direct, fără ocolire:** am cerut măsurători, nu teste, de mai multe mandate — pâlnia în atingeri, distribuțiile MAE/MFE, numărătorile de populație, toate descriptive, niciuna cu verdict. Cei +28% au stat necitiți în timp ce specificam măsurători pentru douăsprezece tipuri de zonă care depindeau de acest verdict. Era inversat. Acest document îl repară.

---

## VERDICTUL: SEMNAL, confirmat statistic la nivel agregat, nu doar consistent ca direcție

**Testul pereche pe cele 654 de perechi, fereastra principală `[entry+1,entry+4]`:**

```
                    medie(d)   IÎ 95% (bootstrap)   mediană(d)   IÎ 95%          P(≤0)_medie   P(≤0)_mediană
AGREGAT (n=654)      +0,232    (0,078; 0,389)         +0,137    (0,028; 0,330)      0,0%           0,9%
```

**IÎ-urile EXCLUD zero clar, pe ambele statistici (medie ȘI mediană).** La `[entry+1,entry+9]`: medie(d)=+0,327 (IÎ 0,117-0,548), mediană=+0,166 (IÎ 0,023-0,395) — la fel de clar în afara lui zero. Efectul NU se atenuează în termeni absoluți la fereastra mai lungă (doar procentual, cum am notat la Mandatul 3.30 — diferența relativă scade pentru că și C crește, dar diferența absolută crește).

**Verificare de robustețe la dependența serială — întrebarea de domeniu de la Mandatul 3.30, rezolvată acum, nu doar pusă:** bootstrap în blocuri (L=28, L=10) dă rezultate **aproape identice** cu bootstrap-ul i.i.d. (P(medie≤0): 0,0000 la L=28, 0,0008 la L=10, față de 0,0 la i.i.d.). **Cele două metode converg — incertitudinea de calibrare pe care am semnalat-o nu afectează concluzia.** Rezultatul e robust, nu doar la eșantion, ci și la presupunerea de independență între evenimente apropiate în timp.

## Semnificativ sau doar consistent ca direcție? AMBELE, la niveluri diferite — exact distincția pe care ai cerut-o

**La nivel AGREGAT (n=654): semnificativ statistic, clar, pe ambele metode de bootstrap.** **La nivel PER REGIM (n=156-275, cu cozi grele, exact grija ta):**

```
regim       medie(d)   IÎ                P(≤0)_medie   mediană(d)   IÎ                P(≤0)_mediană
BEAR         +0,269    (0,023; 0,521)      1,5%          +0,076    (0,000; 0,299)       6,9%
BULL         +0,198    (−0,033; 0,440)     4,9%          +0,187    (−0,028; 0,545)     12,2%
CORECȚIE     +0,214    (−0,139; 0,565)    11,1%          +0,247    (−0,060; 0,603)      6,0%
```

**Niciun regim, luat singur, nu trece un prag strict de 5% pe AMBELE statistici simultan.** Toate trei sunt consistente ca DIRECȚIE (medie și mediană pozitive peste tot), dar la n=156-275 cu cozi grele, medianele singure nu decid — confirmat exact, cum ai anticipat. **Concluzia corectă: AGREGATUL (n=654) e cel care poartă dovada; regimurile individuale sunt CORONARE a direcției, nu trei confirmări independente.** Nu se citește separat câte un verdict per regim.

---

## ANOMALIA DIN BEAR — reală ca observație pe raport, dar NU se descompune într-o poveste bear/supply curată

**Am testat separat componentele — nu doar raportul.** Diferența de MAE (A−C), aceeași metodă de bootstrap:

```
regim       medie(MAE_A−MAE_C)   P(≤0)      mediană     P(≤0)
BEAR              +0,262          1,7%       +0,186       8,3%
BULL              +0,401          1,0%       +0,173       1,7%
CORECȚIE          +0,089         29,1%        0,000      59,5%
```

**BULL are diferența de MAE cea mai MARE și cea mai SEMNIFICATIVĂ dintre toate trei — nu bear.** Asta contrazice o poveste curată „bear/supply e diferit". Zona (A) are MAE mai mare decât retragerea (C) în TOATE regimurile (corecție doar nesemnificativ) — nu e un fenomen specific bear. **Raportul MFE/MAE, ca statistică per-eveniment nonliniară, se comportă diferit de diferența separată a celor două componente** (media unui raport nu e raportul mediilor) — asta explică de ce raportul arată „mai prost" în bear (0,43 vs 0,68) fără ca MAE-ul separat să fie bear-specific.

**Stratificarea pe polaritate (agregată peste regimuri, nu per regim), pe diferența de MFE:**

```
polaritate   n     medie(d)   IÎ                P(≤0)_medie   mediană(d)   P(≤0)_mediană
DEMAND       378   +0,255    (0,047; 0,461)       0,8%          +0,151       1,9%
SUPPLY       276   +0,200    (−0,023; 0,428)      4,1%          +0,120       8,3%
```

**Constatare reală, nu artefact — dar modestă, nu o inversare.** Demand e mai robust semnificativ decât supply pe diferența de MFE (raportul de 0,8% vs 4,1%/8,3%) — dar **supply rămâne pozitiv ca direcție, la limita convenției de 5%, nu absent și nu inversat.** Nu e „cerere funcționează, ofertă nu" — e „cerere funcționează mai clar, ofertă funcționează mai slab, la acest eșantion". **Nu schimbă verdictul agregat** (semnal confirmat), dar devine o STRATIFICARE OBLIGATORIE de raportat în ipoteza formală, nu un motiv să restrângem scopul acum.

---

## IPOTEZA FORMALĂ CARE REZULTĂ — OBDZ-002, specificată acum, fără altă tură de măsurare

**O corecție necesară înainte de a specifica stopul:** MAE de 4,4×ATR citat în context e cifra de pe fereastra OARBĂ de 92 de bare (volatilitate generală, relabelată explicit la Mandatul 3.29) — **NU** cifra corectă pentru derivarea stopului. MAE-ul real, pe fereastra de reacție `[+1,+4]`, e mult mai strâns: mediană **~0,85–1,11×ATR** per regim, agregat ponderat **≈0,98×ATR**. Folosesc ACEASTA, nu 4,4×.

```
nume            OBDZ-002 (family=2 cu OBDZ-001)

bias            H1 ȘI H4 aliniate (neschimbat)
intrare         declanșator compus OB-centric (Decizia 3, v2.7.10, NEATINS) + CONFIRMARE
                Varianta 3 (engulfing+magnitudine E010, zero cod nou, Mandatul 3.28): se așteaptă
                o bară de impuls calificată la sau după bara de mitigare t; intrare = next-open
                după confirmare. ATR-ul de sizing = ATR14 la bara de CONFIRMARE (nu la t) — cea
                mai apropiată de intrarea reală.
SL              1,0 × ATR — ALEASĂ, rotunjire declarată a medianei MAE ponderate (~0,98×) pe
                fereastra de reacție reală [+1,+4], NU 4,4× (care măsura altceva)
TP1             2,0 × ATR -> închide 75%, breakeven exact
TP2             3,0 × ATR -> restul de 25%
                (progresia 1×/2×/3× păstrată, consecventă cu tot ce s-a specificat până acum)
plasă           min(entry+20, EOD) — orizontul Grupei A deja stabilit, neschimbat
eligibilitate   podeaua de ATR, re-derivată la SL=1,0× (3×cost/1,0 ≈ 0,6$) — fără plafon
variabila       net_R, ieșire parțială deja înghețată (partial_exit.py)
test            WP-5' block_bootstrap, L≥28, H0: mean(net_R)≤0, α=0,05
familia         2, cu OBDZ-001 — confirmat, schimbarea (confirmare + stop derivat din date reale,
                nu din intuiție) e informată de aceeași descoperire, nu independentă
diagnostic      obligatoriu: stratificare pe polaritate (demand/supply) la orice rezultat
```

**Populația: NU se estimează — se numără, ca prim pas AUTORIZAT, nu ca o tură nouă de diagnostic.** Aceasta e disciplina standard dinaintea oricărei mașini de stare (identică cu LM-001, OBDZ-001) — o numărătoare mecanică, nu o măsurătoare descriptivă suplimentară. Pragul `n≥25`/regim se aplică ca întotdeauna.

**Ce se deblochează ACUM, direct din acest verdict:** VE implementează mașina de stare OBDZ-002 (compus + confirmare + SL/TP/1,0-2,0-3,0×ATR) și rulează, în ordine: (1) numărătoarea de populație (gate INSUFFICIENT_N), (2) testul complet WP-5' pe `net_R`. **Fără nicio măsurătoare intermediară suplimentară.**

---

## Ce rămâne neatins, cerut explicit

Palnia (respecificată OB-centric, Mandatul 3.34) rămâne gata, nefolosită direct de acest verdict. Cele douăsprezece tipuri de zonă rămân specificate, neautorizate. Session Open rămâne nedefinit. Familia (12) neatinsă suplimentar. **Contractul de confluență (Decizia 3, v2.7.10) — NEATINS, folosit exact cum a fost ratificat.**

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.21 (commit `23eb363`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
