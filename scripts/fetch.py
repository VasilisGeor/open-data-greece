#!/usr/bin/env python3
"""Fetch Diavgeia decisions for a given type and date range into JSONL.

Usage: python3 fetch.py --type Δ.1 --from 2026-05-01 --to 2026-05-31 --out data/raw/d1_2026-05.jsonl
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://diavgeia.gov.gr/opendata/search.json"
PAGE_SIZE = 500
SLEEP_S = 0.7
MAX_RETRIES = 4


def get_page(dtype: str, date_from: str, date_to: str, page: int) -> dict:
    params = urllib.parse.urlencode({
        "type": dtype,
        "from_issue_date": date_from,
        "to_issue_date": date_to,
        "size": PAGE_SIZE,
        "page": page,
    })
    req = urllib.request.Request(f"{BASE}?{params}", headers={"Accept": "application/json"})
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            wait = 2 ** (attempt + 1)
            print(f"  page {page} attempt {attempt + 1} failed ({e}), retrying in {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"page {page} failed after {MAX_RETRIES} retries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", dest="dtype", required=True)
    ap.add_argument("--from", dest="date_from", required=True)
    ap.add_argument("--to", dest="date_to", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    first = get_page(args.dtype, args.date_from, args.date_to, 0)
    total = first["info"]["total"]
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"{args.dtype} {args.date_from}..{args.date_to}: {total} decisions, {pages} pages")

    written = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for page in range(pages):
            data = first if page == 0 else get_page(args.dtype, args.date_from, args.date_to, page)
            decisions = data.get("decisions", [])
            for d in decisions:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
            written += len(decisions)
            print(f"  page {page + 1}/{pages} -> {written}/{total}")
            if page + 1 < pages:
                time.sleep(SLEEP_S)
    print(f"done: {written} decisions -> {args.out}")


if __name__ == "__main__":
    main()
