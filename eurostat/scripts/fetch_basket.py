#!/usr/bin/env python3
"""Pull a curated basket of Greece-vs-EU Eurostat indicators (latest period).
Usage: python3 scripts/fetch_basket.py            # pull + print + save data/basket.json
       python3 scripts/fetch_basket.py describe <dataset>   # show dimensions
JSON-stat 2.0 parsing; each indicator is queried with all dims fixed except geo.
"""
import json
import sys
import urllib.parse
import urllib.request

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
GEOS = ["EL", "EU27_2020", "DE", "ES", "PT", "IT"]

# label, dataset, fixed dims (everything except geo + time)
BASKET = [
    ("Νέοι 25-34 που ζουν με γονείς (%)", "ilc_lvps08", {"sex": "T", "age": "Y25-34", "unit": "PC"}),
    ("Κατώτατος μισθός (€/μήνα)", "earn_mw_cur", {"currency": "EUR"}),
    ("Ανεργία (%)", "une_rt_a", {"sex": "T", "age": "Y15-74", "unit": "PC_ACT"}),
    ("Ανεργία νέων 15-24 (%)", "une_rt_a", {"sex": "T", "age": "Y15-24", "unit": "PC_ACT"}),
    ("Ποσοστό κινδύνου φτώχειας εν εργασία (%)", "ilc_iw01", {"sex": "T", "age": "Y18-64", "unit": "PC", "wstatus": "EMP"}),
    ("ΑΕΠ κατά κεφαλήν σε PPS (EU27=100)", "tec00114", {"indic_ppp": "VI_PPS_EU27_2020_HAB", "ppp_cat18": "GDP"}),
]


def fetch(dataset, params, geos=GEOS):
    q = {"format": "JSON", "lastTimePeriod": "1", **params}
    items = list(q.items()) + [("geo", g) for g in geos]
    url = f"{BASE}/{dataset}?{urllib.parse.urlencode(items)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.loads(r.read())
    gidx = d["dimension"]["geo"]["category"]["index"]      # geo -> position
    glab = d["dimension"]["geo"]["category"]["label"]
    tlab = list(d["dimension"]["time"]["category"]["label"].values())
    pos2geo = {v: k for k, v in gidx.items()}
    out = {}
    for k, val in d["value"].items():
        geo = pos2geo.get(int(k))
        if geo:
            out[geo] = (glab.get(geo, geo), val)
    return tlab[-1] if tlab else "?", out


def describe(dataset):
    url = f"{BASE}/{dataset}?format=JSON&lastTimePeriod=1&geo=EL"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    d = json.loads(urllib.request.urlopen(req, timeout=40).read())
    for dim in d["dimension"].get("id", d.get("id", [])):
        cats = d["dimension"][dim]["category"]["label"]
        print(f"{dim}: {list(cats.items())[:12]}")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "describe":
        describe(sys.argv[2]); return
    results = {}
    for label, ds, params in BASKET:
        try:
            period, vals = fetch(ds, params)
            el = vals.get("EL", (None, None))[1]
            eu = vals.get("EU27_2020", (None, None))[1]
            print(f"\n■ {label}  [{ds}, {period}]")
            for g in GEOS:
                if g in vals:
                    name, v = vals[g]
                    mark = " ←" if g == "EL" else ""
                    print(f"    {name:<28} {v}{mark}")
            results[label] = {"dataset": ds, "period": period,
                              "values": {g: vals[g][1] for g in vals}}
        except Exception as e:
            print(f"\n✗ {label} [{ds}] FAILED: {e}")
    import os
    os.makedirs("data", exist_ok=True)
    with open("data/basket.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n-> data/basket.json")


if __name__ == "__main__":
    main()
