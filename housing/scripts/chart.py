#!/usr/bin/env python3
"""Housing-cluster chart: rent as a share of the minimum wage.
Run from housing/:  python3 scripts/chart.py  → output/young_persons_bill.png
Sources: Eurostat earn_mw_cur (min wage €1.027), Spitogatos SPI Q3 2025 (~€11,5/m² → €575/50m²).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PAPER, INK, RED, GRAY, MUTED = "#F7F4EE", "#1B1B2F", "#D7263D", "#C7CDD4", "#6E6E76"
WAGE, RENT = 1027, 575
REMAIN = WAGE - RENT
rent_pct = round(100 * RENT / WAGE)

fig, ax = plt.subplots(figsize=(11, 4.6), dpi=160)
ax.barh([0], [RENT], color=RED, zorder=3)
ax.barh([0], [REMAIN], left=[RENT], color=GRAY, zorder=3)
ax.text(RENT / 2, 0, f"ΕΝΟΙΚΙΟ\n€{RENT}", ha="center", va="center", color="white",
        fontsize=15, fontweight="bold")
ax.text(RENT + REMAIN / 2, 0, f"ό,τι μένει\n€{REMAIN}", ha="center", va="center",
        color=INK, fontsize=13)
# bracket / total
ax.annotate(f"κατώτατος μισθός: €{WAGE:,}".replace(",", "."), xy=(WAGE, 0.45),
            ha="right", va="bottom", fontsize=11.5, color=MUTED, fontweight="bold")
ax.set_xlim(0, WAGE)
ax.set_ylim(-0.6, 0.7)
ax.axis("off")
fig.suptitle(f"Το ενοίκιο τρώει το {rent_pct}% του κατώτατου μισθού",
             fontsize=19, fontweight="bold", x=0.04, ha="left", color=INK, y=0.96)
fig.text(0.04, 0.82, "Ένα δυάρι 50m² στο κέντρο της Αθήνας vs ο μηνιαίος κατώτατος μισθός (μικτά)",
         fontsize=12, color="#444")
fig.text(0.04, 0.05, "Πηγές: Eurostat (κατώτατος μισθός, €1.027) · Spitogatos Property Index Q3 2025 "
                     "(~€11,5/m² × 50m² = €575) · …πριν καν ρεύμα, φαγητό, μετακίνηση.",
         fontsize=9, color=MUTED)
ax.set_facecolor(PAPER); fig.patch.set_facecolor(PAPER)
fig.tight_layout(rect=[0, 0.08, 1, 0.80])
os.makedirs("output", exist_ok=True)
fig.savefig("output/young_persons_bill.png", facecolor=PAPER, bbox_inches="tight")
print(f"rent={rent_pct}% of wage -> output/young_persons_bill.png")
