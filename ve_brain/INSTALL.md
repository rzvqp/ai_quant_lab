# ve_brain — INSTALARE · UPGRADE · ROLLBACK (gate 9)

Artefact versionat, instalabil de AI Trader FĂRĂ: copiere manuală de cod · importuri prin căi locale · acces de
scriere în repo-ul VE · reconstruirea detectoarelor · dependențe ascunse de branch-ul de dezvoltare.

## Instalare
```
python -m build ve_brain/            # produce dist/ve_brain-0.1.0-*.whl (sdist + wheel)
pip install dist/ve_brain-0.1.0-py3-none-any.whl
```
Verificare: `python -c "import ve_brain; print(ve_brain.build_info())"` — afișează versiunea, commit-ul sursă,
versiunea+statutul contractului de măsurare. Zero dependențe externe (stdlib-only).

## Compatibilitate controlată (eroare EXPLICITĂ)
Înainte de folosire, AI Trader declară contractele așteptate:
```
ve_brain.assert_compatible("ve.market_state.v1", "ve.decision.v1", "ve.strategy.v1")
```
Nepotrivire ⇒ `IncompatibleContractError` (nu comportament tăcut, nu default ascuns).

## Upgrade
`pip install --upgrade dist/ve_brain-<nouă>.whl`. Contractul de intrare/ieșire e versionat (`contract_id`); o versiune
nouă care schimbă schema BUMP-uiește `contract_id` și listele `SUPPORTED_*`. `CHANGELOG.md` declară compatibilitatea.
Rezultatele produse sub versiuni diferite au `configuration_fingerprint` diferit ⇒ NON-COMPARABLE (impus de `compare`).

## Rollback
`pip install --force-reinstall dist/ve_brain-<versiune-anterioară>.whl`. Fiecare versiune e un artefact imuabil,
identificat prin `SOURCE_COMMIT`; rollback = reinstalarea artefactului anterior. Nicio stare persistentă în pachet.

## Aceeași semantică în research / replay / shadow / live
O SINGURĂ implementare, un singur set de contracte (`SEMANTIC_MODES`). Modul nu schimbă formula; schimbă doar dacă
`BROKER_ORDER_SUBMISSION` e permis (mereu DISABLED în acest artefact — dreptul de analiză ≠ dreptul de execuție).
