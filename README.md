# Etsy Digital Product Opportunity Research

Public, read-only research tooling for digital product opportunity analysis and RQ2 new-seller visibility research.

This repository is the canonical source for deterministic analysis of publicly available Etsy active listings. It is not a product generator, Etsy automation bot, scraper-first system, listing publisher, dashboard, or SaaS backend.

Current research question:

- RQ2 - Can new or low-review shops gain visibility in relevant Etsy digital-product tool categories?

Research topics:

- pricing
- competition
- listing concentration
- new-seller visibility
- product-category structure

What this repository does not do:

- create listings
- edit listings
- delete listings
- purchase items
- send messages
- manage shops
- access private member data
- use seller OAuth for the current RQ2 workflow

Data source priority:

1. Etsy Open API v3
2. Etsy browser validation
3. Chrome DevTools MCP
4. Firecrawl for external-web research only

Important:

- API rank != user-visible Etsy SERP rank.
- Live pilot is blocked until local Etsy API credentials are present.
- `ETSY_API_KEYSTRING` and `ETSY_SHARED_SECRET` are required for live preflight and future campaign runs.
- The Etsy `x-api-key` header is composed as `keystring:shared_secret`.
- API credentials stay local and are never committed.

Public documentation:

- [Purpose](PURPOSE.md)
- [Privacy](PRIVACY.md)
- [API Usage](API-USAGE.md)
- [Security](SECURITY.md)
- [Methodology](RESEARCH-METHODOLOGY.md)
- [Public landing page](docs/index.html)

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
