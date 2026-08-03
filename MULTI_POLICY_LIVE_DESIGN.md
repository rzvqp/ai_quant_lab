# Design: Executie DEMO pentru Politici Multiple (CAND-0001 + CAND-0007 + CAND-0009 + CAND-0019)

**Status:** DESIGN, neimplementat. Asteapta confirmare inainte de constructie.
**Data:** 2026-08-04

## 0. Doua constatari care preced designul

Inainte de arhitectura propriu-zisa, doua lucruri descoperite in cod care ating direct fezabilitatea:

### 0.1. "Toate patru au iesiri valide live" — nepotrivire cu ce gasesc in repo

Am verificat `vendor/alpha_automation_demo_gate/CANDIDATE_QUEUE.md` si fisierele `POLICY_*.md` individuale:

- **CAND-0007 (Level-FVG-Confluence)** si **CAND-0009 (Level-Break-Drive)**: Part A (recunoastere) e complet
  definit, dar **Part B (stop/target/management — specificatia de risc) e marcat UNSPECIFIED** in fisierele
  proprii de politica. Asta e exact starea in care era CAND-0001 inainte ca tu si Statisticianul sa
  stabiliti gardurile S1/S2/S3 si sa le legati de un `demo_gate_engine`.
- **CAND-0019 "DZ x Level"**: nu exista nicaieri in repo — nici in `CANDIDATE_QUEUE.md`, nici ca fisier de
  politica, nici ca nume alternativ ("Displacement Zone", "DZ-x-Level"). Cel mai apropiat ca nume e
  CAND-0013 "Demand-Zone-Reentry", dar are alt Part A (re-entry pe zona de cerere/oferta, nu "DZ x Level")
  si Part B tot UNSPECIFIED.

Nu presupun ca sunt gresit — poate Alpha/Statisticianul au avansat Part B pentru 0007/0009 si au deschis
0019 intr-un commit mai nou al submodulului vendor pe care checkout-ul meu local nu-l are inca. Am nevoie
de commit-ul exact (asa cum mi-ai dat `1558397` pentru PDH-PDL) inainte sa pot cabla ceva pentru aceste
trei — designul de mai jos e independent de continutul lor si se aplica oricum, dar **nu pot construi
recognition rules pentru 0007/0009/0019 fara Part B ratificat**, la fel cum n-am putut nici pentru
CAND-0001 inainte de gardurile tale.

### 0.2. Netting vs Hedging — o presupunere ascunsa in codul existent

`LiveMT5FillReader.is_position_open`/`.read_close_price` (deja in productie pentru CAND-0001) filtreaza
`positions_get(symbol)` dupa `magic_number` — asta functioneaza corect DOAR daca contul FusionMarkets-Demo
e in mod **Hedging** (fiecare ordin/pozitie tinut separat, cu magic-ul lui propriu). Daca contul e in mod
**Netting** (un singur rand de pozitie per simbol, cantitatile se compenseaza), doua politici cu semnal opus
pe XAUUSD (vezi 3.3 mai jos, exact cazul PDH-PDL vs Level-Break-Drive) ar plasa doua ordine care s-ar
compensa/inversa la nivel de broker — motorul de audit al FIECAREI politici ar citi date corupte, crezand
ca urmareste propria lui pozitie cand de fapt urmareste rezultatul net al ambelor.

Asta era latent si pentru CAND-0001 singur (nimic cu care sa se compenseze), dar devine activ in clipa in
care a doua politica trimite un ordin pe acelasi simbol. **Trebuie verificat inainte de constructie** —
un singur apel `account_info().margin_mode` pe terminalul real, cateva secunde. Il fac ca parte din
verificarea de conectivitate a pasului urmator, nu acum (asta ar fi implementare).

## 1. Cum ruleaza patru politici simultan, fiecare cu recognition rule proprie

**Un singur proces, un singur bar feed partajat, patru instante independente de recognition rule.**

Toate cele patru politici confirmate ca existand (0001, 0007, 0009 — 0019 neconfirmat) sunt XAUUSD M15.
`LiveBarFeed`-ul actual cheie watermark-ul dupa `(symbol, mt5_timeframe)` fara discriminator de politica —
patru instante separate de `LiveBarFeed` pe acelasi simbol/timeframe, scriind in acelasi state store,
s-ar calca pe watermark (ultimul care scrie castiga, la fel si la restart). Deci: **un singur
`LiveBarFeed`, o singura interogare MT5 pe tick**, bara noua distribuita catre toate cele patru
recognition rules.

Fiecare politica ramane o clasa proprie, independenta (`PdhPdlRecognitionRule`-equivalent), cu propriile
arrays interne (`current_bar_count`/`current_arrays`) si propriul `PdhPdlOrchestrator`-equivalent — fiecare
tine "o pozitie deschisa per politica", exact ca acum, fara sa stie de celelalte trei. Izolarea la nivel de
obiect (nu doar de log) e ce face posibil raspunsul de la intrebarea 5 (o politica pica, celelalte
continua).

Motorul `demo_gate_engine` (`simulate_demo_trade`/`DemoSignal`/`min_executable_risk`) e deja generic —
verificat direct in cod: `DemoSignal` ia doar `(entry_idx, direction, stop, target, atr, effective_spread,
cost, day_end_idx)`, fara nimic specific PDH/PDL. Aceeasi functie servita din acelasi import, chemata de
fiecare orchestrator separat, post-hoc, o data per tranzactie inchisa — **niciodata duplicata**, cum ai
cerut.

Bucla devine, conceptual:

```
tick():
    verifica circuit breaker (o singura data, la nivel de cont, INAINTE de orice politica)
    bars = shared_feed.poll()   # o singura interogare MT5
    pentru fiecare bara noua:
        pentru fiecare politica (ordine fixa, deterministica: 0001, 0007, 0009, 0019):
            daca politica e activa (vezi intrebarea 6):
                try: evaluate / submit / observe_bar / audit post-hoc pentru ACEASTA politica
                except: jurnalizeaza POLICY_ERROR pe jurnalul ACESTEI politici, marcheaza degradata, continua
```

**Alternativa notata, nerecomandata ca implicit**: patru procese OS separate, fiecare cu propriul state
store. Izolare mai puternica la crash (un proces mort nu poate atinge memoria altuia), dar reintroduce
watermark-ul de bar feed x4 (fiecare cu propriul apel MT5) si mai ales cere coordonare SQLite
multi-proces pentru orice stare cu adevarat comuna (circuit breaker, ledger-ul de risc de la intrebarea
2) — SQLite suporta scriere concurenta din mai multe procese, dar cere disciplina suplimentara
(busy_timeout, WAL) pe care un singur proces Python n-o cere deloc. Semnalez optiunea, dar recomand un
singur proces.

## 2. Cum se aloca riscul cand doua semnale apar in aceeasi zi — INTREBAREA CARE CONTEAZA

Fapt din cod, nu presupunere: `compute_sizing` (`risk_manager/sizing.py`) STIE sa limiteze expunerea totala
si pe grup de corelatie — cod real, testat — dar sursa lui de date, `MT5PortfolioStateSource`
(`mt5_pnl_source/source.py`), lasa deliberat `open_positions`/`gross_notional` goale (disclosure propriu in
docstring: "leaves open_positions ... at their type's own empty defaults"). Asta inseamna ca **azi**, chiar
si cu o singura politica activa, gardurile `max_positions`/`max_correlated`/`max_exposure_pct` din
`risk_manager/limits.py` nu vad niciodata o pozitie reala — sunt cod corect, dar mort in calea live.

Deci intrebarea ta nu e ipotetica: nimic din ce ruleaza azi ar opri patru alocari de 0,5% sa se adune la
2% intr-o zi in care toate patru semnaleaza. Si nu e nici coincidenta rara — trei din patru politici
(0001, 0007, 0009 confirmate; 0019 necunoscut) ancoreaza pe **nivelul zilei precedente** — o zi cu miscare
mare care sparge/atinge PDH sau PDL e exact genul de zi in care mai multe din ele pot semnala simultan.
Corelatia structurala e reala, nu accidentala.

Inca un detaliu care schimba magnitudinea: o politica poate inchide o tranzactie si SEMNALA DIN NOU in
aceeasi zi (nimic in `PendingPdhPdlTrade`/orchestrator nu limiteaza la o tranzactie per zi per politica —
doar "o pozitie deschisa o data"). Deci plafonul naiv de "4 x 0,5% = 2%" e de fapt un plafon **inferior**,
nu unul garantat — fara o limita explicita de tranzactii/zi, expunerea zilnica teoretica e nemarginita.

### Optiunile, cu costul fiecareia

**A. Bugete fixe, mai mici, per politica** (ex: 0,25% x 4 = 1% total in cel mai rau caz)
Cel mai ieftin de construit — un singur parametru (`risk_per_trade_pct`) diferit per fabrica de
dependinte, la nivelul de cablare (execution layer), NU in politica inghetata insasi
(`POLICY_PDH_PDL_v2.md` etc. nu specifica niciodata procentul de risc — asta a fost intotdeauna un
parametru de executie, setat de `LivePdhPdlDepsFactory` din `RiskConfig()` implicit; schimbarea lui nu
atinge fisierul de politica si nu reseteaza evidenta). Cost real: fiecare politica captureaza mai putin
edge in dolari per tranzactie (marime mai mica, acelasi % de edge) — compromis cuantificabil, nu doar
inginerie. Nu rezolva "o tranzactie/politica/zi nemarginit" de mai sus.

**B. Bazin comun, dinamic** (ex: 1% total, primul-venit-primul-servit)
Fiecare politica pastreaza 0,5% per tranzactie; un ledger nou, partajat, verifica INAINTE de trimitere
daca riscul cumulat de azi + aceasta tranzactie ar depasi bazinul — daca da, refuza cu
`REFUSED_RISK_POOL_EXHAUSTED`, jurnalizat. Foloseste bugetul mai eficient cand semnalele sunt rare (nu
taie fiecare politica la jumatate "de siguranta"), dar introduce o problema de corectitudine: ordinea fixa
de evaluare din intrebarea 1 (0001, 0007, 0009, 0019) inseamna ca in orice zi cu mai multe semnale,
PRIMELE din ordine castiga bugetul sistematic — un bias structural care ar trebui expus explicit daca
rezultatele astea intra vreodata intr-o comparatie intre politici. Cost de constructie: moderat — un
ledger nou + un gard nou in calea de submitere, per politica.

**C. Populeaza `PortfolioState.open_positions` cu date reale, activeaza mecanismul deja construit**
Solutia arhitectural "corecta": in loc sa inventez un ledger nou, construiesc maparea reala
`positions_get()` (filtrat per magic number → politica) catre `PortfolioState.open_positions`, ceea ce
activeaza `max_positions`/`max_correlated`/`max_exposure_pct`/`max_leverage` — cod deja scris, deja
testat, doar infometat de date azi. Asta rezolva problema pentru cele patru politici ACUM si pentru orice
politica viitoare, automat, fara sa mai construiesc un gard nou de fiecare data. Cost: cel mai mare —
atinge `mt5_pnl_source`, un pachet PARTAJAT (dependinta a lui `LivePdhPdlDepsFactory` deja, si potential a
altor lucruri) — dupa regula de scop din proiect, o modificare aici cere regresie pe TOT arborele
`ai_trader/`, nu doar pe pachetul politicii. In plus, asta a fost deliberat amanat o data — docstring-ul
`mt5_pnl_source/source.py` spune explicit ca reconstruirea `open_positions` "ar necesita maparea
pozitiilor/ordinelor MT5 inapoi la strategy_id/risk_pct/correlation_group, ceea ce acest pas n-a fost
autorizat sa construiasca." Cere autorizare noua explicita, nu doar o decizie de design.

**D. Fara mecanism nou — accepti plafonul, disclosed** (deloc de construit acum)
Zero cost de constructie, dar dat fiind (a) corelatia structurala pe nivel-de-zi intre politici si (b)
posibilitatea de re-semnalare in aceeasi zi per politica, plafonul real necontrolat e mai mare decat 2% si
nemarginit teoretic. Cel mai riscant, cel mai rapid de pornit.

Nu aleg. Astea sunt costurile — spune care combinatie vrei (poti combina, ex: A pentru pornire imediata +
C ca proiect separat, mai mare, de infrastructura).

## 3. Ce se intampla daca doua politici dau semnal opus pe acelasi nivel

Structural asteptat, nu o eroare: **CAND-0009 (Level-Break-Drive) e explicit opusa directional fata de
CAND-0001 (PDH-PDL)** — una e continuare-dupa-ruptura, cealalta e respingere/reversal. Aceeasi atingere de
PDH poate declansa short pe PDH-PDL si long pe Level-Break-Drive in aceeasi bara.

Fiecare politica are orchestratorul ei, pozitia ei "unica" — nimic din designul de la intrebarea 1 le
opreste sa deschida simultan directii opuse pe acelasi simbol. Daca contul e in mod **Hedging** (vezi
0.2), asta functioneaza curat — MT5 tine cele doua pozitii separat, dupa magic number, exact cum
`LiveMT5FillReader` presupune deja azi. **Daca e Netting**, cele doua ordine se compenseaza la nivelul
brokerului — ambele motoare de audit ar citi o realitate corupta.

Pana la verificarea modului de cont (pasul urmator, nu acum), propun ca regula structurala, nu ca decizie
de risc: **un mutex simplu la nivel de simbol** — daca orice politica are deja o pozitie deschisa pe
XAUUSD, o alta politica ce vrea sa deschida (in orice directie) e refuzata cu
`SYMBOL_ALREADY_IN_USE_BY_ANOTHER_POLICY`, jurnalizat, motorul ei propriu nefiind niciodata chemat pentru
acea incercare. Serializeaza politicile pe simbol, nu le lasa niciodata sa concureze la nivel de broker.
Costul: pe zilele cu semnale multiple, doar prima politica din ordinea fixa tranzactioneaza — inca un loc
unde ordinea de evaluare conteaza (acelasi bias ca la optiunea B de mai sus). Daca terminalul confirma
Hedging, mutex-ul asta devine optional (poate ramane totusi ca garda suplimentara, ieftina) — daca
confirma Netting, devine obligatoriu, nu optional.

## 4. Cum se izoleaza jurnalul si auditul per politica

Un singur `SqliteStateStore` de nivel "cont" (circuit breaker, watermark-ul bar feed-ului partajat,
ledger-ul de risc daca alegi B/C de la intrebarea 2) + **cate un `log_name` distinct per politica** pentru
jurnalul de semnale si cel de audit, in acelasi fisier sau in fisiere separate per politica — ambele
variante functioneaza tehnic (verificat: `append_log_entry` are `seq` auto-incrementat per `log_name`, deci
scriitori multipli pe acelasi `log_name` nu se suprascriu niciodata, doar se intercaleaza). Recomand
fisiere SEPARATE per politica (`pdh_pdl_demo_state.db`, `level_fvg_confluence_state.db`, etc.) pentru ca:
usor de arhivat/inspectat o singura politica fara sa atingi altele, usor de sters/reconstruit dupa un
reset de politica fara sa afectezi restul, si evita orice ambiguitate despre cine a scris ce intr-un
tabel comun. Costul: cateva fisiere in plus, neglijabil.

Circuit breaker-ul ramane in mod deliberat la nivel de cont (un singur fisier, o singura sursa de adevar)
— o suspendare din pierderi/drawdown trebuie sa opreasca TOATE politicile, nu doar una, pentru ca
protejeaza contul, nu o politica.

## 5. Daca o politica pica, celelalte continua?

Da — fiecare politica proceseaza in propriul bloc `try/except` in bucla comuna (sectiunea 1). O exceptie
la evaluare/submitere/audit pentru o politica:
- e prinsa, niciodata lasata sa opreasca bucla;
- se jurnalizeaza un tip nou de intrare de audit, `POLICY_ERROR`, in jurnalul ACELEI politici (tip
  exceptie, mesaj, bara la care s-a intamplat);
- politica e marcata automat "degradata" (acelasi mecanism ca oprirea manuala de la intrebarea 6) — NU mai
  primeste semnale noi pana nu o repornesti explicit, in loc sa incerce din nou la fiecare bara si sa
  umple jurnalul cu aceeasi eroare.

Nuanta importanta: daca politica degradata are deja o pozitie DESCHISA, `observe_bar` (detectarea
inchiderii de la broker + inchizatorul mecanic de sfarsit de zi) tot trebuie sa ruleze pentru ea — a opri
monitorizarea unei pozitii deschise e mai rau decat a continua sa o urmaresti pana se inchide singura.
Deci "degradata" inseamna "nu accepta candidati noi", nu "ignora tot ce are deja pe foc".

Circuit breaker-ul si bar feed-ul partajat sunt in afara oricarui bloc per-politica — o eroare intr-o
politica nu poate niciodata sa le atinga.

## 6. Cum se opreste una singura, fara sa opresti procesul

Un flag persistat, per politica, in store-ul de nivel cont — `policy_enabled:{policy_id}` — citit din nou
la INCEPUTUL fiecarui tick pentru fiecare politica, exact aceeasi disciplina ca la circuit breaker ("starea
se consulta fresh, nu se cacheaza"). Setarea lui nu cere sa atingi procesul care ruleaza — un script mic,
separat, scrie direct in acelasi store (aceeasi mecanica `SqliteStateStore.set_value` deja folosita pentru
watermark). Cand o politica e dezactivata: nu mai primeste candidati noi, dar (ca la intrebarea 5) orice
pozitie deja deschisa a ei continua sa fie monitorizata si inchisa normal — o oprire gradata, nu una
brutala care abandoneaza o pozitie pe foc.

## Recapitulare — ce ramane inghetat, ce e nou

- **Inghetat, neatins**: fiecare politica (Part A + Part B, odata ratificate), `demo_gate_engine` (un
  singur import, partajat, niciodata duplicat), gardurile S1/S2/S3 (identice pentru toate), politica deja
  activa CAND-0001.
- **Nou, la nivel de cablare** (nu de politica): un bar feed partajat, patru recognition rules si
  orchestratori independenti, izolare try/except per politica, flag de pauza per politica, jurnal/audit
  separat per politica, si — in functie de raspunsul tau la intrebarea 2 — un mecanism de plafon de risc
  (A, B, C sau D).
- **De verificat inainte de constructie, nu de decis acum**: modul de cont (Netting/Hedging) si commit-ul
  exact / Part B pentru CAND-0007, CAND-0009, si identificarea CAND-0019.

Astept confirmare pe: (1) optiunea de risc de la intrebarea 2, (2) daca mutex-ul pe simbol de la intrebarea
3 e acceptabil ca regula implicita pana verific modul de cont, (3) commit-ul/Part B pentru cele trei
politici noi. Dupa aceea construiesc.
