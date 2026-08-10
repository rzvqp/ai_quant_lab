# STATISTICIAN — IDENTITATEA OPORTUNITĂȚII. SPECIFICAȚIE

**Document ID:** STAT-OPPORTUNITY-IDENTITY-SPEC-v1.0
**Data:** 2026-08-11 · **Autor:** Statistician
**Sub:** `decision_clock = zone_hit` (decizie CEO, opțiunea B). N4 = POST-DECIZIE, evidence-only.
**Prima sarcină a fazei de integrare, înaintea restului cablării.**

**Verificare de sursă:** citit `build_zone_map` integral. **Măsurătoare nouă, P&L-oarbă, care OGLINDEȘTE MODULUL EXACT — și care îmi corectează cifra raportată la v2.7.59.**

---

# PARTEA 0 — CORECȚIE LA PROPRIA MEA MĂSURĂTOARE. Se citește prima.

**La v2.7.59 am raportat 55.170 emisii, 42,77% din bare. Cifra e GREȘITĂ. Harnessul meu nu oglindea modulul: am folosit `PoolTier.INTERNAL` și `detect_swings` cu `k` implicit, în timp ce `build_zone_map` folosește `PoolTier.EXTERNAL` și `k=2`. Rulat oglindind modulul exact:**

```
                                    RAPORTAT de mine      REAL (oglindind modulul)
emisii N3 (k >= 4)                        55.170                   117.631
rata de emisie                            42,77%                    91,19%
oportunități economice                    10.553                    19.840
```

> **Saturația nu e mai mică decât am spus — e MULT MAI MARE. N3 emite pe 91,19% din bare, nu pe 42,77%. Am raportat mai puțin de jumătate din problemă, iar CEO mi-a citat cifra înapoi în mandat.**

**Direcția erorii a fost norocoasă: concluzia „`zone@{bară}` numește o bară, nu o oportunitate" se întărește, nu se clatină. Dar norocul nu e o metodă. Cauza e că am scris un harness paralel în loc să importez modulul; regula pe care mi-o impun de acum e la Partea 6.**

---

# PARTEA 1 — CE ÎNSEAMNĂ „ATINGERE" AICI. O proprietate care schimbă mecanica.

**Citit în cod:**

```python
ref = float(close[i - 1])          # build_zone_map: zona e CENTRATĂ PE PREȚ
band = band_mult * a
```

> **Zona nu e un loc spre care prețul CĂLĂTOREȘTE. E o descriere a locului unde prețul SE AFLĂ DEJA. Deci nu există apropiere, iar `zone_hit` NU e un eveniment separat de creare: atingerea ESTE prima emisie.**

**Consecințe mecanice, toate favorabile ceasului ales:**

```
· `decision_clock = zone_hit`  ≡  decizie la PRIMA EMISIE a oportunității. Fără așteptare,
  fără fereastră, fără nimic de anticipat. Cel mai simplu ceas posibil, și e cauzal banal.
· „prima atingere validă" din regula CEO e bine definită și UNICĂ per oportunitate.
· O SINGURĂ oportunitate poate fi deschisă la un moment dat — prin construcție, nu prin
  regulă: ancora e prețul, iar prețul e într-un singur loc.
```

**Limita, spusă acum ca să nu fie descoperită mai târziu: reparația cheii face obiectul NUMĂRABIL, nu îl face SEMNIFICATIV. ZM-L1 rămâne deschis. „Oportunitate" înseamnă aici: un interval de timp în care prețul a rămas la mai puțin de 1×ATR de unde era când patru trăsături îi erau în preajmă.**

---

# PARTEA 2 — CHEIA. Definiția, cu tot ce e înghețat.

```
IDENTITATEA se definește prin REGULA DE POTRIVIRE; `opportunity_id` e o cheie surogat
(contor monoton sau hash stabil), NICIODATĂ o funcție de indexul barei.

La creare, în bara i0:
    anchor    a  =  close[i0 - 1]                    ÎNGHEȚAT
    band      b  =  BAND_ATR_MULT * atr[i0 - 1]      ÎNGHEȚAT
    created_at   =  i0
Apartenență, la orice bară j > i0:
    |close[j - 1] - a|  <=  b                        cauzal: citește doar j-1
```

## De ce banda se ÎNGHEAȚĂ, și nu se recalculează la fiecare bară

**Nu e o preferință de stil. O bandă vie urmărește prețul:**

```
în expansiune de volatilitate, ATR crește, banda se lărgește, prețul rămâne în ea
   ⇒ oportunitatea nu se închide NICIODATĂ  ⇒  durată de viață NEMĂRGINITĂ.
E același eșec ca fail-closed devenit fail-mort: o regulă protectoare aplicată uniform
produce un obiect care nu se termină.
```

**Înghețarea mărginește durata prin CONSTRUCȚIE. E și alegerea conservatoare: poate doar să închidă mai devreme, niciodată mai târziu.**

---

# PARTEA 3 — CICLUL DE VIAȚĂ. Și de ce sunt DOUĂ ceasuri, nu unul.

**Măsurat, sub cheia propusă, oglindind modulul:**

```
oportunități economice          19.840        reducere 5,93x față de emisii
                                13,97 / zi
durată de viață (bare M15)      mediană 4,0   p75 7,0   p90 13,0   max 153
cauza închiderii                band_exit 19.837   (99,98%);  series_end 3
supraviețuiesc >= 20 bare       4,77%
```

> # **Numai 4,77% dintre oportunități mai sunt în viață la `i0+W+1`, când sosește dovada N4.**
>
> **Durata mediană a obiectului e 4 bare M15 = o oră. Fereastra de dovezi e 20 de bare = cinci ore. FEREASTRA E DE CINCI ORI MAI LUNGĂ DECÂT VIAȚA MEDIANĂ A OBIECTULUI DESPRE CARE VORBEȘTE.**

**Asta coroborează independent măsurătoarea de deplasare de la v2.7.59: acolo, mediana deplasării egala banda la ~5 bare M15; aici, viața mediană a oportunității e 4 bare. Două mărimi diferite, măsurate diferit, același ordin. Niciuna nu e potrivită pe rezultate.**

## Consecința: identitatea trebuie să SUPRAVIEȚUIASCĂ închiderii economice

**Dacă `band_exit` ar distruge id-ul, în 95,23% din cazuri N4 n-ar avea la ce să atașeze descriptorul — iar punctul 7 din regula CEO ar fi inexecutabil. Deci:**

```
STARE            de la              până la                 ce se poate face
─────────────────────────────────────────────────────────────────────────────────
OPEN             i0                 band_exit               refresh (last_seen++)
DECIDED          i0 (ACELAȘI bar)   —                       NIMIC. Înregistrare ÎNGHEȚATĂ.
EVIDENCE_PENDING i0+1               i0+W+1                  N4 atașează, o singură dată
CLOSED           max(band_exit, i0+W+1)                     doar citire, pentru jurnal

CEASUL ECONOMIC   se închide la band_exit  (mediană 4 bare)
CEASUL DE IDENTITATE se închide la i0+W+1  (întotdeauna, indiferent de primul)
Sunt DOUĂ ceasuri. Confundarea lor face punctul 7 al regulii inexecutabil.
```

**D7, aplicat oportunității însăși: `DECIDED` se atinge exact o dată, la `i0`. O emisie ulterioară în aceeași bandă REÎMPROSPĂTEAZĂ, nu redecide. Asta e ce face „o oportunitate = un slot de familie" adevărat mecanic, nu doar declarativ.**

---

# PARTEA 4 — RE-ARMAREA. Măsurată, și acoperită FĂRĂ constantă nouă.

**Pericolul: prețul iese din bandă (oportunitatea se închide), se întoarce peste trei bare, se creează un id nou, se ia o a doua decizie despre același loc. Măsurat:**

```
re-armări în <= 20 bare de la închidere, la aceeași ancoră:   2.266   =  11,42%
```

**Am refuzat soluția evidentă. Un „cooldown" ar fi o constantă nouă, aleasă ca să facă un număr să arate bine — exact clasa de eroare pe care am semnalat-o de patru ori. În schimb:**

> **Ceasul de IDENTITATE, care exista deja pentru că N4 are nevoie de el, acoperă exact fereastra re-armării. Un id rămâne `EVIDENCE_PENDING` până la `i0+W+1`; o emisie în banda lui în acel interval NU creează un id nou — reîmprospătează. Măsurătoarea de mai sus e făcută la orizontul de exact `W`, deci cele 11,42% sunt absorbite PRIN CONSTRUCȚIE.**

**Re-armările de DINCOLO de `W` sunt oportunități genuin noi sub definiția enunțată. Nu se suprimă — se RAPORTEAZĂ, ca fracție, în auditul fiecărei politici. Un mecanism, două cerințe, zero constante noi.**

---

# PARTEA 5 — CE MĂSOR ȘI NU ADOPT: D7 pe TRĂSĂTURI

**`_near_level` și testul de FVG verifică doar `available_idx <= i-1`. NU aplică D7 — o trăsătură atinsă rămâne „prezentă" la nesfârșit, deși D7 („consumat la prima atingere") e convenție RATIFICATĂ. Am măsurat ce s-ar întâmpla dacă s-ar aplica:**

```
                                 FĂRĂ D7 pe trăsături      CU D7 pe trăsături
emisii N3                              117.631                     1.270
rata de emisie                          91,19%                     0,98%
oportunități economice                  19.840                       708
                                     13,97 / zi                 0,50 / zi
re-armare                               11,42%                     5,79%
supraviețuiesc >= W                      4,77%                     8,19%
```

> **Aplicarea unei convenții deja ratificate, dar neaplicate, reduce oportunitățile de 28 de ori. 708 rămâne o populație utilizabilă — comparabilă cu CAND-0001 (1.225) și mai mare decât CAND-0007 (373).**

**NU O ADOPT. Mandatul spune explicit „nu modifica măsurătorile N1-N4", iar asta ar fi o modificare a lui N3 indiferent de cât de bună e descendența ei. O rutez la fel ca fereastra de 75 de minute: Statistician specifică → VE → Red Team → CEO.**

**Un avertisment care merge cu ea, ca să nu fie citită ca o victorie: 0,50 oportunități/zi față de 13,97 nu e „mai bine". E ALT OBIECT. Populația nu se filtrează — se înlocuiește, deci ar fi o ipoteză nouă, cu slot propriu de familie.**

---

# PARTEA 6 — PUNCTUL 6 AL REGULII, IMPUS PRIN TIP

**„N4 NU modifică retroactiv TRADE / NO TRADE" e o interdicție. O interdicție se încalcă; o imposibilitate nu. Se folosește exact instrumentul din contractul unic:**

```python
@dataclass(frozen=True)
class DecisionRecord:              # scris o dată, la i0. Nu are setter, nu are câmp de evidence.
    opportunity_id: str
    decided_at: int                # == i0 == zone_hit
    outcome: Literal["TRADE", "NO_TRADE"]
    inputs_hash: str               # peste N1, N2, N3 AȘA CUM ERAU la i0
    schema_hash: str

@dataclass(frozen=True)
class EvidenceRecord:              # scris o dată, la i0+W+1. NU referă DecisionRecord decât prin id.
    opportunity_id: str
    attached_at: int
    descriptor: LevelOutput[ZoneConfirmationResult]
```

> **Două înregistrări SEPARATE, amândouă imuabile, legate doar prin `opportunity_id`. Nu există nicio cale prin care N4 să atingă decizia — nu pentru că e interzis, ci pentru că nu există câmp de scris. A șasea folosire a aceluiași instrument: starea greșită devine NEREPREZENTABILĂ.**

**Și regula pe care mi-o impun după eroarea din Partea 0:**

```
Orice măsurătoare care raportează o cifră despre un modul ratificat IMPORTĂ modulul.
Un harness paralel e o a doua implementare, deci o a doua sursă de adevăr — exact
defectul pe care l-am cerut eliminat pentru `status: str`. Îl aplic și mie.
```

---

# PARTEA 7 — AUDITUL NON-LOOKAHEAD, verificat pe fiecare cale

```
ancora        close[i0-1]                        <= i0-1   ✓
banda         atr[i0-1], ÎNGHEȚATĂ               <= i0-1   ✓
apartenență   close[j-1] la bara j               <= j-1    ✓
închidere     cunoscută la bara în care se produce         ✓
DECIZIA       la i0, cu N1/N2/N3 as-of i0                  ✓
N4            citește <= i0+W, declarat la i0+W+1          ✓  (verificat: descriptor_available_idx)
```

> **Nu există nicio cale de la viitor la decizie, pentru că decizia se ia ÎNAINTE de a exista fereastra. Ceasul ales de CEO elimină clasa întreagă de risc, nu doar instanța: sub `zone_hit`, un lookahead din N4 ar cere ca `i0 > i0+W`.**

**Și interdicția care rămâne activă: ceasul nu se schimbă în funcție de dovadă. E acum trivial de respectat — `zone_hit` nu are parametru pe care să-l poți acorda.**

---

# PARTEA 8 — SHADOW, ȘI CAPCANA DE GUVERNANȚĂ DE LA CAPĂT

**Punctul 8: descriptorul se jurnalizează pentru Shadow și cercetare ulterioară. Corect. Dar dacă N4 se dovedește predictiv:**

```
· politica v2 delayed-confirmation e o IPOTEZĂ NOUĂ  ⇒  CONSUMĂ UN SLOT DE FAMILIE.
  Familia e MONOTONĂ. De la m=16 la m=17, pragul BH al primei ipoteze scade de la
  0,003125 la 0,002941 — pentru TOATE celelalte, retroactiv.
· MAI IMPORTANT: „am observat că N4 pare predictiv" e un EVENIMENT DE SELECȚIE. Validarea
  lui v2 pe datele în care s-a observat e circulară, oricât de curat ar fi ceasul ei.
  Se înregistrează în REGISTRUL DE EXPLORARE (36), la momentul observării, nu retroactiv.
```

**Asta nu blochează nimic. Spune doar că jurnalizarea e gratuită, iar CITIREA jurnalului nu e.**

---

# PARTEA 9 — DELIMITARE

```
CE ACOPERĂ    identitatea, ciclul de viață, cele două ceasuri, re-armarea, imposibilitatea
              modificării retroactive, auditul de non-lookahead.
CE NU ACOPERĂ ZM-L1 — cheia face obiectul NUMĂRABIL, nu SEMNIFICATIV. Banda măsoară în
              continuare distanța la PREȚ, nu între trăsături.
              D7 pe trăsături: MĂSURAT, ROUTAT, NEADOPTAT. W=60 și starea actuală a lui
              N3 rămân în vigoare.
              Nicio afirmație despre edge. Verdictul formal 001 (ZERO PROMOVĂRI) rămâne
              singura afirmație despre edge din proiect.
```

---

**Manifest:** `config/split_manifest.json` v2.7.60, secțiunea `opportunity_identity_spec_v2_7_60`.
