# cbn-rates

Daily-updated, machine-readable history of official Central Bank of Nigeria exchange rates (NGN per unit of foreign currency), 2001 to today, plus NFEM daily USD market stats since Dec 2024.

## Files

| Path | What |
|---|---|
| `data/rates.csv` | Full history. `date,code,buy,mid,sell`. One row per currency per day. |
| `data/nfem.csv` | NFEM daily USD stats. `date,weighted_avg,simple_avg,high,low,close,deals_interbank,turnover_interbank_usd`. |
| `data/latest.json` | Most recent rate per currency and latest NFEM row. |
| `data/anomalies.csv` | Source rows dropped as duplicates or mislabeled conflicts. |
| `data/meta.json` | Provenance: source URLs, generation time, row counts, date range. |

Currency codes are ISO 4217. `XUA` = WAUA (West African Unit of Account), `XDR` = IMF SDR. CBN label variants (`DANISH KRONA`/`KRONER`, trailing spaces) are merged.

## Raw URLs

```
https://raw.githubusercontent.com/bukunmialuko/cbn-rates/main/data/latest.json
https://raw.githubusercontent.com/bukunmialuko/cbn-rates/main/data/rates.csv
https://raw.githubusercontent.com/bukunmialuko/cbn-rates/main/data/nfem.csv
```

## How it updates

A GitHub Action runs twice daily:

```bash
python scripts/fetch.py       # CBN JSON endpoints -> raw/ (gitignored)
python scripts/normalize.py   # raw/ -> data/
```

`data/` is fully rebuilt each run; a commit happens only when something changed. Git diff is the changelog. No dependencies beyond the Python standard library.

## Cleaning rules

- Labels stripped, uppercased, mapped to ISO codes.
- Duplicate `(code, date)` rows: identical copies dropped; conflicting values resolved by keeping the one closest to the previous day's mid rate. Rejects logged in `anomalies.csv`.
- Schema change, unknown label, or implausibly small payload aborts the run.

## Source

Central Bank of Nigeria:
- `https://www.cbn.gov.ng/api/GetAllExchangeRates?format=json`
- `https://www.cbn.gov.ng/api/GetAllNFEM_Rates`

Data belongs to CBN; this repo only reformats it.
