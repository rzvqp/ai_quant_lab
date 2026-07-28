# STATISTICIAN — RIDICAREA CONDIȚIONĂRII D3, TREI CORECȚII, GUVERNANȚĂ, PATCH RE-ARMARE (Mandat 3.10)

**Document ID:** STAT-D3-FULL-RATIF-GOVERNANCE-v1.0
**Data:** 2026-07-28 · **Autor:** Statistician
**Verificare de sursă:** citit direct `MK01_MK02_VERIFICATION_STEP1.md`, `MK01_D3_VOLUME_AUDIT_STEP2.md`, `code/mk_d3_volume_audit.py` (commit-urile `6b7948f`/`260c4e3`/`16613f0`, branch `discovery-mk-matrix-v1`) — nu doar cifrele din mesaj. Am mers mai departe: **am recalculat independent** barele de descoperire pentru bear/bull/correction direct din `data/market/OANDA_XAUUSD_M15.csv`, folosind exact epoch-urile din manifestul meu — 52.403/52.851/25.237, identice cu cifrele Research Lab, sub convenția semi-deschisă (vezi Sarcina 2). Am verificat și direct în `code/mk_d3_volume_audit.py` că importă doar `detect_swings, label_structure` — `detect_breaks` nu apare deloc în fișier.

---

## SARCINA 1 — D3: RIDICAREA CONDIȚIONĂRII

**D3 trece la RATIFICAT COMPLET, nu doar pe principiu.**

Cel mai prost bloc (correction, 0,0396%) e de ~126× sub pragul de 5% pe care l-am derivat — adânc în categoria "ieftin", fără nevoie de dezvăluire suplimentară per bloc (acel prag era pentru banda 1-5%; aici toate trei blocurile sunt sub 0,04%, cu mult sub pragul de 1%). Măsurătoarea a fost făcută pe date reale, pe blocurile de descoperire M15_v2 reale, exact cum am cerut — nu mai există motiv să rețin ratificarea.

## SARCINA 2 — DOUĂ CORECȚII

### Cifra 6, nu 8 — corectată, eroarea e a mea

Confirmat direct: `bull_partial` (segmentul al patrulea, "2022-10 pre-overlap sliver") **nu are `discovery_range`** în manifest — e `TOO_SHORT_FULLY_SEALED`, deci nu contribuie niciun bar la setul de descoperire. **3 blocuri × 2 tipuri = 6 `UNCLASSIFIED`, nu 8.** Am numărat un bloc care nu există în descoperire, și am ratificat pe propria mea cifră greșită la mandatul anterior. Corectez aici, consemnat ca eroare proprie, nu doar acceptată.

### Regula mecanică de graniță — specificată o dată, ca funcție unică

**Convenție: intervalele din manifest sunt semi-deschise — `start_epoch ≤ t < end_epoch`.** Nu aleasă arbitrar — **verificată direct**: am recalculat barele de descoperire pentru toate trei blocurile (bear/bull/correction) direct din fișierul CSV, folosind exact epoch-urile din `discovery_range`, sub ambele convenții posibile:

| bloc | semi-deschis `[s,e)` | închis `[s,e]` |
|---|---|---|
| bear | **52.403** | 52.404 |
| bull | **52.851** | 52.851 (identic — graniță fără bară exact pe capăt) |
| correction | **25.237** | 25.237 (identic) |

**Semi-deschis reproduce exact cifrele deja publicate de Research Lab** (`THREE_REGIME_PERSISTENCE_RESULT_v1.0.md`, invariant deja verificat) — pentru toate trei blocuri, nu doar pentru bear unde diferența s-a manifestat. VE a folosit implicit o convenție închisă undeva în calculul lui pe bear, de-asta a ieșit 52.404. **Semi-deschis e și alegerea matematic corectă:** granițele adiacente din propriile mele intervale (`discovery_range`→`intra_segment_embargo`→`sealed_range`, care se ating exact la un epoch comun) formează o partiție curată — fără suprapunere, fără gol — DOAR sub semi-deschis. Sub închis, bara exact la graniță ar aparține la DOUĂ intervale simultan.

**De ce se scrie o dată, ca funcție, nu se recalculează:** a treia oară azi (67.321/67.322 la Set A; 16.830/16.831 la Set B; 52.403/52.404 la bear) cu aceeași cauză — asta nu mai e coincidență, e o gaură de proiectare. Recomand ca `edge_research/split_manifest.py` (modulul de citire deja partajat, folosit deja de loader) să expună o funcție unică:

```
def in_range(epoch: int, range_dict: dict) -> bool:
    return range_dict["start_epoch"] <= epoch < range_dict["end_epoch"]
```

Orice diviziune care numără bare într-un interval din manifest o apelează pe asta — nu reimplementează inegalitatea singură. Nu implementez eu acest fișier (nu-l dețin) — specific funcția exact, ca cine îl adaugă să n-aibă nicio ambiguitate.

**Nu rezolv retroactiv Set A/Set B** (67.321/67.322, 16.830/16.831) — sunt dintr-un pipeline diferit, mai vechi, deja închise prin discuție la vremea lor. Regula de mai sus se aplică de acum înainte, mecanic, la orice interval din acest manifest.

## SARCINA 3 — TENSIUNEA DE GUVERNANȚĂ: DECIZIE, NU ANALOGIE

**Confirm mai întâi F1 (importuri):** accept corecția — premisa mea ("restul repo-ului folosește pachete + importuri relative") ținea pentru `validation_engine/ve/`, nu pentru `code/`, care nu e pachet și importă absolut peste tot (`mstrat.py`: `from alpha_lab import CFG`). Importul din draft e consecvent cu convenția locului. VE avea dreptate, corect verificat de tine.

**Decizie: `CROSS_VERIFICATION_SPEC` se aplică ARTEFACTELOR DE DATE DERIVATE, NU codului de verificare generic. Limita, scrisă explicit, ca să nu fie reinterpretată:**

`CROSS_VERIFICATION_SPEC` a fost proiectat pentru un risc SPECIFIC: un fișier derivat (ex. H4/D1/H1_from_M15_v2) a cărui construcție greșită ar scurge tăcut informație sigilată peste o graniță de bloc — de-asta cele cinci proprietăți (containment, corespondența agregării, non-suprapunere, completitudine negativă, absența orfanilor) sunt toate despre verificarea unei bare HTF față de granițele de descoperire ale manifestului. **Acest risc specific nu există la măsurătoarea D3:** auditul de volum (Pasul 2) citește EXCLUSIV prin masca `discovery_range` deja stabilită și deja verificabilă mecanic a manifestului — nu decide singur ce e "descoperire", doar numără ce e deja înăuntrul unei măști sigure. Nu poate scurge sigilat prin construcție, indiferent cine scrie codul de numărare.

**Ce ÎNSEAMNĂ asta practic:** VE scriind teste + rulând măsurătoarea pe propria implementare de test (nu pe modulele CEO, pe care nu le-a modificat) NU declanșează `CROSS_VERIFICATION_SPEC` — nu e nevoie de o a treia divizie care să repete formal cele cinci verificări. **Ce rămâne, totuși, un risc real, mai mic:** codul de test/măsurare al lui VE însuși (nescris de CEO) nu a fost verificat independent de nimeni pentru propriile bug-uri. Pentru un diagnostic o-singură-dată (nu un artefact persistent pe care alte analize se bazează), tratez asta proporțional: **verificare punctuală de către Statistician, nu recenzie formală `CROSS_VERIFICATION_SPEC`** — exact ce am făcut chiar acum, recalculând independent barele de descoperire și confirmând că `detect_breaks` nu apare în `mk_d3_volume_audit.py`.

**Limita, pentru a nu fi reinterpretată:** dacă acest cod de test/măsurare devine vreodată un artefact PERSISTENT, reutilizat pentru a valida ALTE ipoteze dincolo de această măsurătoare unică D3, calculul se schimbă — un instrument de verificare folosit repetat, de mai multe divizii, merită propria lui recenzie independentă, chiar dacă nu sub cele cinci proprietăți specifice HTF. Nu extind `CROSS_VERIFICATION_SPEC` la cod în general — extind doar vigilența dacă rolul codului se schimbă din diagnostic unic în infrastructură persistentă.

## SARCINA 4 — PATCH-UL DE RE-ARMARE

### Regula de corecție

**Swing-ul depășit se elimină definitiv din bazinul de candidați scanați de bucla de activare — la nivel de index/mulțime, nu prin setarea unei variabile downstream (`live_hh = None`) care poate fi rescrisă la bara următoare.**

1. Se menține o **mulțime de consumate** (sau un flag `consumed: bool` pe însuși obiectul `Swing`) — NU doar pointerii `live_hh`/`live_ll`.
2. Un swing intră în mulțimea de consumate exact în momentul în care o rupere/măturare e înregistrată împotriva lui — o singură dată, vreodată.
3. Bucla de activare, la fiecare bară, TREBUIE să filtreze bazinul de candidați excluzând orice swing marcat consumat, ÎNAINTE de a (re)atribui `live_hh`/`live_ll` — filtrarea se întâmplă la nivelul mulțimii/indexului, în amonte de atribuire, nu ca o anulare downstream care poate fi tăcut suprascrisă.
4. Un swing consumat nu reintră NICIODATĂ în bazinul activ, pentru restul blocului care îl conține (consecvent cu D3/D4 — oricum nu supraviețuiește peste graniță).
5. **Test de acceptare a patch-ului, specificat acum:** exemplul sintetic deja construit (un singur HH care produce mai multe BOS_BULL) rulat DUPĂ patch trebuie să arate EXACT O rupere care referă acel swing, niciodată mai mult — asta e testul de acceptare, nu o cifră aleasă după ce se vede rezultatul patch-ului.

### Auditul de volum rămâne valid — decizie, nu doar acceptarea ipotezei tale

**De acord, dar verificat, nu doar acceptat:** am citit direct `code/mk_d3_volume_audit.py` — importă exclusiv `detect_swings, label_structure`; `detect_breaks` nu apare nicăieri în fișier. Bug-ul de re-armare trăiește integral în bucla de activare a lui `detect_breaks`, o funcție separată, niciodată apelată pe calea de cod a Pasului 2. Nu e doar că bug-ul "nu s-a manifestat întâmplător" — funcția care îl conține nu e deloc invocată. **Auditul de volum rămâne valid, nu se reface.** Cifrele de la Sarcina 1 (16/9/10 bare, ≤0,04%) stau neschimbate.

---

**Nu am scris cod, nu am reparat modulele CEO, nu am atins date dincolo de verificarea directă de mai sus. Statistician se oprește aici.**
