# 🔒 Mullvad VPN – Blocked & Broken Sites Tracker

> **Live site:** https://welshman.github.io/mullvad-blocked-sites/

Automatically updated **daily** list of websites that don't work properly when connected to [Mullvad VPN](https://mullvad.net). No human interaction needed — everything runs on GitHub Actions.

## Features

- 🤖 **Fully automated** — GitHub Actions updates data every day at 06:00 UTC
- 🔍 **Community-sourced** — pulls new reports from r/mullvadvpn weekly posts
- 🏷️ **Categorised** — Streaming, Finance, Shopping, Social, etc.
- ⚡ **Fast** — pure static site, no backend, hosted free on GitHub Pages
- 🔎 **Searchable & filterable** — by domain, category, or status

## Status Types

| Status | Meaning |
|---|---|
| 🚫 Blocked | Site fully refuses Mullvad connections |
| ⚠️ Partial | Some features broken or unreliable |
| ⚠️ Captcha Loop | Endless CAPTCHA challenges |

## How It Works

1. `scripts/update_sites.py` runs daily via `.github/workflows/daily-update.yml`
2. The script refreshes `data/sites.json` with today's date and pulls community reports
3. GitHub Pages redeploys `index.html` automatically, which reads the JSON
4. The live website always shows fresh data with zero manual work

## Contributing

Found a site that doesn't work with Mullvad? [Open an issue](https://github.com/welshman/mullvad-blocked-sites/issues) with the domain and what breaks.

---
*Not affiliated with Mullvad AB.*
