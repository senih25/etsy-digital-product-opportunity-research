# API Usage

Primary API: Etsy Open API v3.

Primary endpoint: `findAllListingsActive` or the current official equivalent.

Current path used by the research client: `GET /listings/active`.

Authentication model:

- `x-api-key = keystring:shared_secret`
- real values are never published

Current use:

- public active-listing research only
- no seller OAuth for the current RQ2 workflow

Programmatic access policy:

- Etsy Open API is the supported programmatic path for Etsy marketplace data.
- Do not scrape/crawl Etsy.com.
- Do not use Chrome DevTools MCP, browser automation, scripted screenshots, DOM extraction, or network inspection to extract Etsy.com marketplace data.
- Do not access private, legacy, hidden, or internal Etsy endpoints.
- Firecrawl is not an Etsy data-source fallback; it may be used only for permitted non-Etsy external-web research.

Retention policy:

- Treat live Etsy member/product content as temporary working cache.
- Do not build durable archives of titles, descriptions, images, profile/shop text, or other member content.
- Product information/images displayed by an application must not be more than 6 hours older than Etsy.com.
- Other Etsy content displayed by an application must not be more than 24 hours older than Etsy.com.
- Prefer durable derived aggregate metrics that do not reproduce Etsy member content.
- `research/rq2/raw/` remains local, gitignored, and must have an expiry/deletion control before the live campaign begins.

Attribution and member-content policy:

- Respect member restrictions on use of their content.
- If product information/images are displayed, provide a direct link to the corresponding Etsy content.
- Do not collect or process personal Etsy-member data without specific authorization.

Rate-limit practices:

- conservative requests
- retry/backoff
- `Retry-After` handling
- no aggressive parallelism
- no bypass of technical limits
- no scraping fallback for data available through the official API

Commercial boundary:

- do not resell API access or Etsy member content
- do not charge merely for access to Etsy-provided API/free Etsy features
- do not use the API primarily to divert traffic away from Etsy
- seek Etsy clarification before ambiguous commercial API use or expected high-volume use

Binding project policy:

- [Etsy API Terms Guardrails](ETSY-API-TERMS-GUARDRAILS.md)

Official docs:

- https://developers.etsy.com/documentation/essentials/requests
- https://developers.etsy.com/documentation/reference
