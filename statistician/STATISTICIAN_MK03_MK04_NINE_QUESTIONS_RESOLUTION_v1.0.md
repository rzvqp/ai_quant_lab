# STATISTICIAN — REZOLUȚIA CELOR NOUĂ ÎNTREBĂRI DESCHISE MK-03/MK-04 (Mandat 3.14)

**Document ID:** STAT-MK03-MK04-NINE-QUESTIONS-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician

**Verificare de sursă înainte de decizie:** citit direct `code/imbalance_mechanics.py` și `code/institutional_levels.py` la commit `7984670` (worktree `ai_quant_lab-alpha-automation`, branch `discovery-mk-matrix-v1` — accesat prin obiectele git partajate, fără checkout, `discovery-mk-matrix-v1` fiind deja ocupat de worktree-ul `ai_quant_lab-mk-patch`). Confirmat exact: `tolerances: tuple[float, ...] = (0.0, 0.10, 0.25)` în `count_bpr` — regula de îngheț intactă, a treia încercare rezistată de VE, confirmată direct în cod, nu doar acceptată. Confirmat cele nouă întrebări enumerate exact ca în mandat (MK-03: Q1, Q2, Q4, Q5, Q6; MK-04: Q3-zi, Q3-săptămână, Q4, Q5).

**Descoperire suplimentară, neexplicit cerută dar decisivă pentru Q4 MK-03:** am găsit direct în `edge_research/e010_breaker_block_snatch.py` și `edge_research/e012_inverted_fvg.py` — DOUĂ V0-uri deja ÎNGHEȚATE — o definiție EXACTĂ, identică textual, pentru exact acest tip de eveniment ("polarity flip"/"inversion"): *„the first time a LATER bar's CLOSE falls below the zone's own low — a full, decisive violation, not just an intrabar wick"*. Nu derivez o definiție nouă pentru Q4 — o **reutilizez verbatim**, dintr-un precedent deja înghețat, dublu-corroborat.

---

## FAMILIA 1 (Q5 MK-03, Q5 MK-04) — consumare prin analogie D7, FĂRĂ dimensiunea nouă „sesiune/zi"

Susțin jumătatea I: consumare (nu re-armare), analog D7. **Resping formularea „elimină din matricea activă pentru restul sesiunii/zilei"** — D7 nu specifică nicio durată de viață legată de sesiune/zi, doar „consumat, niciodată refolosit". A adăuga o dimensiune nouă ar cere propria derivare (ce înseamnă „sesiune" pentru un FVG, care n-are graniță de sesiune naturală) — nu o fac fără motiv.

**Decizie: durata de viață e IDENTICĂ cu D7 — consumat definitiv, în interiorul ferestrei de existență deja stabilite a entității (blocul curent pentru FVG; fereastra de disponibilitate curentă pentru PDH/PDL, deja fixată de D3_bis/Q4-MK04), fără o dimensiune nouă de „sesiune" sau „zi".**

**Pentru PDH/PDL, întrebarea reală a lui VE — nu recalcularea zilnică (aia e tautologică, corect observat) — ci: în CADRUL aceleiași zile, un PDH maturat rămâne activ la o a doua atingere?** Răspuns: **NU** — se consumă la prima atingere, în cadrul ferestrei lui de disponibilitate curentă (ziua curentă, deja fixată). Nu e o dimensiune nouă „zi" — e exact fereastra de disponibilitate deja existentă (Q4 MK-04), la care aplic pur și simplu regula D7. „Sesiune/zi" ca dimensiune SEPARATĂ nu se aplică.

## FAMILIA 2 (Q6, Q4 MK-03) — asimetria fitil/închidere, acum cu precedent dublu-verificat

Aveai dreptate — asimetria era corectă dar nescrisă. O scriu, cu precedent din cod, nu doar din analogie D6:

**Gradient în trei trepte, pentru orice FVG (bullish, zonă `[lower, upper]`, simetric pentru bearish):**

1. **Mitigare CE-50 (atingere, prin FITIL):** `low[i] ≤ ce_50` pentru bullish (`high[i] ≥ ce_50` bearish) — exact stilul `touch_mask` deja folosit în `edge_research/e015_order_block_remitigation.py:98` (`(low<=zone_high) & (high>=zone_low)`), aplicat la nivelul CE-50. O atingere, nu o capitulare.
2. **Umplere integrală (prin FITIL, până la marginea îndepărtată):** `low[i] ≤ lower` pentru bullish (`high[i] ≥ upper` bearish) — tot fitil, o treaptă mai adâncă decât CE-50, dar tot o atingere.
3. **Inversare/IFVG (prin ÎNCHIDERE, capitulare):** `close[i] < lower` pentru bullish (`close[i] > upper` bearish) — **reutilizat verbatim din `e010_breaker_block_snatch.py`/`e012_inverted_fvg.py`**: „the first time a LATER bar's CLOSE falls below the zone's own low — a full, decisive violation, not just an intrabar wick." Polaritatea se inversează DOAR aici.

**De ce asimetria, scris explicit:** o atingere (fitil) arată doar că prețul a revenit MOMENTAN în zonă — nu spune nimic despre cine a câștigat bara. O închidere dincolo de marginea îndepărtată arată că partea opusă a ÎNVINS bara respectivă — o capitulare, nu o vizită. Exact distincția pe care D6 o face deja între penetrare (fitil) și revenire (închidere) pentru wick-sweep — aici aplicată la un eveniment mai puternic (inversare de polaritate, nu doar respingere). **Nu e o alegere liberă — e aceeași mecanică D6, confirmată acum și de două V0-uri deja înghețate (E010, E012) care folosesc identic „close beyond zone, not just intrabar wick" pentru evenimentul analog (breaker flip).**

**Consumare per treaptă (leagă de Familia 1):** FVG-ul original se consumă (D7) la PRIMA atingere CE-50 — indiferent dacă mai târziu se umple integral sau se inversează, acelea sunt proprietăți suplimentare înregistrate DUPĂ mitigare, nu re-armări. Dacă se inversează, zona inversată (IFVG) e o entitate NOUĂ, cu propriul ciclu de consumare independent pentru reacția în noua direcție — exact designul deja folosit de E010/E012 („after the flip, does price REVISIT the zone... in the NEW direction").

## FAMILIA 3 — susțin fără rezerve, plus rezolvarea Q3-săptămână

**FVG-urile NU supraviețuiesc unei granițe de bloc** — identic cu D4 pentru bazine: o zonă a cărei formare depinde de bare dintr-un bloc nu poate fi urmărită/acționată într-un bloc ulterior; carantina s-ar încălca prin memorie care traversează granița. La finalul blocului, FVG-ul (mitigat sau nu) iese din scop — nu se marchează „expirat nemitigat", pur și simplu nu mai există ca entitate urmăribilă, la fel ca un swing care nu supraviețuiește lui D4.

**Săptămâni discrete, ancorate la calendarul blocurilor, cu `PARTIAL`** — deja ratificat la D-WEEK, reconfirmat aici neschimbat.

**Q3-săptămână, rezolvată prin derivare din Q3-zi (nu o ancoră nouă):** granița de zi e deja rezolvată (17:00 NY, DST-aware, `code/resample_ny.py`). Nu inventez o a doua ancoră de ceas pentru săptămână — **`week_index` se derivă mecanic din `day_index` deja existent**: o săptămână nouă începe la prima bară a cărei zi calendaristică succede zilei anterioare cu un gol >1 zi calendaristică (weekend-ul produce exact acest gol în etichetele `day_index`). Practic, prima zi de tranzacționare de după weekend (empiric, redeschiderea de duminică seara ora NY) — dar DERIVATĂ din granița de zi deja stabilită, nu asertată separat. Nu blochează modulul (care oricum primește `week_index` de la apelant) — blochează doar derivarea caller-side, acum specificată.

## Q4 MK-03 (IFVG) — REZOLVATĂ, singura blocare completă de primitivă

**Definiție finală, reutilizată verbatim din `e010_breaker_block_snatch.py`/`e012_inverted_fvg.py`:** un FVG bullish se inversează prima dată când o bară ULTERIOARĂ are `close < lower` (marginea de jos a zonei) — o violare decisivă prin ÎNCHIDERE, nu doar un fitil intrabar. Bearish, simetric: `close > upper`. Rezolvă ambele ambiguități semnalate: (a) NU e engulfing de corp al unei singure bare — e prima închidere ulterioară dincolo de margine, indiferent cât de multe bare au trecut; (b) e ÎNCHIDERE, nu fitil. **Deblochează `detect_inverse_fvgs`.**

## Cele trei mici, ratificate formal

- **Q1 MK-03** (`confirmed_idx=i+1`): **RATIFICAT.** Mecanic forțat — o fereastră de 3 bare nu poate fi cunoscută înainte de bara i+1, exact ca D1. Nicio alternativă lookahead-safe.
- **Q4 MK-04** (`available_idx` = prima bară a perioadei curente): **RATIFICAT.** Aceeași mecanică forțată ca D1, aplicată la niveluri zilnice/săptămânale.
- **Q3-zi MK-04** (17:00 NY, DST-aware): **RECONFIRMAT**, deja rezolvat de CEO, neblocant pentru modul.

---

**Nu am rulat niciun backtest, nu am atins date reale dincolo de citirea directă a codului deja commit-uit. Independent de calibrarea S8 aflată în derulare la VE (n≈21.000, LM-001) — subiecte disjuncte, cum ai confirmat.**

**Manifestul se incrementează la v2.5.6 după publicarea acestui document.** Statistician se oprește aici.
