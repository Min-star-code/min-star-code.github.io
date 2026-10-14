"""Build the compact data files the project pages load.

Reads each project's own cleaned output (one folder up) and writes data/*.js.
Standard library only. Run from anywhere: python3 portfolio-site/build_data.py
"""

import csv
import json
import sqlite3
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
OUT = SITE / "data"


def write(name, payload):
    OUT.mkdir(exist_ok=True)
    text = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    (OUT / f"{name}.js").write_text(f"window.DATA={text};\n", encoding="utf-8")
    print(f"{name}.js  {len(text) / 1024:.0f} KB")


class Index:
    """Maps labels to small integers in a fixed or first-seen order."""

    def __init__(self, values=()):
        self.values = list(values)
        self.lookup = {v: i for i, v in enumerate(self.values)}

    def __call__(self, value):
        if value not in self.lookup:
            self.lookup[value] = len(self.values)
            self.values.append(value)
        return self.lookup[value]


def ontario():
    rows = list(csv.DictReader(open(ROOT / "ontario-infrastructure-analysis/data/projects_clean.csv", encoding="utf-8")))
    cat = Index(["Transit", "Health care", "Education", "Communities", "Roads and bridges", "Child care", "Recreation"])
    reg = Index(["Central", "Southwest", "East", "Northeast", "Northwest", "Province-wide / not assigned"])
    sta = Index(["Complete", "Under construction", "Planning", "Not reported"])
    d = {k: [] for k in ("cat", "reg", "sta", "yr", "bud", "lat", "lon")}
    for r in rows:
        d["cat"].append(cat(r["category"]))
        d["reg"].append(reg(r["region"]))
        d["sta"].append(sta(r["status"]))
        d["yr"].append(int(r["completion_year"]) if r["completion_year"] else 0)
        d["bud"].append(round(float(r["budget"]) / 1e6, 3) if r["budget"] else None)
        has_point = r["latitude"] and r["longitude"]
        d["lat"].append(round(float(r["latitude"]), 3) if has_point else None)
        d["lon"].append(round(float(r["longitude"]), 3) if has_point else None)
    assert len(rows) == 5935
    assert sum(b is not None for b in d["bud"]) == 3930
    assert abs(sum(b or 0 for b in d["bud"]) - 163842.87) < 1
    assert sum(v is not None for v in d["lat"]) == 5518
    write("ontario", {"n": len(rows), "cats": cat.values, "regs": reg.values, "stas": sta.values, **d})


def outbreaks():
    rows = list(csv.DictReader(open(ROOT / "toronto-outbreak-data-quality/data/outbreaks_clean.csv", encoding="utf-8")))
    setting = Index(["LTCH", "Retirement Home", "Hospital-Acute Care", "Hospital-Chronic Care", "Hospital-Psychiatric", "Transitional Care", "Shelter"])
    kind = Index(["Respiratory", "Enteric", "Other"])
    agent = Index()
    d = {k: [] for k in ("yr", "set", "typ", "agt", "mon", "dur")}
    for r in rows:
        d["yr"].append(int(r["source_year"]))
        d["set"].append(setting(r["setting"]))
        d["typ"].append(kind(r["outbreak_type"]))
        d["agt"].append(agent(r["agent_group"]))
        d["mon"].append(int(r["date_began"][5:7]))
        d["dur"].append(int(r["duration_days"]) if r["duration_days"] else None)
    assert len(rows) == 7029 and len(agent.values) == 13
    write("outbreaks", {"n": len(rows), "settings": setting.values, "types": kind.values, "agents": agent.values, **d})


def _canonical_line(raw):
    # Same rules as ttc-subway-delay-analysis/ttc_analysis.py
    compact = raw.strip().upper().replace(" ", "")
    if not compact:
        return "Unknown"
    if "/" in compact or compact.startswith("YU-BD"):
        return "Multiple lines"
    if compact in {"YU", "YUS", "LINE1"}:
        return "Line 1 (YU)"
    if compact == "BD" or compact.startswith("LINE2-"):
        return "Line 2 (BD)"
    if compact == "SHP":
        return "Line 4 (SHP)"
    return "Other / unclassified"


def _clean_description(raw):
    text = raw.strip()
    if "â" in text:
        try:
            text = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return text.replace("–", " - ").replace("—", " - ").replace("“", '"').replace("”", '"').replace("  ", " ")


def ttc():
    base = ROOT / "ttc-subway-delay-analysis/data"
    codes = {}
    for r in csv.DictReader(open(base / "code_descriptions.csv", encoding="utf-8")):
        code = (r["CODE"] or "").strip().upper()
        if code:
            codes[code] = _clean_description(r["DESCRIPTION"] or "")
    line = Index(["Line 1 (YU)", "Line 2 (BD)", "Line 4 (SHP)", "Multiple lines", "Unknown", "Other / unclassified"])
    cause = Index()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    d = {k: [] for k in ("mon", "day", "hr", "line", "cause", "min")}
    for r in csv.DictReader(open(base / "ttc_subway_delays_2025.csv", encoding="utf-8")):
        code = r["Code"].strip().upper()
        d["mon"].append(int(r["Date"][5:7]))
        d["day"].append(days.index(r["Day"].strip()))
        d["hr"].append(int(r["Time"].strip()[:2]))
        d["line"].append(line(_canonical_line(r["Line"] or "")))
        d["cause"].append(cause(codes.get(code) or f"Unmapped ({code or 'blank'})"))
        d["min"].append(int(r["Min Delay"]))
    n = len(d["min"])
    assert n == 25737 and sum(d["min"]) == 70768 and d["min"].count(0) == 16642
    by_line = [0] * len(line.values)
    for i in range(n):
        by_line[d["line"][i]] += d["min"][i]
    assert by_line[:3] == [40232, 27404, 3115]
    assert sum(c.startswith("Unmapped") for c in (cause.values[i] for i in d["cause"])) == 145
    write("ttc", {"n": n, "lines": line.values, "causes": cause.values, "days": days, **d})


def adventureworks():
    db = sqlite3.connect(ROOT / "adventureworks-sales-analysis/database/adventureworks.db")
    query = """
      SELECT month_start, sales_channel, category_name, territory_name,
        CASE WHEN discount_rate = 0 THEN 'No discount' WHEN discount_rate <= 0.05 THEN '0-5%'
             WHEN discount_rate <= 0.10 THEN '5-10%' WHEN discount_rate <= 0.20 THEN '10-20%' ELSE '20%+' END,
        SUM(revenue), SUM(estimated_gross_profit), SUM(order_qty), COUNT(*)
      FROM v_sales_line GROUP BY 1, 2, 3, 4, 5 ORDER BY 1"""
    month, chan = Index(), Index(["Reseller", "Online"])
    cat = Index(["Bikes", "Components", "Clothing", "Accessories"])
    terr = Index()
    band = Index(["No discount", "0-5%", "5-10%", "10-20%", "20%+"])
    d = {k: [] for k in ("mon", "ch", "cat", "terr", "band", "rev", "gp", "units")}
    lines = 0
    for m, c, k, t, b, rev, gp, units, n in db.execute(query):
        d["mon"].append(month(m[:7]))
        d["ch"].append(chan(c))
        d["cat"].append(cat(k))
        d["terr"].append(terr(t))
        d["band"].append(band(b))
        d["rev"].append(round(rev, 2))
        d["gp"].append(round(gp, 2))
        d["units"].append(units)
        lines += n
    assert lines == 121317
    assert abs(sum(d["rev"]) - 109846381.40) < 5 and abs(sum(d["gp"]) - 12557780.60) < 5
    write("adventureworks", {"n": len(d["rev"]), "months": month.values, "chans": chan.values, "cats": cat.values,
                             "terrs": terr.values, "bands": band.values, **d})


if __name__ == "__main__":
    ontario()
    outbreaks()
    ttc()
    adventureworks()
