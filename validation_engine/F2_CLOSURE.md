# ÎNCHIDEREA OFICIALĂ A FAZEI F2
### Validation Engine — validatorul de specificație, taxonomia de erori, vocabularul executabil (registru v1.0 → v1.4)

**Document ID:** VE-F2-CLOSURE-v1.0
**Data:** 2026-07-25 · **Autor:** Validation Engine
**Statut:** **ÎNCHIDERE F2 — confirmată de CEO 2026-07-25.** F3 NU este autorizat. Registrul nu a fost modificat pentru acest document; nicio implementare nouă.
**Documente guvernante:** `STATISTICIAN_VALIDATION_ENGINE_CONTRACT_v1.0.md` · `VALIDATION_ENGINE_ARCHITECTURE_v1.0.md`

> Acest document este bilanțul complet și auditabil al fazei F2. Consolidează, într-o singură referință, obiectivele, cele opt goluri descoperite (G1–G8), rezolvarea fiecăruia, deciziile de guvernanță, starea finală a registrului v1.4, ce rămâne explicit în afara F2 și condițiile pentru autorizarea F3.

---

## 1. Obiectivele inițiale ale F2

F2, conform planului de faze din arhitectură (§8), a avut un mandat strict delimitat:

- **F2.1 (obiectiv de bază):** validatorul de specificație, taxonomia de erori (E1–E9), cererea de clarificare și bateria de mutații — **fără** metode statistice, acces la date reale, population builder, holdout loader sau execuția protocoalelor.
- Cerințe cardinale: toate referințele rezolvate fail-closed; o referință inexistentă respinsă **înainte de orice acces la date**; duplicate de id respinse; cicluri detectate; garda de disponibilitate; semantica listelor definită normativ; **zero accesări de date pentru toate erorile de validare**.
- Invarianți permanenți pe toată durata F2: **toate metodele rămân `UNVALIDATED`; registrul rămâne `PUBLISHED_NOT_EXECUTABLE`; zero metode executabile; schema JSON neschimbată dacă implementarea permite; F3 neînceput.**

F2 a crescut, prin decizii CEO succesive, de la validatorul de bază la un ciclu complet de maturizare a vocabularului executabil (registru v1.0 → v1.4), declanșat de faptul că fiecare încercare de a exprima un design real a descoperit un gol.

---

## 2. Cele opt goluri (G1–G8) — descoperire și rezolvare

Toate cele opt au apărut din aceeași disciplină: **un catalog nu se auditează citindu-l, ci încercând să scrii cu el.** Poarta de publicare instituită de CEO (o specificație completă pentru un design real înainte de fiecare versiune de registru) le-a scos la iveală sistematic.

| Gol | Problema | Descoperit la | Rezolvare | Registru |
|---|---|---|---|---|
| **G1** | Nu exista primitivă pentru seria brută OHLCV; comparația preț↔nivel imposibilă | specificația DC-0004 (F2.1) | `raw_series@v1 {source_id, field}`, validat față de coloanele sursei, sub garda de leakage | v1.1 |
| **G2** | Statisticile nu își puteau primi parametrii; motorul ar fi trebuit să deducă variabila | specificația DC-0004 (F2.1) | apel parametrizat `statistic_call {id, statistic, params}`; + retipizarea `variable_ref` din `string` | v1.1 |
| **G3** | Nicio primitivă care să transforme un predicat într-o variabilă-indicator (expunere-eveniment) | specificația DC-0004 (F2.2) | `indicator@v1 {predicate}`, 0/1, cu regulă de disponibilitate recursivă + detectare de cicluri | v1.2 |
| **G4** | Semantica listelor de predicate nedefinită (conjuncție presupusă) | specificația DC-0004 (F2.2) | documentare normativă în registru (conjuncție; `exclude` la orice potrivire; liste goale; denominator per criteriu) | v1.2 |
| **G5** | 13 parametri de referință tipizați ca `string`; referință nerezolvată prinsă abia la execuție | specificația DC-0004 (F2.2) | retipizare completă + tipurile `test_ref` și `predicate_ref`; unicitate globală de id-uri de predicat | v1.2 |
| **G6** | Nicio sursă M1/M5 și nicio primitivă de agregare sub-bară (expunerea R a DC-0008) | specificația DC-0008 (F2.2) | **NEREZOLVAT** — decizie CEO explicită (în afara acestei faze) | — |
| **G7** | Nicio primitivă „prima apariție în domeniu"; evenimentul in-sample al DC-0004 inexprimabil | verificarea scripturilor Alpha (F2.3) | `first_in_scope@v1 {scope, predicate}`, lookahead-safe; scope `day` = 00:00 UTC | v1.3 |
| **G8** | Familia de corecție cu apartenență dependentă de date (n≥25) inexprimabilă | replicarea Calea A a DC-0004 (F2.3→F2.4) | `member_eligibility {field, op, value}` pe lista albă pre-rezultat `[n, denominator, event_count]`; R3 impusă prin vocabular | v1.4 |

**Șapte rezolvate, unul (G6) deliberat lăsat în afara F2.** Niciunul nu a cerut o versiune nouă de schemă — invariantul „extinderea vocabularului nu atinge schema" a rezistat prin toate cele patru revizuiri.

---

## 3. Deciziile de guvernanță adoptate în F2

Toate luate de CEO; consemnate aici pentru trasabilitate. Sunt separate de rezolvările tehnice pentru că guvernează *cum* lucrează laboratorul, nu doar *ce* exprimă motorul.

| # | Decizie | Data | Efect permanent |
|---|---|---|---|
| **D1** | **JSON-only** (A1) — specificațiile se scriu exclusiv în JSON; YAML produce oprire E3 | 2026-07-24 | politica de format |
| **D2** | **A5/A6/A7 acceptate permanent** — consolă UTF-8; etapa 2 nu rulează după eșecul etapei 1; garda de acces rămâne instalată pe durata procesului | 2026-07-24 | comportament de motor |
| **D3** | **Poarta de publicare a registrului** — înainte de fiecare versiune, o specificație completă pentru un design real | 2026-07-24 | proces obligatoriu; a produs G3–G8 |
| **D4** | **Granița sigilată** `2025-10-23T09:15:00Z` ratificată provizoriu ca graniță oficială de lucru (P4) | 2026-07-24 | convenție de date; protecția efectivă la F4/F8 |
| **D5** | **DC-0004 = Calea A (replicare strictă)** — convențiile in-sample (00:00 UTC, 4 sesiuni UTC, prima depășire, K6, baseline per sesiune, one-sided, familie empirică n≥25) sunt oficiale; definițiile din `OPERATIONAL_DEFINITIONS` NU se aplică acestui re-test | 2026-07-24 | definiția oficială DC-0004 |
| **D6** | **Seed rămâne `derived_from_spec_hash`**, fără excepție; `seed=7` literal nu se introduce | 2026-07-25 | politica de reproductibilitate primează asupra literalului in-sample |
| **D7** | **G8 = varianta V1** (eligibilitate declarativă pe listă albă pre-rezultat); tratat ca limitare generică, nu particularitate DC-0004 | 2026-07-25 | mecanism generic de familie |
| **D8** | **G6 nerezolvat în F2**; DC-0008 nemodificat ca design | 2026-07-24/25 | domeniu amânat |

Două rezultate de proces produse de F2, dincolo de cod:
- **Reconcilierea definițiilor** (`RECONCILIATION_DEFINITIONS_v1.0.md`) — a expus că definițiile propuse de Statistician **contrazic** convențiile in-sample (graniță de zi, 4 vs 3 sesiuni, definiția evenimentului); a dus la decizia D5.
- **Verificarea împotriva scripturilor Alpha** (`SCRIPT_VERIFICATION_Q1_Q3.md`) — a stabilit că „replicare" are un singur sens verificabil, și a descoperit G7.

---

## 4. Starea finală a registrului v1.4

```
registry_id:  VE-CAPREG-v1.4
status:       PUBLISHED_NOT_EXECUTABLE
```

| Categorie | Număr | Note |
|---|---|---|
| Surse de date | 4 | OANDA XAUUSD M15/H1/H4/D1, hash-uri verificate; graniță sigilată unică |
| Primitive de variabile | 16 | incl. `raw_series@v1` (G1), `indicator@v1` (G3) |
| Predicate de populație | 11 | incl. `first_in_scope@v1` (G7) |
| Statistici | 7 | invocate prin `statistic_call` (G2) |
| Metode de test | 12 | **toate `UNVALIDATED`** |
| Metode de corecție | 3 | **toate `UNVALIDATED`**; Bonferroni/BH cu `member_eligibility` (G8) |
| Reguli normative | 19 | incl. lista albă R3, disponibilitatea recursivă, semantica listelor |
| Câmpuri de eligibilitate (listă albă) | 3 | `n, denominator, event_count` — niciun câmp de rezultat |
| **Metode executabile (`VALIDATED`)** | **0** | poarta de calibrare intactă |

**Invarianți verificați mecanic la închidere:**
- schema JSON `SPEC_SCHEMA_v1.0.json` **neschimbată** de la F1 (hash `f1ba7009…`) — niciun `default`, `additionalProperties: false` peste tot;
- `ve capabilities` raportează **0 metode executabile**;
- **360 de teste trec**, **87 de mutații** (E1:18, E2:55, E3:12, E5:2) opresc toate fail-closed cu zero accesări de date;
- hash-urile celor 4 surse de piață identice cu cele înregistrate la F1;
- nimic modificat în afara `validation_engine/`.

**Specificațiile de referință, la închidere:**
- **DC-0004** (`reference_spec_dc0004.json`) — replicare strictă **completă**, fără substituent sau câmp nenormativ; validează 4×E3 (doar porți de calibrare).
- **DC-0008** (`reference_spec_dc0008.json`) — mașinărie statistică integral exprimabilă (8×E3); expunerea reală R blocată de G6, cu substituent structural explicit marcat.

---

## 5. Ce rămâne explicit în afara F2

### 5.1 Goluri deschise
- **G6** — sursă la timeframe mai fin (M1/M5) + primitivă de agregare sub-bară; blochează expunerea reală a DC-0008. Decizie CEO: în afara acestei faze.

### 5.2 Datorie de scop amânată (S1–S7 din backlog) — aparține fazelor F3+
- **S1** metodele statistice (12 test + 3 corecție), fiecare cu bateria de calibrare — **F5–F6**;
- **S2** population builder + denominatorul per criteriu — **F4+**;
- **S3** construcția variabilelor + garda de leakage la runtime (azi doar verificarea declarației) — **F4+**;
- **S4** stratul de date, sigilarea pe fereastră la loader, jurnalul de acces — **F4**;
- **S5** manifest, PRE-MANIFEST, checksums, bundle write-once, ledger — **F3**;
- **S6** subcomenzile `rehearse`, `run`, `verify` — **F3/F7**;
- **S7** protocolul de resursă sigilată (repetiție + token + consum unic) — **F8**.

### 5.3 Puncte de arhitectură rămase deschise
- **P1** — dacă VE evaluează mecanic criteriile preînregistrate (`true/false`); azi blocat activ (schema respinge `return.criteria_evaluation`) — decizie înainte de **F7**;
- **P4** — deținerea și impunerea sigiliului holdout; parțial decis (granița ratificată), efectiv la **F8**.

### 5.4 Comportamente specificate dar neexecutate (aparțin execuției)
- excluderea membrilor neeligibili și oprirea pe familie vidă (G8) — reguli scrise, aplicare la **F5+**;
- verificarea reală a hash-ului de date la sursă (E4), verificarea token-ului CEO (E5 complet) — **F4/F8**.

---

## 6. Condițiile necesare pentru autorizarea F3

F3 (conform arhitecturii §8) livrează **manifestul, checksums, ledger-ul și integritatea repository-ului** — infrastructura de audit a unei rulări, **înainte** de orice metodă statistică sau atingere de date reale. Recomand ca autorizarea F3 să fie condiționată de:

1. **Confirmarea explicită a domeniului F3** — doar infrastructura de audit (manifest/PRE-MANIFEST, checksums, ledger append-only, hash repo înainte/după). **Fără** metode statistice (F5–F6), **fără** stratul de date (F4), **fără** execuția protocoalelor.
2. **Ratificarea punctelor care ating direct F3:** niciunul blocant — P1 și P4 ating F7/F8, nu F3. De confirmat doar că F3 nu are voie să atingă date reale (rularea goală produce manifest fără a deschide vreo sursă).
3. **Menținerea tuturor invarianților F2** ca precondiție permanentă: metode `UNVALIDATED`, registru `PUBLISHED_NOT_EXECUTABLE`, schema neschimbată, zero accesări de date la validare.
4. **Decizia de secvențiere G6**: dacă G6 se rezolvă înainte sau după infrastructura F3 — recomand după, pentru că G6 este un gol de domeniu (date), nu de audit, și nu blochează F3.
5. **Confirmarea că specificația oficială DC-0004 (Calea A) este acceptată ca prima țintă de execuție** — nu executată încă, dar fixată ca reper pentru ce va trebui să producă lanțul F3→F8.

Odată aceste cinci puncte confirmate de CEO, F3 poate începe fără a atinge niciun invariant al F2.

---

## 7. Concluzie

F2 și-a îndeplinit mandatul și l-a depășit disciplinat: a livrat validatorul fail-closed cerut, iar prin poarta de publicare a maturizat vocabularul executabil de la v1.0 la v1.4, rezolvând șapte din opt goluri fără a atinge vreodată schema, o metodă executabilă sau o dată de piață. Motorul se **oprește corect** înainte să calculeze ceva — proprietatea pe care arhitectura a pus-o deliberat înaintea oricărei capacități de calcul.

**F2 este închis. Nicio metodă este executabilă. Nicio dată de piață a fost citită. F3 nu a fost început.**

**Validation Engine se oprește și așteaptă aprobarea CEO pentru autorizarea F3.**
