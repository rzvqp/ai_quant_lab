# RANGE V4.3 — Raport Performanță (Faza 5, mandat §14)

**Autor:** VE · **Data:** 2026-08-19

## Metodologie

Două regimuri sintetice, fiecare rulat pe exact 355.696 bare (numărul citat în mandat), cu ATR
sintetic fix = 1.0, măsurând timpul per chunk de 35.569 bare (10 chunk-uri):

- **`mixed`** — nivelul de bază se schimbă la fiecare 400 bare (forțează închideri, breakout-uri,
  promovări, deschideri de candidați noi în mod repetat pe toată durata rulării — regimul "realist").
- **`pinned`** — adversarial: UN SINGUR nivel pe toată durata (100±10), nicio închidere forțată —
  stres țintit pe acumularea NEMĂRGINITĂ (`_UnboundedSlope._n`, `Structure.n_bars`,
  `Cluster.members` înainte de îngheț) pe care designul O(1)/O(n) trebuie s-o suporte fără degradare.

## Rezultate

| regim | bare | timp total | μs/bară (medie) | primul chunk | ultimul chunk | evenimente |
|---|---:|---:|---:|---:|---:|---:|
| `mixed` | 355.696 | 12,70 s | 35,7 μs | 34,5 μs | 37,2 μs | 20.498 |
| `pinned` | 355.696 | 11,07 s | 31,1 μs | 29,6 μs | 30,4 μs | 1 |

**Cost per-bară pe toate cele 10 chunk-uri (secunde/35.569 bare):**

- `mixed`: 1,227 / 1,259 / 1,266 / 1,276 / 1,273 / 1,282 / 1,263 / 1,270 / 1,267 / 1,322 — plat, fără
  tendință de creștere (variație totală ~7%, consistentă cu jitter de sistem, nu cu degradare O(n²)).
- `pinned`: 1,054 / 1,053 / 1,022 / 1,092 / 1,029 / 1,016 / 1,077 / 1,144 / 1,500 / 1,082 — plat
  similar (un singur chunk cu vârf izolat, 1,50s la #9, urmat de revenire la 1,08s la #10 — consistent
  cu o pauză GC izolată, nu cu o tendință susținută).

**Concluzie:** costul per-bară NU crește pe măsură ce istoria acumulată crește, în NICIUNUL din cele
două regimuri — inclusiv în cazul adversarial `pinned`, unde o singură structură rămâne activă și
acumulează closes pe TOATE cele 355.696 bare fără nicio evacuare (`_UnboundedSlope` n-are fază de
evicție, spre deosebire de fereastra mărginită a lui 0.4.1). Semnătura empirică e O(1) amortizat per
bară / O(n) total, nu O(n²) — exact defectul din care 0.4.0 s-a auto-corectat (`_RunningMedian`) și
exact ce mandatul §14 interzice explicit.

## Memorie / istoric mărginit

- `internal_history_len` a atins exact plafonul `maxlen=64` în regimul `mixed` (multe cicluri de
  deschidere/închidere pe 355k bare) — confirmă că istoricul NU crește nemărginit.
- În regimul `pinned`, clusterul MACRO-ului (singura structură activă) are doar 3/4 membri la final
  (nu 355.696) — confirmă că îngheț-ul la confirmare (§6 mandat, `Cluster.frozen`) oprește efectiv
  creșterea listei de membri pt. orice structură long-lived, nu doar teoretic.

## Snapshot / restore la scară

După cele 355.696 bare (`mixed`): snapshot = **0,246 ms**, restore = **2,0 ms**, dimensiune
serializată ~60 KB — dominat de cele ≤64 intrări din istoricul mărginit, NU de numărul total de bare
procesate. Overhead-ul de snapshot/restore nu scalează cu durata rulării.

## Configurații adversariale acoperite

- Structură unică, niciodată închisă, acumulare nemărginită pe `_drift`/`n_bars` — **`pinned`**, de mai sus.
- Cicluri repetate de deschidere/închidere/promovare, presiune pe istoricul mărginit — **`mixed`**, de mai sus.
- Bucle O(n²): niciuna identificată — designul evită explicit `sorted(members)` la fiecare citire
  (`_RunningMedian`, deviere deliberată de la harness, documentată în `Cluster`) și evită re-parcurgeri
  ale istoricului complet la fiecare bară (`_UnboundedSlope` — actualizare O(1) prin statistici
  suficiente, fără fereastră de evacuat, dar și fără re-scanare).

## Verdict

Niciun defect de performanță identificat pe cele două regimuri testate, la scara cerută de mandat
(355.696 bare). Nu blochează livrarea prototipului conform §14.
