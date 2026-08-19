# SPECIFICAȚIE BYTE-EXACTĂ — `bars_sha256` · versiune `bars_sha256_v1`

Normativă. Remediază `ESCROW-UNREPRODUCIBLE-ANCHOR` (RT-RANGE-0009, `e504fcf`).
Reprodusă **48/48** contra ancorelor deja publicate. Nicio ancoră nu a fost înlocuită.

---

## 0 — De ce au eșuat ~7.700 de convenții

Ordinea câmpurilor este **`H, L, O, C`** — nu `OHLC`. Red Team a încercat ~24 de convenții,
eu încă ~7.700; toate presupuneau ordinea `OHLC` sau serializare textuală. Ancora nu e text:
e un buffer binar `int64`.

---

## 1 — Sursa barelor

| element | valoare |
|---|---|
| repo / ramură | `ai_quant_lab-alpha-automation`, `alpha-automation-v1` |
| loader | `edge_research/_common.py`, funcția `load` |
| cheie timeframe | `M15_v2` |
| `data_split_id` | `pre_holdout_2025-10-23T09-15-00Z_v1` |
| `cutoff` | `2025-10-23T09:15:00Z` |
| fișier sursă | `data/market/OANDA_XAUUSD_M15.csv` (urmărit în Git) |
| SHA-256 sursă | `57f4ed9544993c8fbba28d9c1e3319f2e0665ef5db211fb09d9f4622222ccd37` |
| rânduri livrate | **197.094** |
| segmente discovery | **4** |
| amprentă corpus | `af3bf2f6ffc35ba4c4f4c6da9963c06ff5c99c4952b5ab62d42218cc7b254cf3` |

> ★ **Care loader.** Loaderul din `ai_quant_lab-wp5b` returnează **130.491** de bare pentru
> ACELAȘI timeframe, fiindcă manifestul lui declară **3** segmente de discovery, nu 4.
> Divergența era deja consemnată în manifestul Statisticianului. Ramura de mai sus este
> singura care produce cele patru blocuri oficiale. Aici a stat, de fapt, prima jumătate a
> blocajului: corpusul nu lipsea — era în celălalt worktree.

> ★ **Invarianță peste data sigilării.** Intrarea `M15_v2` din manifest e byte-identică la
> v2.7.92 (`6ae0837`), v2.7.93 (`96a7352`) și v2.7.94 (`14d4c22`) — amprentă
> `5d1cccabc3be9784ab8164ac79303774`. Reproductibilitatea **nu** depinde de o versiune de
> manifest scrisă după sigilare.

## 2 — Care bare: fereastra **RANDATĂ**

```
[render_start, render_end)      ← interval SEMI-DESCHIS: start inclus, end exclus
```

Fereastra randată = fereastra canonică plus contextul **24 + 24** de bare, deci
`render_end − render_start = L + 48`.

★ **NU** se folosește `[canonical_index_start, canonical_index_end)`. Red Team a declarat
această ambiguitate explicit deschisă (§7.2). E tranșată empiric, nu prin preferință:
fereastra randată dă **48/48**, cea canonică dă **0/48**.

Relația verificată pe toate cele 48: `canonical_index_end − canonical_index_start == L`, iar
`canonical_index_start` rezolvă la `start_utc` și `canonical_index_end − 1` la `end_utc`
(48/48 pe toate trei).

## 3 — Serializarea, byte cu byte

```
1. patru vectori, CONCATENAȚI pe coloane în ordinea:   high, low, open, close
      blob = concat( H[0..n) , L[0..n) , O[0..n) , C[0..n) )
   ★ concatenare pe COLOANE, nu întrețesere pe rânduri
2. fiecare valoare:   int64( valoare × 1e6 )
      numpy .astype("int64") = TRUNCHIERE spre zero, NU rotunjire
3. reprezentare:  8 bytes/element, little-endian, ordine C, contiguu
      ndarray.tobytes()
4. hash:  sha256(blob)  →  hex minuscul, 64 caractere
```

**Nu intră în hash:** timestamp, volum, header, separatori, ghilimele, encoding textual,
newline, ID-ul ferestrei, `L`, indicii. Fluxul e pur binar.

Câmpuri excluse explicit: `time`, `volume`, `atr14`, `session`, `dow`.

Implementare de referință: `escrow_repro/canonical_corpus.py`, funcția `bars_sha256`.

## 4 — Rezoluție și limita ei, măsurată

Scalarea `1e6` cu trunchiere dă o rezoluție de `1e-6` în preț. **Măsurat, nu presupus:** o
perturbație de *exact* `1e-6` poate fi absorbită de rotunjirea `float64` înainte de trunchiere
(pe prima bară a ferestrei verificate exact asta se întâmplă); de la `2e-6` în sus detecția e fermă.

Consemnat ca **proprietate a ancorei, nu ca defect**: un tick XAUUSD este **0,01** (corectat
2026-08-20, mandat 3.107 — aici scria 0,001, greșit; tickul normativ e declarat în `SymbolMeta`
pe patru subsisteme AI Trader și ratificat de Red Team în `RT-AUDIT-MEAS-0001`), adică **10.000**
de unități după scalare — o marjă de **patru** ordine de mărime, deci concluzia se întărește. Ancora există ca să detecteze un corpus
diferit sau o fereastră substituită, iar pentru asta rezoluția e mai mult decât suficientă.
Testul `test_15b` fixează această limită în suită ca să nu fie descoperită din nou prin surpriză.

## 5 — Ce NU acoperă această specificație

`window_list_sha256` (`d9f77eea…`) **nu** a fost reprodusă din câmpurile mapping-ului. Ea a fost
calculată peste lista de ferestre *înainte* de orice citire OHLC, într-o formă textuală
intermediară care nu e reconstructibilă din artefactele sigilate. Nu inventez o rețetă pentru
ea și nu o înlocuiesc.

**Nu blochează** §4 din mandatul RT-RANGE-0009: verificarea cerută acolo este a barelor
(`bars_sha256`), care e acum reproductibilă 48/48. `window_list_sha256` rămâne o ancoră
istorică nereproductibilă și e declarată ca atare — vezi raportul, §Blocaje reziduale.
