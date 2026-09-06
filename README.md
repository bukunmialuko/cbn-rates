# cbn-rates

Official Central Bank of Nigeria exchange rates as CSV and JSON. Updated twice daily.

## Data

| File | Contents |
|---|---|
| [`data/latest.json`](data/latest.json) | Current rate per currency |
| [`data/rates.csv`](data/rates.csv) | Full history since 2001. `date,code,buy,mid,sell` |
| [`data/nfem.csv`](data/nfem.csv) | NFEM daily USD stats since Dec 2024 |

## Use

```
https://raw.githubusercontent.com/bukunmialuko/cbn-rates/main/data/latest.json
https://raw.githubusercontent.com/bukunmialuko/cbn-rates/main/data/rates.csv
https://raw.githubusercontent.com/bukunmialuko/cbn-rates/main/data/nfem.csv
```

Rates are NGN per one unit of the currency. Codes are ISO 4217.

See [docs](docs/README.md) for sources, update process, and cleaning rules.

## License

Code is MIT. The rate data is published by the Central Bank of Nigeria and remains theirs; this repo reformats it and offers no warranty on accuracy.
