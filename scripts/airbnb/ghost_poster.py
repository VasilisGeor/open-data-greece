#!/usr/bin/env python3
"""Ghost-hotels poster (Airbnb Athens concentration) — HTML → headless Chrome, 4:5.

Usage: python3 scripts/airbnb_ghost_poster.py
Output: output/airbnb_ghost_poster.{html,png} (2160x2700)
"""
import csv
import gzip
import math
import os
import subprocess
from collections import Counter

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAPER, INK, RED, ORANGE, GRAY, MUTED = "#F7F4EE", "#1B1B2F", "#D7263D", "#F5A623", "#C7CDD4", "#6E6E76"


def gr(n):
    return f"{n:,}".replace(",", ".")


def main():
    with gzip.open("data/raw/airbnb/athens.csv.gz", "rt", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    n = len(rows)
    host = Counter(r["host_id"] for r in rows)
    H = len(host)
    counts = sorted(host.values(), reverse=True)
    top5 = sum(counts[: round(H * 0.05)])
    top5_pct = round(100 * top5 / n)
    n_top5 = round(H * 0.05)
    max_op = counts[0]
    # biggest building cluster (same host + rounded coords)
    cl = Counter()
    for r in rows:
        try:
            la, lo = round(float(r["latitude"]), 4), round(float(r["longitude"]), 4)
        except (ValueError, KeyError):
            continue
        cl[(r["host_id"], la, lo)] += 1
    max_cluster = max(cl.values())

    # buckets by share of listings
    buckets = [
        ("1 κατάλυμα", 1, 1, GRAY),
        ("2-4", 2, 4, GRAY),
        ("5-9", 5, 9, ORANGE),
        ("10-49", 10, 49, RED),
        ("50+", 50, 10**9, RED),
    ]
    seg = ""
    for lab, lo, hi, col in buckets:
        hosts = [c for c in counts if lo <= c <= hi]
        lshare = 100 * sum(hosts) / n
        hshare = 100 * len(hosts) / H
        seg += (f'<div class="seg" style="width:{lshare:.1f}%;background:{col}">'
                f'<div class="segtop">{lshare:.0f}%</div>'
                f'<div class="segbot">{lab}<br><span>{hshare:.0f}% των διαχειριστών</span></div></div>')

    html = f"""<!doctype html><html lang="el"><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px}}
body{{background:{PAPER};font-family:-apple-system,"Helvetica Neue",Arial,sans-serif;color:{INK};position:relative;overflow:hidden}}
.kicker{{position:absolute;left:64px;top:44px;width:96px;height:8px;background:{RED}}}
.eyebrow{{position:absolute;left:64px;top:72px;font-size:21px;font-weight:600;letter-spacing:.1em;color:{MUTED}}}
.hook{{position:absolute;left:64px;top:118px;width:952px;font-size:33px;line-height:1.32}}
.hook b{{font-weight:700}}
.big{{position:absolute;left:58px;top:236px;font-size:200px;font-weight:800;color:{RED};letter-spacing:-.03em;font-variant-numeric:tabular-nums}}
.rev{{position:absolute;left:64px;top:470px;width:952px;font-size:31px;line-height:1.3;font-weight:700}}
.rev span{{color:{MUTED};font-weight:400;font-size:25px}}
.bartitle{{position:absolute;left:64px;top:600px;font-size:21px;color:{MUTED}}}
.bar{{position:absolute;left:64px;top:632px;width:952px;height:120px;display:flex}}
.seg{{position:relative;height:100%;border-right:3px solid {PAPER}}}
.seg:first-child{{border-radius:6px 0 0 6px}}
.seg:last-child{{border-radius:0 6px 6px 0;border-right:none}}
.segtop{{position:absolute;top:8px;left:0;right:0;text-align:center;color:white;font-weight:800;font-size:24px}}
.segbot{{position:absolute;bottom:-72px;left:-10px;right:-10px;text-align:center;font-size:16px;font-weight:700;line-height:1.2;color:{INK}}}
.segbot span{{font-weight:400;color:{MUTED};font-size:13px}}
.kick{{position:absolute;left:64px;top:888px;width:952px;background:#fff;border:2px solid {RED};border-radius:12px;padding:28px 32px}}
.kicknum{{font-size:30px;font-weight:800;color:{RED}}}
.kicksub{{font-size:24px;margin-top:6px;line-height:1.35}}
.legal{{position:absolute;left:64px;top:1058px;width:952px;font-size:22px;color:#44444f;line-height:1.4}}
.footer{{position:absolute;left:64px;bottom:30px;width:952px;font-size:18px;color:{MUTED};line-height:1.5}}
</style></head><body>
<div class="kicker"></div>
<div class="eyebrow">AIRBNB ΑΘΗΝΑ · 15.584 ΚΑΤΑΛΥΜΑΤΑ · ΣΕΠ 2025</div>
<div class="hook">6.196 «οικοδεσπότες» στην Αθήνα — αλλά το «μοιράζομαι το σπίτι μου»
έχει γίνει <b>επιχείρηση</b>.</div>
<div class="big">{top5_pct}%</div>
<div class="rev">των Airbnb της Αθήνας τα διαχειρίζονται μόλις {gr(n_top5)} άνθρωποι/εταιρείες
<span>— το 5% των διαχειριστών.</span></div>
<div class="bartitle">Μερίδιο καταλυμάτων, ανά μέγεθος διαχειριστή</div>
<div class="bar">{seg}</div>
<div class="kick">
<div class="kicknum">👻 Ένας διαχειριστής: {max_op} καταλύματα.</div>
<div class="kicksub">Τα {max_cluster} από αυτά στο <b>ίδιο ακριβώς κτίριο</b> — ντε φάκτο ξενοδοχείο χωρίς ταμπέλα.</div>
</div>
<div class="legal">Όλα νόμιμα και δηλωμένα. Αλλά τα δεδομένα δείχνουν κάτι διαφορετικό από «sharing economy».</div>
<div class="footer">Πηγή: InsideAirbnb (Σεπ 2025) · 15.584 καταλύματα · 6.196 διαχειριστές (host_id)<br>
Ανάλυση: Vasilis Georgakas · github.com/VasilisGeor/open-data-greece</div>
</body></html>"""

    os.makedirs("output/airbnb", exist_ok=True)
    hp = "output/airbnb/ghost_poster.html"
    open(hp, "w", encoding="utf-8").write(html)
    png = os.path.abspath("output/airbnb/ghost_poster.png")
    subprocess.run([CHROME, "--headless=new", f"--screenshot={png}",
                    "--window-size=1080,1350", "--force-device-scale-factor=2",
                    "--hide-scrollbars", f"file://{os.path.abspath(hp)}"],
                   check=True, capture_output=True)
    print(f"top5%={top5_pct}% ({n_top5} ops) · max_op={max_op} · max_cluster={max_cluster}")
    print("-> output/airbnb/ghost_poster.png")


if __name__ == "__main__":
    main()
