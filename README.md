# Etsy Digital Product Opportunity Research

Public, read-only research tooling for digital product opportunity analysis and RQ2 new-seller visibility research.

This repository is the canonical source for deterministic analysis of publicly available Etsy active listings through the supported Etsy Open API. It is not a product generator, Etsy automation bot, scraper-first system, listing publisher, dashboard, or SaaS backend.

Current research question:

- RQ2 - Can new or low-review shops appear in Etsy Open API keyword-relevance results for relevant digital-product tool categories?

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
- scrape or crawl Etsy.com
- automate Etsy.com through Chrome DevTools, browser bots, screenshots, DOM extraction, or internal/private endpoints

Data source policy:

1. Etsy Open API v3 is the supported programmatic source for Etsy marketplace data.
2. Automated access to Etsy.com pages is out of scope unless Etsy explicitly authorizes it.
3. Firecrawl may be used only for non-Etsy external-web research where permitted by the target source.
4. Chrome DevTools MCP may be used for this project's own local/testing surfaces, not to programmatically inspect or extract data from Etsy.com.

Important:

- API rank != user-visible Etsy rank. Treat this as API Search Entry Signal, not SERP visibility unless the official API explicitly defines it that way.
- Live pilot is blocked until local Etsy API credentials are present.
- `ETSY_API_KEYSTRING` and `ETSY_SHARED_SECRET` are required for live preflight and future campaign runs.
- The Etsy `x-api-key` header is composed as `keystring:shared_secret`.
- API credentials stay local and are never committed.
- Live raw Etsy member content must be treated as temporary cache, not a durable research archive.
- Durable research outputs should prefer derived aggregate metrics that do not reproduce Etsy member content.
- All new Etsy integrations must pass the binding [Etsy API Terms Guardrails](ETSY-API-TERMS-GUARDRAILS.md) before implementation.

Public documentation:

- [Purpose](PURPOSE.md)
- [Privacy](PRIVACY.md)
- [API Usage](API-USAGE.md)
- [Security](SECURITY.md)
- [Methodology](RESEARCH-METHODOLOGY.md)
- [Etsy API Terms Guardrails](ETSY-API-TERMS-GUARDRAILS.md)
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

Project contact:

- `senih@senihbayankulu.com`

Trademark notice:

> "Etsy" is a trademark of Etsy, Inc. This application uses the Etsy API but is not endorsed or certified by Etsy, Inc.
