# STATISTICIAN — ETICHETA FORMALĂ FINALĂ: CELE 47 (EXCLUSION-DEPENDENT → REJECTED)

**Document ID:** STAT-47-FINAL-LABEL-v1.0
**Data:** 2026-07-27 · **Autor:** Statistician
**Verificare de sursă:** cifrele de mai jos provin din diagnosticul Research Lab, commit `f1486c3`, raportate de CEO — subtipul celor 7.371 tranzacții excluse și fracția de excludere per ipoteză vs. corp. Verificarea podelei de stop (`max(2×spread, 5×tick, 0,10×ATR)`, componenta `5×tick`=0,50 dominantă pe M15 și M5) e verificarea CEO, confirmată aici prin consecvență cu `MIN_STOP_FLOOR_PREREG.md` (formula, constantele k_spread=2/k_tick=5/k_atr=0,10, deja citite direct anterior în această sesiune).

---

## ETICHETĂ FINALĂ: `REJECTED`. Nu `NOT-MEASURABLE`.

## De ce datele decid clar

**Subtipul de excludere e dominat de `gap_stop` (78,9%), nu de ambiguitate genuină (`ambiguous`=8,2%).** `gap_stop` = stopul floor-uit e lovit chiar pe bara de intrare, ținta nici măcar nu e atinsă — asta nu e o ambiguitate de fill nerezolvabilă din OHLC, e un EȘEC DE EXECUȚIE: setup-ul plasează stopul suficient de aproape de intrare încât mișcarea normală a pieței, imediat după intrare, îl lovește. Fracția de excludere a celor 47 (mediană 5,6%, până la 30,4%) e un outlier clar față de corpul întreg (mediană 0,0000, p90 0,052) — cele 47 depășesc, la mediană, al 90-lea percentil al ÎNTREGULUI corp.

**De ce nu `NOT-MEASURABLE`:** eticheta ar implica faptul că o rezoluție diferită ar putea rezolva problema. Podeaua de stop (`max(2×spread, 5×tick, 0,10×ATR)`) e dominată de componenta `5×tick` = 0,50 pe AMBELE rezoluții verificate (0,10×ATR = 0,24 pe M15, ≈0,084 pe M5 — ambele sub componenta tick). Componenta care domină e legată de tick-ul instrumentului (o constantă de structură de piață), nu de durata barei — **nu se micșorează cu rezoluția**. Un `gap_stop` la M15 rămâne `gap_stop` la M5, pentru exact același motiv structural. Nu există, în principiu, o rezoluție la care aceste 47 ar deveni testabile — obstacolul nu e rezoluția de observare, e o nepotrivire între propriul prag de plasare a stopului al ipotezei și o limită de execuție fixă, independentă de rezoluție. `NOT-MEASURABLE` ar fi înșelător — ar sugera o cale de rezolvare care nu există.

**De ce `REJECTED`, cu scop precis, nu extins peste ceea ce arată dovada:** `REJECTED` aici înseamnă specific — *profitabilitatea raportată a celor 47, AȘA CUM SUNT SPECIFICATE (parametrul lor înghețat de distanță a stopului), nu e dovadă a unui avantaj real; e un artefact al eliminării propriilor eșecuri de execuție garantate structural (gap_stop, dominat de podeaua de tick, independent de rezoluție)*. **NU** înseamnă că nicio versiune a ideii de piață subiacente n-ar putea funcționa vreodată — o respecificare cu o distanță de stop suficient de largă față de podea ar fi o ipoteză NOUĂ, care ar cere propria ei revizuire evidențială completă de la zero, nu o resuscitare a acestor 47. Nu recomand și nu sugerez o asemenea respecificare aici — doar delimitez ce `REJECTED` nu închide, ca să nu fie citit greșit peste șase luni ca "ideea a fost testată și infirmată definitiv la orice parametrizare".

## Consecință

Cele 47, alături de cele 22 (`CONVENTION-ARTIFACT`, deja respinse), rămân AMBELE în afara oricărui pool de certificare/FDR global — permanent, nu provizoriu. Promovarea metodologiei `reproduction_d2` la canonic (autorizată anterior, `STATISTICIAN_BRACKET_69_VERDICT_v1.0.md`) rămâne neschimbată — cele 357 originale își păstrează statutul complet, neafectate.

---

**Nu am modificat parquet-ul, nu am executat nimic. Statistician se oprește aici.**
