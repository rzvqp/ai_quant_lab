"""Strategy Loader — discovery, parsing, structural + schema validation
(``STRATEGY_MANAGER_ARCHITECTURE.md`` §4).

Reads ``strategy.json`` files under the Strategy Library; never writes to it (architecture §1, §7
invariant 7 "Read-only over the Library"). Every failure — a missing file, invalid JSON, a schema
violation — becomes a classified :class:`LoadOutcome`, never an exception raised across this
module's boundary (the Manager's fail-safe policy, architecture §9): "The Loader never throws
across the API boundary for expected failures."
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from ai_trader.strategy_manager.contract import Contract, parse_contract
from ai_trader.strategy_manager.schema_validation import validate_contract
from ai_trader.strategy_manager.types import (
    CompatibilityResult,
    ContractRef,
    Health,
    Lifecycle,
    RegistryEntry,
)

_CONTRACT_FILENAME = "strategy.json"


def discover(library_path: Path) -> tuple[Path, ...]:
    """Enumerate ``<library_path>/*/strategy.json``, deterministically sorted by path.

    Architecture §4: "Deterministic ordering by ``identity.id``." The Library's own folder naming
    convention (``S<NN>_<slug>/``, two-digit zero-padded) makes lexicographic path order coincide
    with numeric id order for every strategy that parses successfully. A file that fails to parse
    has no ``identity.id`` at all, so path order is also the only ordering available for it —
    keeping the whole discovery→processing pipeline deterministic regardless of outcome, without
    requiring a two-pass "parse everything, then sort by id" scheme.
    """
    if not library_path.is_dir():
        return ()
    return tuple(sorted(library_path.glob(f"*/{_CONTRACT_FILENAME}")))


class LoadOutcome:
    """The result of loading one ``strategy.json`` file: either a valid, schema-checked
    :class:`~ai_trader.strategy_manager.contract.Contract`, or a classified failure. Never raises."""

    __slots__ = ("source_path", "id", "slug", "contract", "contract_ref", "health", "reasons")

    def __init__(
        self,
        source_path: str,
        id_: str | None,
        slug: str | None,
        contract: Contract | None,
        contract_ref: ContractRef,
        health: Health,
        reasons: tuple[str, ...] = (),
    ) -> None:
        self.source_path = source_path
        self.id = id_
        self.slug = slug
        self.contract = contract
        self.contract_ref = contract_ref
        self.health = health
        self.reasons = reasons

    @property
    def ok(self) -> bool:
        """``True`` iff a :class:`Contract` was successfully parsed and schema-validated (does NOT
        imply compatibility — see :mod:`ai_trader.strategy_manager.compatibility`)."""
        return self.contract is not None


def _content_hash(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def load_one(path: Path) -> LoadOutcome:
    """Read, parse, and schema-validate a single contract file.

    Classification (architecture §4/§9):
    - unreadable file / invalid JSON / non-object root -> ``CORRUPTED``
    - readable + valid JSON but fails ``strategy_contract.v1.schema.json`` -> ``INVALID``
    - passes schema validation -> a parsed :class:`Contract`, health ``LOADED`` (compatibility is
      checked separately by the caller; a contract can be schema-valid yet still incompatible)
    """
    source_path = str(path)
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        return LoadOutcome(
            source_path, None, None, None, ContractRef(),
            Health.CORRUPTED, (f"could not read file: {exc}",),
        )

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        return LoadOutcome(
            source_path, None, None, None, ContractRef(),
            Health.CORRUPTED, (f"not valid UTF-8: {exc}",),
        )

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return LoadOutcome(
            source_path, None, None, None, ContractRef(),
            Health.CORRUPTED, (f"invalid JSON: {exc}",),
        )

    if not isinstance(data, dict):
        return LoadOutcome(
            source_path, None, None, None, ContractRef(),
            Health.CORRUPTED, (f"contract root must be a JSON object, got {type(data).__name__}",),
        )

    content_hash = _content_hash(raw_bytes)
    schema_errors = validate_contract(data)
    if schema_errors:
        # best-effort id/version extraction for diagnostics even though the contract is invalid —
        # never raises: a schema-invalid file may be missing `identity` entirely.
        identity = data.get("identity") if isinstance(data.get("identity"), dict) else {}
        partial_id = identity.get("id") if isinstance(identity, dict) else None
        partial_version = identity.get("version") if isinstance(identity, dict) else None
        interface_version = data.get("interface_version")
        return LoadOutcome(
            source_path,
            partial_id if isinstance(partial_id, str) else None,
            None,
            None,
            ContractRef(
                identity_version=partial_version if isinstance(partial_version, str) else None,
                interface_version=interface_version if isinstance(interface_version, str) else None,
                content_hash=content_hash,
            ),
            Health.INVALID,
            tuple(schema_errors),
        )

    contract = parse_contract(data)
    return LoadOutcome(
        source_path,
        contract.identity.id,
        contract.identity.slug,
        contract,
        ContractRef(
            identity_version=contract.identity.version,
            interface_version=contract.interface_version,
            content_hash=content_hash,
        ),
        Health.LOADED,
        (),
    )


def load_all(library_path: Path) -> tuple[LoadOutcome, ...]:
    """Discover and load every contract under ``library_path``, in deterministic order.

    Best-effort (architecture §12 "Startup is fail-safe"): one bad file never aborts the others.
    """
    return tuple(load_one(path) for path in discover(library_path))


#: The Library's folder-naming convention (``S<NN>_<slug>/``) always starts with an ``S<digits>``
#: prefix that itself already satisfies the registry schema's ``RegistryEntry.id`` pattern
#: (``^S\d+$`` — leading zeros are just more digits, so ``"S01"`` matches directly). Used as a
#: best-effort id for entries whose contract failed to parse far enough to have its own
#: ``identity.id`` (``STRATEGY_REGISTRY_SCHEMA.json`` requires EVERY entry, including quarantined
#: ones, to carry a schema-conformant id -- there is no "no id" escape hatch in the frozen schema).
_FOLDER_ID_RE = re.compile(r"^(S\d+)_")


def _fallback_id_from_folder(source_path: str) -> str:
    folder = Path(source_path).parent.name
    match = _FOLDER_ID_RE.match(folder)
    if match:
        return match.group(1)
    # Pathological case: a folder that doesn't follow the Library's own naming convention at all.
    # "S0" is a safe sentinel -- ids in the real Library start at S1, so this can never collide with
    # a genuine strategy while still satisfying the schema's `^S\d+$` pattern.
    return "S0"


def draft_registry_entry(
    outcome: LoadOutcome, compatibility: CompatibilityResult, lifecycle: Lifecycle
) -> RegistryEntry:
    """Build the :class:`~ai_trader.strategy_manager.types.RegistryEntry` for one
    :class:`LoadOutcome`, given its already-computed
    :class:`~ai_trader.strategy_manager.compatibility.CompatibilityChecker` result and initial
    :class:`~ai_trader.strategy_manager.types.Lifecycle` (both are the caller's responsibility —
    see :mod:`ai_trader.strategy_manager.manager` for the orchestration order: load -> compatibility
    check -> initial lifecycle -> draft entry). ``slug`` falls back to the containing folder name
    when the contract failed to parse far enough to have its own ``identity.slug``; ``id`` falls
    back to the folder's own ``S<digits>`` prefix for the same reason (see
    :func:`_fallback_id_from_folder`).
    """
    slug = outcome.slug or Path(outcome.source_path).parent.name
    entry_id = outcome.id or _fallback_id_from_folder(outcome.source_path)
    return RegistryEntry(
        id=entry_id,
        slug=slug,
        source_path=outcome.source_path,
        lifecycle=lifecycle,
        health=outcome.health,
        loaded=outcome.ok,
        contract=outcome.contract,
        contract_ref=outcome.contract_ref,
        compatibility=compatibility,
        last_review=outcome.contract.lifecycle.last_review if outcome.contract is not None else None,
        errors=list(outcome.reasons),
    )
