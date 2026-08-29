"""session_tz.py — SESSION_TIMING_LIQUIDITY_DISCOVERY_V1 time governance (DST-correct native timezones -> causal UTC anchors).
Anchors (CEO): LONDON open = 08:00 Europe/London; US MACRO = 08:30 America/New_York; NYSE OPEN = 09:30 America/New_York; LBMA PM =
15:00 Europe/London. Each historical date's anchor is converted to a UTC epoch with correct DST via zoneinfo (tzdata present).
No hardcoded clock offsets. Returns per-date UTC-epoch anchors, recorded exactly."""
import datetime as _dt
from zoneinfo import ZoneInfo
NY=ZoneInfo("America/New_York"); LDN=ZoneInfo("Europe/London"); UTC=_dt.timezone.utc
def _utc_epoch(y,mo,d,hh,mm,tz):
    return int(_dt.datetime(y,mo,d,hh,mm,tzinfo=tz).astimezone(UTC).timestamp())
def anchors_for_date(dobj):
    """dobj = datetime.date. Returns dict of UTC epochs for the day's session anchors (DST-correct)."""
    y,mo,d=dobj.year,dobj.month,dobj.day
    return dict(
        london_open=_utc_epoch(y,mo,d,8,0,LDN),      # 08:00 Europe/London
        us_macro   =_utc_epoch(y,mo,d,8,30,NY),      # 08:30 America/New_York
        nyse_open  =_utc_epoch(y,mo,d,9,30,NY),      # 09:30 America/New_York
        lbma_pm    =_utc_epoch(y,mo,d,15,0,LDN),     # 15:00 Europe/London
    )
def build_anchor_maps(dates):
    """dates = iterable of datetime.date. Returns {anchor_name: {date: utc_epoch}}."""
    out={k:{} for k in ("london_open","us_macro","nyse_open","lbma_pm")}
    for d in set(dates):
        a=anchors_for_date(d)
        for k,v in a.items(): out[k][d]=v
    return out
if __name__=="__main__":
    for ds in ["2021-07-15","2021-01-15","2013-03-31","2013-10-27"]:
        y,m,d=map(int,ds.split("-")); a=anchors_for_date(_dt.date(y,m,d))
        f=lambda e:_dt.datetime.fromtimestamp(e,UTC).strftime("%H:%MZ")
        print(f"{ds}: London={f(a['london_open'])} US0830={f(a['us_macro'])} NYSE0930={f(a['nyse_open'])} LBMA_PM={f(a['lbma_pm'])}")
