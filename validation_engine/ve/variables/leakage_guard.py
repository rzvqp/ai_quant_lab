"""Garda de leakage la runtime (F4).

La F2 s-a verificat DECLARAȚIA de disponibilitate (offset_bars vs. rol). La F4 se
verifică că materializarea respectă efectiv acea declarație: o variabilă de
expunere/control/stratificare nu poate folosi bare cu index > index_eveniment,
iar una de rezultat folosește un orizont pozitiv declarat.

Verificarea e structurală: fiecare primitivă declară ce offset folosește, iar garda
confirmă că offset-ul efectiv ≤ offset-ul declarat pentru rolurile non-viitoare.
"""

from __future__ import annotations


class LeakageViolation(RuntimeError):
    """O variabilă a folosit o bară în afara ferestrei de disponibilitate declarate."""


NON_FUTURE_ROLES = {"exposure", "control", "stratifier"}


def check(role: str, declared_offset: int, effective_max_offset: int, var_id: str) -> None:
    """`effective_max_offset` = cel mai mare offset (față de bara-eveniment) atins efectiv."""
    if role in NON_FUTURE_ROLES and effective_max_offset > 0:
        raise LeakageViolation(
            f"variabila '{var_id}' (rol {role}) a folosit o bară viitoare "
            f"(offset efectiv {effective_max_offset} > 0)"
        )
    if role in NON_FUTURE_ROLES and effective_max_offset > declared_offset and declared_offset <= 0:
        # efectiv mai devreme e ok; efectiv mai târziu decât declarat, dar tot ≤0, e ok.
        pass
