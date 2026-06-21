#!/usr/bin/env python3
"""Eurostat Greece-vs-EU charts from data/basket.json.
Usage: python3 scripts/charts.py  → output/scorecard.png, output/living_with_parents.png
"""
import json
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAPER, INK, RED, GRAY, EUBLUE, MUTED = "#F7F4EE", "#1B1B2F", "#D7263D", "#C7CDD4", "#2B4B8C", "#6E6E76"
NAMES = {"EL": "Ελλάδα", "EU27_2020": "ΕΕ-27", "DE": "Γερμανία", "ES": "Ισπανία", "PT": "Πορτογαλία", "IT": "Ιταλία"}
ORDER = ["DE", "ES", "IT", "PT", "EU27_2020", "EL"]

basket = json.load(open("data/basket.json", encoding="utf-8"))


def bars(ax, label, key, fmt, title, note=""):
    vals = basket[key]["values"]
    geos = [g for g in ORDER if g in vals]
    v = [vals[g] for g in geos]
    cols = [RED if g == "EL" else (EUBLUE if g == "EU27_2020" else GRAY) for g in geos]
    ax.barh([NAMES[g] for g in geos], v, color=cols, zorder=3)
    for i, x in enumerate(v):
        ax.text(x, i, " " + fmt(x), va="center", ha="left", fontsize=11,
                fontweight="bold" if geos[i] == "EL" else "normal",
                color=RED if geos[i] == "EL" else INK)
    ax.set_title(title, fontsize=13.5, fontweight="bold", loc="left", color=INK, pad=8)
    if note:
        ax.text(0, 1.0, note, transform=ax.transAxes, fontsize=9.5, color=MUTED)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, max(v) * 1.18)
    ax.tick_params(labelsize=10.5)
    ax.grid(axis="x", alpha=0.3, zorder=0)


# --- Chart 1: living with parents (the headline) ---
fig, ax = plt.subplots(figsize=(10, 5.8), dpi=160)
bars(ax, "lwp", "Νέοι 25-34 που ζουν με γονείς (%)", lambda x: f"{x:.1f}%".replace(".", ","),
     "Νέοι 25-34 που ζουν ακόμα με τους γονείς τους")
fig.suptitle("Η Ελλάδα στην κορυφή της Ευρώπης — για λάθος λόγο", fontsize=16, fontweight="bold", x=0.02, ha="left")
fig.text(0.02, 0.925, "Ποσοστό 25-34 ετών που μένουν στο πατρικό · Eurostat 2025 (ilc_lvps08)", fontsize=10.5, color="#444")
fig.text(0.98, 0.02, "Πηγή: Eurostat · ilc_lvps08 · 2025", ha="right", fontsize=9, color=MUTED)
ax.set_facecolor(PAPER); fig.patch.set_facecolor(PAPER)
fig.tight_layout(rect=[0, 0.02, 1, 0.90])
os.makedirs("output", exist_ok=True)
fig.savefig("output/living_with_parents.png", facecolor=PAPER, bbox_inches="tight")
print("-> output/living_with_parents.png")

# --- Chart 2: scorecard (4-panel Greece vs EU) ---
panels = [
    ("Νέοι 25-34 που ζουν με γονείς (%)", lambda x: f"{x:.0f}%", "ζουν με γονείς (25-34)"),
    ("Κατώτατος μισθός (€/μήνα)", lambda x: f"€{x:,.0f}".replace(",", "."), "κατώτατος μισθός"),
    ("ΑΕΠ κατά κεφαλήν σε PPS (EU27=100)", lambda x: f"{x:.0f}", "αγοραστική δύναμη (ΕΕ=100)"),
    ("Ανεργία νέων 15-24 (%)", lambda x: f"{x:.0f}%", "ανεργία νέων 15-24"),
]
fig, axes = plt.subplots(2, 2, figsize=(12, 9), dpi=160)
for ax, (key, fmt, t) in zip(axes.flat, panels):
    if key in basket:
        bars(ax, key, key, fmt, t)
fig.suptitle("Ελλάδα vs Ευρώπη — η εικόνα σε 4 νούμερα", fontsize=18, fontweight="bold", x=0.02, ha="left")
fig.text(0.98, 0.005, "Πηγή: Eurostat (2025-2026) · κόκκινο = Ελλάδα, μπλε = μέσος όρος ΕΕ-27",
         ha="right", fontsize=9.5, color=MUTED)
for ax in axes.flat:
    ax.set_facecolor(PAPER)
fig.patch.set_facecolor(PAPER)
fig.tight_layout(rect=[0, 0.02, 1, 0.95])
fig.savefig("output/scorecard.png", facecolor=PAPER, bbox_inches="tight")
print("-> output/scorecard.png")
