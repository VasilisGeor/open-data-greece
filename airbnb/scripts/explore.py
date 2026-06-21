#!/usr/bin/env python3
"""Explore InsideAirbnb detailed listings for Greek areas — find the strongest finding.

Usage: python3 scripts/airbnb_explore.py data/raw/athens.csv.gz
"""
import csv
import gzip
import statistics
import sys
from collections import Counter


def load(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(s):
    if not s:
        return None
    s = str(s).replace("$", "").replace(",", "").replace("€", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def main(path):
    rows = load(path)
    n = len(rows)
    area = path.split("/")[-1].replace(".csv.gz", "")
    print(f"\n{'='*60}\n{area.upper()} — {n:,} listings (πραγματικά records)\n{'='*60}")

    # Room type
    rt = Counter(r.get("room_type", "") for r in rows)
    entire = rt.get("Entire home/apt", 0)
    print(f"Ολόκληρα σπίτια: {entire:,} ({100*entire//n}%) | δωμάτια: {n-entire:,}")

    # Host concentration via calculated_host_listings_count (per-listing, robust)
    host = Counter(r.get("host_id", "") for r in rows)
    n_hosts = len(host)
    multi5 = [h for h, c in host.items() if c >= 5]
    multi10 = [h for h, c in host.items() if c >= 10]
    l_by_5 = sum(c for h, c in host.items() if c >= 5)
    l_by_10 = sum(c for h, c in host.items() if c >= 10)
    print(f"\nHosts: {n_hosts:,}")
    print(f"  5+ listings: {len(multi5)} hosts ({100*len(multi5)//n_hosts}%) → {l_by_5:,} listings ({100*l_by_5//n}%)")
    print(f"  10+ listings: {len(multi10)} hosts → {l_by_10:,} listings ({100*l_by_10//n}%)")
    print(f"  Top host: {host.most_common(1)[0][1]} listings")

    # Availability: de-facto full-time tourist rentals
    av = [num(r.get("availability_365")) for r in rows]
    av = [a for a in av if a is not None]
    if av:
        ge300 = sum(1 for a in av if a >= 300)
        ge180 = sum(1 for a in av if a >= 180)
        print(f"\nΔιαθεσιμότητα/365: διάμεσος {statistics.median(av):.0f} μέρες")
        print(f"  ≥300 μέρες (ντε φάκτο ξενοδοχεία): {ge300:,} ({100*ge300//len(av)}%)")
        print(f"  ≥180 μέρες: {ge180:,} ({100*ge180//len(av)}%)")

    # License presence
    lic = [r.get("license", "").strip() for r in rows]
    has_lic = sum(1 for l in lic if l and l.lower() not in ("", "exempt", "none"))
    print(f"\nΜε αριθμό μητρώου (license): {has_lic:,} ({100*has_lic//n}%) | χωρίς: {n-has_lic:,} ({100*(n-has_lic)//n}%)")

    # Price
    prices = [num(r.get("price")) for r in rows]
    prices = [p for p in prices if p and 0 < p < 100000]
    if prices:
        prices.sort()
        med = prices[len(prices)//2]
        print(f"\nΤιμή/βράδυ: διάμεσος €{med:.0f} | p25 €{prices[len(prices)//4]:.0f} | p75 €{prices[3*len(prices)//4]:.0f}")
        print(f"  Μηνιαίο ισοδύναμο (διάμεσος×30): €{med*30:,.0f}")

    # Top neighbourhoods
    nb = Counter(r.get("neighbourhood_cleansed", "") for r in rows)
    print("\nTop 6 περιοχές:")
    for k, v in nb.most_common(6):
        print(f"  {k}: {v:,} ({100*v//n}%)")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
