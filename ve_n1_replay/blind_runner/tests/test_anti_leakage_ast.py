"""Teste STRUCTURALE (AST, nu convenție) -- mandat §4 + §11 item 6: demonstrează prin parsare de
sursă, nu prin citire de cod, că:
  - inference NU importă scoring sau labels;
  - scoring NU importă detectorul;
  - nu există funcție comună care permite rularea detectorului DUPĂ citirea etichetelor.
"""
from __future__ import annotations

import ast
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent.parent

DETECTOR_MODULE_NAMES = {
    "range_semantic_v4_3", "range_engine_v4_3",
    "ve_n1_replay.range_semantic_v4_3", "ve_n1_replay.range_engine_v4_3",
}
LABEL_RELATED_MODULE_NAMES = {"scoring", "labels", "level_mapping", "parse_windows"}
SCORING_MODULE_NAMES = {"scoring"}


def _imported_module_names(path: Path) -> set[str]:
    """Toate numele de module importate (`import X`, `from X import ...`, `from .X import ...`) --
    normalizate la ultimul segment (`ve_n1_replay.range_semantic_v4_3` -> și `range_semantic_v4_3`
    verificate) ca să prindă și importuri relative echivalente."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
                names.add(alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
                names.add(node.module.split(".")[-1])
    return names


def test_inference_does_not_import_scoring() -> None:
    imports = _imported_module_names(_PKG_DIR / "inference.py")
    leaked = imports & SCORING_MODULE_NAMES
    assert not leaked, f"inference.py importă module de scoring: {leaked}"


def test_inference_does_not_import_labels_or_mapping() -> None:
    imports = _imported_module_names(_PKG_DIR / "inference.py")
    leaked = imports & LABEL_RELATED_MODULE_NAMES
    assert not leaked, f"inference.py importă module legate de etichete/mapping: {leaked}"


def _non_docstring_string_constants(tree: ast.AST) -> list[str]:
    """Toate literalele string, EXCLUZÂND docstring-urile (primul `Expr` string dintr-un body de
    modul/funcție/clasă -- text explicativ, nu o valoare folosită la rulare) -- ca să nu confunde
    o PROPOZIȚIE care documentează o interdicție ("nu accesează PnL") cu o valoare REALĂ folosită
    (un nume de fișier, o cheie de dict) care ar sugera acces efectiv."""
    docstring_nodes: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                docstring_nodes.add(id(body[0].value))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstring_nodes:
            out.append(node.value)
    return out


def test_inference_source_has_no_label_or_pnl_or_mapping_string_literals() -> None:
    """Verificare suplimentară, la nivel de literal de sursă (nu doar import) -- niciun literal
    string FOLOSIT LA RULARE (exclus docstring-urile explicative) care ar sugera citirea directă a
    unui fișier de etichete/mapping/PnL, ocolind importul."""
    tree = ast.parse((_PKG_DIR / "inference.py").read_text(encoding="utf-8"))
    forbidden_substrings = ("LEVEL_MAPPING", "LOCKED_LABELS", "PROVISIONAL_LABELS", "CORRECTION_ADDENDUM", "pnl", "PnL")
    for value in _non_docstring_string_constants(tree):
        for f in forbidden_substrings:
            assert f not in value, f"literal suspect (non-docstring) în inference.py: {value!r} conține {f!r}"


def test_scoring_does_not_import_detector() -> None:
    imports = _imported_module_names(_PKG_DIR / "scoring.py")
    leaked = imports & DETECTOR_MODULE_NAMES
    assert not leaked, f"scoring.py importă module ale detectorului: {leaked}"


def test_scoring_does_not_import_inference() -> None:
    """Scorerul nu poate re-rula inference-ul -- verificat structural: niciun import al modulului
    `inference` (care ar da acces indirect la detector + la re-rulare)."""
    imports = _imported_module_names(_PKG_DIR / "scoring.py")
    assert "inference" not in imports, "scoring.py importă inference.py -- ar putea re-rula detectorul"


def test_no_module_in_package_imports_both_detector_and_labels() -> None:
    """Nicio funcție/modul comun nu poate rula detectorul DUPĂ ce a citit etichete -- verificat
    structural: pt. fiecare fișier .py din acest pachet (exclusiv teste), setul de module importate
    nu conține SIMULTAN un modul al detectorului ȘI un modul legat de etichete."""
    label_ish = LABEL_RELATED_MODULE_NAMES | {"construction_reproduction", "parse_windows"}
    for py_file in _PKG_DIR.glob("*.py"):
        imports = _imported_module_names(py_file)
        has_detector = bool(imports & DETECTOR_MODULE_NAMES)
        has_labels = bool(imports & label_ish)
        assert not (has_detector and has_labels), (
            f"{py_file.name} importă ATÂT detectorul CÂT ȘI module legate de etichete -- "
            f"ar permite rularea detectorului după citirea etichetelor în același loc"
        )


def test_scoring_has_no_detector_construction_calls() -> None:
    """Verificare suplimentară, la nivel de apel de funcție (nu doar import) -- niciun apel la
    numele claselor detectorului, chiar dacă ar fi importate dinamic (`importlib`) ocolind
    verificarea de import static."""
    tree = ast.parse((_PKG_DIR / "scoring.py").read_text(encoding="utf-8"))
    forbidden_calls = {"RangeSemanticProducerV43", "RangeSemanticEngineV43", "ConfigV43", "importlib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            assert node.id not in forbidden_calls, f"scoring.py referențiază {node.id!r}"
        if isinstance(node, ast.Attribute):
            assert node.attr not in forbidden_calls, f"scoring.py referențiază atributul {node.attr!r}"
