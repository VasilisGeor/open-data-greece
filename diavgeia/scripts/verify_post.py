#!/usr/bin/env python3
"""Independent verification of all numbers quoted in the LinkedIn post."""
import json, glob, math
from collections import Counter

files = sorted(glob.glob("/Users/vasilisg/Documents/GitHub/open-data-greece/data/raw/d1_*.jsonl"))
print("files:", [f.split('/')[-1] for f in files])

total_decisions = 0
amounts = []          # all valid amounts 0 < a <= 50M (matching bunching.py filter)
per_month_under = {}
per_month_over = {}

for path in files:
    month = path.split("_")[-1].replace(".jsonl", "")
    n = 0
    u = o = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            n += 1
            d = json.loads(line)
            efv = d.get("extraFieldValues") or {}
            amt = efv.get("awardAmount")
            if isinstance(amt, dict):
                amt = amt.get("amount")
            if amt is not None and 0 < float(amt) <= 50_000_000:
                a = float(amt)
                amounts.append(a)
                if 29000 <= a <= 30000: u += 1
                if 30000 < a <= 31000: o += 1
    total_decisions += n
    per_month_under[month] = u
    per_month_over[month] = o

print(f"\nTOTAL decisions (all rows):        {total_decisions:,}")
print(f"TOTAL with structured amount:      {len(amounts):,}")

# (a) exactly 37200.00
exact_37200 = sum(1 for a in amounts if a == 37200.0)
# (b) band (37000, 37200]
band_37000_37200 = sum(1 for a in amounts if 37000 < a <= 37200)
# also closed-left [37000,37200] for sensitivity
band_37000_37200_cl = sum(1 for a in amounts if 37000 <= a <= 37200)
# (c) band (37200, 38000]
band_37200_38000 = sum(1 for a in amounts if 37200 < a <= 38000)
# (d) exactly 24800.00
exact_24800 = sum(1 for a in amounts if a == 24800.0)
# (e) overall ratio 29-30k vs 30-31k
under = sum(1 for a in amounts if 29000 <= a <= 30000)
over  = sum(1 for a in amounts if 30000 < a <= 31000)
exact_30000 = sum(1 for a in amounts if a == 30000.0)

print(f"\n(a) exactly 37200.00:              {exact_37200:,}   [post says 2.072]")
print(f"(b) band (37000,37200]:            {band_37000_37200:,}   [post says 3.469]")
print(f"    band [37000,37200] closed-L:   {band_37000_37200_cl:,}")
print(f"(c) band (37200,38000]:            {band_37200_38000:,}   [post says 64]")
print(f"(d) exactly 24800.00:              {exact_24800:,}   [post says 509]")
print(f"(e) 29-30k = {under:,}, 30-31k = {over:,}, ratio = {under/max(over,1):.2f}x   [post says 4-6x]")
print(f"    exactly 30000.00:              {exact_30000:,}   [README says 816]")

print("\nPer-month ratio (post claims 4-6x every month, no exception):")
mn = 99; mx = 0
for m in sorted(per_month_under):
    u = per_month_under[m]; o = per_month_over[m]
    r = u/max(o,1)
    mn = min(mn, r); mx = max(mx, r)
    print(f"  {m}: 29-30k={u:>4} 30-31k={o:>4} ratio={r:.2f}x")
print(f"  range across months: {mn:.2f}x – {mx:.2f}x   [README says 3.3x-6.0x]")

# cliff framing in README: 3469 vs 64 = 54x
print(f"\ncliff (37000-37200 vs 37200-38000): {band_37000_37200} / {band_37200_38000} = {band_37000_37200/max(band_37200_38000,1):.0f}x [README says 54x]")
