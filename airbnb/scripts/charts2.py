#!/usr/bin/env python3
"""Charts for growth + prices posts.
Usage: python3 scripts/airbnb_charts2.py
Outputs: output/growth.png, output/prices.png
"""
import csv
import gzip
import os
from collections import Counter, defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAPER, INK, RED, BLUE, GREEN, GRAY, MUTED = "#F7F4EE", "#1B1B2F", "#D7263D", "#3B6FB0", "#2E8B57", "#C7CDD4", "#6E6E76"


def num(s):
    try:
        return float(str(s).replace("$", "").replace(",", "").strip())
    except ValueError:
        return None


def growth():
    yr = Counter()
    with gzip.open("data/raw/athens_reviews.csv.gz", "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            d = row.get("date", "")
            if len(d) >= 4 and d[:4].isdigit():
                yr[int(d[:4])] += 1
    years = list(range(2015, 2026))
    vals = [yr.get(y, 0) for y in years]
    peak2019 = yr.get(2019, 0)

    def color(y):
        if y in (2020, 2021):
            return RED
        if y >= 2022:
            return GREEN
        return BLUE
    cols = [color(y) for y in years]
    fig, ax = plt.subplots(figsize=(11, 7), dpi=160)
    bars = ax.bar([str(y) for y in years], vals, color=cols, zorder=3)
    bars[-1].set_hatch("////"); bars[-1].set_edgecolor("white")
    ax.axhline(peak2019, color=INK, lw=1.6, ls="--", zorder=4)
    ax.annotate(f"peak 2019: {peak2019:,}".replace(",", "."), xy=(0.2, peak2019),
                xytext=(0.2, peak2019 + 9000), fontsize=11, fontweight="bold", color=INK)
    ax.annotate("+148% vs 2019", xy=(9, vals[9]), xytext=(6.0, vals[9] + 4000),
                fontsize=13, fontweight="bold", color=GREEN,
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.6))
    for i, v in enumerate(vals):
        ax.text(i, v + 2500, f"{v:,}".replace(",", "."), ha="center", fontsize=9, color=MUTED)
    ax.set_title("Η έκρηξη του Airbnb στην Αθήνα, 2015–2025",
                 fontsize=17, fontweight="bold", loc="left", color=INK, pad=42)
    ax.text(0, 1.045, "Reviews ανά έτος (proxy κρατήσεων) · μπλε=ανάπτυξη · κόκκινο=COVID · πράσινο=ρεκόρ",
            transform=ax.transAxes, fontsize=11, color="#444")
    ax.set_ylabel("reviews / έτος", fontsize=11, color=MUTED)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    fig.text(0.99, 0.01, "*2025: μέχρι 26/9 (μερικό έτος) · Πηγή: InsideAirbnb, snapshot Σεπ 2025 · 874.286 reviews",
             ha="right", fontsize=9, color=MUTED)
    fig.patch.set_facecolor(PAPER); ax.set_facecolor(PAPER)
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    fig.savefig("output/growth.png", facecolor=PAPER, bbox_inches="tight")
    print(f"growth: 2019={peak2019}, 2024={vals[9]}, 2025*={vals[10]} -> output/growth.png")


def prices():
    with gzip.open("data/raw/athens.csv.gz", "rt", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_nb = defaultdict(list)
    allp = []
    for r in rows:
        p = num(r.get("price"))
        if p and 0 < p < 100000:
            allp.append(p)
            by_nb[r.get("neighbourhood_cleansed", "")].append(p)
    allp.sort()
    city_med = allp[len(allp) // 2]
    med = {k: sorted(v)[len(v) // 2] for k, v in by_nb.items() if len(v) >= 30}
    ranked = sorted(med.items(), key=lambda x: -x[1])
    top = ranked[:6]
    bot = ranked[-4:]
    sel = top + bot
    labels = [k.split("-")[0].title() for k, _ in sel]
    vals = [v for _, v in sel]
    colors = [RED] * len(top) + [GRAY] * len(bot)

    # cross-city medians
    cities = {"Αθήνα": "athens", "Θεσσαλονίκη": "thessaloniki", "Κρήτη": "crete", "Νότιο Αιγαίο": "south-aegean"}
    cmed = {}
    for name, fn in cities.items():
        ps = []
        with gzip.open(f"data/raw/{fn}.csv.gz", "rt", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                p = num(r.get("price"))
                if p and 0 < p < 100000:
                    ps.append(p)
        ps.sort(); cmed[name] = ps[len(ps) // 2]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 7), dpi=160, gridspec_kw={"width_ratios": [1.5, 1]})
    y = range(len(sel))
    a1.barh(list(y), vals, color=colors, zorder=3)
    a1.axvline(city_med, color=INK, lw=1.6, ls="--", zorder=4)
    a1.annotate(f"διάμεσος πόλης €{city_med:.0f}", xy=(city_med, len(sel) - 0.5),
                xytext=(city_med + 4, len(sel) - 0.6), fontsize=10.5, fontweight="bold", color=INK)
    a1.set_yticks(list(y)); a1.set_yticklabels(labels, fontsize=11)
    a1.invert_yaxis()
    for i, v in enumerate(vals):
        a1.text(v + 2, i, f"€{v:.0f}", va="center", fontsize=10, fontweight="bold")
    a1.set_title("Ακριβότερες vs φθηνότερες γειτονιές", fontsize=14, fontweight="bold", loc="left", color=INK)
    a1.set_xlabel("διάμεση τιμή/νύχτα (€)", fontsize=10, color=MUTED)
    a1.spines[["top", "right"]].set_visible(False); a1.grid(axis="x", alpha=0.3, zorder=0)

    cnames = list(cmed.keys()); cvals = list(cmed.values())
    ccolors = [RED if n == "Αθήνα" else GRAY for n in cnames]
    a2.bar(cnames, cvals, color=ccolors, zorder=3)
    for i, v in enumerate(cvals):
        a2.text(i, v + 2, f"€{v:.0f}", ha="center", fontsize=11, fontweight="bold")
    a2.set_title("Αθήνα vs υπόλοιπη Ελλάδα", fontsize=14, fontweight="bold", loc="left", color=INK)
    a2.set_ylabel("διάμεση τιμή/νύχτα (€)", fontsize=10, color=MUTED)
    a2.tick_params(axis="x", labelrotation=20, labelsize=10)
    a2.spines[["top", "right"]].set_visible(False); a2.grid(axis="y", alpha=0.3, zorder=0)

    fig.suptitle("Η γεωγραφία της τιμής στο Airbnb της Αθήνας", fontsize=17, fontweight="bold", x=0.02, ha="left")
    fig.text(0.99, 0.01, "Πηγή: InsideAirbnb (Σεπ 2025) · διάμεσες τιμές, γειτονιές n≥30 · €",
             ha="right", fontsize=9, color=MUTED)
    for ax in (a1, a2):
        ax.set_facecolor(PAPER)
    fig.patch.set_facecolor(PAPER)
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])
    fig.savefig("output/prices.png", facecolor=PAPER, bbox_inches="tight")
    print(f"prices: city_med €{city_med:.0f}, cross-city {cmed} -> output/prices.png")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    growth()
    prices()
