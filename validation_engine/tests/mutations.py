"""Bateria de mutații — catalogul mutațiilor aplicate specificației de referință.

Fiecare intrare: (id, descriere, mutator, cod_așteptat, etapă_așteptată).
Mutatorul primește o copie proaspătă a specificației și o modifică pe loc.
"""

from __future__ import annotations

import copy

MUTATIONS: list[tuple] = []


def mutation(mid: str, description: str, code: str, stage: int):
    def deco(fn):
        MUTATIONS.append((mid, description, fn, code, stage))
        return fn
    return deco


# ─────────────────── E1 — câmpuri obligatorii absente (etapa 1) ───────────────

@mutation("M01", "spec_id absent", "E1", 1)
def _(s): del s["spec_id"]


@mutation("M02", "secțiunea population absentă", "E1", 1)
def _(s): del s["population"]


@mutation("M03", "secțiunea tests absentă", "E1", 1)
def _(s): del s["tests"]


@mutation("M04", "secțiunea variables absentă", "E1", 1)
def _(s): del s["variables"]


@mutation("M05", "secțiunea criteria absentă", "E1", 1)
def _(s): del s["criteria"]


@mutation("M06", "secțiunea multiple_testing absentă", "E1", 1)
def _(s): del s["multiple_testing"]


@mutation("M07", "secțiunea return absentă", "E1", 1)
def _(s): del s["return"]


@mutation("M08", "secțiunea data absentă", "E1", 1)
def _(s): del s["data"]


@mutation("M09", "secțiunea authorization absentă", "E1", 1)
def _(s): del s["authorization"]


@mutation("M10", "clauza de oprire absentă", "E1", 1)
def _(s): del s["on_missing_or_ambiguous"]


@mutation("M11", "identificarea candidatului absentă", "E1", 1)
def _(s): del s["candidate"]


@mutation("M12", "fereastra fără inclusivitate declarată (bounds)", "E1", 1)
def _(s): del s["population"]["window"]["bounds"]


@mutation("M13", "fereastră deschisă la capăt (end absent)", "E1", 1)
def _(s): del s["population"]["window"]["end"]


@mutation("M14", "cooldown absent (ce este un eveniment distinct rămâne nedefinit)", "E1", 1)
def _(s): del s["population"]["cooldown"]


@mutation("M15", "min_n absent", "E1", 1)
def _(s): del s["population"]["min_n"]


@mutation("M16", "availability absentă la o variabilă", "E1", 1)
def _(s): del s["variables"][0]["availability"]


@mutation("M17", "seed_policy absentă la un test", "E1", 1)
def _(s): del s["tests"][0]["seed_policy"]


@mutation("M18", "cells absente la un test", "E1", 1)
def _(s): del s["tests"][0]["cells"]


# ─────────────────── E2 — formă ambiguă sau invalidă (etapa 1) ────────────────

@mutation("M19", "prag descriptiv în loc de numeric", "E2", 1)
def _(s): s["criteria"][0]["threshold"] = "volatilitate ridicată"


@mutation("M20", "prag numeric scris ca șir de caractere", "E2", 1)
def _(s): s["criteria"][0]["threshold"] = "0.05"


@mutation("M21", "clauză de oprire permisivă", "E2", 1)
def _(s): s["on_missing_or_ambiguous"] = "continue_with_defaults"


@mutation("M22", "câmp necunoscut la nivel superior", "E2", 1)
def _(s): s["optimize_thresholds"] = True


@mutation("M23", "criteria_evaluation cerut în return (rezervat până la P1)", "E2", 1)
def _(s): s["return"]["criteria_evaluation"] = True


@mutation("M24", "versiune de contract diferită", "E2", 1)
def _(s): s["contract_version"] = "STAT-VE-CONTRACT-v2.0"


@mutation("M25", "emitent diferit de Statistician", "E2", 1)
def _(s): s["issued_by"] = "Alpha"


@mutation("M26", "seed_policy aleasă ad-hoc", "E2", 1)
def _(s): s["tests"][0]["seed_policy"] = "random"


@mutation("M27", "hash de îngheț malformat", "E2", 1)
def _(s): s["candidate"]["freeze_hash"] = "abc"


@mutation("M28", "capăt de fereastră gol", "E2", 1)
def _(s): s["population"]["window"]["end"] = ""


@mutation("M29", "listă de includere goală (populație nedefinită)", "E2", 1)
def _(s): s["population"]["include"] = []


@mutation("M30", "mode necunoscut", "E2", 1)
def _(s): s["mode"] = "optimize"


# ─────────────────── E3 — vocabular inexistent (etapa 2) ──────────────────────

@mutation("M31", "metodă de test inexistentă în registru", "E3", 2)
def _(s): s["tests"][0]["method"] = "bayes_factor@v1"


@mutation("M32", "predicat specific unei ipoteze, inexistent în registru", "E3", 2)
def _(s): s["population"]["include"][0]["predicate"] = "sweep_reject@v1"


@mutation("M33", "primitivă de variabilă inexistentă", "E3", 2)
def _(s): s["variables"][0]["primitive"] = "magic_indicator@v1"


@mutation("M34", "sursă de date inexistentă în registru", "E3", 2)
def _(s):
    s["data"][0]["source_id"] = "OANDA_XAUUSD_M5@v1"
    s["population"]["source_id"] = "OANDA_XAUUSD_M5@v1"


@mutation("M35", "metodă de corecție inexistentă", "E3", 2)
def _(s): s["multiple_testing"]["method"] = "holm@v1"


# ─────────────────── E2 — vocabular / domenii (etapa 2) ───────────────────────

@mutation("M36", "parametru obligatoriu al metodei absent (B)", "E2", 2)
def _(s): del s["tests"][0]["params"]["B"]


@mutation("M37", "parametru necunoscut strecurat în metodă", "E2", 2)
def _(s): s["tests"][0]["params"]["optimize_threshold"] = True


@mutation("M38", "valoare în afara domeniului (tail)", "E2", 2)
def _(s): s["tests"][0]["params"]["tail"] = "sideways"


@mutation("M39", "valoare sub limita inferioară a domeniului (B)", "E2", 2)
def _(s): s["tests"][0]["params"]["B"] = 10


@mutation("M40", "statistică inexistentă în registru", "E2", 2)
def _(s): s["tests"][0]["params"]["statistic"]["statistic"] = "mode@v1"


@mutation("M41", "variabilă de control care folosește date din viitor", "E2", 2)
def _(s): s["variables"][2]["availability"]["offset_bars"] = 3


@mutation("M42", "criteriu care referă un test inexistent", "E2", 2)
def _(s): s["criteria"][0]["target"]["test_id"] = "T9_inexistent"


@mutation("M43", "membru de familie care referă o celulă inexistentă", "E2", 2)
def _(s): s["multiple_testing"]["members"][0]["cell"] = "ny_up"


@mutation("M44", "sursa populației nedeclarată în secțiunea data", "E2", 2)
def _(s): s["population"]["source_id"] = "OANDA_XAUUSD_D1@v1"


@mutation("M45", "hash de date diferit de cel înregistrat", "E2", 2)
def _(s): s["data"][0]["sha256"] = "0" * 64


@mutation("M46", "versiune de registru diferită de cea instalată", "E2", 2)
def _(s): s["capability_registry_version"] = "9.9"


@mutation("M47", "identificator de variabilă duplicat", "E2", 2)
def _(s): s["variables"][1]["id"] = "atr14"


@mutation("M48", "două teste cu aceeași ordine de execuție", "E2", 2)
def _(s):
    dup = copy.deepcopy(s["tests"][0])
    dup["test_id"] = "T2_duplicat"
    s["tests"].append(dup)


@mutation("M49", "identificator de predicat duplicat (denominator ambiguu)", "E2", 2)
def _(s): s["population"]["include"].append(copy.deepcopy(s["population"]["include"][0]))


@mutation("M50", "none@v1 fără justificare declarată", "E2", 2)
def _(s):
    s["multiple_testing"]["method"] = "none@v1"
    s["multiple_testing"]["params"] = {}


@mutation("M51", "referință la o ieșire pe care metoda nu o produce", "E2", 2)
def _(s): s["criteria"][0]["target"]["output"] = "profit_factor"


# ─────────────────── E5 — autorizare (etapa 2) ────────────────────────────────

@mutation("M52", "fereastra atinge holdout-ul sigilat fără autorizare", "E5", 2)
def _(s): s["population"]["window"]["end"] = "2026-01-01T00:00:00Z"


@mutation("M53", "fereastra atinge exact granița sigilată, capăt inclusiv", "E5", 2)
def _(s):
    s["population"]["window"]["end"] = "2025-10-23T10:00:00Z"
    s["population"]["window"]["bounds"] = "[]"


# ─────────────────── registru v1.1 — golurile G1 și G2 ────────────────────────

@mutation("M54", "G2: statistica dată ca identificator gol, fără parametri", "E2", 2)
def _(s): s["tests"][0]["params"]["statistic"] = "mean@v1"


@mutation("M55", "G2: apel de statistică fără parametrul obligatoriu al statisticii", "E2", 2)
def _(s): s["tests"][0]["params"]["statistic"]["params"] = {}


@mutation("M56", "G2: apel de statistică ce referă o variabilă nedeclarată", "E2", 2)
def _(s): s["tests"][0]["params"]["statistic"]["params"]["variable_ref"] = "inexistenta"


@mutation("M57", "G2: apel de statistică fără câmpul id", "E2", 2)
def _(s): del s["tests"][0]["params"]["statistic"]["id"]


@mutation("M58", "G1: serie brută cu câmp inexistent în sursă", "E2", 2)
def _(s):
    s["variables"][0] = {
        "id": "atr14", "primitive": "raw_series@v1",
        "params": {"source_id": "OANDA_XAUUSD_H1@v1", "field": "spread"},
        "availability": {"anchor": "event_time", "offset_bars": 0, "source_id": "OANDA_XAUUSD_H1@v1"},
        "role": "exposure",
    }


@mutation("M59", "G1: serie brută care cere coloana 'sub' de la M15 (sursă fără ea)", "E2", 2)
def _(s):
    s["data"].append({
        "source_id": "OANDA_XAUUSD_M15@v1",
        "sha256": "c777cb9c6097287850b590b205ea4227b1a32ecb9255bdd611723f0364c64e86",
    })
    s["variables"][0] = {
        "id": "atr14", "primitive": "raw_series@v1",
        "params": {"source_id": "OANDA_XAUUSD_M15@v1", "field": "sub"},
        "availability": {"anchor": "event_time", "offset_bars": 0, "source_id": "OANDA_XAUUSD_M15@v1"},
        "role": "exposure",
    }


@mutation("M60", "G1: serie brută de rol exposure care folosește o bară viitoare", "E2", 2)
def _(s):
    s["variables"][0] = {
        "id": "atr14", "primitive": "raw_series@v1",
        "params": {"source_id": "OANDA_XAUUSD_H1@v1", "field": "close"},
        "availability": {"anchor": "event_time", "offset_bars": 2, "source_id": "OANDA_XAUUSD_H1@v1"},
        "role": "exposure",
    }


# ─────────────────── registru v1.2 — G3 (indicator@v1) ────────────────────────

def _add_indicator(s, predicate, offset=0):
    """Adaugă un indicator@v1 și îl folosește ca exposure într-o regresie."""
    s["variables"].append({
        "id": "evt", "primitive": "indicator@v1", "params": {"predicate": predicate},
        "availability": {"anchor": "event_time", "offset_bars": offset, "source_id": "OANDA_XAUUSD_H1@v1"},
        "role": "exposure",
    })
    s["tests"].append({
        "order": 2, "test_id": "T2_reg", "method": "regression_control@v1",
        "params": {"outcome_ref": "fwd6", "exposure_ref": "evt", "controls": ["volhour"],
                   "interaction": [["evt", "volhour"]], "se_estimator": "hac_newey_west",
                   "se_params": {"lags": 6}},
        "cells": [{"id": "all", "predicates": []}], "seed_policy": "derived_from_spec_hash",
    })


@mutation("M61", "G3: indicator valabil (indicator@v1 + regresie de control)", "E3", 2)
def _(s):
    # Complet corect: se oprește doar pe poarta de calibrare (E3), ca specificația de referință.
    _add_indicator(s, {"id": "ev_ok", "predicate": "compare@v1",
                       "params": {"left": "atr14", "op": ">", "right": 2.0}})


@mutation("M62", "G3: indicator cu predicat inexistent în registru", "E3", 2)
def _(s):
    _add_indicator(s, {"id": "ev_bad", "predicate": "sweep_reject@v1",
                       "params": {"left": "atr14", "op": ">", "right": 2.0}})


@mutation("M63", "G3: indicator cu variabilă nedeclarată în predicat", "E2", 2)
def _(s):
    _add_indicator(s, {"id": "ev_bad", "predicate": "compare@v1",
                       "params": {"left": "inexistenta", "op": ">", "right": 2.0}})


@mutation("M64", "G3: indicator disponibil înaintea variabilei folosite de predicat", "E2", 2)
def _(s):
    # atr14 este la offset -1; indicatorul la -5 ar exista înaintea intrării lui.
    _add_indicator(s, {"id": "ev_ok", "predicate": "compare@v1",
                       "params": {"left": "atr14", "op": ">", "right": 2.0}}, offset=-5)


@mutation("M65", "G3: ciclu de referință între variabile (indicator ↔ lag)", "E2", 2)
def _(s):
    # evt (indicator pe predicat ce folosește loopvar) <-> loopvar (lag pe evt)
    s["variables"].append({
        "id": "evt", "primitive": "indicator@v1",
        "params": {"predicate": {"id": "ev_cyc", "predicate": "compare@v1",
                   "params": {"left": "loopvar", "op": ">", "right": 0.0}}},
        "availability": {"anchor": "event_time", "offset_bars": 0, "source_id": "OANDA_XAUUSD_H1@v1"},
        "role": "exposure"})
    s["variables"].append({
        "id": "loopvar", "primitive": "lag@v1", "params": {"variable_ref": "evt", "bars": 1},
        "availability": {"anchor": "event_time", "offset_bars": 0, "source_id": "OANDA_XAUUSD_H1@v1"},
        "role": "exposure"})


@mutation("M66", "G3: indicator cu obiect-predicat malformat (chei lipsă)", "E2", 2)
def _(s):
    s["variables"].append({
        "id": "evt", "primitive": "indicator@v1",
        "params": {"predicate": {"predicate": "compare@v1", "params": {"left": "atr14", "op": ">", "right": 1.0}}},
        "availability": {"anchor": "event_time", "offset_bars": 0, "source_id": "OANDA_XAUUSD_H1@v1"},
        "role": "exposure"})


@mutation("M67", "G3: predicatul indicatorului duplică un id de predicat existent", "E2", 2)
def _(s):
    _add_indicator(s, {"id": "p_atr_above", "predicate": "compare@v1",
                       "params": {"left": "atr14", "op": ">", "right": 2.0}})


# ─────────────────── registru v1.2 — G5 (referințe rezolvate) ─────────────────

@mutation("M68", "G5: forward_return_ref inexistent (forward_excess)", "E2", 2)
def _(s):
    s["variables"].append({
        "id": "exc", "primitive": "forward_excess@v1",
        "params": {"forward_return_ref": "inexistent", "baseline_ref": "fwd6"},
        "availability": {"anchor": "event_time", "offset_bars": 6, "source_id": "OANDA_XAUUSD_H1@v1"},
        "role": "outcome"})


@mutation("M69", "G5: base_test_ref inexistent (test_ref)", "E2", 2)
def _(s):
    s["tests"].append({
        "order": 2, "test_id": "T2_mv", "method": "multiverse@v1",
        "params": {"base_test_ref": "T9_inexistent", "grid": {"horizon_bars": [4, 8]}},
        "cells": [{"id": "all", "predicates": []}], "seed_policy": "derived_from_spec_hash"})


@mutation("M70", "G5: base_test_ref care e chiar un test existent (test_ref valid)", "E3", 2)
def _(s):
    s["tests"].append({
        "order": 2, "test_id": "T2_mv", "method": "multiverse@v1",
        "params": {"base_test_ref": "T1_matched_null", "grid": {"horizon_bars": [4, 8]}},
        "cells": [{"id": "all", "predicates": []}], "seed_policy": "derived_from_spec_hash"})


@mutation("M71", "G5: predicate_ref inexistent (proportion statistic)", "E2", 2)
def _(s):
    s["tests"][0]["params"]["statistic"] = {
        "id": "s_prop", "statistic": "proportion@v1",
        "params": {"variable_ref": "fwd6", "predicate_ref": "inexistent"}}


@mutation("M72", "G5: predicate_ref către un predicat declarat (valid)", "E3", 2)
def _(s):
    s["tests"][0]["params"]["statistic"] = {
        "id": "s_prop", "statistic": "proportion@v1",
        "params": {"variable_ref": "fwd6", "predicate_ref": "p_atr_above"}}


@mutation("M73", "G5: dip_test.variable_ref inexistent (fost string, acum rezolvat)", "E2", 2)
def _(s):
    s["tests"].append({
        "order": 2, "test_id": "T2_dip", "method": "dip_test@v1",
        "params": {"variable_ref": "inexistenta", "B": 20000},
        "cells": [{"id": "all", "predicates": []}], "seed_policy": "derived_from_spec_hash"})


@mutation("M74", "G5: regression_control.exposure_ref inexistent", "E2", 2)
def _(s):
    s["tests"].append({
        "order": 2, "test_id": "T2_reg", "method": "regression_control@v1",
        "params": {"outcome_ref": "fwd6", "exposure_ref": "inexistent", "controls": ["volhour"],
                   "interaction": [], "se_estimator": "ols", "se_params": {}},
        "cells": [{"id": "all", "predicates": []}], "seed_policy": "derived_from_spec_hash"})


# ─────────────────── registru v1.3 — G7 (first_in_scope@v1) ───────────────────

@mutation("M75", "G7: first_in_scope cu scope invalid", "E2", 2)
def _(s):
    s["population"]["include"].append({
        "id": "p_first_bad", "predicate": "first_in_scope@v1",
        "params": {"scope": "century", "predicate": {"id": "pf_inner",
                   "predicate": "compare@v1", "params": {"left": "atr14", "op": ">", "right": 1.0}}}})


@mutation("M76", "G7: first_in_scope cu variabilă nedeclarată în predicatul intern", "E2", 2)
def _(s):
    s["population"]["include"].append({
        "id": "p_first_bad", "predicate": "first_in_scope@v1",
        "params": {"scope": "day", "predicate": {"id": "pf_inner",
                   "predicate": "compare@v1", "params": {"left": "inexistenta", "op": ">", "right": 1.0}}}})


@mutation("M77", "G7: first_in_scope valid (se oprește doar pe calibrare)", "E3", 2)
def _(s):
    s["population"]["include"].append({
        "id": "p_first_ok", "predicate": "first_in_scope@v1",
        "params": {"scope": "day", "predicate": {"id": "pf_inner_ok",
                   "predicate": "compare@v1", "params": {"left": "atr14", "op": ">", "right": 1.0}}}})


@mutation("M78", "G7: id de predicat duplicat în interiorul first_in_scope", "E2", 2)
def _(s):
    s["population"]["include"].append({
        "id": "p_first_dup", "predicate": "first_in_scope@v1",
        "params": {"scope": "day", "predicate": {"id": "p_atr_above",  # duplică include[0].id
                   "predicate": "compare@v1", "params": {"left": "atr14", "op": ">", "right": 1.0}}}})


# ─────────────── registru v1.4 — G8 (member_eligibility, regula de aur R3) ─────
# Baseline are member_eligibility {field:n, op:>=, value:1}. Mutațiile atacă R3.

@mutation("M79", "G8 R3: eligibilitate filtrată după p-value (INTERZIS)", "E2", 2)
def _(s):
    s["multiple_testing"]["params"]["member_eligibility"] = {"field": "p_hat", "op": "<", "value": 0.05}


@mutation("M80", "G8 R3: eligibilitate filtrată după efectul observat (INTERZIS)", "E2", 2)
def _(s):
    s["multiple_testing"]["params"]["member_eligibility"] = {"field": "observed", "op": "<", "value": 0.0}


@mutation("M81", "G8 R3: eligibilitate filtrată după statistică (INTERZIS)", "E2", 2)
def _(s):
    s["multiple_testing"]["params"]["member_eligibility"] = {"field": "statistic", "op": ">", "value": 1.0}


@mutation("M82", "G8: câmp de eligibilitate inexistent în lista albă", "E2", 2)
def _(s):
    s["multiple_testing"]["params"]["member_eligibility"] = {"field": "sharpe", "op": ">", "value": 1.0}


@mutation("M83", "G8: value de eligibilitate ne-numeric", "E2", 2)
def _(s):
    s["multiple_testing"]["params"]["member_eligibility"] = {"field": "n", "op": ">=", "value": "mult"}


@mutation("M84", "G8: regulă de eligibilitate malformată (chei lipsă)", "E2", 2)
def _(s):
    s["multiple_testing"]["params"]["member_eligibility"] = {"field": "n", "op": ">="}


@mutation("M85", "G8: member_eligibility absent (parametru obligatoriu al Bonferroni)", "E2", 2)
def _(s):
    del s["multiple_testing"]["params"]["member_eligibility"]


@mutation("M86", "G8: eligibilitate validă pe denominator (se oprește doar pe calibrare)", "E3", 2)
def _(s):
    s["multiple_testing"]["params"]["member_eligibility"] = {"field": "denominator", "op": ">=", "value": 100}


@mutation("M87", "G8: eligibilitate validă pe event_count (se oprește doar pe calibrare)", "E3", 2)
def _(s):
    s["multiple_testing"]["params"]["member_eligibility"] = {"field": "event_count", "op": ">=", "value": 25}
