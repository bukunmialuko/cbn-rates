# cbn-rates

Machine-readable history of official CBN exchange rates. Data repo only; the MCP server lives in a separate repo (`naira-mcp`). Remote: https://github.com/bukunmialuko/cbn-rates

## Layout

- `scripts/fetch.py` downloads CBN JSON endpoints into `raw/` (gitignored)
- `scripts/normalize.py` rebuilds everything in `data/` from `raw/`
- `data/rates.csv` canonical history, `date,code,buy,mid,sell`, ISO 4217 codes
- `data/nfem.csv` NFEM daily USD stats
- `data/latest.json`, `data/meta.json`, `data/anomalies.csv` derived outputs
- `.github/workflows/update.yml` scheduled fetch + normalize + commit-if-changed
- `docs/README.md` full explanation; root `README.md` stays short and functional

## Rules

- Rebuild, never append. `data/` is fully regenerated from `raw/`; git diff is the changelog.
- Never hand-edit files in `data/`. Fix the script or the raw file.
- Unknown currency label or schema change must abort the run, not be silently skipped.
- Python standard library only. No third-party dependencies.
- Verify with `python scripts/fetch.py && python scripts/normalize.py` before proposing a commit.

## Commits

- **One-line conventional commits only.** `type(scope): subject` on a single
  line. No body, no footer, no bullet list.
- **Never add `Co-Authored-By`** or any other trailer. Nothing that attributes
  the commit to Claude.
- **Suggest, never apply.** End a response with a proposed commit when there are
  uncommitted changes worth committing. Only run `git commit` when explicitly
  told to.
- Types: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `build`, `perf`.
- Subject in imperative mood, lowercase, no trailing period.
