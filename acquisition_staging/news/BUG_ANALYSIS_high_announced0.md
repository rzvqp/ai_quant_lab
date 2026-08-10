# BUG — știre HIGH cu `announced=0` în ledger. ANALIZĂ DE CAUZĂ (înainte de reparare)

**Simptom raportat (AI Trader):** ledger 41→49 intrări, 1 HIGH ("BOJ Sept Rate Hike…", 12:08 UTC, ID 1412592), `announced=0`, "alerte trimise: 0". "Exact funcția pentru care există sistemul."

**Concluzie:** trei constatări distincte. Alerta **A PLECAT** — bug-ul reportat e de **persistență/raportare**, NU de trimitere. Separat, golul de canar pe care l-ai numit e **REAL și independent** (nu a cauzat acest incident, dar există).

---

## 1. Cum a intrat: prin TESTUL MEU manual, nu prin ciclul programat

Cronologie dovedită de `read_ts`:
- Rândul din ledger pentru 1412592 are `read_ts_utc = 2026-08-10T14:07:31Z` = epoch 1786370851 = **ciclul meu `--dry-run`** de acceptanță. Dry-run inserează rândul cu `announced=0` și, prin construcție, **NU trimite** și **NU scrie în `announced_ids.txt`**.
- `--once` real ulterior (read_ts ~14:08Z) a văzut 1412592 ca HIGH, **a trimis alerta** (`high_alerted=1` la momentul rulării) și a adăugat `1412592` în `announced_ids.txt`.

## 2. Alerta A PLECAT → `announced=0` e eroare de PERSISTENȚĂ, nu de trimitere

Dovadă: **`announced_ids.txt` conține `1412592`**, iar acel fișier se scrie **DOAR după un send confirmat `ok` de Telegram** (`if ok and not dry_run: append_announced(...)`). Deci Telegram a confirmat trimiterea. Confirmă exact ipoteza ta: *"dacă aceea e știrea din ledger, atunci announced=0 e o eroare de persistență."*

**De ce coloana din ledger minte:** ledger-ul e **append-only**; rândul unei știri se scrie **o singură dată**, la prima vedere (`is_new`). Rândul lui 1412592 a fost scris de **dry-run** (announced=0). Când alerta a plecat (ciclul următor), știrea nu mai era `is_new` → **niciun rând nou** → coloana rămâne `0` pentru totdeauna.

**Mai grav:** **toate cele 49 de rânduri au `announced=0`.** Coloana e `1` doar dacă o știre e văzută-prima-dată ȘI alertată-cu-succes în **același** ciclu ne-dry. Pentru orice știre văzută întâi într-un dry-run (sau ratată la send și alertată mai târziu), coloana rămâne `0`. Deci coloana `announced` din ledger e **structural nefiabilă** — diverge de `announced_ids.txt` (autoritatea). Un consumator care citește coloana (AI Trader) e indus în eroare → "0 alerte" e o citire a unui snapshot învechit.

## 3. Ordinea scrierii (ipoteza ta #3): CORECTĂ, nu e bug-ul

`announced_ids.txt` se scrie **DUPĂ** send reușit. Un send eșuat NU marchează → se reîncearcă la ciclul următor (verificarea de re-alertă e independentă de `seen`). Deci partea de "before/after send" e corectă.

## 4. Detecția HIGH (ipoteza ta #2): aici a mers, DAR golul e real

În acest incident, 1412592 **a fost** parsată corect ca `high` și alertată. Însă analiza ta structurală e corectă și rămâne un gol:

> Iconița de impact apare pe ~17% din știri, asociată prin **proximitate în DOM**. Parserul caută `impact-ff-(high|medium|low)` **în chunk-ul fiecărei știri** (split pe `news-block__item`). Dacă iconița unei știri HIGH e randată **în afara** granițelor chunk-ului (sau cu altă structură), per-story regex nu găsește nimic → `impact=none` → **fără alertă**. Canarul numără iconițele **pe toată pagina**, deci cât timp ALTE știri au iconițe, canarul rămâne **sănătos** → ratarea e **tăcută**.

**Deci DA: o știre HIGH poate trece nedetectată, iar canarul actual NU acoperă cazul** (verifică prezența pe pagină, nu asocierea corectă per-știre).

---

## Ce AR acoperi golul canarului (cerut: "spune ce ar acoperi-o")

Recomandat, minimal și țintit:
1. **Canar de RECONCILIERE prin numărare.** Numără iconițele `impact-ff-high` pe toată pagina (H_page) și numărul de știri taguite `high` de parser (H_parsed). Dacă `H_parsed < H_page` → alertă **`[NEWS IMPACT ASSOCIATION MISMATCH]`**. Transformă ratarea tăcută în alertă zgomotoasă — exact filozofia mitigărilor. (Acoperă direct cazul tău: o iconiță high există pe pagină dar nu s-a legat de nicio știre.)

Suplimentar, ca să RATĂM mai puțin (nu doar să aflăm că am ratat):
2. **Împerechere globală icon↔ID** în loc de doar-în-chunk: leagă fiecare iconiță `impact-ff-*` de cel mai apropiat `/news/<ID>` de pe pagină, lărgind fereastra de asociere → o iconiță aflată chiar peste granița chunk-ului tot se leagă de știrea ei.
3. **Cross-check cu caruselul hot-stories** (semnal independent, aceeași pagină): dacă un titlu/ID apare `high` în carusel dar `none` în stream → tratează ca `high` (uniunea celor două parse-uri). Breaking-ul HIGH apare aproape mereu în hot-stories.

---

## Bug-ul de persistență de reparat (coloana `announced`)

La reparare, coloana trebuie să reflecte adevărul (announced_ids.txt), nu snapshot-ul de inserare. Opțiuni de propus:
- (a) Consumatorii tratează **`announced_ids.txt` ca autoritate**; coloana din ledger se marchează explicit drept "snapshot la inserare" sau se elimină.
- (b) Se ține un index lateral care poate fi actualizat (ledger rămâne append-only pentru date, dar starea `announced` se derivă din announced_ids.txt la citire).
- (c) La fiecare ciclu, se poate emite un `NEWS_LEDGER_announced.csv` derivat (id→1) regenerat din announced_ids.txt, ca vederea de consum să fie mereu corectă.

**NU repar încă — aștept GO** (cauza raportată, per ordin). Recomand: (1) canar de reconciliere + (2) împerechere globală + fix coloana `announced` prin (a)/(c).
