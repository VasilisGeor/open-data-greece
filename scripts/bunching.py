#!/usr/bin/env python3
"""Cross-month threshold-bunching analysis + post chart.

Usage: python3 bunching.py data/raw/d1_2026-03.jsonl data/raw/d1_2026-04.jsonl data/raw/d1_2026-05.jsonl
"""
import json
import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

MAGIC = {24800.0: "20.000 + ΦΠΑ", 29760.0: "24.000 + ΦΠΑ", 30000.0: "30.000 ακριβώς"}


def load_amounts(path):
    amounts = []
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            n += 1
            d = json.loads(line)
            efv = d.get("extraFieldValues") or {}
            amt = efv.get("awardAmount")
            if isinstance(amt, dict):
                amt = amt.get("amount")
            if amt and 0 < float(amt) <= 50_000_000:
                amounts.append(float(amt))
    return n, amounts


def stats(amounts):
    under = sum(1 for a in amounts if 29000 <= a <= 30000)
    over = sum(1 for a in amounts if 30000 < a <= 31000)
    clean_eur = sum(a for a in amounts if a <= 60000)
    magic = {v: sum(1 for a in amounts if a == v) for v in MAGIC}
    return under, over, clean_eur, magic


def main(paths):
    all_amounts = []
    print(f"{'month':<10}{'decisions':>10}{'w/amount':>10}{'29-30k':>8}{'30-31k':>8}{'ratio':>7}{'≤60k €M':>9}"
          f"{'@24.8k':>8}{'@29.76k':>9}{'@30k':>7}")
    for path in paths:
        month = path.split("_")[-1].replace(".jsonl", "")
        n, amounts = load_amounts(path)
        under, over, clean_eur, magic = stats(amounts)
        print(f"{month:<10}{n:>10}{len(amounts):>10}{under:>8}{over:>8}{under/max(over,1):>7.1f}"
              f"{clean_eur/1e6:>9.1f}{magic[24800.0]:>8}{magic[29760.0]:>9}{magic[30000.0]:>7}")
        all_amounts += amounts

    under, over, clean_eur, magic = stats(all_amounts)
    print(f"{'TOTAL':<10}{'':>10}{len(all_amounts):>10}{under:>8}{over:>8}{under/max(over,1):>7.1f}"
          f"{clean_eur/1e6:>9.1f}{magic[24800.0]:>8}{magic[29760.0]:>9}{magic[30000.0]:>7}")

    # ---- Chart: 25k-38.5k window catches both the net (30k) and gross (37.2k) spikes ----
    LO, HI, W = 25000, 38500, 500
    nb = (HI - LO) // W
    bins = Counter()
    for a in all_amounts:
        if LO <= a < HI:
            bins[int((a - LO) // W)] += 1
    xs = [LO + b * W for b in range(nb)]
    ys = [bins[b] for b in range(nb)]

    def color(x):
        if x in (29500, 37000):
            return "#d62728"          # the two bunching spikes (net / gross)
        if x == 29000:
            return "#f5a623"
        if x == 30000:
            return "#5b7a99"          # exactly-€30,000 cluster
        return "#9bb0c1"

    colors = [color(x) for x in xs]
    n_exact_30k = sum(1 for a in all_amounts if a == 30000.0)
    n_exact_372 = sum(1 for a in all_amounts if a == 37200.0)
    ymax = max(ys)

    fig, ax = plt.subplots(figsize=(12.8, 6.75), dpi=160)
    ax.bar([x + W / 2 for x in xs], ys, width=W - 40, color=colors, zorder=3)
    ax.axvline(30000, color="#1a1a2e", lw=2, ls="--", zorder=4)
    ax.axvline(37200, color="#1a1a2e", lw=2, ls=":", zorder=4)
    ax.annotate("Όριο €30.000\n(προ ΦΠΑ)", xy=(30000, ymax * 0.62),
                xytext=(30900, ymax * 0.70), fontsize=11.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", lw=1.4))
    ax.annotate("€30.000 + 24% ΦΠΑ\n= €37.200", xy=(37200, ymax * 0.97),
                xytext=(33300, ymax * 0.90), fontsize=11.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", lw=1.4))
    i_375 = xs.index(37000)
    ax.annotate(f"{ys[i_375]} αναθέσεις στα €37.000–37.499\n— οι {n_exact_372} ακριβώς €37.200,00",
                xy=(37250, ys[i_375]), xytext=(31300, ymax * 1.0), fontsize=11.5,
                color="#d62728", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5))
    i_295 = xs.index(29500)
    ax.annotate(f"{ys[i_295]} αναθέσεις\nστα €29.500–29.999", xy=(29750, ys[i_295]),
                xytext=(25400, ymax * 0.62), fontsize=11.5, color="#d62728", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.5))
    i_300 = xs.index(30000)
    ax.annotate(f"εκ των οποίων {n_exact_30k}\nακριβώς €30.000,00", xy=(30250, ys[i_300]),
                xytext=(25400, ymax * 0.40), fontsize=10, color="#5b7a99",
                arrowprops=dict(arrowstyle="->", color="#5b7a99", lw=1.2))
    ax.set_title("Το ίδιο όριο, δύο φορές: απευθείας αναθέσεις κάτω από τα €30.000 — με και χωρίς ΦΠΑ",
                 fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("Ποσό ανάθεσης (€)", fontsize=12)
    ax.set_ylabel("Αριθμός αναθέσεων", fontsize=12)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{int(v/1000)}k"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    months = len(paths)
    fig.text(0.99, 0.01, f"Πηγή: Διαύγεια (open data API) · {months} μήνες · {len(all_amounts):,} αποφάσεις Δ.1 με ποσό",
             ha="right", fontsize=9, color="#666")
    fig.tight_layout()
    out = "output/bunching_30k.png"
    import os
    os.makedirs("output", exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    print(f"\nchart -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
