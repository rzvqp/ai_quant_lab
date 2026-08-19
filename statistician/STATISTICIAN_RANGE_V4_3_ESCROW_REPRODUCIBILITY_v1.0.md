# REMEDIEREA `ESCROW-UNREPRODUCIBLE-ANCHOR`

**Divizia Statistician · mandat 3.106 · 2026-08-19**
**Status: `RANGE_V4_3_ESCROW_REPRODUCIBILITY_PACKAGE_READY_FOR_RED_TEAM`**
`self_declared_pass = false` · **48/48 ancore reproduse independent** · **zero ancore înlocuite**

Pachet executabil: `ai_quant_lab-alpha-automation`, ramura `alpha-automation-v1`, `escrow_repro/`,
commituri `6b96430` + `dc1d9ed`. Amprentă pachet
`2f8dd39c567bd0e888d88505b9bd28664d3ca37ac37a1dca30ec8271037162e2`.

---

## 1 — VERIFICAREA SURSELOR (înainte de orice modificare)

Toate cele zece commituri citate de mandat **există**; `local = remote` pe toate patru oglinzile.

| commit | conținut verificat direct din Git |
|---|---|
| `d6e599e` | pachetul contractual V4.3 (Statistician) |
| `14d4c22` | manifest v2.7.94 |
| `2c113ef` | RT-RANGE-0006, audit static (E81) |
| `f224e7d` | prototipul VE îngheţat |
| `b7c6fa8` | RT-RANGE-0007, două verdicte (E82) |
| `82f27c0` | runnerul reproductibil |
| `eb62d3e` | RT-RANGE-0008, audit runner (E83) |
| `38daf9b` | protocolul pre-run RT-RANGE-0009 |
| `e504fcf` | verdictul `BLOCKED_ESCROW` (E84) |
| `8e04dd7` | raportul curăţat de timestampuri sigilate |

Am citit verdictul Red Team integral, nu rezumatul din mandat. **Constatarea lor e corectă și
este a mea de reparat.** Nu am reinterpretat niciun verdict: `RANGE_V4_3_REAL_BAR_EXECUTION_BLOCKED_ESCROW`,
`RANGE_V4_3_REAL_BAR_METRICS_INVALID`, `INDEPENDENT_SEMANTIC_BLIND = FALSE`,
`BLIND_PASS_NOT_PERMITTED` rămân în picioare până când Red Team decide altfel.

---

## 2 — CE ERA, DE FAPT, DEFECTUL

### 2.1 Corpusul nu lipsea — era în celălalt worktree

Red Team a căutat un fișier de ~197.094 rânduri în `ai_quant_lab-wp5b`, `ai_quant_lab` și în folderul
escrow, și **nu a găsit niciunul. Corect.** Corpusul canonic nu este un fișier: e **ce livrează
loaderul pre-holdout** — iar cele două worktree-uri **nu sunt de acord**:

```
ai_quant_lab-wp5b            _common.load('M15_v2')  ->  130.491 bare   (manifest cu 3 segmente)
ai_quant_lab-alpha-automation _common.load('M15_v2')  ->  197.094 bare   (manifest cu 4 segmente)
```

Divergenţa era **deja consemnată în propriul meu manifest**, ca defect măsurat side-by-side — de
acolo am ajuns la ea. Indicele `178.230` „depăşea 84.152 şi era decalat faţă de 355.696" exact
fiindcă aparţine unui al treilea spaţiu de indexare, cel cu patru blocuri.

**Verificat, nu presupus** — pe toate cele 48 de ferestre:

| verificare | rezultat |
|---|---|
| `canonical_index_start` → `start_utc` sigilat | **48/48** |
| `canonical_index_end − 1` → `end_utc` sigilat | **48/48** |
| `canonical_index_end − canonical_index_start == L` | **48/48** |

Şi corpusul e **invariant peste data sigilării**: intrarea `M15_v2` din manifest e byte-identică la
v2.7.92 (`6ae0837`), v2.7.93 (`96a7352`) şi v2.7.94 (`14d4c22`) — amprentă `5d1cccab…`.
Reproductibilitatea **nu** depinde de o versiune de manifest scrisă de mine după sigilare.

### 2.2 Reţeta nu e text, iar ordinea câmpurilor e `H, L, O, C`

Aici a stat cauza reală a celor ~24 de convenţii încercate de Red Team şi a încă **~7.700** încercate
de mine: **toate presupuneau ordinea `OHLC` sau o serializare textuală.** Ancora e un buffer binar:

```
blob = concat( H , L , O , C )        ← concatenare pe COLOANE, nu întreţesere pe rânduri
       fiecare valoare: int64( x × 1e6 )     (TRUNCHIERE spre zero, nu rotunjire)
       ndarray.tobytes()  → 8 bytes/element, little-endian, ordine C
bars_sha256 = sha256(blob)
```

Fără timestamp, fără volum, fără header, fără separatori.

**Nu am inventat reţeta.** Am recuperat codul real de sigilare şi apoi l-am **verificat** contra
ancorelor deja publicate: **48/48** pe escrow-ul îngheţat. Recuperare plus verificare, nu invenţie —
distincţia contează, fiindcă §8 din mandat interzice explicit inventarea.

### 2.3 Întrebarea deschisă a Red Team, tranşată

Red Team a lăsat explicit deschis (§7.2) dacă se hashuiește fereastra `L` sau cea randată.
**Fereastra RANDATĂ** `[render_start, render_end)`, cu contextul 24 + 24. Tranşat empiric, nu prin
preferinţă: **randată 48/48, canonică 0/48.**

---

## 3 — MATRICEA PASS/FAIL PE CERINŢE

| § | cerinţă | rezultat |
|---|---|---|
| 1 | commituri verificate din Git, `local=remote` ×4 | **PASS** |
| 2 | verdictele Red Team nereinterpretate | **PASS** |
| 4A | reconstrucţie deterministă a corpusului | **PASS** — 197.094 exact, 4 segmente |
| 4A | SHA-256 sursă publicat | **PASS** — `57f4ed95…`, fişier urmărit în Git |
| 4A | schemă, filtre, ordine, concatenare definite | **PASS** — `canonical_corpus.py` |
| 4A | SHA-256 rezultat publicat | **PASS** — `af3bf2f6…` |
| 4A | două execuţii curate → acelaşi artefact | **PASS** — amprentă identică în 2 checkout-uri |
| 5 | specificaţie byte-exactă completă | **PASS** — `BARS_SHA256_SPEC.md` |
| 5 | script care reproduce din corpus + mapping, fără valori hardcodate per fereastră | **PASS** |
| 6 | verificator, punct de intrare unic | **PASS** — `verify_range_v43_escrow.py` |
| 6 | PASS numai la 48/48, exit nenul altfel | **PASS** — exit 0 la 48/48, 1 la nepotrivire, 2 la excepţie |
| 6 | output fără date sigilate | **PASS** — test 21 verifică mecanic |
| 7 | 48/48 reproduse | **PASS** |
| 7 | zero lipsă / zero suplimentare | **PASS** |
| 7 | exact 13.824 bare · 16×96 + 16×288 + 16×480 | **PASS** |
| 7 | BLIND-046=288 · 047=96 · 048=480 | **PASS** |
| 7 | determinism: 2 directoare curate, 2 execuţii | **PASS** (după corecţia de la §5) |
| 7 | independenţă de locale şi de calea absolută | **PASS** |
| 7 | refuz: corpus / schemă / ordine rânduri / ordine coloane | **PASS** |
| 7 | refuz: o singură valoare, mutaţie de un bit | **PASS** |
| 7 | refuz: mapping / manifest / cheie greşită | **PASS** |
| 7 | rulare în clean checkout | **PASS** — 48/48 şi 22/22 din `git archive` |
| 8 | ancorele existente reproduse, nu înlocuite | **PASS** — 0 ancore modificate, 0 resigilări |
| 9 | scanare de scurgeri înainte de commit | **PASS** — o scurgere proprie găsită şi eliminată |
| 11 | manifest versionat, amprentă după îngheţare | **PASS** |
| 12 | `self_declared_pass = false` | **PASS** |

**Suită: 22 teste, 22 trec, 0 eşecuri.** `mypy --strict` curat pe toate cele trei module.

---

## 4 — IZOLARE (§10), verificat prin starea mediului

Nicio etichetă citită. Scorerul, detectorul şi orice metrică semantică — neatinse; `recall`,
`precision`, `IoU` nu au fost calculate şi nu există în acest pachet. Zero SEALED/OOS, zero PnL,
zero broker, zero LIVE_SHADOW, zero Alpha, zero Strategy Catalog, niciun wheel.

**Dovada de neatingere a artefactelor îngheţate**, prin identitate de blob Git între `f224e7d` şi
`82f27c0`:

```
ve_n1_replay/ve_n1_replay/range_semantic_v4_3.py    IDENTIC   (sha256 continut e8df0c77…)
ve_n1_replay/tests/test_range_semantic_v4_3.py      IDENTIC   (sha256 continut 8ac12b92…)
git diff 82f27c0..HEAD -- ve_n1_replay/             GOL
```

Mapping-ul decriptat a fost manipulat exclusiv într-o locaţie off-git şi **nu e comis**.

---

## 5 — CORECŢII PROPRII, DECLARATE

**(1) Scurgere de date sigilate, a mea.** O linie explicativă din specificaţie şi un docstring de test
citau o **valoare OHLC reală** dintr-o fereastră sigilată, ca ilustrare a limitei de cuantizare.
§9 interzice publicarea barelor. Eliminată înainte de commit, înlocuită cu o formulare care nu
identifică nimic. Scanarea a fost făcută **înainte** de commit, exact fiindcă mandatul o cere.

**(2) Amprenta pachetului depindea de line-endings.** Descoperită rulând chiar testul de determinism
cerut de mandat, nu prin raţionament: `git archive` restaurează CRLF pe Windows, aşa că două
directoare curate au produs `65d10e6c…` şi `e6f4018b…` pentru conţinut identic. O amprentă care se
mişcă odată cu politica de checkout nu e o amprentă. Corectat prin normalizare LF; amprenta finală
`2f8dd39c…` e identică în ambele checkout-uri curate. Am pus-o într-un **commit separat**, nu am
amendat: numărul vechi fusese deja scris într-un fişier comis, iar rescrierea tăcută a unui număr
publicat e mai gravă decât numărul însuşi.

**(3) Limita reală a ancorei, măsurată nu presupusă.** Scalarea `1e6` cu trunchiere rezolvă `1e-6` în
preţ, iar o perturbaţie de **exact** `1e-6` poate fi absorbită de rotunjirea `float64` înainte de
trunchiere; de la `2e-6` detecţia e fermă. Primul meu test negativ a eşuat tocmai din acest motiv —
şi eşecul era corect, testul era naiv. Consemnat ca **proprietate**, nu ca defect: un tick XAUUSD e
0,001, adică 1000 de unităţi după scalare — marjă de trei ordine de mărime. Testul `15b` fixează
limita în suită ca să nu fie redescoperită prin surpriză.

---

## 6 — BLOCAJE REZIDUALE

**`window_list_sha256` (`d9f77eea…`) NU a fost reprodusă.** A fost calculată peste lista de ferestre
*înainte* de orice citire OHLC, într-o formă textuală intermediară care nu e reconstructibilă din
artefactele sigilate. **Nu inventez o reţetă pentru ea şi nu o înlocuiesc** — rămâne ancoră istorică
nereproductibilă, declarată ca atare în manifest.

**Nu blochează** re-atacul: §4 din mandatul RT-RANGE-0009 cere verificarea **conţinutului de bare**
(`bars_sha256`), care e acum reproductibilă 48/48. Semnalez asimetria explicit, ca Red Team să
decidă, nu ca s-o treacă cu vederea.

Nicio resigilare nu a fost efectuată şi niciuna nu e propusă: condiţia din §8 care ar declanşa-o —
imposibilitatea de a reproduce ancorele — **nu s-a materializat**.

---

## 7 — CUM SE RULEAZĂ

```bash
python escrow_repro/verify_range_v43_escrow.py \
    --payload <off-git>/payload-b7e103a3d9b86f72.bin \
    --key     <off-git>/escrow_key_v3.bin \
    --tool    <off-git>/escrow_tool.py
```

Exit 0 numai la 48/48. Nicio cale absolută nu e codată în sursă. Payload-ul, cheia şi unealta rămân
în afara Git.

---

## 8 — DOMENIU

**Autorizează exact un lucru:** re-atacul RT-RANGE-0009 de către Red Team.

**Nu autorizează** şi nu afirmă nimic despre: PASS semantic, BLIND PASS, PASS pentru detector,
rularea detectorului, wheel, Strategy Catalog, Alpha, AI Trader, LIVE_SHADOW, broker sau tranzacţii.
Acest pachet spune **doar** că ancorele escrow sunt acum verificabile independent — nu spune nimic
despre dacă V4.3 recunoaşte structurile etichetate de CEO. Întrebarea aceea rămâne deschisă şi
răspunsul e al Red Team, nu al meu.

---

*Divizia Statistician · `SEALED/OOS_ACCESS = 0` · detector NErulat · etichete NEcitite · invariante neatinse*
