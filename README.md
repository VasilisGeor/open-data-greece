# open-data-greece

Αναλύσεις και ευρήματα από τα ανοιχτά δεδομένα της Ελλάδας.

I dig through Greek open datasets and publish data-driven findings.
The code lives here so every finding is fully reproducible — same API,
same scripts, same numbers.

## Διαύγεια — απευθείας αναθέσεις

Data source: [Diavgeia Open Data API](https://diavgeia.gov.gr/opendata) (no auth required).

- `scripts/fetch.py` — paginated fetcher for any decision type / date range → JSONL
- `scripts/analyze.py` — first-pass stats: totals, coverage, categories, top organizations
- `scripts/bunching.py` — threshold-bunching analysis around the €30.000 direct-award limit + chart

### Usage

```bash
python3 scripts/fetch.py --type Δ.1 --from 2026-05-01 --to 2026-05-31 --out data/raw/d1_2026-05.jsonl
python3 scripts/analyze.py data/raw/d1_2026-05.jsonl
python3 scripts/bunching.py data/raw/d1_2026-*.jsonl
```

No dependencies beyond Python 3 stdlib + matplotlib (for charts).

## Airbnb — Αθήνα & Ελλάδα

Data source: [InsideAirbnb](https://insideairbnb.com/get-the-data/) (Sep 2025 snapshots, public).

- `scripts/airbnb_explore.py` — per-area stats (room type, host concentration, availability, price)
- `scripts/airbnb_ghost_poster.py` — operator-concentration poster ("ghost hotels")
- `scripts/airbnb_charts.py` — availability (Athens vs islands) + Athens density map
- `scripts/airbnb_charts2.py` — review-growth timeline + price geography
- `scripts/airbnb_revenue_chart.py` — honest revenue range + concentration

Prices are recorded with a `$` sign by InsideAirbnb but are **EUR** for Greek listings.
"Operators" = `host_id` (the managing account), not necessarily the property owner.

## Findings log

### 2026-06 — Airbnb Αθήνα: όχι «sharing economy», αλλά επαγγελματική αγορά

Athens, Sep 2025 · 15,584 listings · 6,196 operators (verified, adversarial fact-check).

- **Concentration:** top 5% of operators (310) control **41%** of listings; top 1% → 20%.
  70% of hosts (single-listing) hold only 28%. Max operator: 165 listings.
- **"Ghost hotels":** 196 clusters of 5+ listings at the same coordinates; **biggest = 82
  listings of one operator in a single building** (Plaka).
- **Year-round vs seasonal:** Athens median availability 300 days/yr (50% open 300+ days)
  vs South Aegean (Santorini/Mykonos) 159 days (24%) vs Crete 185 (30%). Athens is the
  *more* hotel-ized — islands are seasonal.
- **Growth:** reviews/yr (booking proxy) 75,243 (2019) → 186,767 (2024, +148%); 2025
  on track for a new record (June 2025 = biggest month ever). 874,286 reviews total.
- **Price geography:** median €78/night, mean €122.9 (heavy right tail; max €38,000).
  Zappeio €118 vs cheapest ~€40. Athens is *cheaper* than the islands (€143) and Crete (€108).
- **Revenue (honest range):** ~€60–90M/year (reviews model; review_rate 0.7→€63M, 0.5→€89M).
  €187M (calendar) is a theoretical ceiling, not an estimate. ~64% of revenue to operators with 3+ listings.

Charts: `output/airbnb_ghost_poster.png`, `airbnb_availability.png`, `airbnb_density_athens.png`,
`airbnb_growth.png`, `airbnb_prices.png`, `airbnb_revenue.png`.

**Data-quality notes:** ~92% of Athens listings are entire homes; `availability_365` mixes
booked + host-blocked nights (a "free/blocked" signal, not occupancy); reviews are a
booking *proxy* (~50–72% of stays leave one). A separate Airbnb-vs-long-term arbitrage
analysis was **withheld** — occupancy can't be pinned down reliably from this data alone.

## Findings log (Διαύγεια)

### 2026-06 — Το ίδιο όριο, δύο φορές: bunching στο όριο απευθείας ανάθεσης

Period: Jun 2025 – May 2026 (12 months) · 315,614 Δ.1 decisions · 180,392 with
structured amounts · €1.31B/year in ≤€60k direct awards (measured, not extrapolated).

The €30,000 (pre-VAT) direct-award limit — άρθρο 118 Ν.4412/2016, as replaced
by άρθρο 50 Ν.4782/2021 — shows up **twice** in the awarded-amount distribution,
because contracting authorities record amounts inconsistently (net vs gross):

- **Net side:** awards at €29,000–30,000 outnumber €30,001–31,000 by 4.4×
  (range 3.3×–6.0×, positive in all 12 months). 816 awards at exactly €30,000.00.
- **Gross side:** 2,072 awards at exactly **€37,200.00** (= €30,000 + 24% VAT);
  the (37,000–37,200] band holds 3,469 awards vs 64 in (37,200–38,000] (54× cliff).
- **Ghost threshold:** 509 awards at exactly €24,800 (= €20,000 + VAT) —
  the *pre-2021* limit, still anchoring behavior 5 years after repeal.
- **Works limit (€60,000):** same fingerprint — 331 awards at €59–60k vs 28
  just above; 121 at exactly €74,400 (= €60,000 + VAT).
- **Seasonality teaser:** December 2025 is the year's peak month on every
  metric (35,312 decisions, €180M clean spend, 436 awards in the €29–30k band);
  January 2026 the trough (13,093). Classic budget-burn — future post.

Chart: `output/bunching_30k.png`

**Data-quality notes:** ~57% of Δ.1 decisions carry a machine-readable amount;
large tender-procedure documents are routinely misfiled as Δ.1 (naive totals
overstate direct-award spend ~4×); net/gross recording varies by authority.
