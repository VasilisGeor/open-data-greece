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

Period: Mar–May 2026 · 78,852 Δ.1 decisions · 43,773 with structured amounts.

The €30,000 (pre-VAT) direct-award limit — άρθρο 118 Ν.4412/2016, as replaced
by άρθρο 50 Ν.4782/2021 — shows up **twice** in the awarded-amount distribution,
because contracting authorities record amounts inconsistently (net vs gross):

- **Net side:** awards at €29,000–30,000 outnumber €30,001–31,000 by ~5×,
  stable every month (4.6× / 5.1× / 5.3×). 221 awards at exactly €30,000.00.
- **Gross side:** 508 awards at exactly **€37,200.00** (= €30,000 + 24% VAT);
  the €37,000–37,200 band holds 927 awards vs 13 in €37,201–38,000.
- **Ghost threshold:** 111 awards at exactly €24,800 (= €20,000 + VAT) —
  the *pre-2021* limit, still anchoring behavior 5 years after repeal.
- **Works limit (€60,000):** same fingerprint — 65 awards at €59–60k vs 9
  just above; 32 at exactly €74,400 (= €60,000 + VAT).

Chart: `output/bunching_30k.png`

**Data-quality notes:** ~57% of Δ.1 decisions carry a machine-readable amount;
large tender-procedure documents are routinely misfiled as Δ.1 (naive totals
overstate direct-award spend ~4×); net/gross recording varies by authority.
