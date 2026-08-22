# Etsy Digital Product Opportunity Research

Purpose: RQ2 Etsy new-seller visibility research.

This repository is a read-only, reproducible research scaffold. It is not a product generator, Etsy automation bot, scraper, listing publisher, dashboard, or SaaS backend.

Data source priority:

1. Etsy Open API v3
2. Browser validation
3. DevTools verification
4. Firecrawl for external intelligence only

Important:

- API rank is not the same as visible Etsy SERP rank.
- Live market verdicts require real Etsy data.
- `ETSY_API_KEY` is required for live preflight and future campaign runs.

Current scope:

- RQ2 research scaffold
- config and threshold validation
- deterministic normalization and analysis
- synthetic fixture analysis
- read-only Etsy API client preflight

Quick start:

```powershell
python -m etsy_research.cli validate-config
python -m etsy_research.cli analyze-fixture tests/fixtures/strong_entry.json
python -m etsy_research.cli preflight
```

Official Etsy docs referenced by the scaffold:

- [Request standards](https://developers.etsy.com/documentation/essentials/requests)
- [API reference](https://developers.etsy.com/documentation/reference)

