"""Etapa 2 — validarea vocabularului, față de `capabilities.json`.

Verifică: existența ID-urilor, prezența TUTUROR parametrilor obligatorii, absența
parametrilor necunoscuți, respectarea domeniilor, regulile de disponibilitate
(anti-leakage la nivel de declarație), coerența referințelor și suprapunerea cu
ferestrele sigilate.

Registrul este sursa unică de adevăr. Un ID absent din registru nu este
interpretat, aproximat sau acceptat provizoriu — oprește rularea (E3).
"""

from __future__ import annotations

import functools
import json
import re

from .. import paths
from ..errors import VEError
from . import domains

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

#: Roluri pentru care variabila trebuie să fie disponibilă cel târziu la momentul
#: evenimentului. Regula este verificată, nu dedusă.
NON_FUTURE_ROLES = {"exposure", "control", "stratifier"}

#: Parametri de predicat care conțin alte predicate (recursie).
_NESTED_PRED_PARAMS = ("operands", "steps")


def _iter_predicates(pred):
    """Parcurge recursiv un predicat și sub-predicatele lui.

    Sub-predicatele apar în parametri-listă (`operands`, `steps`) și, de la
    registrul v1.3, într-un parametru-predicat singular (`predicate` al lui
    `first_in_scope@v1`).
    """
    if not isinstance(pred, dict):
        return
    yield pred
    params = pred.get("params") or {}
    for key in _NESTED_PRED_PARAMS:
        sub = params.get(key)
        if isinstance(sub, list):
            for item in sub:
                yield from _iter_predicates(item)
    inner = params.get("predicate")   # first_in_scope@v1 (G7)
    if isinstance(inner, dict):
        yield from _iter_predicates(inner)


def _all_predicate_roots(spec):
    """(cale, predicat) pentru fiecare predicat-rădăcină din întreaga specificație.

    Include predicatele de populație, predicatele din celule și predicatele
    declarate inline de `indicator@v1` — toate participă la unicitatea globală a
    id-urilor și la referirea prin `predicate_ref`.
    """
    pop = spec.get("population", {})
    for group in ("include", "exclude"):
        for i, p in enumerate(pop.get(group, []) or []):
            yield f"population/{group}/{i}", p
    for i, t in enumerate(spec.get("tests", []) or []):
        for j, c in enumerate(t.get("cells", []) or []):
            for k, p in enumerate(c.get("predicates", []) or []):
                yield f"tests/{i}/cells/{j}/predicates/{k}", p
    for i, v in enumerate(spec.get("variables", []) or []):
        if v.get("primitive") == "indicator@v1":
            p = (v.get("params") or {}).get("predicate")
            if isinstance(p, dict):
                yield f"variables/{i}/params/predicate", p


def _param_is_variable_ref(descriptor) -> bool:
    """True dacă descriptorul de domeniu referă o variabilă (direct sau într-o uniune)."""
    dom = domains.parse(descriptor)
    if dom.kind == "reference" and dom.detail == "variable_ref":
        return True
    if dom.kind == "union":
        return any(d.kind == "reference" and d.detail == "variable_ref" for d in dom.detail)
    return False


@functools.lru_cache(maxsize=1)
def load_registry() -> dict:
    with open(paths.CAPABILITIES_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


@functools.lru_cache(maxsize=1)
def registry_domains_are_parseable() -> tuple[bool, tuple[str, ...]]:
    """Auto-verificare fail-closed a registrului.

    Dacă un descriptor de domeniu din registru nu este acoperit de gramatică,
    validatorul refuză să valideze orice specificație.
    """
    reg = load_registry()
    bad: list[str] = []
    for section in (
        "variable_primitives",
        "population_predicates",
        "statistics",
        "test_methods",
        "correction_methods",
    ):
        for entry_id, entry in reg.get(section, {}).items():
            for param, descriptor in (entry.get("required_params") or {}).items():
                try:
                    domains.parse(descriptor)
                except domains.UnsupportedDomain as exc:
                    bad.append(f"{section}.{entry_id}.{param}: {exc}")
    return (not bad), tuple(bad)


class _Ctx:
    """Context de rezolvare a referințelor dintr-o specificație."""

    def __init__(self, spec: dict, reg: dict):
        self.spec = spec
        self.reg = reg
        self.declared_sources = {d.get("source_id") for d in spec.get("data", [])}
        self.variable_ids = {v.get("id") for v in spec.get("variables", [])}
        self.test_ids = {t.get("test_id") for t in spec.get("tests", [])}
        self.cells_by_test = {
            t.get("test_id"): {c.get("id") for c in t.get("cells", [])}
            for t in spec.get("tests", [])
        }
        # G5: id-urile de predicat devin referibile prin predicate_ref, deci trebuie
        # colectate din întreaga specificație (nu doar din include/exclude) și
        # verificate pentru unicitate globală.
        self.predicate_ids: set[str] = set()
        self.duplicate_predicate_ids: list[str] = []
        _seen: set[str] = set()
        for _root_path, _root in _all_predicate_roots(spec):
            for node in _iter_predicates(_root):
                pid = node.get("id")
                if not isinstance(pid, str):
                    continue
                if pid in _seen and pid not in self.duplicate_predicate_ids:
                    self.duplicate_predicate_ids.append(pid)
                _seen.add(pid)
                self.predicate_ids.add(pid)
        self.errors: list[VEError] = []

    def allowed_outputs(self, test_id: str) -> set[str]:
        """Ieșiri referibile pentru un test: ale metodei + ale corecției declarate.

        `p_adjusted` nu este produs de metoda de test, ci de metoda de corecție,
        deci ambele mulțimi sunt admise ca ținte de referință.
        """
        out: set[str] = set()
        for t in self.spec.get("tests", []):
            if t.get("test_id") == test_id:
                meta = self.reg["test_methods"].get(t.get("method"))
                if meta:
                    out |= set(meta.get("outputs", []))
        mt = self.spec.get("multiple_testing", {})
        cmeta = self.reg["correction_methods"].get(mt.get("method"))
        if cmeta:
            out |= set(cmeta.get("outputs", []))
        return out


def _resolver(ctx: _Ctx, where: str):
    def resolve(kind: str, value) -> str | None:
        if kind == "data_source_id":
            if not isinstance(value, str):
                return "identificatorul sursei trebuie să fie șir de caractere"
            if value not in ctx.reg["data_sources"]:
                return f"sursa '{value}' nu există în registru"
            if value not in ctx.declared_sources:
                return f"sursa '{value}' nu este declarată în secțiunea data"
            return None
        if kind == "statistic_id":
            if value not in ctx.reg["statistics"]:
                return f"statistica '{value}' nu există în registru"
            return None
        if kind == "statistic_call":
            # G2 (registru v1.1): declarație inline parametrizată, în forma predicatelor.
            if not isinstance(value, dict) or set(value) != {"id", "statistic", "params"}:
                return "statistica trebuie declarată ca obiect cu exact câmpurile id, statistic, params"
            return _check_entry(
                ctx, "statistics", value.get("statistic"), value.get("params"),
                f"{where}/{value.get('id')}",
            )
        if kind == "variable_ref":
            if value not in ctx.variable_ids:
                return f"variabila '{value}' nu este declarată în secțiunea variables"
            return None
        if kind == "test_ref":
            # G5: trimite la un test declarat (ex. base_test_ref).
            if value not in ctx.test_ids:
                return f"testul '{value}' nu este declarat în secțiunea tests"
            return None
        if kind == "predicate_ref":
            # G5: trimite la id-ul unui predicat declarat oriunde în specificație.
            if value not in ctx.predicate_ids:
                return f"predicatul '{value}' nu este declarat în specificație"
            return None
        if kind == "eligibility_rule":
            # G8 (registru v1.4): regula de eligibilitate a membrilor familiei.
            # REGULA DE AUR R3: field DOAR din lista albă de câmpuri PRE-REZULTAT.
            # Orice referire la p-value/statistică/efect este respinsă aici, înainte de date.
            if not isinstance(value, dict) or set(value) != {"field", "op", "value"}:
                return "regula de eligibilitate trebuie să aibă exact câmpurile field, op, value"
            whitelist = ctx.reg.get("member_eligibility_fields", [])
            if value.get("field") not in whitelist:
                return (
                    f"câmpul '{value.get('field')}' nu este un câmp pre-rezultat admis; "
                    f"eligibilitatea NU poate referi rezultate (p-value/statistică/efect). "
                    f"câmpuri admise: {', '.join(whitelist)}"
                )
            if value.get("op") not in {"<", "<=", ">", ">=", "==", "!="}:
                return "operator de comparație invalid"
            v = value.get("value")
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                return "value trebuie să fie numeric"
            return None
        if kind == "iso8601":
            if not isinstance(value, str) or not _ISO.match(value):
                return "momentul trebuie scris ca YYYY-MM-DDTHH:MM:SSZ"
            return None
        if kind == "window_object":
            if not isinstance(value, dict) or set(value) != {"start", "end", "bounds"}:
                return "fereastra trebuie să aibă exact câmpurile start, end, bounds"
            if not _ISO.match(str(value.get("start", ""))) or not _ISO.match(str(value.get("end", ""))):
                return "capetele ferestrei trebuie scrise ca YYYY-MM-DDTHH:MM:SSZ"
            if value.get("bounds") not in {"[)", "[]", "(]", "()"}:
                return "inclusivitatea capetelor trebuie declarată explicit"
            return None
        if kind == "predicate":
            if not isinstance(value, dict) or set(value) != {"id", "predicate", "params"}:
                return "predicatul trebuie să aibă exact câmpurile id, predicate, params"
            sub = _check_entry(
                ctx, "population_predicates", value.get("predicate"), value.get("params"),
                f"{where}/{value.get('id')}",
            )
            return sub
        if kind == "test_target":
            if not isinstance(value, dict) or set(value) != {"test_id", "cell", "output"}:
                return "ținta trebuie să aibă exact câmpurile test_id, cell, output"
            tid = value["test_id"]
            if tid not in ctx.test_ids:
                return f"testul '{tid}' nu este declarat în secțiunea tests"
            if value["cell"] not in ctx.cells_by_test.get(tid, set()):
                return f"celula '{value['cell']}' nu este declarată la testul '{tid}'"
            allowed = ctx.allowed_outputs(tid)
            if allowed and value["output"] not in allowed:
                return f"ieșirea '{value['output']}' nu este produsă de metoda testului sau de corecție"
            return None
        return None

    return resolve


def _check_entry(ctx: _Ctx, section: str, entry_id, params, where: str) -> str | None:
    """Verifică un ID de registru + parametrii lui. Întoarce un motiv sau None."""
    catalog = ctx.reg.get(section, {})
    if entry_id not in catalog:
        return f"'{entry_id}' nu există în registru ({section})"
    required = catalog[entry_id].get("required_params") or {}
    if not isinstance(params, dict):
        return "params trebuie să fie obiect"
    missing = sorted(set(required) - set(params))
    if missing:
        return "parametri obligatorii absenți: " + ", ".join(missing)
    unknown = sorted(set(params) - set(required))
    if unknown:
        return "parametri necunoscuți (registrul nu admite parametri opționali): " + ", ".join(unknown)
    resolve = _resolver(ctx, where)
    for name, descriptor in required.items():
        dom = domains.parse(descriptor)
        reason = domains.check(dom, params[name], resolve, f"{where}/{name}")
        if reason:
            return f"parametrul '{name}': {reason}"
    return None


def _predicate_variable_refs(ctx: _Ctx, pred) -> set[str]:
    """Toate variabilele referite în interiorul unui predicat (recursiv)."""
    refs: set[str] = set()
    for node in _iter_predicates(pred):
        meta = ctx.reg["population_predicates"].get(node.get("predicate"), {})
        req = meta.get("required_params") or {}
        params = node.get("params") or {}
        for pn, desc in req.items():
            if pn in _NESTED_PRED_PARAMS:
                continue
            if _param_is_variable_ref(desc):
                val = params.get(pn)
                if isinstance(val, str) and val in ctx.variable_ids:
                    refs.add(val)
    return refs


def _variable_direct_deps(ctx: _Ctx, var: dict) -> set[str]:
    """Variabilele de care depinde direct o variabilă declarată.

    Sunt luate din parametrii tipizați `variable_ref` și, pentru `indicator@v1`,
    din toate variabilele folosite de predicatul lui.
    """
    deps: set[str] = set()
    meta = ctx.reg["variable_primitives"].get(var.get("primitive"), {})
    req = meta.get("required_params") or {}
    params = var.get("params") or {}
    for pn, desc in req.items():
        if desc == "predicate":
            deps |= _predicate_variable_refs(ctx, params.get(pn))
        elif isinstance(desc, str) and _param_is_variable_ref(desc):
            val = params.get(pn)
            if isinstance(val, str) and val in ctx.variable_ids:
                deps.add(val)
    return deps


def _check_variable_graph(ctx: _Ctx) -> list[VEError]:
    """Detectarea ciclurilor de referință + regula de disponibilitate recursivă.

    Regula (G3, dar generică pentru orice primitivă): nicio variabilă nu poate
    declara o disponibilitate mai timpurie decât oricare dintre dependențele ei —
    `offset_bars(var) >= offset_bars(dep)`. Un offset mai negativ înseamnă mai
    devreme; o variabilă nu poate exista înaintea intrărilor ei.
    """
    errors: list[VEError] = []
    variables = ctx.spec.get("variables", []) or []
    by_id: dict[str, dict] = {}
    path_by_id: dict[str, str] = {}
    for i, v in enumerate(variables):
        vid = v.get("id")
        if isinstance(vid, str) and vid not in by_id:
            by_id[vid] = v
            path_by_id[vid] = f"variables/{i}"

    deps = {vid: _variable_direct_deps(ctx, v) for vid, v in by_id.items()}

    # --- detectarea ciclurilor (DFS cu marcaje) ------------------------------
    WHITE, GREY, BLACK = 0, 1, 2
    color = {vid: WHITE for vid in by_id}
    cyclic: set[str] = set()
    reported: set[frozenset] = set()

    def dfs(u: str, stack: list[str]) -> None:
        color[u] = GREY
        stack.append(u)
        for w in sorted(deps.get(u, ())):
            if w not in color:
                continue
            if color[w] == GREY:
                cycle = stack[stack.index(w):] + [w]
                key = frozenset(cycle)
                cyclic.update(cycle)
                if key not in reported:
                    reported.add(key)
                    errors.append(VEError(
                        "E2", f"{path_by_id.get(cycle[0], 'variables')}/id",
                        "Ciclu de referință între variabile: " + " -> ".join(cycle) + ".",
                        "referințele dintre variabile trebuie să formeze un graf aciclic",
                    ))
            elif color[w] == WHITE:
                dfs(w, stack)
        stack.pop()
        color[u] = BLACK

    for vid in sorted(by_id):
        if color[vid] == WHITE:
            dfs(vid, [])

    # --- regula de disponibilitate (numai pe grafuri aciclice) ---------------
    def offset_of(vid: str):
        off = (by_id[vid].get("availability") or {}).get("offset_bars")
        return off if isinstance(off, int) else None

    for vid, v in by_id.items():
        if vid in cyclic:
            continue
        off = offset_of(vid)
        if off is None:
            continue
        for dep in sorted(deps.get(vid, ())):
            if dep in cyclic:
                continue
            doff = offset_of(dep)
            if doff is not None and off < doff:
                errors.append(VEError(
                    "E2", f"{path_by_id[vid]}/availability/offset_bars",
                    f"Variabila '{vid}' declară disponibilitate la offset {off}, mai devreme "
                    f"decât dependența '{dep}' (offset {doff}); nicio variabilă nu poate exista "
                    "înaintea intrărilor ei.",
                    "regulă: offset_bars(variabilă) >= offset_bars(dependență)",
                ))
    return errors


def _registry_info(ctx: _Ctx, section: str, entry_id=None) -> str:
    catalog = ctx.reg.get(section, {})
    if entry_id in catalog:
        req = catalog[entry_id].get("required_params") or {}
        return f"{entry_id} cere: " + (", ".join(sorted(req)) if req else "(niciun parametru)")
    return f"ID-uri existente în registru ({section}): " + ", ".join(sorted(catalog))


def validate_vocabulary(spec: dict) -> list[VEError]:
    ok, bad = registry_domains_are_parseable()
    if not ok:
        return [
            VEError(
                code="E3",
                field_path="capabilities.json",
                reason=(
                    "Registrul conține descriptori de domeniu neacoperiți de gramatică; "
                    "validarea este refuzată fail-closed: " + "; ".join(bad)
                ),
                registry_info="",
            )
        ]

    reg = load_registry()
    ctx = _Ctx(spec, reg)
    errors = ctx.errors

    # --- R1 versiunea registrului -------------------------------------------
    if spec.get("capability_registry_version") != reg.get("registry_version"):
        errors.append(VEError(
            "E2", "capability_registry_version",
            f"Specificația este scrisă pentru registrul {spec.get('capability_registry_version')!r}, "
            f"iar registrul instalat este {reg.get('registry_version')!r}.",
            f"versiunea registrului instalat: {reg.get('registry_version')!r}",
        ))

    # --- R2 sursele de date --------------------------------------------------
    for i, entry in enumerate(spec.get("data", [])):
        sid = entry.get("source_id")
        if sid not in reg["data_sources"]:
            errors.append(VEError(
                "E3", f"data/{i}/source_id",
                f"Sursa '{sid}' nu există în registru.",
                _registry_info(ctx, "data_sources"),
            ))
            continue
        declared = entry.get("sha256")
        known = reg["data_sources"][sid]["sha256"]
        if declared != known:
            errors.append(VEError(
                "E2", f"data/{i}/sha256",
                "Hash-ul declarat nu corespunde hash-ului înregistrat pentru această sursă.",
                f"hash înregistrat pentru {sid}: {known}",
            ))

    # --- R3 populația --------------------------------------------------------
    pop = spec.get("population", {})
    if pop.get("source_id") not in ctx.declared_sources:
        errors.append(VEError(
            "E2", "population/source_id",
            "Sursa populației nu este declarată în secțiunea data.",
            "surse declarate: " + ", ".join(sorted(str(s) for s in ctx.declared_sources)),
        ))

    # --- R4 predicatele de populație ----------------------------------------
    # Unicitatea id-urilor de predicat este verificată global (G5) în R9, peste
    # întreaga specificație — nu doar în include/exclude — pentru că id-urile sunt
    # acum referibile prin predicate_ref, iar denominatorul per criteriu depinde
    # de unicitatea lor.
    for group in ("include", "exclude"):
        for i, pred in enumerate(pop.get(group, [])):
            path = f"population/{group}/{i}"
            reason = _check_entry(ctx, "population_predicates", pred.get("predicate"), pred.get("params"), path)
            if reason:
                code = "E3" if pred.get("predicate") not in reg["population_predicates"] else "E2"
                errors.append(VEError(
                    code, path, reason,
                    _registry_info(ctx, "population_predicates", pred.get("predicate")),
                ))

    # --- R5 variabilele ------------------------------------------------------
    seen_var_ids: set[str] = set()
    for i, var in enumerate(spec.get("variables", [])):
        path = f"variables/{i}"
        vid = var.get("id")
        if vid in seen_var_ids:
            errors.append(VEError("E2", f"{path}/id", f"Identificatorul de variabilă '{vid}' este duplicat."))
        seen_var_ids.add(vid)

        prim = var.get("primitive")
        reason = _check_entry(ctx, "variable_primitives", prim, var.get("params"), path)
        if reason:
            code = "E3" if prim not in reg["variable_primitives"] else "E2"
            errors.append(VEError(code, path, reason, _registry_info(ctx, "variable_primitives", prim)))

        # G1 (registru v1.1): câmpul unei serii brute trebuie să existe efectiv în sursă.
        # M15 nu are coloana 'sub' pe care H1/H4/D1 o au — verificare mecanică, nu convenție.
        if prim == "raw_series@v1":
            vparams = var.get("params") or {}
            src, field = vparams.get("source_id"), vparams.get("field")
            source_meta = reg["data_sources"].get(src)
            if source_meta and field not in source_meta.get("columns", []):
                errors.append(VEError(
                    "E2", f"{path}/params/field",
                    f"Câmpul '{field}' nu există în sursa '{src}'.",
                    f"coloane declarate pentru {src}: " + ", ".join(source_meta.get("columns", [])),
                ))

        avail = var.get("availability", {})
        role = var.get("role")
        offset = avail.get("offset_bars")
        if role in NON_FUTURE_ROLES and isinstance(offset, int) and offset > 0:
            errors.append(VEError(
                "E2", f"{path}/availability/offset_bars",
                f"Rolul '{role}' cere disponibilitate cel târziu la momentul evenimentului "
                f"(offset_bars ≤ 0), dar s-a declarat {offset}.",
                "regula din registru: " + reg["availability_rules"][role],
            ))
        if avail.get("source_id") not in ctx.declared_sources:
            errors.append(VEError(
                "E2", f"{path}/availability/source_id",
                "Sursa de disponibilitate nu este declarată în secțiunea data.",
                "surse declarate: " + ", ".join(sorted(str(s) for s in ctx.declared_sources)),
            ))

    # --- R6 testele ----------------------------------------------------------
    seen_test_ids: set[str] = set()
    seen_orders: set[int] = set()
    for i, test in enumerate(spec.get("tests", [])):
        path = f"tests/{i}"
        tid = test.get("test_id")
        if tid in seen_test_ids:
            errors.append(VEError("E2", f"{path}/test_id", f"Identificatorul de test '{tid}' este duplicat."))
        seen_test_ids.add(tid)

        order = test.get("order")
        if order in seen_orders:
            errors.append(VEError(
                "E2", f"{path}/order",
                f"Ordinea {order} este folosită de mai multe teste; ordinea de execuție ar fi ambiguă.",
            ))
        seen_orders.add(order)

        method = test.get("method")
        meta = reg["test_methods"].get(method)
        if meta is None:
            errors.append(VEError(
                "E3", f"{path}/method", f"Metoda '{method}' nu există în registru.",
                _registry_info(ctx, "test_methods"),
            ))
        else:
            if meta.get("calibration_status") != "VALIDATED":
                errors.append(VEError(
                    "E3", f"{path}/method",
                    f"Metoda '{method}' are statusul de calibrare "
                    f"{meta.get('calibration_status')!r} și nu poate fi executată oficial.",
                    "statusuri executabile: VALIDATED · suite de acceptare cerute: "
                    + ", ".join(meta.get("acceptance_suites", [])),
                ))
            reason = _check_entry(ctx, "test_methods", method, test.get("params"), path)
            if reason:
                errors.append(VEError("E2", f"{path}/params", reason, _registry_info(ctx, "test_methods", method)))

        seen_cells: set[str] = set()
        for j, cell in enumerate(test.get("cells", [])):
            cpath = f"{path}/cells/{j}"
            if cell.get("id") in seen_cells:
                errors.append(VEError("E2", f"{cpath}/id", f"Celula '{cell.get('id')}' este duplicată în test."))
            seen_cells.add(cell.get("id"))
            for k, pred in enumerate(cell.get("predicates", [])):
                r = _check_entry(ctx, "population_predicates", pred.get("predicate"), pred.get("params"), f"{cpath}/predicates/{k}")
                if r:
                    code = "E3" if pred.get("predicate") not in reg["population_predicates"] else "E2"
                    errors.append(VEError(
                        code, f"{cpath}/predicates/{k}", r,
                        _registry_info(ctx, "population_predicates", pred.get("predicate")),
                    ))

    # --- R7 corecția family-wise --------------------------------------------
    mt = spec.get("multiple_testing", {})
    cmethod = mt.get("method")
    cmeta = reg["correction_methods"].get(cmethod)
    if cmeta is None:
        errors.append(VEError(
            "E3", "multiple_testing/method", f"Metoda de corecție '{cmethod}' nu există în registru.",
            _registry_info(ctx, "correction_methods"),
        ))
    else:
        if cmeta.get("calibration_status") != "VALIDATED":
            errors.append(VEError(
                "E3", "multiple_testing/method",
                f"Metoda de corecție '{cmethod}' are statusul {cmeta.get('calibration_status')!r} "
                "și nu poate fi executată oficial.",
                "statusuri executabile: VALIDATED",
            ))
        reason = _check_entry(ctx, "correction_methods", cmethod, mt.get("params"), "multiple_testing")
        if reason:
            errors.append(VEError("E2", "multiple_testing/params", reason, _registry_info(ctx, "correction_methods", cmethod)))

    resolve = _resolver(ctx, "multiple_testing/members")
    for i, member in enumerate(mt.get("members", [])):
        r = resolve("test_target", member)
        if r:
            errors.append(VEError("E2", f"multiple_testing/members/{i}", r))

    # --- R8 criteriile preînregistrate --------------------------------------
    resolve_c = _resolver(ctx, "criteria")
    for i, crit in enumerate(spec.get("criteria", [])):
        r = resolve_c("test_target", crit.get("target"))
        if r:
            errors.append(VEError("E2", f"criteria/{i}/target", r))

    # --- R9 unicitatea globală a id-urilor de predicat (G5) ------------------
    for pid in ctx.duplicate_predicate_ids:
        errors.append(VEError(
            "E2", "population/predicates",
            f"Identificatorul de predicat '{pid}' este folosit de mai multe ori în "
            "specificație; id-urile de predicat sunt referibile prin predicate_ref și "
            "trebuie unice, iar denominatorul per criteriu ar deveni altfel ambiguu.",
            "fiecare id de predicat trebuie să fie unic în întreaga specificație",
        ))

    # --- R10 graful de variabile: cicluri + disponibilitate (G3) -------------
    errors.extend(_check_variable_graph(ctx))

    # --- R11 suprapunerea cu ferestrele sigilate -----------------------------
    errors.extend(_check_sealed(spec, reg))

    return errors


def _check_sealed(spec: dict, reg: dict) -> list[VEError]:
    """Verifică autorizarea față de granița sigilată, folosind DOAR metadate.

    Nu se deschide niciun fișier de date: comparația se face între fereastra
    declarată în specificație și fereastra sigilată înregistrată în registru.
    """
    out: list[VEError] = []
    sealed = reg.get("sealed_registry", {})
    windows = sealed.get("windows", {})
    pop = spec.get("population", {})
    src = pop.get("source_id")
    win = pop.get("window", {})
    entry = windows.get(src)
    if not entry or not isinstance(win, dict):
        return out

    sealed_first = entry.get("sealed_first")
    end = win.get("end")
    bounds = win.get("bounds", "")
    if not (isinstance(end, str) and isinstance(sealed_first, str)):
        return out

    # Format ISO fix -> comparația lexicografică este cronologică.
    overlaps = end > sealed_first or (end == sealed_first and bounds.endswith("]"))
    authorized = bool(spec.get("authorization", {}).get("required"))
    if overlaps and not authorized:
        out.append(VEError(
            "E5", "authorization/required",
            f"Fereastra populației se întinde peste granița sigilată {sealed_first} "
            f"pentru sursa '{src}', dar autorizarea nu este declarată.",
            f"registrul de resurse sigilate: {src} sigilat de la {sealed_first} "
            f"({entry.get('sealed_rows')} bare); status registru: {sealed.get('status')}",
        ))
    return out
