# H1_from_M15_v2 — reconciliere file_path (date pentru Statistician)

**Divizie:** Data Acquisition · **Data:** 2026-08-10 · **Rol:** furnizez faptele; corecția (dacă e nevoie) e a Statisticianului.

## Verdict: DEJA RECONCILIAT în manifest v2.7.48

| Entry | Path în manifest | Path pe disc | Hash disc | Hash manifest | Verdict |
|---|---|---|---|---|---|
| **H1_from_M15_v2** (context-derived) | `data/market/OANDA_XAUUSD_H1_from_M15_v2.csv` | există (2.645.110 B) | `524977d02aff…343f660` | `524977d02aff…343f660` | ✅ **MATCH** |

Path-ul din manifest = path-ul pe disc, iar hash-ul fizic = hash-ul înregistrat (`data_file_sha256.status = CONFIRMED_BY_STATISTICIAN`). **Nimic de corectat pentru acest entry.**

Istoric al discrepanței (rezolvat): v2.4.1 înregistrase greșit `acquisition_staging/..._UNREGISTERED.csv` → v2.4.2 revert la `pending` → hotfix (commit `d99d241`) a mutat fișierul la numele canonic cu `.gitattributes -text` pinuit ÎNAINTE de mutare (evitând coruperea CRLF a hash-ului) → re-hash independent la noul path = byte-identic.

## Faptul adiacent (ca nimic să nu rămână ascuns)

Trei fișiere „H1" pe disc; două sunt referite corect de manifest, unul e orfan:

| Fișier pe disc | Bytes | Hash | Status în manifest |
|---|---|---|---|
| `data/market/OANDA_XAUUSD_H1_from_M15_v2.csv` | 2.645.110 | `524977d0…343f660` | ✅ referit de `context_derived_htf/H1_from_M15_v2` |
| `acquisition_staging/OANDA_XAUUSD_H1.csv` | 6.077.821 | `414adcbe…2643b1078a` | ✅ referit de `timeframes/H1` (native, `AWAITING_REGIME_MAP`, în carantină — intenționat) |
| `data/market/OANDA_XAUUSD_H1.csv` | 1.109.701 | `5ff7420a…18868baa` | ⚠️ **ORFAN — absent din manifest** |

Orfanul `data/market/OANDA_XAUUSD_H1.csv` este H1-ul nativ **original** al repo-ului (mai mic, ~1,1 MB), pre-existent, **neatins de Data Acquisition**. Nu e menționat de nicio intrare din manifest.

**Decizia Statisticianului** (nu a mea): fie (a) se înregistrează explicit dacă are un rol, fie (b) se marchează deprecat/curăță dacă native H1 din `acquisition_staging` îl înlocuiește. Îl semnalez doar — nu-l ating.
