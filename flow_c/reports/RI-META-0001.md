─────────────────────────────────────────────
FLOW C — META ANALYSIS (P2 / WP1)
ID:              RI-META-0001
Data:            2026-07-21
Autor:           Research Intelligence
Nivel epistemic: cunoaștere-observațională relațională (P2)
Încredere:       scăzută (C1 — Speculativ). Inferență la nivel de familie (n=20, efectiv slabă);
                 concluzia principală (nul) a supraviețuit leave-S1-out. Un singur corpus.
─────────────────────────────────────────────
BAZA DE DOVEZI (Evidence base)
  • Sursă:      results/FAMILY_RESULTS.parquet (reprodus bit-exact). Agregat la nivel de familie (20).
  • Metodă:     Spearman (rank) pe unitatea FAMILIE; CI bootstrap pe familii (10.000, seed 20260721);
                p permutațional (20.000); BH-FDR pe cele 2 primare. Conform Contract §7 (WP1).
  • NON-fabricare: toate cifrele derivă din calcul direct pe corpul existent; nicio dată nouă generată.
─────────────────────────────────────────────
PLAFON EPISTEMIC (P2):
  Relații ASOCIATIVE, la nivel de corp. NU cauzale, NU explicative, NU validate. Mecanismele = 🔒 P4.
  „Semnificativ" aici = discernabil în ACEST corpus, NU edge validat.
─────────────────────────────────────────────

# 1. ÎNTREBAREA RELAȚIONALĂ ÎNREGISTRATĂ (WP1)

Dominanța S1 în numărul de câștigători (73%) și extremele mari la familii mici sunt un **artefact de enumerare / mărime de eșantion**, sau o asociere reală mărime↔rezultat la nivel de familie?

**Populație/unitate:** toate 20 familiile; unitate = familia (n=20); corpus-wide.
**Estimand (primar):** Spearman ρ(mărime familie, hit-rate familie) și ρ(mărime, exp_max familie).

---

# 2. REZULTATE

### 2.1 Tabel la nivel de familie (unit=familie)
Mărimile variază masiv (S1=1152 … S19=12); 6 familii au hit-rate 0. (Tabel complet în anexa de calcul; extrase mai jos.)
- S1: n=1152, hit-rate 0,227, exp_max 0,391
- exemple mici: S19 n=12 hit-rate 0,333 exp_max 0,915; S14 n=16 hit-rate 0,375 exp_max 0,579; S9 n=32 hit-rate 0,375.

### 2.2 Estimand-uri primare (Spearman, n=20, cu FDR)
| Relație | ρ | 95% CI (bootstrap familii) | perm p | BH-FDR |
|---|---|---|---|---|
| mărime × hit-rate | **−0,211** | [−0,626; +0,315] | 0,367 | 0,566 |
| mărime × exp_max | **−0,135** | [−0,607; +0,434] | 0,566 | 0,566 |

Ambele CI includ 0; ambele effect-size mici și de semn **negativ** (nu pozitiv).

### 2.3 Descompunerea enumerării (S1)
- S1 = **58,4%** din ipoteze → **73,1%** din câștigători.
- hit-rate S1 = 0,227; hit-rate non-S1 (pooled) = 0,117.
- Câștigători S1 așteptați la rata non-S1 = **135**; observați = **261**; „exces" = **126**.

### 2.4 Leave-S1-out (robustețe la clusterul dominant)
- ρ(mărime, hit-rate) fără S1 = −0,309 (era −0,211).
- ρ(mărime, exp_max) fără S1 = −0,219 (era −0,135).
Scoaterea S1 NU produce o asociere pozitivă mărime→rezultat; dacă ceva, mai negativă.

### 2.5 Verificarea artefactului de sampling-max
Dacă extremele ar fi pur „max din n extrageri", mărime mare → exp_max mare (ρ pozitiv). Observat: ρ(mărime,exp_max)=−0,135; S1(n=1152) exp_max 0,391 < S19(n=12) 0,915. **Nu se confirmă** artefactul de sampling-max.

---

# 3. STĂRI DE EVIDENȚĂ (per rezultat)

| Rezultat | Stare de evidență |
|---|---|
| mărime familie × hit-rate | **NULL / INCONCLUSIVE** (CI include 0; effect-size mic, negativ) |
| mărime familie × exp_max | **NULL / INCONCLUSIVE** (CI include 0); refuză artefactul de sampling-max pentru extreme |
| Dominanța S1 în NUMĂRUL de câștigători (73%) | **ARTIFACT-SUSPECT** pentru orice citire „S1 e o familie mai bună" — 73% din câștigători vine în mare parte din 58% din extrageri (enumerare) |
| Rata per-ipoteză elevată a S1 (0,227 vs 0,117 non-S1; exces ~126) | **FRAGILE / DATA-LIMITED** — un singur cluster (n=1 familie), negeneralizabil; posibil artefact de multiplicitate intra-S1 |

---

# 4. REGISTRU COMPLET DE TESTE (inclusiv nule)

1. Spearman ρ(mărime, hit-rate) = −0,211, CI[−0,626;0,315], p=0,367, FDR=0,566 → NUL.
2. Spearman ρ(mărime, exp_max) = −0,135, CI[−0,607;0,434], p=0,566, FDR=0,566 → NUL.
3. Descompunere enumerare S1 (descriptiv, fără test): exces ~126 câștigători peste rata non-S1.
4. Leave-S1-out (robustețe): ρ rămân ne-pozitive.
5. Sampling-max check (descriptiv): neconfirmat.

*Toate raportate, inclusiv cele nule (per Contract §7.6).*

---

# 5. LIMITĂRI

- **Inferență slabă la nivel de familie:** n=20 (6 legate la hit-rate 0); CI foarte largi. Se înclină spre descriptiv, nu spre p-values (decizie CEO 2).
- **Rata elevată a S1** e o observație pe UN cluster → nu se poate adjudeca dacă e proprietate reală a familiei sau artefact (multiplicitate intra-familie, construcție) — 🔒 P4.
- Semantica coloanelor; „valid" per-familie — neatinse (moștenit din P1).

---

# 6. EFECT ASUPRA WP2–WP5 (autoritate WP1, Contract §7.10)

**WP1 nu invalidează WP2–WP5, dar impune o întărire obligatorie:**
- **Pseudo-replicare confirmată severă:** S1 = 58% din rânduri; setul pooled de câștigători (357) e 73% S1. Orice analiză relațională pooled va fi dominată de S1.
- **MANDAT pentru WP2–WP5:** fiecare estimare pooled trebuie însoțită **obligatoriu** de (a) inferență cluster-familie și (b) o versiune **leave-S1-out** (robustețe la clusterul dominant). O relație care dispare fără S1 = **FRAGILE**.
- Fără redesign de scop: pachetele rămân ca în plan; se adaugă doar cerința de robustețe S1 + cluster, deja compatibilă cu Contract §7.8.

---

# 7. ÎNTREBĂRI ÎN COADĂ PENTRU P4 (mecanism — NU se răspund aici)

- De ce are S1 o rată per-ipoteză mai mare decât restul (dacă e reală, nu artefact intra-familie)? 🔒 P4.
- Extremele mari la familii mici (S19/S14/S6) — mecanism vs artefact de eșantion mic? 🔒 P4 (S6 deja tiny-stop).

---

# 8. INTERPRETĂRI INTERZISE (explicit, per Contract §7.11 + §8 guvernanță)

- ❌ „S1 e o familie mai bună / privilegiată structural." (Dominanța de count e enumerare; rata elevată e single-cluster, nedecisă.)
- ❌ „Familiile mari produc edge-uri mai bune." (ρ mărime×rezultat = nul/negativ.)
- ❌ Orice afirmație cauzală despre DE CE S1 diferă.

─────────────────────────────────────────────
CONCLUZIE WP1 (artifact-first):
  Asocierea mărime-familie ↔ rezultat este NULĂ/INCONCLUSIVĂ. Dominanța S1 în numărul de câștigători
  este în mare parte un efect de ENUMERARE, nu un gradient de calitate legat de mărime. Rata per-ipoteză
  elevată a S1 rămâne FRAGILE/DATA-LIMITED (single cluster). Consecință obligatorie: WP2–WP5 rulează
  cluster-familie + leave-S1-out. WP1 = clean, fără invalidare, cu întărire de robustețe impusă.
─────────────────────────────────────────────
*Sfârșitul RI-META-0001 (WP1). Doar WP1. NU am executat WP2–WP5.*
─────────────────────────────────────────────
