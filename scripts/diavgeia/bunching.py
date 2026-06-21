#!/usr/bin/env python3
"""Cross-month threshold-bunching analysis + post chart.

Usage: python3 bunching.py data/raw/d1_2026-03.jsonl data/raw/d1_2026-04.jsonl data/raw/d1_2026-05.jsonl
"""
import json
import math
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

    # ---- Chart: two panels, one per recording convention (net vs gross) ----
    W = 500
    GRAY, RED, DARK = "#b8c4cf", "#d62728", "#1a1a2e"
    n_exact_372 = sum(1 for a in all_amounts if a == 37200.0)
    ratio_str = f"{under / max(over, 1):.1f}".replace(".", ",")
    n_band372 = sum(1 for a in all_amounts if 37000 <= a <= 37200)
    n_after372 = sum(1 for a in all_amounts if 37200 < a <= 38000)

    def histo(ax, lo, hi, w, red_bins, vline):
        nb = (hi - lo) // w
        bins = Counter()
        for a in all_amounts:
            if lo < a <= hi:                      # right-inclusive: (lo, lo+w]
                bins[math.ceil((a - lo) / w) - 1] += 1
        xs = [lo + b * w for b in range(nb)]
        ys = [bins[b] for b in range(nb)]
        colors = [RED if x in red_bins else GRAY for x in xs]
        ax.bar([x + w / 2 for x in xs], ys, width=w - 50, color=colors, zorder=3)
        ax.axvline(vline, color=DARK, lw=2.2, ls="--", zorder=4)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"€{v/1000:g}k"))
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3, zorder=0)
        ax.set_ylabel("αναθέσεις", fontsize=11)
        return xs, ys

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 11), dpi=160)

    # Panel 1: net-recorded amounts bunch under €30,000
    xs, ys = histo(ax1, 27000, 33000, 500, {29000, 29500}, 30000)
    top = max(ys)
    ax1.set_title("1. Όσοι καταχωρούν την ΚΑΘΑΡΗ αξία (χωρίς ΦΠΑ)",
                  fontsize=13.5, fontweight="bold", loc="left", pad=10)
    ax1.annotate("όριο €30.000", xy=(30000, top * 0.78), xytext=(30450, top * 0.86),
                 fontsize=11.5, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", lw=1.4))
    ax1.annotate(f"{ratio_str}× περισσότερες αναθέσεις\nακριβώς κάτω από το όριο",
                 xy=(29600, ys[xs.index(29500)] * 0.97), xytext=(27200, top * 0.72),
                 fontsize=11.5, color=RED, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))

    # Panel 2: gross-recorded amounts bunch under €37,200 (= €30,000 + 24% VAT)
    xs, ys = histo(ax2, 34000, 40000, 400, {36400, 36800}, 37200)
    top = max(ys)
    ax2.set_title("2. Όσοι καταχωρούν την αξία ΜΕ ΦΠΑ — το ίδιο όριο, μεταφρασμένο",
                  fontsize=13.5, fontweight="bold", loc="left", pad=10)
    ax2.annotate("€30.000 + 24% ΦΠΑ\n= €37.200", xy=(37200, top * 0.80), xytext=(37650, top * 0.84),
                 fontsize=11.5, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", lw=1.4))
    e372 = f"{n_exact_372:,}".replace(",", ".")
    ax2.annotate(f"{e372} αναθέσεις ακριβώς\n€37.200,00 (= το όριο με ΦΠΑ)…",
                 xy=(37000, top * 0.98), xytext=(34200, top * 0.80),
                 fontsize=11.5, color=RED, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))
    ax2.annotate(f"…και μόλις {n_after372}\nαμέσως μετά", xy=(37800, top * 0.04),
                 xytext=(38200, top * 0.28), fontsize=11.5, color=DARK, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color=DARK, lw=1.4))
    ax2.set_xlabel("Ποσό ανάθεσης (€)", fontsize=12)

    fig.suptitle("Το όριο των €30.000 εμφανίζεται δύο φορές στα δεδομένα",
                 fontsize=17, fontweight="bold", x=0.02, ha="left", y=0.985)
    fig.text(0.02, 0.948, "Απευθείας αναθέσεις δημοσίου: άλλοι φορείς καταχωρούν καθαρή αξία, "
                          "άλλοι με ΦΠΑ — όλοι σταματούν στο ίδιο όριο.",
             fontsize=11.5, color="#444")
    months = len(paths)
    fig.text(0.98, 0.005, f"Πηγή: Διαύγεια (open data API) · {months} μήνες (Ιούν 2025 – Μάι 2026) · "
                          f"{len(all_amounts):,}".replace(",", ".") + " αποφάσεις Δ.1 με ποσό",
             ha="right", fontsize=9, color="#666")
    fig.tight_layout(rect=[0, 0.015, 1, 0.94])
    out = "output/diavgeia/bunching_30k.png"
    import os
    os.makedirs("output/diavgeia", exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    print(f"\nchart -> {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
