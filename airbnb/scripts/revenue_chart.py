#!/usr/bin/env python3
"""Revenue chart: honest range €60-90M + theoretical ceiling + concentration.
Verified model outputs (workflow 2026-06-21): reviews-model €63M (review_rate 0.7)
→ €89M (0.5), LOS~2.2; calendar-ceiling €187M (not an estimate); ~64% of revenue
to operators with 3+ listings.
Usage: python3 scripts/airbnb_revenue_chart.py → output/revenue.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAPER, INK, RED, GRAY, MUTED = "#F7F4EE", "#1B1B2F", "#D7263D", "#C7CDD4", "#6E6E76"
LOW, HIGH, CEIL = 63, 89, 187
CONC = 64  # % of revenue to operators with 3+ listings

fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6.2), dpi=160, gridspec_kw={"width_ratios": [2, 1]})

# Panel 1: honest range vs theoretical ceiling, on a €M axis
a1.set_xlim(0, 200)
a1.set_ylim(0, 1)
# ceiling marker
a1.axvline(CEIL, color=MUTED, lw=2, ls=":", zorder=3)
a1.annotate("€187M\nθεωρητικό ταβάνι\n(όχι εκτίμηση)", xy=(CEIL, 0.5), xytext=(CEIL - 4, 0.5),
            ha="right", va="center", fontsize=11, color=MUTED, fontweight="bold")
# honest range bar
a1.barh([0.5], [HIGH - LOW], left=LOW, height=0.26, color=RED, zorder=4)
a1.annotate(f"€{LOW}M", xy=(LOW, 0.5), xytext=(LOW - 3, 0.5), ha="right", va="center",
            fontsize=15, fontweight="bold", color=INK)
a1.annotate(f"€{HIGH}M", xy=(HIGH, 0.5), xytext=(HIGH + 3, 0.5), ha="left", va="center",
            fontsize=15, fontweight="bold", color=INK)
a1.text((LOW + HIGH) / 2, 0.68, "τίμιο εύρος", ha="center", fontsize=12.5, fontweight="bold", color=RED)
a1.text((LOW + HIGH) / 2, 0.34, "ετήσια έσοδα", ha="center", fontsize=10.5, color="white", fontweight="bold")
a1.text(LOW - 3, 0.30, "αν 70% αφήνουν review", ha="right", fontsize=9, color=MUTED)
a1.text(HIGH + 3, 0.30, "αν 50%", ha="left", fontsize=9, color=MUTED)
a1.set_yticks([])
a1.set_xticks([0, 50, 100, 150, 187])
a1.set_xticklabels(["€0", "€50M", "€100M", "€150M", "€187M"], fontsize=10, color=MUTED)
a1.spines[["top", "right", "left"]].set_visible(False)
a1.set_title("Πόσα βγάζει η Airbnb-Αθήνα τον χρόνο;", fontsize=16, fontweight="bold", loc="left", color=INK)
a1.text(0, 1.12, "Δύο μέθοδοι, ένα τίμιο εύρος — όχι ένα εντυπωσιακό μονό νούμερο.",
        transform=a1.transAxes, fontsize=11, color="#444")

# Panel 2: concentration
a2.bar([0], [CONC], color=RED, zorder=3, width=0.6)
a2.bar([0], [100 - CONC], bottom=[CONC], color=GRAY, zorder=3, width=0.6)
a2.text(0, CONC / 2, f"{CONC}%", ha="center", va="center", color="white", fontsize=22, fontweight="bold")
a2.text(0, CONC + (100 - CONC) / 2, f"{100-CONC}%", ha="center", va="center", color=INK, fontsize=14)
a2.set_ylim(0, 100)
a2.set_xlim(-0.7, 0.7)
a2.set_xticks([])
a2.set_yticks([])
a2.spines[["top", "right", "left", "bottom"]].set_visible(False)
a2.set_title("Πού πάνε τα έσοδα", fontsize=14, fontweight="bold", loc="left", color=INK)
a2.text(0, -6, "κόκκινο = διαχειριστές\nμε 3+ καταλύματα", ha="center", fontsize=10.5, color=MUTED)

fig.text(0.99, 0.01, "Πηγή: InsideAirbnb (Σεπ 2025) · εκτίμηση από reviews (proxy) · €187M = όλες οι μη-διαθέσιμες νύχτες ως κρατήσεις",
         ha="right", fontsize=8.5, color=MUTED)
for ax in (a1, a2):
    ax.set_facecolor(PAPER)
fig.patch.set_facecolor(PAPER)
fig.tight_layout(rect=[0, 0.03, 1, 0.94])
os.makedirs("output", exist_ok=True)
fig.savefig("output/revenue.png", facecolor=PAPER, bbox_inches="tight")
print("-> output/revenue.png")
