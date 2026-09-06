# How cbn-rates works

## Sources

The CBN rates page is backed by two unauthenticated JSON endpoints:

- `https://www.cbn.gov.ng/api/GetAllExchangeRates?format=json` — full exchange-rate history for all currencies, 2001 to today (~62k rows, ~8MB).
- `https://www.cbn.gov.ng/api/GetAllNFEM_Rates` — NFEM daily USD market stats (weighted average, high, low, close, turnover) since December 2024.

Both match the "Export to Excel" download on the CBN site.

## Update process

A GitHub Action (`.github/workflows/update.yml`) runs at 06:00 and 18:00 UTC:

```bash
python scripts/fetch.py       # endpoints -> raw/ (gitignored)
python scripts/normalize.py   # raw/ -> data/
```

`data/` is rebuilt from scratch on every run, never appended to. A commit is made only when output changed, so git history is the changelog and CBN revisions to old rates are picked up automatically.

Python standard library only.

## Output files

| File | Description |
|---|---|
| `data/rates.csv` | One row per `(date, code)`. Columns `date,code,buy,mid,sell`. Sorted by date then code. |
| `data/nfem.csv` | One row per date. Columns `date,weighted_avg,simple_avg,high,low,close,deals_interbank,turnover_interbank_usd`. |
| `data/latest.json` | `{base, as_of, rates: {CODE: {name, date, buy, mid, sell}}, nfem: {...}}` |
| `data/anomalies.csv` | Source rows dropped during cleaning, with a reason. |
| `data/meta.json` | Source URLs, generation timestamp, row counts, date range, currency list. |

## Currency codes

| CBN label | Code |
|---|---|
| US DOLLAR | USD |
| POUNDS STERLING, POUND STERLING | GBP |
| EURO | EUR |
| YEN, JAPANESE YEN | JPY |
| CFA | XOF |
| RIYAL | SAR |
| SWISS FRANC | CHF |
| SDR | XDR |
| WAUA | XUA |
| YUAN/RENMINBI | CNY |
| DANISH KRONA, DANISH KRONER | DKK |
| SOUTH AFRICAN RAND | ZAR |
| UAE DIRHAM | AED |
| NAIRA | NGN (8 source rows, likely mislabeled) |
| POESO | UNKNOWN (3 source rows, CBN typo, excluded from `latest.json`) |

## Cleaning rules

- Labels are stripped of whitespace, uppercased, and mapped to the codes above. An unknown label aborts the run.
- Duplicate `(code, date)` rows with identical values: one is kept, the rest logged as `identical_duplicate`.
- Duplicate rows with conflicting values (usually one currency's rate mislabeled as another): the value closest to that currency's previous-day mid rate is kept, the rest logged as `conflict_rejected`.
- A schema change or an implausibly small payload aborts the run so a broken fetch never overwrites good data.

## Running locally

```bash
git clone https://github.com/bukunmialuko/cbn-rates
cd cbn-rates
python scripts/fetch.py && python scripts/normalize.py
```
