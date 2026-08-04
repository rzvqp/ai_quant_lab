# STATISTICIAN — CRITERIUL DE TRIAJ, GESTIUNEA FAMILIEI, ȘI PROTOCOALELE LOTULUI DE SESIUNE

**Document ID:** STAT-TRIAGE-CRITERION-BATCH-PROTOCOLS-v1.0
**Data:** 2026-07-30 · **Autor:** Statistician

**Verificare de sursă:** citit direct `reports/phase1_screening_results.json`. **Cifra citată pentru CAND-0020 se confirmă exact (n=34.006, −15.408,7 R).** Dar citirea completă a fișierului arată că **cei șase NU sunt un grup uniform** — vezi mai jos.

---

# PARTEA 0 — CEI ȘASE NU SUNT ÎN ACEEAȘI CATEGORIE

```
candidat   politică                    n        total R      R/tranzacție
0020       LIQUIDITY-SWEEP-RETURN   34.006    −15.408,7        −0,453
0021       BOS-RETEST               11.477     −8.194,0        −0,714
0022       CHOCH-REVERSAL           18.168     −2.846,2        −0,157
0023       LEVEL-BOS-CONFLUENCE          7        −1,9        −0,266   ← n=7 !!
0024       SWEEP-FVG-CONFLUENCE     18.852     −2.605,3        −0,138
0025       SWEEP-OB-CONFLUENCE       7.088     −1.369,9        −0,193
```

**CAND-0023 are n=7. Nu e „decisiv negativ" — e SUB pragul de raportare (N_MIN=25) de patru ori.** −1,9 R pe 7 tranzacții e zgomot, nu dovadă. **A-l arhiva ca „negativ" ar fi o eroare de categorie: absența dovezii nu e dovada absenței** — exact distincția pe care am impus-o în tot acest track.

**Și tiparul e familiar:** `LEVEL-BOS-CONFLUENCE` e o **CONJUNCȚIE** de două condiții — iar conjuncțiile produc populații mici prin construcție. **E aceeași formă ca PWH/PWL (n=6), unde am arătat că degenerarea venea din ÎNCADRARE, nu din mecanism.** CAND-0023 merită aceeași descompunere de pâlnie, nu o arhivare.

---

# PARTEA 1 — CRITERIUL DE TRIAJ, cu TREI rezultate, nu două

```
A. ARHIVAT-NEGATIV     n >= N_MIN în fiecare regim  ȘI  expectanță negativă în TOATE
                       regimurile  ȘI  niciun an pozitiv.
                       ⇒ semnul e STRUCTURAL, nu marginal. Nu consumă familie.

B. ARHIVAT-INSUFICIENT n < N_MIN într-un regim ⇒ candidatul n-a fost NICIODATĂ testabil.
                       NU e dovadă negativă. Cere descompunere de pâlnie înainte de orice
                       concluzie. Nu consumă familie.

C. PROTOCOL FORMAL     orice altceva — semn mixt, marginal, sau pozitiv undeva.
                       Consumă un slot de familie.
```

**De ce „niciun an pozitiv ȘI niciun regim pozitiv" e criteriul potrivit, nu o cifră agregată:** un edge real degradat de cost sau execuție ar arăta **măcar o subperioadă pozitivă**. Negativitatea uniformă pe fiecare an și fiecare regim înseamnă că semnul e structural — un test formal ar doar confirma, cheltuind un slot de familie pentru o concluzie deja evidentă.

**Aplicat:** 0020, 0021, 0022, 0024, 0025 → **A (arhivat-negativ)**. 0023 → **B (arhivat-insuficient)**. **Niciunul → C.**

## Verificarea de robustețe pe care o adaug: rezistă arhivarea corecției de cost?

**Singura revizuire cunoscută în curs e costul ($0,20 → posibil $0,05).** Beneficiu maxim ≈ 0,15$/tranzacție ≈ **0,075 R** (la R ≈ 1×ATR ≈ 2$ în epoca de descoperire). Aplicat:

```
0020  −0,453 → −0,378     0021  −0,714 → −0,639     0022  −0,157 → −0,082
0024  −0,138 → −0,063     0025  −0,193 → −0,118
```

**Niciunul nu se apropie de zero. Arhivarea e robustă la singura revizuire cunoscută în curs.** Verificare aproximativă (R variază per tranzacție) — **dacă corecția de cost iese material mai mare decât presupun, 0022 și 0024 sunt cele mai apropiate de zero și ar fi primele de reexaminat.** Le numesc acum, ca reexaminarea să nu fie o alegere de conveniență ulterioară.

## Ce înseamnă ARHIVAT — și ce NU înseamnă

**Arhivat ≠ respins statistic.** Niciunul n-a fost testat formal, deci niciunul n-a fost infirmat. Eticheta corectă e **„nu merită un slot de familie la dovezile actuale"**. Dacă dovezile se schimbă — o corecție de cost materială, sau o re-încadrare ca la CAND-0006 — un candidat arhivat poate reveni, **și atunci consumă un slot.** Nu e o poartă gratuită.

---

# PARTEA 2 — FAMILIA: două registre distincte, nu unul

**Aici e miezul întrebării, și răspunsul cere separarea a două lucruri care se confundă ușor:**

```
REGISTRUL DE FAMILIE (pentru α)       câte ipoteze au fost TESTATE FORMAL (p-value + verdict).
REGISTRUL DE EXPLORARE (pentru onestitate)  câți candidați au fost PRIVIȚI, indiferent de rezultat.
```

**De ce arhivarea negativilor NU încalcă disciplina de testare multiplă:** corecția FDR protejează împotriva **FALSELOR POZITIVE** — controlează fracția de *respingeri* care sunt false. **Un candidat care nu e testat nu produce nicio respingere. Un candidat decisiv negativ, arhivat, nu produce nicio respingere.** Deci arhivarea negativilor **nu poate umfla FDR-ul.** Nu e o scăpare — e o consecință a ce măsoară FDR.

**Dar biasul pe care arhivarea CHIAR l-ar crea, dacă e nedeclarată, e altul: rata de reușită aparentă.** „Am testat 7, 3 au mers" ar fi grav înșelător dacă 19 au fost examinați. **De aceea registrul de explorare trebuie ținut, vizibil, chiar dacă nu intră în α.**

**Cele două numere servesc scopuri diferite și nu trebuie amestecate. Asta rezolvă tensiunea din mandat: nu e nevoie să alegi între „a testa tot" (distrugând puterea) și „a arhiva tăcut" (ascunzând explorarea).**

## Regula, fixată acum

```
FAMILIA = 7 + K,  unde K = numărul de candidați care TREC TRIAJUL și sunt testați formal.
  lotul MK (0020-0025):        K += 0   — cinci arhivați-negativ, unul arhivat-insuficient
  lotul sesiune (0026-0031):   K += (câți trec criteriul de mai sus, DUPĂ screening)
EXPLORARE = 7 + 12 + tot ce urmează = numărul de candidați PRIVIȚI. Raportat lângă orice rezultat.
```

**Criteriul e fixat ÎNAINTE ca screening-ul de sesiune să se încheie** — deci nu poate fi ajustat pe rezultate. Exact tiparul folosit la V1/V2/V3 (familia = 2+K, regula fixată înainte de numărători).

**Dependența, verificată:** 0026 ⊂ 0027, iar 0029/0030/0031 ⊂ 0027 + a doua structură — relații de **submulțime, deci dependență POZITIVĂ**, compatibilă PRDS ⇒ **BH rămâne valid.** (Spre deosebire de perechea CAND-0001↔CAND-0009, singura cu dependență negativă, deja rezolvată prin partiție.)

---

# PARTEA 3 — PROTOCOALELE LOTULUI DE SESIUNE (0026-0031), condiționate de triaj

**Elementele comune sunt cele de la STAT-BATCH-A-0001/A-0002, reutilizate neschimbat:** cele 3 regimuri; N_MIN=25 cu suprimare-nu-etichetare; oracolul WP-5' block_bootstrap (L≥28) pe `net_R`; **BH-FDR α=0,05 peste familia de 7+K**; holdout sigilat; walk-forward 2 pliuri pe granițele de regim deja stabilite.

## W-incr — obligatoriu pentru patru din șase

```
0026 ⊂ 0027                         H0: mean(net_R_0026) <= mean(net_R_0027 | ACELEAȘI bare)
0029, 0030, 0031 ⊂ 0027 + structură  H0: mean(net_R_sub) <= mean(net_R_0027 | ACELEAȘI bare)
```
**Pe subsetul EXACT de bare unde declanșează subsetul, niciodată pe populația mai mare a părintelui, niciodată contra unui null aleator.** Identic cu CAND-0007 și CAND-0010.

## CAND-0028 — regula „latura de apropiere" e o IPOTEZĂ, și trebuie testată ca atare

**La `session_levels.py` am stabilit că `Mid` nu are latură intrinsecă și că orice politică trebuie să DECLARE cum se determină direcția. Alpha a declarat „latura de apropiere". Dar a declara o presupunere nu o validează** — iar aici presupunerea poartă **întreaga direcție a tranzacției**.

**Nulul potrivit nu e zero — e regula INVERSĂ:**

```
H0 (componenta de direcție) :  mean(net_R | latura de apropiere) <= mean(net_R | latura INVERSĂ),
                               pe ACELEAȘI bare de atingere.
```

**Motivul:** un rezultat pozitiv contra lui zero ar putea proveni integral din faptul că atingerile de Mid au un edge într-o direcție *oarecare*, cu regula de apropiere neadăugând nimic. **Doar comparația cu regula inversă izolează contribuția presupunerii.** Aceeași logică incrementală ca la W-incr, aplicată unei reguli de DIRECȚIE în loc de un filtru.

## Alinierea de feed — precondiție DEMO, nu element de protocol

**„Asia High din backtest nu e Asia High live"** e o problemă de **transfer backtest→live**, nu de validitate a backtestului. **Nu afectează protocolul statistic** (care rulează pe date de descoperire). **Devine precondiție OBLIGATORIE înainte ca oricare din cei șase să atingă DEMO:** nivelul de sesiune calculat live trebuie verificat că se potrivește cu cel calculat în backtest. **Aceeași categorie cu „costul e OBSERVAT, nu modelat"** — un gol de transfer, rutat la etapa unde contează.

---

# PARTEA 4 — DOUĂ CONSEMNĂRI, una despre propria mea alarmă

## F4 la CAND-0022: alarma mea a fost măsurată și e ZERO

**Verificat direct în `phase1_screening_results.json`:** `ambiguous_dual_sign_choch_bars_per_regime = {bear: 0, bull: 0, correction: 0}, total: 0`.

**La v2.7.38 am semnalat că noua semantică de cascadă LĂRGEȘTE suprafața lui F4. Măsurat: zero bare, în toate regimurile.** Semnalarea a fost corectă ca precauție — riscul era real teoretic — **dar empiric e nul.** Consecință: **regula de no-trade la coliziune pe CAND-0022 e INERTĂ — nu se declanșează niciodată.** Rămâne (nu costă nimic), dar acum se știe că nu face nimic. **Rata e măsurată, nu presupusă**, exact cum am cerut la ratificare.

## Predicția weekly — fixez metrica de confirmare ÎNAINTE ca cifrele să apară

**Cinci din șase candidați de sesiune moștenesc structura „nivel atins urcând, tranzacționat short"** (doar 0028, prin conținere, e exempt). **Predicția mea (v2.7.40): anti-corelația se agravează cu lungimea perioadei ⇒ sesiunea suferă MAI PUȚIN decât ziua.**

```
METRICA:   fracția de atingeri care sunt bias-aliniate.
MĂSURAT:   săptămână = 2,2%  (6/275)
CERUT:     fracția DIURNĂ (PDH/PDL) calculată în ACEEAȘI trecere, ca să fie comparabilă —
           altfel comparația e între metrici diferite.
CONFIRMĂ:  ordinea  sesiune > zi > săptămână.
INFIRMĂ:   sesiune <= zi. În acel caz predicția mea e greșită și o consemnez ca atare.
```

**Fixat înainte de rezultate, cu condiția de infirmare scrisă explicit.** Dacă iese invers, e a doua oară în acest track când o predicție a mea e pusă la încercare — și trebuie raportată la fel de clar ca o confirmare.

---

## HANDOFF

**VE — în ordinea asta:** (1) termină screening-ul de sesiune în curs; (2) aplică criteriul de triaj din Partea 1 celor șase de sesiune, **raportând în care din cele trei categorii cade fiecare**; (3) execută protocoalele din Partea 3 **doar** pentru cei care ajung în categoria C, cu familia = 7+K unde K e numărul lor; (4) calculează fracția diurnă pentru testul de predicție din Partea 4. **Nimic nu se rulează înainte de (1).**

**Recomandare separată, nu decizie a mea:** CAND-0023 (n=7) merită o descompunere de pâlnie ca la PWH/PWL înainte de a fi considerat închis — conjuncția poate fi cauza, nu mecanismul.

---

**Publicat pe `statistician-foundation`. Manifestul incrementat la v2.7.42 (commit `938710d`, `alpha-automation-v1`) — mypy --strict curat, content_hash reverificat independent (blank-and-rehash), pytest 139/143 trecute (aceleași 4 eșecuri pre-existente).**
