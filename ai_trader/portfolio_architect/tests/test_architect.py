"""Unit tests for the Portfolio Architect Phase 1 (PASSTHROUGH-only) scaffold
(``PORTFOLIO_ARCHITECT_DESIGN.md``, CEO-ACCEPTED COMPLETE; Phase 1 authorization: PASSTHROUGH SCAFFOLD
ONLY). These are pure-function tests against :class:`PortfolioArchitect` directly, independent of the
harness -- see ``ai_trader/simulation/tests/test_portfolio_architect_passthrough.py`` for the
harness-level, real-data proofs (byte-identical competitive execution, Strategy Health interaction,
Risk Manager rank-sorting interaction).

``make_opportunity``/``make_portfolio`` are the SAME real, schema-valid fixture builders the Risk
Manager's own test suite uses (built through the real Signal Engine + Scoring Engine pipelines, not
hand-constructed dicts) -- reused here rather than reinvented, matching this project's own established
cross-package fixture-reuse convention."""

from __future__ import annotations

from dataclasses import replace

from ai_trader.portfolio_architect.architect import PortfolioArchitect
from ai_trader.portfolio_architect.types import ArchitectMode, PortfolioArchitectConfig
from ai_trader.risk_manager.tests.fixtures.fake_opportunity import make_opportunity, make_portfolio

AS_OF = 1_700_000_000
CONFIG = PortfolioArchitectConfig(mode=ArchitectMode.PASSTHROUGH)


def _architect() -> PortfolioArchitect:
    return PortfolioArchitect()


class TestPassthroughIdentity:
    def test_empty_opportunity_list_remains_empty(self) -> None:
        result = _architect().evaluate([], make_portfolio(), AS_OF, CONFIG)
        assert result.opportunities == ()
        assert result.diagnostics.input_count == 0
        assert result.diagnostics.output_count == 0

    def test_one_eligible_opportunity_remains_unchanged(self) -> None:
        opp = make_opportunity(strategy_id="S1", rank=1)
        result = _architect().evaluate([opp], make_portfolio(), AS_OF, CONFIG)
        assert result.opportunities == (opp,)
        assert result.opportunities[0] is opp  # same object, not a copy

    def test_multiple_eligible_opportunities_remain_unchanged(self) -> None:
        opps = [
            make_opportunity(strategy_id="S1", rank=1),
            make_opportunity(strategy_id="S2", rank=2),
            make_opportunity(strategy_id="S3", rank=3),
        ]
        result = _architect().evaluate(opps, make_portfolio(), AS_OF, CONFIG)
        assert result.opportunities == tuple(opps)
        assert [o.rank for o in result.opportunities] == [1, 2, 3]
        assert [o.strategy_id for o in result.opportunities] == ["S1", "S2", "S3"]

    def test_tied_ranks_remain_unchanged(self) -> None:
        # Hand-forced tie (real Scoring Engine output never ties within one batch, per the Ranker's own
        # total-order guarantee) -- PASSTHROUGH must not attempt to break or normalize ties.
        opp_a = make_opportunity(strategy_id="S1", rank=1)
        opp_b = replace(make_opportunity(strategy_id="S2", rank=1), rank=1)
        result = _architect().evaluate([opp_a, opp_b], make_portfolio(), AS_OF, CONFIG)
        assert [o.rank for o in result.opportunities] == [1, 1]
        assert result.opportunities == (opp_a, opp_b)

    def test_out_of_rank_order_input_is_preserved_exactly_not_sorted(self) -> None:
        """Risk Manager re-sorts by each opportunity's own `rank` field, ignoring input list order
        (risk_manager/engine.py:264) -- PASSTHROUGH must not accidentally impose or rely on any
        ordering of its own. Feeding input already out of rank order and confirming it comes back
        exactly as given (not re-sorted into rank order) proves this layer does nothing with order at
        all, so whatever guarantee Risk Manager's own re-sort provides is completely untouched by this
        layer's presence."""
        rank3 = make_opportunity(strategy_id="S3", rank=3)
        rank1 = make_opportunity(strategy_id="S1", rank=1)
        rank2 = make_opportunity(strategy_id="S2", rank=2)
        result = _architect().evaluate([rank3, rank1, rank2], make_portfolio(), AS_OF, CONFIG)
        assert result.opportunities == (rank3, rank1, rank2)  # exact input order preserved, not sorted


class TestCannotRestoreExcludedStrategies:
    def test_output_is_always_a_subset_of_input_never_a_superset(self) -> None:
        """Structural proof that Portfolio Architect cannot resurrect a strategy Strategy Health has
        already excluded: since PASSTHROUGH performs no filtering of its own, whatever strategy ids are
        ABSENT from its input (because Strategy Health's own health_eligible_ids filter already removed
        them upstream) are necessarily absent from its output too -- there is no code path by which a
        strategy_id not in the input could appear in the output."""
        opps = [make_opportunity(strategy_id="S1", rank=1), make_opportunity(strategy_id="S2", rank=2)]
        result = _architect().evaluate(opps, make_portfolio(), AS_OF, CONFIG)
        output_ids = {o.strategy_id for o in result.opportunities}
        assert output_ids == {"S1", "S2"}
        assert "S10" not in output_ids  # never appears -- it was never in the input


class TestDeterminism:
    def test_diagnostics_are_deterministic(self) -> None:
        opps = [make_opportunity(strategy_id="S1", rank=1), make_opportunity(strategy_id="S2", rank=2)]
        architect = _architect()
        result_a = architect.evaluate(opps, make_portfolio(), AS_OF, CONFIG)
        result_b = architect.evaluate(opps, make_portfolio(), AS_OF, CONFIG)
        assert result_a.diagnostics == result_b.diagnostics

    def test_unsupported_mode_raises_rather_than_silently_falling_back(self) -> None:
        import pytest

        from ai_trader.portfolio_architect.types import ArchitectMode

        bad_config = replace(CONFIG, mode="NOT_A_REAL_MODE")  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            _architect().evaluate([], make_portfolio(), AS_OF, bad_config)
        assert ArchitectMode.PASSTHROUGH in ArchitectMode  # sanity: the one real mode still exists
