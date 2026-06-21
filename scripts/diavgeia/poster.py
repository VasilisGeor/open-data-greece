#!/usr/bin/env python3
"""Post #1 poster: big-number + cliff histogram, rendered via headless Chrome.

Usage: python3 scripts/poster.py data/raw/d1_*.jsonl
Output: output/diavgeia/poster_37200.html + output/diavgeia/poster_37200.png (2160x2700, 4:5)
"""
import glob
import json
import math
import os
import subprocess
import sys

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PAPER, INK, RED, BAR, GRID, MUTED = "#F7F4EE", "#1B1B2F", "#D7263D", "#C7CDD4", "#E5E1D8", "#6E6E76"

# Plot geometry (CSS px on a 1080x1350 canvas)
PLOT_X, PLOT_W, PLOT_TOP, PLOT_H = 64, 952, 590, 545
LO, HI, W = 35000, 39000, 200          # 20 right-inclusive bins (lo, lo+W]
YMAX = 3800
NBINS = (HI - LO) // W
RED_BIN = 10                            # (37000, 37200]
SLOT = PLOT_W / NBINS                   # 47.6
BARW = 42


def load_amounts(paths):
    amounts = []
    n_total = 0
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                n_total += 1
                d = json.loads(line)
                efv = d.get("extraFieldValues") or {}
                a = efv.get("awardAmount")
                if isinstance(a, dict):
                    a = a.get("amount")
                if a and 0 < float(a) <= 50_000_000:
                    amounts.append(float(a))
    return n_total, amounts


def gr(n):
    return f"{n:,}".replace(",", ".")


def main(paths):
    n_total, amounts = load_amounts(paths)
    bins = [0] * NBINS
    for a in amounts:
        if LO < a <= HI:
            bins[math.ceil((a - LO) / W) - 1] += 1
    n_red = bins[RED_BIN]
    n_after = sum(bins[RED_BIN + 1:RED_BIN + 5])     # (37200, 38000]
    n_exact = sum(1 for a in amounts if a == 37200.0)
    print(f"checksums: red bin {n_red}, after-band {n_after}, exact-37200 {n_exact}, "
          f"decisions {n_total}, with amount {len(amounts)}")

    bars = ""
    for i, c in enumerate(bins):
        h = max(round(c / YMAX * PLOT_H, 1), 2)
        color = RED if i == RED_BIN else BAR
        x = round(i * SLOT + (SLOT - BARW) / 2, 1)
        bars += f'<div class="bar" style="left:{x}px;height:{h}px;background:{color}"></div>\n'

    glines = ""
    for c in (1000, 2000, 3000):
        y = round(PLOT_H - c / YMAX * PLOT_H, 1)
        glines += (f'<div class="gline" style="top:{y}px"></div>'
                   f'<div class="glabel" style="top:{y - 26}px">{gr(c)}</div>\n')

    line_x = round((RED_BIN + 1) * SLOT, 1)          # right edge of the red bin
    xticks = ""
    for v, cls in ((35000, ""), (36000, ""), (37200, "hot"), (38000, ""), (39000, "")):
        x = round(PLOT_X + (v - LO) / (HI - LO) * PLOT_W, 1)
        label = f"€{gr(v)}" if v == LO else gr(v)
        xticks += f'<div class="xtick {cls}" style="left:{x}px">{label}</div>\n'

    html = f"""<!doctype html><html lang="el"><head><meta charset="utf-8"><style>
* {{margin:0;padding:0;box-sizing:border-box}}
html,body {{width:1080px;height:1350px}}
body {{background:{PAPER};font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;
      color:{INK};position:relative;overflow:hidden}}
.kicker {{position:absolute;left:64px;top:44px;width:96px;height:8px;background:{RED}}}
.eyebrow {{position:absolute;left:64px;top:72px;font-size:22px;font-weight:600;
          letter-spacing:.12em;color:{MUTED}}}
.hook {{position:absolute;left:64px;top:120px;width:952px;font-size:34px;line-height:1.3}}
.hook b {{font-weight:700}}
.big {{position:absolute;left:58px;top:218px;font-size:162px;font-weight:800;color:{RED};
      letter-spacing:-.02em;font-variant-numeric:tabular-nums}}
.rev1 {{position:absolute;left:64px;top:412px;font-size:42px;font-weight:700}}
.rev2 {{position:absolute;left:64px;top:472px;width:952px;font-size:28px;color:#44444f;
       line-height:1.35}}
.caption {{position:absolute;right:64px;top:558px;font-size:21px;color:{MUTED}}}
.plot {{position:absolute;left:{PLOT_X}px;top:{PLOT_TOP}px;width:{PLOT_W}px;height:{PLOT_H}px}}
.bar {{position:absolute;bottom:0;width:{BARW}px}}
.gline {{position:absolute;left:0;width:100%;height:1px;background:{GRID}}}
.glabel {{position:absolute;left:0;font-size:21px;color:{MUTED}}}
.baseline {{position:absolute;bottom:0;left:0;width:100%;height:2px;background:{INK}}}
.threshold {{position:absolute;top:0;bottom:0;left:{line_x}px;width:0;
            border-left:3px dashed {INK}}}
.ttag {{position:absolute;left:{line_x + 14}px;top:-2px;font-size:23px;font-weight:600}}
.annA {{position:absolute;left:8px;top:18px;font-size:28px;font-weight:700;color:{RED};
       line-height:1.25}}
.connA {{position:absolute;left:312px;top:64px;width:164px;height:2px;background:{RED}}}
.annB {{position:absolute;left:640px;top:190px;font-size:28px;font-weight:600;
       line-height:1.25}}
.connB {{position:absolute;left:700px;top:320px;width:2px;height:260px;background:{INK}}}
.xtick {{position:absolute;top:{PLOT_TOP + PLOT_H + 10}px;transform:translateX(-50%);
        font-size:23px;color:{MUTED}}}
.xticks .hot {{color:{RED};font-weight:600}}
.footer {{position:absolute;left:64px;bottom:26px;width:952px;font-size:18px;
         color:{MUTED};line-height:1.5;white-space:nowrap}}
</style></head><body>
<div class="kicker"></div>
<div class="eyebrow">ΔΙΑΥΓΕΙΑ · ΑΠΕΥΘΕΙΑΣ ΑΝΑΘΕΣΕΙΣ · ΙΟΥΝ 2025 – ΜΑΪ 2026</div>
<div class="hook">Ένα ποσό εμφανίζεται <b>{gr(n_exact)} φορές</b> στις αναθέσεις του
δημοσίου — πάντα το ίδιο, μέχρι το δεκαδικό:</div>
<div class="big">€37.200,00</div>
<div class="rev1">37.200 ÷ 1,24 = 30.000</div>
<div class="rev2">Ακριβώς το όριο της απευθείας ανάθεσης (€30.000 χωρίς ΦΠΑ) —
καταχωρημένο με ΦΠΑ 24%.</div>
<div class="caption">Αναθέσεις ανά ζώνη €200</div>
<div class="plot">
{glines}
{bars}
<div class="baseline"></div>
<div class="threshold"></div>
<div class="ttag">το όριο, με ΦΠΑ</div>
<div class="annA">{gr(n_red)} αναθέσεις<br>λίγο πριν το όριο</div>
<div class="connA"></div>
<div class="annB">μόλις {n_after}<br>αμέσως μετά</div>
</div>
<div class="xticks">
{xticks}
</div>
<div class="footer">Πηγή: Διαύγεια (Open Data API) · {gr(n_total)} αποφάσεις Δ.1 · {gr(len(amounts))} με ποσό · Ιούν 2025 – Μάι 2026<br>
Η απευθείας ανάθεση έως €30.000 (χωρίς ΦΠΑ) είναι νόμιμη<br>
Ανάλυση: Vasilis Georgakas · github.com/VasilisGeor/open-data-greece</div>
</body></html>"""

    os.makedirs("output/diavgeia", exist_ok=True)
    html_path = "output/diavgeia/poster_37200.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    png_path = os.path.abspath("output/diavgeia/poster_37200.png")
    subprocess.run([CHROME, "--headless=new", f"--screenshot={png_path}",
                    "--window-size=1080,1350", "--force-device-scale-factor=2",
                    "--hide-scrollbars", f"file://{os.path.abspath(html_path)}"],
                   check=True, capture_output=True)
    print(f"poster -> output/diavgeia/poster_37200.png")


if __name__ == "__main__":
    main(sorted(sys.argv[1:]) or sorted(glob.glob("data/raw/diavgeia/d1_*.jsonl")))
