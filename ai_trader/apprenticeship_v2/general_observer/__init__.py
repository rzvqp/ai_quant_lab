"""AI Trader General Market Observer V1.1 -- implements
`docs/trader_apprenticeship/apprenticeship_v2/AI_TRADER_GENERAL_OBSERVATION_DESIGN_V1_1_DEFINITIONAL_LOCK.md`
exactly. See that document for every semantic rule; nothing in this package invents a trigger
condition, threshold, or dedup rule not already frozen there.

Deliberately a separate subpackage from the S5 pathway (`loop.py`/`s5_observer.py`) -- imports FROM
`schemas`/`durable_store`/`mt5_read_only_source` only, never the reverse, and never imports
`s5_observer` at all (S5 isolation, design doc Section 15)."""
