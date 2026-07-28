# STATISTICIAN — AUDITUL DE GEOMETRIE LM-001 + REZOLVAREA MK-03/MK-04

**Document ID:** STAT-LM001-GEOMETRY-MK03-MK04-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician
**Precedent:** Mandatul 3.10 (D3 ratificat complet, cifra 6, convenție semi-deschisă, `STATISTICIAN_D3_FULL_RATIFICATION_AND_GOVERNANCE_v1.0.md`, commit `2a36897`).

---

## Nota preliminară — 130.491, nu 130.492

Confirmat, deja verificat independent la Mandatul 3.10 (nu repet acum, doar consemnez): 52.403+52.851+25.237 = **130.491**. Cifra corectă e a Research Lab; discrepanța de unu a VE (130.492 auto-semnalată) e exact convenția închisă-vs-semi-deschisă deja rezolvată. Nicio acțiune suplimentară necesară aici.

**O verificare colaterală, cu discrepanță reală de semnalat:** am recalculat independent ATR median M15 (Wilder 14 și SMA 14, atât pe tot setul cât și restrâns strict la cele 130.491 bare de descoperire, folosind exact epoch-urile din manifest). Rezultat: **~1,64–1,71 dolari (16–17 pips)**, nu 2,395 dolari (24 pips) cum s-a afirmat. Nu știu sursa exactă a diferenței (perioadă diferită, metodă diferită de calcul, sau altă subsetare) și nu o rezolv aici pentru că **nu afectează sarcina de față** — motivul exact pentru care măsurăm distanța la extremul fitilului direct, în loc să deducem geometria din ATR ca proxy. Semnalez, nu ignor.

---

## SARCINA 1 — SPECIFICAȚIA AUDITULUI DE GEOMETRIE LM-001

Nicio podea/plafon nu se îngheață acum. Se măsoară întâi. Specificația de mai jos e completă și mecanică — VE execută exact, fără nicio alegere de definiție.

### Definiții (Statistician alege, VE nu)

**A. Bazin valid pentru acest audit** — un bazin de lichiditate construit exact conform deciziilor deja ratificate D1/D2/D4/D5/D7 (`market_structure_ratification`, manifest v2.5.3): provine dintr-un swing CLASSIFIED, nu supraviețuiește peste graniță de bloc de descoperire (D4), nu e deja consumat în acest bloc (D7).

**B. Wick-sweep valid pe bara `c`** — exact D6, evaluat integral pe bara curentă, fără lookahead:
- latură de suport: `low[c] < basin_level AND close[c] > basin_level`
- latură de rezistență: `high[c] > basin_level AND close[c] < basin_level`

La detectare, bazinul e marcat consumat (D7) — fiecare bazin contribuie **cel mult un** eveniment în tot auditul.

**C. Extremul fitilului de manipulare:**
- latură de suport: `low[c]`
- latură de rezistență: `high[c]`

**D. Intrarea "next-open"** = `open[c+1]`, **doar dacă** bara `c+1` există și aparține ACELUIAȘI `discovery_range` ca bara `c`, sub convenția semi-deschisă `[start_epoch, end_epoch)` ratificată la Mandatul 3.10 (`in_range()`). Dacă `c` e ultima bară din `discovery_range`-ul blocului, evenimentul e **EXCLUS** din audit — nu există next-open sigur intra-carantină. Excluderile se raportează explicit (numărul lor), nu se ascund tăcut.

**E. Distanța în puncte:**
- latură de suport: `distance = open[c+1] - low[c]`
- latură de rezistență: `distance = high[c] - open[c+1]`

Conversie în pips: `distance_pips = distance / TICK`, unde **TICK = 0,10 dolari** — verificat direct (`code/mstrat.py:10` `TICK=0.1`; `code/alpha_lab.py:11` `tick=0.1`), nu asumat. Valoarea poate fi rar negativă (gap peste extrem) — se raportează ca atare, nu se trunchiază la zero și nu se exclude.

**F. Interdicții explicite:**
- Fără P&L, fără simulare de tranzacții, fără optimizare de parametri — numere de geometrie, atât.
- **Interzisă invocarea `detect_breaks`** (bug-ul de re-armare din Mandatul 3.10, nereparat) — acest audit folosește exclusiv `detect_swings`/`label_structure` + logica de bazin/wick-sweep din `liquidity_mechanics.py` (D6/D7), niciodată `detect_breaks`. Cale de cod izolată, la fel ca auditul de volum D3.
- Auditul NU derivă și NU recomandă o podea/plafon nou — asta e o decizie separată, a Statisticianului, DUPĂ ce distribuția există.

### Raportare cerută (VE)

Pe cele 130.491 bare de descoperire (excluzând segmentul al 4-lea, fără `discovery_range`):

1. **Distribuție brută agregată** (toate evenimentele valide, toate cele 3 blocuri): min, p10, p25, mediană, p75, p90, max, N total, N exclus (fără next-open valid).
2. **Defalcat pe cele 3 regimuri macro** (bear/bull/correction) — aceleași statistici, per regim.
3. **Defalcat pe cele 4 sesiuni UTC fixe deja stabilite în cod** (nu inventate acum — `code/mtf.py:37-38`): `asia` = oră UTC `<8`, `london` = `[8,13)`, `ny` = `[13,21)`, `late` = `≥21`. Sesiunea se atribuie după ora UTC a barei evenimentului `c`, nu a barei `next-open`.
4. **Fracția sub 40 pips, `[40,65)` pips, `≥65` pips** — pe agregat ȘI per regim/sesiune, cu N explicit per celulă (nu doar procent — o celulă cu N mic trebuie vizibilă ca atare, marcată "SUB-PRAG (n<25), informativ" dacă e cazul, nu ascunsă în spatele unui procent).

## SARCINA 2 — CELE TREI ÎNTREBĂRI DIN SCHELETE

### MK-03 — BPR: numărătoare la trei toleranțe, regulă de îngheț decisă ACUM

Definiție (CTO): suprapunere între un FVG bullish și unul bearish într-o fereastră de maxim 3 bare. Rezerva mea, tratată nu ocolită: prețul aurului are 2 zecimale — coincidența EXACTĂ la toleranță 0,00 între două goluri independente e foarte improbabilă. Zero evenimente la 0,00 nu ar demonstra că BPR nu există, ar putea demonstra doar că toleranța cere o precizie pe care prețul n-o are.

**Comandă către VE:** numără evenimentele de suprapunere la toate trei toleranțele — 0,00 / 0,10 / 0,25 dolari — pur descriptiv, fără nicio alegere în acest pas.

**Regula de îngheț, specificată ACUM, înainte de a exista vreo numărătoare** (ca să nu fie aleasă după ce se vede care dă mai multe evenimente): **se îngheață CEA MAI MICĂ dintre {0,00 / 0,10 / 0,25} a cărei numărătoare atinge pragul minim deja stabilit în lab, n≥25.** Dacă 0,00 atinge pragul, se îngheață 0,00 (cea mai strictă, cea mai defensabilă). Dacă nu, se trece la 0,10, apoi la 0,25. Dacă nici 0,25 nu atinge n≥25, BPR sub această definiție **nu e testabilă** la M15_v2 cu acest n — se raportează ca atare, nu se forțează un prag artificial doar ca să existe date. Regula e monotonă și mecanică — nu favorizează "mai multe evenimente", favorizează precizia maximă care rămâne fezabilă statistic.

### MK-04 — D3_bis: confirmat

Memoria zilnică (PDH/PDL) se **resetează complet** la fiecare graniță de carantină (graniță de bloc de descoperire M15_v2); prima zi din segmentul nou e **UNCLASSIFIED** — nu există o "zi precedentă" validă în interiorul blocului, iar a împrumuta una din afara blocului ar încălca exact arhitectura de carantină deja stabilită. Analogul exact al D3 pentru niveluri zilnice, aceeași justificare: nicio construcție alternativă nu e sigură fără lookahead, dat fiind ce e deja ratificat. **D3_bis: RATIFICAT**, aceeași motivație ca D3.

### MK-04 — săptămâna trunchiată: flag de completitudine, nu tratare identică

Răspuns la întrebarea ridicată: o săptămână redusă la 2 zile în interiorul unui bloc **PRODUCE** un Weekly High/Low (calculat exclusiv pe barele active din bloc, fără împrumut extern, cum s-a cerut) — dar acest nivel **nu se tratează identic** cu unul din 5 zile. Un nivel "săptămânal" din 2 zile înseamnă altceva decât unul din 5, iar consumatorii din aval trebuie să vadă diferența, nu să o ghicească.

**Regulă:** fiecare nivel Weekly High/Low calculat poartă obligatoriu:
- `days_contributing`: numărul de zile de tranzacționare active care au contribuit efectiv (1-5)
- `completeness`: `"COMPLETE"` (5 zile) sau `"PARTIAL"` (<5 zile, trunchiat de granița de carantină)

Nicio ipoteză din aval nu poate consuma silent un nivel `PARTIAL` identic cu unul `COMPLETE` — trebuie fie să excludă `PARTIAL`, fie să-l trateze ca strat separat, declarat explicit. Aceeași disciplină ca D3/D4: discontinuitățile de graniță trebuie să fie vizibile, nu netezite tăcut.

---

**Prioritate confirmată:** auditul de geometrie (Sarcina 1) e pregătit pentru execuție imediată de VE, independent de patch-ul de re-armare (Mandatul 3.10) — cale de cod complet separată. Nu am scris cod, nu am rulat nimic pe date reale dincolo de verificările de mai sus (130.491, ATR, TICK=0,1, sesiunile din `mtf.py`). Statistician se oprește aici.
