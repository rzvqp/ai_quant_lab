# STATISTICIAN — ÎNCHIDEREA NUMERICĂ `w_atr` / `s_max`

**Document ID:** STAT-RANGE-V2-NUMERIC-CLOSURE-v1.0 · **Data:** 2026-08-18 · **Autor:** Statistician
**Status terminal:** **`RANGE_V2_NUMERIC_CONFIG_BLOCKED_INSUFFICIENT_CONSTRUCTION_DATA`**
**Comparație VE:** **`VE_DEFAULTS_DIFFER_FROM_FINAL_CONFIG`**
**BLIND_UNTOUCHED** · **SEALED/OOS_ACCESS = 0** · fără PnL, cost, p-value, strategie, Alpha, AI Trader, LIVE_SHADOW, broker.

---

# PARTEA 0 — VERIFICAREA DIN GIT ȘI TREI CONTRADICȚII

**Verificate, toate prezente și corecte:**

```
3aac2cc  ruling SEMANTIC_SPEC_DEFECT (Statistician)                             ✔
18aa2a1  manifest v2.7.78                                                        ✔
d307aec  „ve_n1_replay 0.3.0: RANGE_STATE SPEC V2 -- remediu SEMANTIC_SPEC_DEFECT" ✔
22e1496  „ve_n1_replay 0.3.0 delivery: finalize manifest (build d307aec)"         ✔
wheel 0.3.0  SHA-256 RE-CALCULAT din artefact
   = 34603375de736de3d2b48d3471881a76d4107bcb48487100cf3af33f84ee63e0 = DECLARAT  ✔ MATCH
RangeConfigV2  w_atr = 0.25 · s_max = 0.15 · ambele marcate „NERATIFICAT"          ✔
```

## Contradicția 1 — `w_atr = 0,25` moștenește numărul din grila pe care am DEMONSTRAT-O defectă

**Docstring-ul VE, verbatim: „`w_atr = 0.25`: reutilizează punctul median al GRILEI deja pre-înregistrate în v1 ({0.10,0.25,0.50}×ATR, Partea F @aca7801)".**

> **Aceea e exact grila a cărei insuficiență am diagnosticat-o la v2.7.78 ca fiind DEFECTUL. Valoarea implicită importă numărul din obiectul invalidat. VE a semnalat el însuși riscul („grila veche era calibrată pt. o construcție diferită — max+close"), deci nu e o eroare a VE — e o moștenire care trebuia ruptă explicit, iar acest document o rupe.**

## Contradicția 2 — și aici mă corectez pe mine, nu pe VE

**La v2.7.78 am scris că „regiunea semantic plauzibilă începe abia pe la 1,00×ATR (33,9%)". Măsurătoarea aceea era sub geometria V1 (ancoră = MAX, atingere pe CLOSE). Sub geometria V2 (ancoră = MEDIANĂ, atingere pe INTERVAL) am măsurat acum altceva:**

```
rata de SUPRAPUNERE a zonelor (o singură bară atinge AMBELE limite ⇒ regula DEGENEREAZĂ),
pe episoadele de construcție, d_min = 96:
   w_atr    RC-03    RC-04    RC-05
    0,25     0,0%     0,6%     0,3%
    0,50     5,5%     4,1%     2,7%
    0,75    25,8%    16,5%    13,4%
    1,00    36,7%    29,8%    27,9%
    1,25    52,1%    44,7%    47,3%
```

> **Sub V2, `w = 1,00` NU e regiunea plauzibilă — e regiunea DEGENERATĂ: în ~30% din ferestre o singură bară atinge ambele limite, deci „≥2 atingeri pe fiecare limită" se satisface trivial cu două bare oriunde la mijloc. Factorul 160× măsurat sub V1 NU se transferă la V2. Avertismentul VE era CORECT, iar extrapolarea mea ar fi fost greșită. O consemnez ca a doua corecție a propriului raționament pe acest subiect.**

## Contradicția 3 — subsetul BLIND e contaminat de subsetul de CONSTRUCȚIE

```
RC-05 (range7) = 2022-12-16 → 2022-12-30, 873 bare   → subset de CONSTRUCȚIE
RC-06 (range8) = 2022-12-16 → 2022-12-29, 785 bare   → subset BLIND
RC-06 ⊂ RC-05 INTEGRAL (l-am stabilit la v2.7.78)
```

> **Dacă VE calibrează pe RC-05, a văzut 785 din cele 785 de bare ale lui RC-06. RC-06 NU E BLIND. Separarea pe care am pre-înregistrat-o eu la v2.7.78 e defectă: am pus un episod și supra-mulțimea lui în jumătăți opuse. Blindul efectiv se reduce la RC-07 și RC-08. Nu îl repar unilateral — îl semnalez, fiindcă orice remaniere a subseturilor e o decizie de pre-înregistrare, nu o corecție tehnică.**

---

# PARTEA 1 — DE CE E BLOCAT: pozitivele NU IDENTIFICĂ

**Am măsurat recunoașterea semantică a celor trei episoade de construcție sub geometria V2, pe toată plaja de candidați:**

```
acoperirea episodului de către >=1 fereastră care se califică (mediană + zonă + atingere pe interval)
  w_atr:  0,10   0,25   0,40   0,50   0,75   1,00   1,25
  d_min=24:  toate trei episoadele >= 99,9%  la FIECARE valoare
  d_min=96:  toate trei episoadele = 100,0%  la FIECARE valoare
```

> **Criteriul „range-urile pozitive de construcție trebuie recunoscute după momentul cauzal" e satisfăcut de ÎNTREAGA plajă de candidați, la ambele clase de durată. Nu discriminează între 0,10 și 1,25. Informația despre `w_atr` din pozitive este ZERO.**

**Motivul e structural, nu un artefact: ancora MEDIANĂ stă în MIJLOCUL distribuției de swing-uri, nu la extremă, iar atingerea pe INTERVAL e foarte permisivă. Două atingeri pe 24 sau 96 de bare se obțin trivial la orice lățime. Exact reparația care a rezolvat defectul V1 a eliminat și puterea de discriminare a pozitivelor.**

## Ce ar identifica, și unde se află

```
INFORMAȚIA DISCRIMINANTĂ e în CONTROALELE NEGATIVE: un `w_atr` prea mare clasifică un CANAL
drept range. Aceea e singura direcție care pune o limită INFERIOARĂ utilă pe discriminare.
RC-07 și RC-08 (canal ascendent / canal descendent) sunt în subsetul BLIND, prin propria mea
pre-înregistrare de la v2.7.78.
```

**Singura constrângere identificantă disponibilă din pozitive e o limită SUPERIOARĂ, din disjuncția zonelor:**

```
separarea ancorelor (anchor_up − anchor_dn)/ATR, percentila 5 pe episoade și clase de durată:
   RC-03: 1,17 (d24) · 0,99 (d96)      RC-04: 1,20 · 1,04      RC-05: 1,22 · 1,13
minimul care leagă = 0,99  ⇒  zone disjuncte cere 2·w < 0,99  ⇒  w < 0,495
```

> **Mulțimea identificată e un INTERVAL, `w_atr ∈ (0 , 0,495)`, nu un PUNCT. Iar informația care ar fixa punctul e în blind.**

## De ce NU aleg un punct în interval

> **Exact asta a fost eroarea diagnosticată la v2.7.78: am ales cu grijă mijlocul unei grile fără să verific dacă grila acoperă regiunea corectă, iar concluzia mea de atunci a fost „o alegere atentă într-un interval greșit e tot greșită". A alege acum 0,25 sau 0,40 fiindcă „e la mijloc" ar fi A TREIA OARĂ aceeași eroare, cu o justificare de aceeași formă. Refuz.**

**Mandatul prevede exact această situație: „Dacă subsetul de construcție nu este suficient pentru o alegere identificabilă, oprește-te cu status BLOCKED. Nu deschide blindul pentru a completa informația." Nu îl deschid.**

---

# PARTEA 2 — CE POT ÎNCHIDE COMPLET: `s_max` NU E UN PARAMETRU LIBER

**`s_max` nu trebuie ales — se DERIVĂ din `w_atr`, iar derivarea e completă și fără constantă liberă:**

```
Dacă deriva cumulată pe durata stării depășește LĂȚIMEA ZONEI, prețul a părăsit zona PRIN
CONSTRUCȚIE — nu mai e un range, e un canal. Deci pragul de pantă e determinat de geometrie:

    |slope_OLS| × d_min  <=  2 · w_atr · ATR_ref          (deriva cumulată <= lățimea TOTALĂ)

în formă normalizată, adimensională, exact cum trebuie implementat:

    S  :=  |slope_OLS| × d_min / ATR_ref  <=  s_max ,   cu   s_max  ≡  2 · w_atr
```

> **`s_max` NU e un al doilea grad de libertate. Fixarea lui independent de `w_atr` permite o pantă ADMISĂ care iese deja din zonă — o contradicție internă de aceeași natură cu defectul V1 (două cerințe care se bat). Cuplarea o face imposibilă.**

**Consecință directă pentru comparația cu VE (Partea 4): la `w_atr = 0,25`, valoarea derivată e `s_max = 0,50`, nu `0,15`. VE a ales `0,15` ca o constantă LIBERĂ, admisibilă (mai strictă decât derivata) dar NEDERIVATĂ.**

## Formula completă a pantei, implementabilă bit-identic

```
FEREASTRA          exact cele `d_min` bare ÎNCHISE care se termină la bara de evaluare `i`:
                   indici [i − d_min + 1 , i]
REGRESIA           OLS pe `close`, cu x = 0,1,…,d_min−1 (indici de bară, NU timp calendaristic)
                   slope = Σ(x−x̄)(close−closē) / Σ(x−x̄)²        [preț / bară]
NORMALIZARE        S = |slope| × d_min / ATR_ref                   [adimensional]
ATR_ref            ATR(14) pe M15, indexul `i` (bara de evaluare, ÎNCHISĂ) — ACELAȘI index și
                   aceeași instanță ca pentru zonă. O singură lectură, nu două.
PRAG               S <= s_max = 2·w_atr        → RANGE_STATE admis pe axa pantei
                   S >  s_max  ȘI  slope > 0   → CHANNEL_UP        reason CHANNEL_UP_SLOPE
                   S >  s_max  ȘI  slope < 0   → CHANNEL_DOWN      reason CHANNEL_DOWN_SLOPE
                   Σ(x−x̄)² == 0 (imposibil la d_min>=2) sau ATR indisponibil
                                               → Unavailable       reason SLOPE_UNAVAILABLE
TIMESTAMP CAUZAL   `confirm_ts` = bara `i`; toate intrările au index <= i. ZERO lookahead.
```

---

# PARTEA 3 — SPECIFICAȚIA COMPLETĂ A ZONEI (tot ce NU depinde de valoarea numerică)

**Închid integral forma, unitățile și comportamentul de graniță. Rămâne liber DOAR scalarul `w_atr`.**

```
`w_atr` este SEMILĂȚIMEA, în unități ATR. Lățimea TOTALĂ a zonei = 2 · w_atr · ATR_ref.
ZONA           zone_up = [anchor_up − w_atr·ATR_ref , anchor_up + w_atr·ATR_ref]
               zone_dn = [anchor_dn − w_atr·ATR_ref , anchor_dn + w_atr·ATR_ref]
ANCORELE       anchor_up = MEDIANA (`high` a swing-urilor high confirmate din fereastră)
               anchor_dn = MEDIANA (`low`  a swing-urilor low  confirmate din fereastră)
               mediană pe număr PAR de elemente = media celor două centrale (convenție fixată,
               altfel două implementări diverg)
ATINGEREA      bara j atinge zone_up  ⟺  high[j] >= anchor_up − w·ATR  ȘI  low[j] <= anchor_up + w·ATR
               (INTERSECȚIE de intervale; o respingere prin FITIL e o atingere)
               NEINTERSECȚIA NU e atingere. Fără toleranță suplimentară, fără „aproape".
SIMETRIE       ACEEAȘI valoare `w_atr` pentru limita superioară ȘI inferioară. Un `w` asimetric
               ar introduce o preferință direcțională nedeclarată.
ATR_ref        ATR(14), M15, index = bara de evaluare `i` (ÎNCHISĂ). Cauzal.
ATR INDISPONIBIL / NaN / <= 0  →  `Unavailable(reason="ATR_UNAVAILABLE")`. NICIODATĂ o zonă
               presupusă, niciodată o lățime implicită, niciodată zero. Fail-closed.
NEMONOTONIE    ancora e MEDIANĂ, deci NU e nedescrescătoare în lungimea ferestrei ⇒ o extremă
               nouă NU șterge retroactiv atingerile confirmate. Aceasta e reparația centrală
               față de V1 și e o proprietate a MEDIANEI, nu o regulă adăugată.
```

---

# PARTEA 4 — COMPARAȚIA CU DEFAULTURILE VE

```
                        VE 0.3.0        închiderea mea
w_atr                   0,25            NEÎNCHIS — interval identificat (0 , 0,495), punct BLOCAT
s_max                   0,15            DERIVAT: s_max ≡ 2·w_atr  (la w=0,25 ⇒ 0,50)
cuplarea w↔s            ABSENTĂ         OBLIGATORIE
```

> # **`VE_DEFAULTS_DIFFER_FROM_FINAL_CONFIG`**
>
> **Diferă STRUCTURAL, nu doar numeric: în 0.3.0 `s_max` e o constantă liberă; în închiderea mea nu e un parametru deloc. Chiar dacă `w_atr` s-ar fixa la 0,25, `s_max` derivat ar fi 0,50, nu 0,15. Valoarea VE e admisibilă (mai strictă), dar nederivată — iar o constantă liberă lângă una derivată e exact cuplarea absentă care a produs defectul V1.**

---

# PARTEA 5 — ANALIZA DE SENSIBILITATE (fără selecție, fără blind)

```
Sub geometria V2, pe subsetul de CONSTRUCȚIE:
  recunoașterea pozitivelor        INSENSIBILĂ la `w_atr` pe (0,10 … 1,25) — 99,9-100% peste tot
  degenerarea zonelor             MONOTON CRESCĂTOARE: 0,3% la 0,25 → ~4% la 0,50 → ~18% la 0,75
                                  → ~30% la 1,00 → ~48% la 1,25
  separarea ancorelor (p05)        0,99-1,22 ATR ⇒ limita superioară de disjuncție w < 0,495
Nicio configurație nu e declarată primară, deci NICIUNA nu primește p-value sau slot.
NU am ales configurația cu cea mai mare ocupare. NU am folosit niciun rezultat blind.
```

---

# PARTEA 6 — CE AR DEBLOCA, MINIM ȘI FĂRĂ A ATINGE BLINDUL

```
Lipsește UN control NEGATIV în subsetul de CONSTRUCȚIE. Toate cele trei episoade de construcție
sunt POZITIVE, iar pozitivele s-au dovedit neidentificante. Fără un canal în construcție,
limita inferioară pe discriminare nu poate fi stabilită decât din blind.

CEREREA MEA, decizie CEO — trei opțiuni, în ordinea preferinței:
 (A) CEO furnizează UN episod NOU de canal (ascendent SAU descendent), din populația canonică,
     etichetat semantic, care intră în CONSTRUCȚIE. RC-07/RC-08 rămân BLIND, intacte.
 (B) CEO MUTĂ unul dintre RC-07/RC-08 în construcție și îl ÎNLOCUIEȘTE în blind cu un episod
     nou. Blindul rămâne nevăzut de VE, dar se re-pre-înregistrează explicit.
 (C) CEO ratifică o valoare pentru `w_atr` prin DECIZIE, nu prin derivare din date, cu
     consemnarea explicită că e o alegere de model. `s_max` urmează automat prin cuplare.
NU aleg între ele. NU deschid blindul. NU aleg un punct în intervalul identificat.
```

**Și repar defectul de separare pe care l-am creat eu: orice re-pre-înregistrare trebuie să verifice INCLUZIUNEA între episoade. RC-06 ⊂ RC-05 a scăpat pentru că am verificat apartenența la populație, nu relația dintre episoade.**

---

# PARTEA 7 — INSTRUCȚIUNEA PENTRU VE (executabilă la deblocare, NU acum)

```
NU autorizez validarea blind pe 0.3.0. Motive, ambele independente:
  (1) 0.3.0 declară valorile „VE-proposed", deci nu e un artefact normativ;
  (2) `s_max` din 0.3.0 e o constantă liberă, incompatibilă cu cuplarea `s_max ≡ 2·w_atr`.

LA DEBLOCARE, VE livrează `ve_n1_replay 0.3.1`, imuabil:
  · `w_atr` = valoarea ratificată (din opțiunea A/B/C)
  · `s_max` = CALCULAT ca `2 * w_atr` în cod, NU stocat ca literal independent — cuplarea
    trebuie să fie NEREPREZENTABILĂ ca doi parametri liberi
  · panta: OLS pe close, x = indici de bară, normalizare × d_min / ATR(14)[i]
  · citează ACEST commit Statistician ca sursă normativă
  · `range_spec_id` recalculat ⇒ rezultatele 0.3.0 devin NON-COMPARABILE PRIN TIP
  · sidecar manifest actualizat; 0.3.0 NU se suprascrie, rămâne pentru audit
  · restul logicii BYTE-IDENTIC dacă `w_atr` coincide cu 0,25
Red Team primește EXCLUSIV 0.3.1 pin-uit, niciodată 0.3.0.
```

---

# PARTEA 8 — PROTOCOLUL RED TEAM BLIND

```
1. Red Team NU deschide blindul până când `w_atr` și `s_max` sunt fixate, hash-uite și publicate.
   Condiția NU e îndeplinită de acest document — statutul e BLOCKED.
2. Episoadele blind NU se dezvăluie către VE. Intervalele lor se transmit DOAR Red Team.
3. RC-06 e DECLARAT CONTAMINAT (⊂ RC-05, care e în construcție). Blindul efectiv = RC-07, RC-08.
   Dacă se dorește un blind de trei episoade, al treilea trebuie să fie NOU.
4. Testul DECISIV rămâne P2: un detector care marchează un canal drept range a eșuat,
   indiferent de ocupare.
5. Red Team verifică independent zero-lookahead și snapshot bit-identic.
6. Nicio ratificare fără RT PASS și aprobare CEO. Nu ratific detectorul.
```

---

# PARTEA 9 — DESCHIS, CLASIFICAT

```
BLOCKING     `w_atr` NEIDENTIFICABIL din subsetul de construcție: pozitivele sunt insensibile pe
             toată plaja (99,9-100% la orice valoare), iar informația discriminantă e în blind.
             Interval identificat (0 , 0,495) din disjuncția zonelor; punctul rămâne deschis.
BLOCKING     `s_max` e complet DERIVAT (`≡ 2·w_atr`), deci moștenește indeterminarea lui `w_atr`.
             Formula e închisă; valoarea nu.
MATERIAL     RC-06 ⊂ RC-05 ⇒ subsetul BLIND pe care l-am pre-înregistrat EU e contaminat.
             Blindul efectiv = RC-07, RC-08. Nu îl remaniez unilateral.
MATERIAL     `w_atr = 0,25` al VE moștenește numărul din grila diagnosticată ca defectă.
             Admisibil în intervalul meu, dar moștenirea trebuie ruptă explicit.
MATERIAL     `VE_DEFAULTS_DIFFER_FROM_FINAL_CONFIG` — diferența e STRUCTURALĂ (cuplarea absentă),
             nu doar numerică. 0.3.0 nu se validează blind.
LIMITATION   îmi corectez a doua concluzie de la v2.7.78: „plauzibil de la 1,00×ATR" era valabil
             sub geometria V1 (max+close). Sub V2 (mediană+interval), 1,00 e regiunea DEGENERATĂ
             (~30% suprapunere). Avertismentul VE era corect; extrapolarea mea ar fi fost greșită.
LIMITATION   RC-07/RC-08 nu au încă intervale canonice rezolvate — nu le pot rezolva fără a le
             atinge, iar atingerea lor ar deschide blindul.
```

**Invariante neatinse și verificate: `n_generated_total = 363` · `m_inference = 26` · tombstones · registrul Alpha · verdictele existente · F1-F6 și cele 44 `BLOCKED_PENDING_RANGE_SEMANTIC_FIX` · F7 `SAFETY_GUARD`. Alpha nepornit; AI Trader, LIVE_SHADOW, autoritatea și broker gate neatinse.**

---

**Manifest:** `config/split_manifest.json` v2.7.79, secțiunea `range_v2_numeric_closure_v2_7_79`.
