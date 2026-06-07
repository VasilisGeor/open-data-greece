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

## Findings log

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
