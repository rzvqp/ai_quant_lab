# H4/H1 context vechi de 9 luni — CAUZĂ (raport înainte de a regenera)

**Divizie:** Data Acquisition · **Data:** 2026-08-13 · manifest v2.7.57
**Verdict:** NU e achiziție. NU e o derivare veche rulată pe date vechi. **Este segmentare — treaba Statisticianului.** NU am regenerat (ar fi byte-identic). NU am atins manifestul / M15_v2 / M5.

---

## 1. Ce merge până unde (disc + manifest, hash-uri confirmate)

| Fișier | Prima bară | Ultima bară | Hash disc = manifest |
|---|---|---|---|
| **M15_v2** | 2011-07-26 16:30Z | **2026-07-27 16:15Z** ✅ curent | MATCH (`57f4ed95…`) |
| M5 | 2021-07-27 15:45Z | 2026-07-27 17:55Z ✅ | MATCH (`cbb6eebe…`) |
| H4_from_M15_v2 | 2011-07-26 17:00Z | **2025-10-10 17:00Z** ⚠️ | MATCH (`f8f23f6e…`) |
| H1_from_M15_v2 | 2011-07-26 17:00Z | **2025-10-12 22:00Z** ⚠️ | MATCH (`524977d0…`) |

**M15_v2 e LA ZI (2026-07).** Deci, per arborele tău de decizie: nu e problemă de achiziție.

## 2. De ce se opresc H4/H1 exact la 2025-10 — și de ce NU e o derivare veche

Regula HTF ratificată (`context_derived_htf.mechanical_rule`): o bară HTF se construiește **doar dacă toate cele N bare M15_v2 componente aparțin integral unui SINGUR bloc discovery** din `m15_v2_discovery_blocks`. Bare sealed/embargo/lipsă → bara HTF e absentă (fail-closed anti-leakage).

Blocurile discovery din manifest sunt **patru**, iar ultimul se termină la:

> **`m15_v2_discovery_blocks[-1]` = 2022-12-16T10:45Z → 2025-10-12T23:15:00Z**

- H1 se termină la **2025-10-12 22:00Z** = ultima fereastră H1 integral în ultimul bloc discovery (blocul se închide la 23:15Z).
- H4 se termină la **2025-10-10 17:00Z** = ultima H4 de vineri; weekendul 11-12 oct n-are bare, iar deschiderea de duminică 22:00+ ar depăși capătul blocului.

**Nu e o rulare veche:** `context_derived_htf.source_file_sha256 == M15_v2 hash curent` (`57f4ed95…`) → **derivarea a fost făcută DIN M15_v2 curent** și e completă pentru blocurile discovery care există. Se oprește la 2025-10-12 pentru că **acolo se termină ultimul bloc discovery**, nu pentru că a fost rulată pe date vechi.

**Consecință:** a regenera acum cu aceeași regulă + aceeași segmentare produce un rezultat **byte-identic** — tot până în 2025-10-12. Regenerarea NU ar repara nimic. De asta m-am oprit și raportez (per "raportează înainte de a regenera, dacă găsești ceva neașteptat").

## 3. A cui e treaba: STATISTICIANUL

Cele 9 luni de M15_v2 (2025-10-12 → 2026-07-27) **nu sunt în niciun bloc discovery.** Ca H4/H1 să ajungă în 2026-07, **segmentarea discovery/embargo/sealed trebuie extinsă dincolo de 2025-10-12** — adică noi blocuri discovery peste coada recentă.

Asta e explicit al Statisticianului, nu al Data Acquisition:
- `context_derived_htf.who_does_what`: *"Statistician specifies this rule and registers it here. Data Acquisition executes the generation and supplies the resulting data_file_sha256."*
- Segmentarea (regime_segments, discovery/embargo/sealed, `m15_v2_discovery_blocks`) trăiește în `config/split_manifest.json`, pe care Data Acquisition **nu îl modifică**.

**Ordinea corectă:** (1) Statisticianul extinde blocurile discovery peste 2025-10-12 în manifest → (2) Data Acquisition regenerează H4/H1 (aceleași convenții ratificate, invariant de contabilitate, single-block) până la noul capăt și **sup-plimentează hash-urile noi** → (3) Statisticianul le ratifică. Sunt gata să execut pasul 2 imediat ce pasul 1 e făcut.

---

## 4. Întrebarea de proiectare: cine ține cele patru timeframe-uri aliniate la Shadow live?

**Răspuns: nimeni. Piesa NU există.**

- Derivarea actuală e **un batch offline, o singură dată** (`generate_htf_context.py` rulat, fișiere comise, hash în manifest). **Nu există niciun component care să avanseze H4/H1 continuu** odată cu barele M15_v2 noi.
- La Shadow live cele patru TF trebuie să avanseze împreună. Acum nu o fac → N1/N2 citesc context înghețat la ultimul bloc discovery (2025-10), N3/N4 citesc coada M5 proaspătă (2026-07). **Decizii greșite TĂCIT**, exact cum ai spus.

**Mai adânc — regula offline ≠ regula live:** derivarea offline e mărginită la blocuri discovery *tocmai ca să nu scurgă* din bare sealed/viitoare. La marginea LIVE nu există "viitor sealed" de scurs (barele live sunt prezentul). Deci **regula de derivare live e o regulă diferită** și trebuie specificată — nu e simpla extindere a celei offline.

**Piesa lipsă = un agregator HTF live** care rulează la runtime-ul Shadow și rulează M15_v2→H4/H1/D1 pe măsură ce fiecare fereastră HTF se închide, avansând toate cele patru împreună. Distinct de derivarea offline (mărginită la discovery pentru leakage).
- **Specificarea regulii live = Statisticianul** (deține specificarea regulii de derivare, ca la cea offline).
- **Construirea agregatorului = o pot face eu** (Data Acquisition — e derivare de date), odată ce regula live e specificată.
- **Integrarea în bucla de decizie + alinierea celor patru clocks = runtime-ul Shadow** (Research Lab / execuție).

Semnalez piesa lipsă; nu o construiesc fără specificarea regulii live.

---

## Ce NU am făcut
NU am regenerat (byte-identic cu ce există). NU am modificat manifestul. NU am atins M15_v2 / M5. Aștept: (a) Statisticianul să extindă blocurile discovery, apoi regenerez; (b) decizia despre agregatorul HTF live.
