"""Teste pentru orchestratorul gardat (run_production_pipeline.py) — Mandat 5.10.

Verifică cele DOUĂ garduri INDEPENDENTE. Nu se rulează pipeline-ul, nu se apelează `.load()` efectiv:
fiecare test lovește un gard ÎNAINTE de orice acces la date.
"""

import os
import sys

import pytest

_CODE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code")
if _CODE not in sys.path:
    sys.path.insert(0, _CODE)

import run_production_pipeline as RP  # noqa: E402


# ── GARD 1 ──────────────────────────────────────────────────────────────────────────────────────
def test_execute_raises_while_gated_by_cto():
    """.execute() ridică excepție cât timp GATED_BY_CTO e True (oprește orice execuție, înainte de date)."""
    assert RP.GATED_BY_CTO is True
    with pytest.raises(RP.CtoGateError):
        RP.ProductionPipeline().execute()


# ── GARD 2 — cel care contează: fără el, gardul e o convenție, nu un mecanism ───────────────────────
def test_sealed_access_raises_without_authorization():
    """Accesul la sigilat ridică excepție FĂRĂ autorizare scrisă explicită."""
    with pytest.raises(RP.SealedAccessError):
        RP.ProductionPipeline().authorize_segment(RP.DataSegment.SEALED)      # authorization=None implicit


def test_sealed_access_raises_with_incomplete_authorization():
    """Autorizare incompletă (câmp gol) → tot refuzat (fail-closed pe câmpuri, nu doar pe prezență)."""
    incomplete = RP.WrittenAuthorization(authorized_by="CTO", reason="", document_ref="doc#1")
    with pytest.raises(RP.SealedAccessError):
        RP.ProductionPipeline().authorize_segment(RP.DataSegment.SEALED, incomplete)


def test_sealed_access_passes_with_complete_authorization():
    """Cu autorizare scrisă COMPLETĂ, GARD 2 lasă să treacă — mecanism cu deblocare reală, nu blocare oarbă."""
    auth = RP.WrittenAuthorization(authorized_by="CTO", reason="F8 unseal", document_ref="commit:abc123")
    assert RP.ProductionPipeline().authorize_segment(RP.DataSegment.SEALED, auth) is RP.DataSegment.SEALED


def test_discovery_is_default_and_needs_no_authorization():
    """Implicit se livrează DOAR descoperirea — fără autorizare, fără atingerea sigilatului (fail-closed)."""
    assert RP.ProductionPipeline().authorize_segment(RP.DataSegment.DISCOVERY) is RP.DataSegment.DISCOVERY


# ── INDEPENDENȚA celor două garduri: ridicarea GARD 1 NU deschide sigilatul ─────────────────────────
def test_guards_are_independent_lifting_gate1_does_not_open_sealed(monkeypatch):
    """Chiar dacă cineva ridică GARD 1 (GATED_BY_CTO=False), accesul la sigilat FĂRĂ autorizare tot ridică
    SealedAccessError (GARD 2), NU CtoGateError — exact scenariul în care holdout-ul s-a ars tăcut.
    Două decizii separate, două momente separate."""
    monkeypatch.setattr(RP, "GATED_BY_CTO", False)
    with pytest.raises(RP.SealedAccessError):
        RP.ProductionPipeline().execute(segment=RP.DataSegment.SEALED, authorization=None)


def test_structure_net_R_vector_is_a_signature_over_prices():
    """Vectorul net_R se structurează doar cu prețuri furnizate explicit (Corecția 3, module inerte)."""
    sig = RP.StrategySignal(family="S1", trigger_idx=5, entry_idx=6, direction=+1, spike_pips=20.0,
                            selection_end=6, measurement_start=6, measurement_end=26)
    prices = [100.0] * 30
    vec = RP.structure_net_R_vector([sig], prices, prices)
    assert len(vec) == 1 and isinstance(vec[0], float)
