# Security

This repo contains a small Python pipeline and public exchange-rate data. It stores no secrets and runs no server.

## Reporting

Report vulnerabilities privately via GitHub: Security tab > "Report a vulnerability". Do not open a public issue.

In scope: the fetch/normalize scripts, the GitHub Actions workflow, and anything that could let a third party alter published data.

## Data integrity

Published data is regenerated from CBN's public endpoints on every run. If you find published rates that don't match the CBN source, open a regular issue with the date and currency.
