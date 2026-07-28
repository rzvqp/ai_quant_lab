# CROSS-VERIFICATION — trading_strategies.py (136fadc)

**Document ID:** STAT-TS-XVERIFY-v1.0 · **Autor:** Research Lab (divizie neutră, nu a atins modulele MK) · **Data:** 2026-07-28
**Țintă:** `code/trading_strategies.py`, commit `136fadc` (Mandat 5.9) — nouă mașini de stare SMC_S*, scrise+testate de VE.
**Metodă:** suită externă independentă (`tests/test_trading_strategies_cross.py`), matrici sintetice în memorie, cazuri din **definiția ratificată**, nu din cod. Nu reutilizează testele VE. Audit software pur: **fără `.load()`, fără date XAUUSD, fără P&L, fără simulare.**
**Rezultat: 17/17 teste TREC · `mypy --strict` curat · NICIUN defect găsit.**

## Sarcina 1 — bariera anti-E010 (verificarea centrală)
**La SURSĂ (`_emit`, prin care trec TOATE cele 9 familii) — verificat exhaustiv:**
- `selection_end == entry_idx` (selecția se termină EXACT la intrare); `measurement_start == entry_idx`; `measurement_end == min(entry+H, n)` — **clamped la n** (nu citește niciodată dincolo). Interioarele selecție `[.., entry)` și măsurare `(entry, end)` sunt **disjuncte**.
- **FAIL-CLOSED** (nu doar corect): `entry ≥ n` sau `entry < 0` → `None`; spike ∉ `[10.1, 65)` pips → `None` (SKIP). Nu există API care să accepte ferestre suprapuse — ferestrele se calculează intern, deci „apel cu ferestre suprapuse" e imposibil prin construcție, iar out-of-range e respins, nu tăcut.

**Mutation-invariance per familie** (mut artificial TOATE barele strict după `entry_idx` și confirm că semnalul e reprodus bit-identic → selecția e funcție pură de barele `≤ entry_idx`): **7/9 empiric** — S1, S2, S10, S11, S13, S16, S17. Toate trec: niciun semnal nu se schimbă când fereastra de măsurare (și tot viitorul) e distrusă.

**Acoperire — declarat cinstit:** **S3 și S7 nu au aprins** pe fixturile mele sintetice în bugetul sesiunii — declanșatorul lor (retest post-BOS pentru S3; secvență HH+HL cu spike eligibil pentru S7) și filtrul strict de eligibilitate spike∈`[10.1,65)`pips nu au fost satisfăcute simultan de datele mele construite. **Nu e o constatare despre modul** — e o limitare a fixturii mele. Pentru ele bariera e verificată **la sursă** (`_emit` + tiparul comun `entry = trigger+1`, unde `trigger` e ultima bară de SELECȚIE), dar NU empiric prin mutation. 7/9 empiric + 9/9 la sursă.

## Sarcina 2 — substituția SMC_S10 (BOS-ca-displacement): VERDICT
**Constatare: substituția DECUPLEAZĂ magnitudinea de structură** (exact reperul semnalat). `detect_s10` declanșează pe un **body-BOS** (structură pură, prin `detect_breaks`), iar poarta lui de magnitudine e banda **ABSOLUTĂ** de spike `[10.1,65)` pips (comună tuturor familiilor), **NU** o displacement relativă la volatilitate (ATR). Consecință: o rupere structurală mică în termeni de ATR **aprinde**; o mișcare mare în ATR care nu rupe nicio structură **NU aprinde**. Verificat în test: fără poartă ATR în sursă; toate spike-urile S10 în banda absolută.
- **Grad de libertate nedeclarat? NU.** Substituția e DECLARATĂ (docstring §S10) și de fapt **ELIMINĂ** un DOF (nu există multiplu-ATR de reglat), nu adaugă unul ascuns.
- **Schimbă natura teoretică? DA.** „Displacement-continuation" (magnitudine relativă la volatilitate) devine „BOS-continuation" (moment structural). Sunt corelate, nu identice.

**Verdict tehnic: REBUCLĂ (la nivel de concept, nu de cod).** Codul e sănătos, declarat, fără DOF ascuns — dar **nu e o aproximare transparentă a „displacement", ci o substituție care schimbă ipoteza economică** (structură în loc de magnitudine). Recomand Statisticianului: fie (a) **re-ratifică explicit S10 ca „BOS-continuation"** (acceptând ipoteza structurală, cu eticheta care se potrivește cu ce se măsoară), fie (b) **rebuclă** pentru a restaura un criteriu de magnitudine/volatilitate dacă displacement-ca-magnitudine e esențial familiei. Alinierea concept↔cod e decizia proprietarului de concept; pe puf de decuplare, aprobarea „ca displacement" nu se susține.

## Sarcina 3 — SMC_S17 și regula D7
- **Consumare o singură dată la prima atingere cu fitil, FĂRĂ re-armare:** verificat. 1 atingere → 1 semnal; **4 atingeri → tot 1 semnal** (aceeași primă intrare). Simptomul din `market_structure.py` (1 eveniment → 4 ruperi, prin re-armare) **NU apare** — S17 consumă prin `break` din bucla per-nivel.
- **Reutilizare fidelă (nu reimplementare divergentă):** confirmat prin comparație de sursă. Bucla inline D7 a S17 e **structural identică** cu `institutional_levels.detect_level_touches` (zilnic): același scan `available_idx..block.end`, `break` la ieșirea din perioadă, aceeași condiție de atingere fitil (`high[j]>=price` / `low[j]<=price`), `break` la prima atingere. Diferă DOAR `day_index→week_index` și `PDH/PDL→WEEKLY_*`. Regula e reutilizată verbatim; `institutional_levels.py` neatins.

## Extras — inerție / acoperire de formalizare
- **Exact nouă `detect_s*`:** {S1, S2, S3, S7, S10, S11, S13, S16, S17} — confirmat.
- **S15 NEimplementat:** `detect_s15` absent; `S15` în `UNFORMALIZED_FAMILIES` marcat „GENUIN GOL".
- **`net_R` definit ca semnătură DAR NU apelat** în niciun `detect_s*` (verificat pe sursă) → modulele rămân **inerte**.

## Notă de proces
Patru teste au „picat" în dezvoltare — **toate erori ale MELE** (S13 emite mai multe semnale la aceeași intrare, deci match pe egalitate completă nu pe (trigger,entry); filtru `detect_s*` prea larg prindea `detect_swings`/`detect_sweeps` importate; dict-de-lambda confuza inferența `mypy`; un heredoc de escaping). Corectate și dezvăluite. **Modulul era corect de fiecare dată** — exact valoarea verificării independente (a 4-a oară consecutiv că testele independente prind presupunerile MELE, nu ale modulului).

**Niciun defect. Nu am reparat nimic (nu e codul meu). Un singur verdict de rebuclă conceptuală pe S10, la decizia Statisticianului. Holdout SEALED; fără date de descoperire; `trading_strategies.py` și cele 7 primitive neatinse.**
