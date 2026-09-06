#!/usr/bin/env python3
"""Normalize raw CBN JSON into canonical CSV/JSON.

Usage: python scripts/normalize.py

Reads:
  raw/exchange-rates.json   full history from /api/GetAllExchangeRates
  raw/nfem.json             NFEM daily USD stats from /api/GetAllNFEM_Rates
Writes:
  data/rates.csv            one row per (date, code): date,code,buy,mid,sell
  data/nfem.csv             one row per date: date,weighted_avg,simple_avg,high,low,close,deals_interbank,turnover_interbank_usd
  data/latest.json          most recent rate per currency + latest NFEM
  data/anomalies.csv        source rows rejected as duplicates/conflicts
  data/meta.json            provenance
"""
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
DATA = ROOT / "data"

# CBN label (stripped, uppercased) -> ISO 4217 code
CODES = {
    "US DOLLAR": "USD",
    "POUNDS STERLING": "GBP",
    "POUND STERLING": "GBP",
    "EURO": "EUR",
    "YEN": "JPY",
    "JAPANESE YEN": "JPY",
    "CFA": "XOF",
    "RIYAL": "SAR",
    "SWISS FRANC": "CHF",
    "SDR": "XDR",
    "WAUA": "XUA",
    "YUAN/RENMINBI": "CNY",
    "DANISH KRONA": "DKK",
    "DANISH KRONER": "DKK",
    "SOUTH AFRICAN RAND": "ZAR",
    "UAE DIRHAM": "AED",
    "NAIRA": "NGN",
    "POESO": "UNKNOWN",  # CBN typo, 3 rows, currency unclear
}

NAMES = {
    "USD": "US Dollar", "GBP": "Pound Sterling", "EUR": "Euro", "JPY": "Japanese Yen",
    "XOF": "CFA Franc", "SAR": "Saudi Riyal", "CHF": "Swiss Franc", "XDR": "IMF SDR",
    "XUA": "WAUA", "CNY": "Chinese Yuan", "DKK": "Danish Krone", "ZAR": "South African Rand",
    "AED": "UAE Dirham", "NGN": "Naira", "UNKNOWN": "Unknown",
}


def num(x):
    x = (x or "").strip()
    return round(float(x), 4) if x else None


def load_rates(path: Path):
    rows = json.loads(path.read_text())
    expected = {"currency", "ratedate", "buyingrate", "centralrate", "sellingrate"}
    out = []
    for r in rows:
        if not expected <= r.keys():
            sys.exit(f"schema changed: {sorted(r.keys())}")
        label = str(r["currency"]).strip().upper()
        code = CODES.get(label)
        if code is None:
            sys.exit(f"unknown currency label: {label!r}")
        date = str(r["ratedate"]).strip()[:10]
        datetime.strptime(date, "%Y-%m-%d")
        out.append({
            "date": date, "code": code, "label": label,
            "buy": num(r["buyingrate"]), "mid": num(r["centralrate"]), "sell": num(r["sellingrate"]),
        })
    return out


def load_nfem(path: Path):
    rows = json.loads(path.read_text())
    out = {}
    for r in rows:
        date = datetime.strptime(r["ratedate"], "%B-%d-%Y").strftime("%Y-%m-%d")
        out[date] = {
            "date": date,
            "weighted_avg": num(r["weightedAvgRate"]),
            "simple_avg": num(r["simpleAvgRate"]),
            "high": num(r["highestrate"]),
            "low": num(r["lowestrate"]),
            "close": num(r["closingrate"]),
            "deals_interbank": int(r["noOfDeals_InterBank"] or 0) or None,
            "turnover_interbank_usd": num(r["interBank_Total_Turnover"]),
        }
    return [out[d] for d in sorted(out)]


def dedupe(rows):
    by_key = defaultdict(list)
    for r in rows:
        by_key[(r["code"], r["date"])].append(r)

    kept, anomalies = [], []
    for code in sorted({k[0] for k in by_key}):
        dates = sorted(d for c, d in by_key if c == code)
        prev_mid = None
        for d in dates:
            cands = by_key[(code, d)]
            uniq = {(c["buy"], c["mid"], c["sell"]): c for c in cands}
            if len(uniq) == 1:
                chosen = cands[0]
                for extra in cands[1:]:
                    anomalies.append({**extra, "reason": "identical_duplicate"})
            else:
                if prev_mid is None:
                    chosen = min(uniq.values(), key=lambda c: c["mid"])
                else:
                    chosen = min(uniq.values(), key=lambda c: abs(c["mid"] - prev_mid))
                for c in uniq.values():
                    if c is not chosen:
                        anomalies.append({**c, "reason": f"conflict_rejected(prev_mid={prev_mid})"})
            kept.append(chosen)
            prev_mid = chosen["mid"]
    return kept, anomalies


def fmt(x):
    return "" if x is None else f"{x:.4f}"


def write(kept, anomalies, nfem):
    DATA.mkdir(exist_ok=True)
    kept.sort(key=lambda r: (r["date"], r["code"]))

    with (DATA / "rates.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "code", "buy", "mid", "sell"])
        for r in kept:
            w.writerow([r["date"], r["code"], fmt(r["buy"]), fmt(r["mid"]), fmt(r["sell"])])

    nfem_fields = ["date", "weighted_avg", "simple_avg", "high", "low", "close", "deals_interbank", "turnover_interbank_usd"]
    with (DATA / "nfem.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=nfem_fields)
        w.writeheader()
        for r in nfem:
            w.writerow({k: (fmt(v) if isinstance(v, float) else ("" if v is None else v)) for k, v in r.items()})

    with (DATA / "anomalies.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "code", "label", "buy", "mid", "sell", "reason"])
        w.writeheader()
        for a in sorted(anomalies, key=lambda r: (r["date"], r["code"])):
            w.writerow(a)

    latest = {}
    for r in kept:
        latest[r["code"]] = {"name": NAMES[r["code"]], "date": r["date"], "buy": r["buy"], "mid": r["mid"], "sell": r["sell"]}
    latest.pop("UNKNOWN", None)
    (DATA / "latest.json").write_text(json.dumps({
        "base": "NGN",
        "as_of": kept[-1]["date"],
        "rates": latest,
        "nfem": nfem[-1] if nfem else None,
    }, indent=2) + "\n")

    meta = {
        "source": "Central Bank of Nigeria",
        "source_urls": [
            "https://www.cbn.gov.ng/api/GetAllExchangeRates?format=json",
            "https://www.cbn.gov.ng/api/GetAllNFEM_Rates",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rates_rows": len(kept),
        "nfem_rows": len(nfem),
        "anomalies": len(anomalies),
        "first_date": kept[0]["date"],
        "last_date": kept[-1]["date"],
        "currencies": sorted(latest),
    }
    (DATA / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(f"rates {len(kept)} rows, nfem {len(nfem)} rows, {len(anomalies)} anomalies, {meta['first_date']}..{meta['last_date']}")


if __name__ == "__main__":
    kept, anomalies = dedupe(load_rates(RAW / "exchange-rates.json"))
    nfem = load_nfem(RAW / "nfem.json")
    write(kept, anomalies, nfem)
