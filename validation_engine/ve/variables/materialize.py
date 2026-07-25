"""Materializarea variabilelor pe barele sursei de populație (F4).

Fiecare variabilă declarată devine o coloană pandas aliniată la barele sursei de
populație. Cross-source (ex. PDH din D1) se mapează prin ultima bară a zilei
completate anterioare. NICIO statistică, niciun test — doar valori.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..data import calendar
from ..data.sources import Series


class VariableError(RuntimeError):
    """Primitivă de variabilă neimplementată sau parametri incompatibili la runtime."""


def series_to_frame(s: Series) -> pd.DataFrame:
    df = pd.DataFrame({
        "time": s.time, "open": s.open, "high": s.high,
        "low": s.low, "close": s.close, "volume": s.volume,
    })
    df["day"] = (df["time"] // calendar.SECONDS_PER_DAY).astype("int64")
    return df


def _prior_day_extreme(base: pd.DataFrame, src: pd.DataFrame, which: str, periods_back: int) -> pd.Series:
    """Extrema zilei UTC anterioare (periods_back zile în urmă), din sursa dată,
    grupată pe zi calendaristică UTC — identic cu `add_prior_day` din scripturile in-sample.
    """
    daily = src.groupby("day").agg(hi=("high", "max"), lo=("low", "min")).reset_index()
    daily["pd"] = daily["hi" if which == "high" else "lo"].shift(periods_back)
    m = daily.set_index("day")["pd"]
    return base["day"].map(m)


def materialize(
    variables: list[dict],
    base: pd.DataFrame,
    aux_frames: dict,
    base_source_id: str = "",
) -> tuple[dict, dict]:
    """Întoarce (valori: {var_id: pd.Series}, rezumat: {var_id: {...}}). Fără statistici."""
    values: dict[str, pd.Series] = {}
    summary: dict[str, dict] = {}
    n = len(base)

    for var in variables:
        vid = var["id"]
        prim = var["primitive"]
        p = var.get("params", {})
        col: pd.Series

        if prim == "raw_series@v1":
            col = base[p["field"]].astype(float)
        elif prim == "prior_period_extreme@v1":
            # sursa poate fi baza însăși (PDH = max high al zilei UTC anterioare din H1,
            # ca în add_prior_day) sau o sursă auxiliară.
            src = base if p["source_id"] == base_source_id else aux_frames.get(p["source_id"])
            if src is None:
                raise VariableError(f"{vid}: sursa {p['source_id']} nu e încărcată")
            col = _prior_day_extreme(base, src, p["extreme"], int(p.get("periods_back", 1)))
        elif prim == "session_label@v1":
            col = base["time"].map(lambda t: calendar.session_of(int(t), p["boundaries"]))
        elif prim == "forward_return@v1":
            k = int(p["horizon_bars"])
            c = base["close"].to_numpy()
            fwd = np.full(n, np.nan)
            if n > k:
                fwd[:-k] = c[k:] - c[:-k]
            col = pd.Series(fwd, index=base.index)
        elif prim == "baseline_forward_mean@v1":
            k = int(p["horizon_bars"])
            c = base["close"].to_numpy()
            fwd = np.full(n, np.nan)
            if n > k:
                fwd[:-k] = c[k:] - c[:-k]
            fwd_s = pd.Series(fwd, index=base.index)
            strata = p.get("strata", [])
            if strata and strata[0] in values:
                grp = values[strata[0]]
                col = fwd_s.groupby(grp).transform("mean")
            else:
                col = pd.Series(np.full(n, np.nanmean(fwd)), index=base.index)
        elif prim == "forward_excess@v1":
            fr = values.get(p["forward_return_ref"])
            bl = values.get(p["baseline_ref"])
            if fr is None or bl is None:
                raise VariableError(f"{vid}: referințe forward_excess nematerializate")
            col = fr - bl
        elif prim == "volume_zscore@v1":
            w = int(p["window"])
            vol = base["volume"]
            mean = vol.rolling(w, min_periods=int(p["min_periods"])).mean()
            std = vol.rolling(w, min_periods=int(p["min_periods"])).std(ddof=0)
            col = (vol - mean) / std.replace(0, np.nan)
        elif prim == "indicator@v1":
            # materializat de builder (are nevoie de evaluatorul de predicate); marcaj
            col = pd.Series(np.full(n, np.nan), index=base.index)
            summary[vid] = {"primitive": prim, "note": "indicator materializat în builder"}
            values[vid] = col
            continue
        else:
            raise VariableError(f"{vid}: primitivă nematerializabilă în F4: {prim}")

        values[vid] = col
        finite = int(col.notna().sum()) if col.dtype.kind in "fc" else int(col.notna().sum())
        summary[vid] = {
            "primitive": prim, "role": var.get("role"),
            "materialized": finite, "total_bars": n,
        }

    return values, summary
