"""Validation Engine — componenta executivă a validării statistice.

Faza implementată: F2 (validator de specificație + taxonomie de erori + cerere de
clarificare). NU sunt implementate: metode statistice, acces la date reale,
population builder, holdout loader, execuția protocoalelor.

Importul acestui pachet instalează garda de acces la date (audit hook la nivel de
proces). Garda este inactivă implicit; se activează doar în interiorul unui context
`access_audit.recording(...)`.
"""

from . import paths  # noqa: F401
from .audit import access_audit  # noqa: F401  (instalează hook-ul la import)

__version__ = "0.2.0-F2"
__phase__ = "F2"
