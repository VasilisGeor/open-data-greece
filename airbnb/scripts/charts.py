#!/usr/bin/env python3
"""Airbnb charts: (1) Athens-vs-islands availability, (2) Athens density map.

Usage: python3 scripts/airbnb_charts.py
Outputs: output/availability.png, output/density_athens.png
"""
import csv
import gzip
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAPER, INK, RED, GRAY, MUTED = "#F7F4EE", "#1B1B2F", "#D7263D", "#C7CDD4", "#6E6E76"
RAW = "data/raw"


def load(name):
    with gzip.open(f"{RAW}/{name}.csv.gz", "rt", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def avail(rows):
    out = []
    for r in rows:
        try:
            v = float(r.get("availability_365") or -1)
        except ValueError:
            continue
        if 0 <= v <= 365:
            out.append(v)
    return out


def chart_availability():
    ath = avail(load("athens"))
    sa = avail(load("south-aegean"))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 8.5), dpi=160, sharex=True)
    bins = list(range(0, 381, 20))
    for ax, data, name, med, pct in (
        (a1, ath, "ΑΘΗΝΑ", 300, 50),
        (a2, sa, "ΝΟΤΙΟ ΑΙΓΑΙΟ (Σαντορίνη, Μύκονος, Ρόδος)", 159, 24),
    ):
        n = len(data)
        ax.hist(data, bins=bins, weights=[100 / n] * n, color=GRAY, zorder=3)
        ge = [d for d in data if d >= 300]
        ax.hist(ge, bins=[b for b in bins if b >= 300], weights=[100 / n] * len(ge),
                color=RED, zorder=4)
        ax.axvline(med, color=INK, lw=2, ls="--", zorder=5)
        ax.set_title(name, fontsize=13, fontweight="bold", loc="left", color=INK)
        ax.set_ylim(0, 24)
        # median line label — small, just right of the line, high up in clear space
        ax.annotate(f"διάμεσος\n{med} μέρες", xy=(med, 22), xytext=(med + 6, 19.5),
                    fontsize=10.5, color=INK, fontweight="bold", va="top")
        # the headline % — boxed callout in empty upper-middle, arrow to the red block
        ax.annotate(f"{pct}% διαθέσιμα\n300+ μέρες τον χρόνο", xy=(335, 7),
                    xytext=(150, 15), fontsize=12, color=RED, fontweight="bold", ha="center",
                    arrowprops=dict(arrowstyle="->", color=RED, lw=1.6),
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=RED, lw=1.2))
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylabel("% των listings", fontsize=10, color=MUTED)
    a2.set_xlabel("Μέρες διαθέσιμα τον χρόνο (availability/365)", fontsize=11, color=INK)
    fig.suptitle("Τα νησιά νοικιάζουν εποχικά. Η Αθήνα όλο τον χρόνο.",
                 fontsize=17, fontweight="bold", x=0.02, ha="left", y=0.98, color=INK)
    fig.text(0.02, 0.935, "Κατανομή διαθεσιμότητας Airbnb — όσο πιο δεξιά, τόσο πιο «μόνιμο ξενοδοχείο».",
             fontsize=11, color="#444")
    fig.text(0.98, 0.01, "Πηγή: InsideAirbnb (Σεπ 2025) · Αθήνα 15.584 · Νότιο Αιγαίο 37.139 listings",
             ha="right", fontsize=9, color=MUTED)
    for ax in (a1, a2):
        ax.set_facecolor(PAPER)
    fig.patch.set_facecolor(PAPER)
    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    os.makedirs("output", exist_ok=True)
    fig.savefig("output/availability.png", facecolor=PAPER, bbox_inches="tight")
    print("-> output/availability.png")


def chart_density():
    rows = load("athens")
    lon, lat = [], []
    for r in rows:
        try:
            x, y = float(r["longitude"]), float(r["latitude"])
        except (ValueError, KeyError):
            continue
        if 23.65 < x < 23.80 and 37.94 < y < 38.04:
            lon.append(x)
            lat.append(y)
    fig, ax = plt.subplots(figsize=(9, 9.6), dpi=160)
    ax.set_facecolor("#10001a")
    hb = ax.hexbin(lon, lat, gridsize=60, cmap="inferno", mincnt=1, linewidths=0.2)
    cb = fig.colorbar(hb, ax=ax, shrink=0.55, pad=0.02)
    cb.set_label("Airbnb ανά κελί", fontsize=10, color=INK)
    # label central neighbourhoods with a leader dot, placed to avoid the title row
    labels = {
        "Σύνταγμα/Πλάκα": (23.733, 37.973),
        "Κουκάκι": (23.724, 37.958),
        "Εξάρχεια": (23.737, 37.989),
        "Κολωνάκι": (23.747, 37.980),
        "Παγκράτι": (23.752, 37.967),
    }
    for name, (x, y) in labels.items():
        ax.scatter([x], [y], s=10, color="white", zorder=6)
        ax.annotate(name, xy=(x, y), xytext=(4, 4), textcoords="offset points",
                    fontsize=10, color="white", fontweight="bold")
    ax.set_xlim(23.66, 23.79)
    ax.set_ylim(37.945, 38.025)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect(1 / 0.79)  # rough lat/lon aspect at 38°N
    fig.suptitle("Πού είναι τα 15.584 Airbnb της Αθήνας",
                 fontsize=17, fontweight="bold", color=INK, x=0.04, ha="left", y=0.97)
    fig.text(0.04, 0.925, "47% συγκεντρωμένα στο ιστορικό κέντρο — 1 στα 5 μόνο στην Πλάκα",
             fontsize=11.5, color="#444")
    fig.text(0.98, 0.02, "Πηγή: InsideAirbnb (Σεπ 2025) · θέσεις 15.584 listings",
             ha="right", fontsize=9, color=MUTED)
    fig.patch.set_facecolor(PAPER)
    fig.tight_layout(rect=[0, 0.02, 1, 0.91])
    fig.savefig("output/density_athens.png", facecolor=PAPER, bbox_inches="tight")
    print("-> output/density_athens.png")


if __name__ == "__main__":
    chart_availability()
    chart_density()
