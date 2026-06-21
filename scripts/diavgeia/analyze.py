#!/usr/bin/env python3
"""First-pass analysis of fetched Diavgeia Δ.1 decisions.

Usage: python3 analyze.py data/raw/d1_2026-05.jsonl
"""
import json
import re
import statistics
import sys
import time
import urllib.request
from collections import Counter, defaultdict

# Amounts like "4.207,65 €", "ποσού 1.234,56 ευρώ", "€ 7.900,00"
AMOUNT_RE = re.compile(
    r"(?:€\s*|ποσο[ύυ]\s+(?:των\s+)?)?(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*(?:€|ευρώ|ΕΥΡΩ)",
    re.IGNORECASE,
)

CATEGORIES = {
    "Καύσιμα/Ενέργεια": ["καύσιμ", "πετρέλαι", "βενζίν", "ενέργει", "ηλεκτρικ ρεύμα", "φυσικ αέρι"],
    "Συντήρηση/Επισκευές": ["συντήρησ", "επισκευ", "αποκατάστασ", "ανακαίνισ"],
    "Πληροφορική/Τηλεπ.": ["πληροφορικ", "λογισμικ", "ηλεκτρονικ υπολογιστ", "η/υ", "τηλεφων", "internet", "software", "server", "εκτυπωτ"],
    "Τρόφιμα/Catering": ["τρόφιμ", "εδέσμα", "catering", "γεύμα", "σίτισ", "καφ"],
    "Καθαριότητα": ["καθαριότητ", "καθαρισμ", "απολύμανσ"],
    "Μελέτες/Σύμβουλοι": ["μελέτ", "σύμβουλ", "consulting", "εμπειρογνωμ"],
    "Υγεία/Φάρμακα": ["φάρμακ", "υγειονομικ", "ιατρικ", "νοσοκομειακ", "αντιδραστήρι"],
    "Οχήματα/Μεταφορές": ["όχημα", "οχημάτων", "μεταφορ", "ελαστικ", "ανταλλακτικ"],
    "Εκδηλώσεις/Προβολή": ["εκδήλωσ", "εορτασμ", "προβολ", "διαφήμισ", "τουριστικ προβολ"],
    "Κτίρια/Εξοπλισμός": ["έπιπλ", "εξοπλισμ", "κλιματισ", "γραφική ύλη", "χαρτικ"],
}


def parse_amount_from_text(text):
    matches = AMOUNT_RE.findall(text or "")
    vals = []
    for m in matches:
        try:
            vals.append(float(m.replace(".", "").replace(",", ".")))
        except ValueError:
            pass
    return max(vals) if vals else None  # max: subjects often quote net + gross; gross is larger


def categorize(subject):
    s = (subject or "").lower()
    for cat, kws in CATEGORIES.items():
        if any(kw in s for kw in kws):
            return cat
    return "Άλλο"


def org_name(org_id, cache={}):
    if org_id in cache:
        return cache[org_id]
    try:
        url = f"https://diavgeia.gov.gr/opendata/organizations/{org_id}.json"
        with urllib.request.urlopen(url, timeout=15) as r:
            cache[org_id] = json.loads(r.read()).get("label", org_id)
    except Exception:
        cache[org_id] = str(org_id)
    time.sleep(0.3)
    return cache[org_id]


def main(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    n = len(rows)
    structured, recovered, missing = 0, 0, 0
    amounts = []
    org_spend = defaultdict(float)
    org_count = Counter()
    cat_spend = defaultdict(float)
    cat_count = Counter()
    biggest = []

    for d in rows:
        efv = d.get("extraFieldValues") or {}
        amt = efv.get("awardAmount")
        if isinstance(amt, dict):
            amt = amt.get("amount")
        source = "structured" if amt else None
        if not amt:
            amt = parse_amount_from_text(d.get("subject"))
            source = "recovered" if amt else None
        if source == "structured":
            structured += 1
        elif source == "recovered":
            recovered += 1
        else:
            missing += 1
            continue
        amt = float(amt)
        if amt <= 0 or amt > 50_000_000:  # junk guard
            continue
        amounts.append(amt)
        org_spend[d.get("organizationId")] += amt
        org_count[d.get("organizationId")] += 1
        cat = categorize(d.get("subject"))
        cat_spend[cat] += amt
        cat_count[cat] += 1
        biggest.append((amt, d.get("subject", "")[:110], d.get("ada")))

    total_eur = sum(amounts)
    print(f"=== Δ.1 direct awards: {path} ===")
    print(f"decisions: {n}")
    print(f"amount coverage: structured {structured} ({100*structured//n}%), "
          f"recovered-from-text {recovered} ({100*recovered//n}%), missing {missing} ({100*missing//n}%)")
    print(f"\nTOTAL: €{total_eur:,.0f} across {len(amounts)} awards")
    print(f"median €{statistics.median(amounts):,.0f} | mean €{statistics.mean(amounts):,.0f} "
          f"| p90 €{sorted(amounts)[int(len(amounts)*0.9)]:,.0f} | max €{max(amounts):,.0f}")

    print("\n--- Categories (keyword v0) ---")
    for cat, spend in sorted(cat_spend.items(), key=lambda x: -x[1]):
        print(f"{cat:<22} €{spend:>14,.0f}  ({cat_count[cat]} awards)")

    print("\n--- Top 10 organizations by spend ---")
    top_orgs = sorted(org_spend.items(), key=lambda x: -x[1])[:10]
    for oid, spend in top_orgs:
        print(f"€{spend:>12,.0f}  ({org_count[oid]:>4} awards)  {org_name(oid)}")

    print("\n--- 10 biggest single awards ---")
    for amt, subj, ada in sorted(biggest, reverse=True)[:10]:
        print(f"€{amt:>12,.0f}  {subj}  [{ada}]")


if __name__ == "__main__":
    main(sys.argv[1])
