#!/usr/bin/env python3
"""Download the CBN exchange-rate and NFEM datasets into raw/.

Usage: python scripts/fetch.py
Aborts on HTTP error, non-JSON body, or an implausibly small payload.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"

SOURCES = {
    "exchange-rates.json": ("https://www.cbn.gov.ng/api/GetAllExchangeRates?format=json", 50_000),
    "nfem.json": ("https://www.cbn.gov.ng/api/GetAllNFEM_Rates", 100),
}

UA = "cbn-rates (+https://github.com/bukunmialuko/cbn-rates)"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        if resp.status != 200:
            sys.exit(f"{url}: HTTP {resp.status}")
        return resp.read()


def main():
    RAW.mkdir(exist_ok=True)
    for name, (url, min_rows) in SOURCES.items():
        body = fetch(url)
        data = json.loads(body)
        if not isinstance(data, list) or len(data) < min_rows:
            sys.exit(f"{name}: expected >= {min_rows} rows, got {len(data) if isinstance(data, list) else type(data)}")
        (RAW / name).write_text(json.dumps(data, separators=(",", ":")) + "\n")
        print(f"{name}: {len(data)} rows")


if __name__ == "__main__":
    main()
