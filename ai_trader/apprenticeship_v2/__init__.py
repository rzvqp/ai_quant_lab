"""AI Trader Continuous Market Apprenticeship V2 (CEO mandate, 2026-09-02).

Live, forward, causal market-observation layer for XAUUSD. Structurally observation-only: no module
in this package imports or calls any MT5 order-submission function (`order_send`, `order_check`,
`order_calc_margin`, `order_calc_profit`, `positions_close`, or any position/order-modification call).
The sole MT5 import point for this package is `mt5_read_only_source.py`, which documents exactly
which read-only calls it uses and no others -- mirroring the repo's own established
`mt5_connectivity_probe.py` discipline.

Does not modify S5, P007, or MGMT-004. Does not submit broker orders. Does not run alongside or
interfere with the existing `AITraderS5MT5DemoSoak` / `AITraderLiveShadow` scheduled tasks -- this
package opens its own independent, read-only MT5 client attachment to the same already-open terminal
and never touches those processes' own state.
"""
