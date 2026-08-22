# Etsy API Terms Guardrails

Status: **Binding project policy**

Source basis: Etsy API Terms supplied and reviewed on 2026-08-22. These guardrails must be checked before any new data-source, crawler, browser-automation, storage, publication, monetization, or Etsy integration work.

## 1. Supported access path

- Programmatic Etsy marketplace access must use the supported Etsy API.
- Do not automate Etsy.com pages with crawlers, spiders, bots, headless browsers, scripted screenshots, DOM extraction, or similar tooling unless Etsy gives explicit authorization.
- Do not inspect or reverse-engineer Etsy internal/private/legacy APIs or internal data flows.
- Chrome DevTools MCP may be used for this repository's own local application/testing surfaces, but **not** to programmatically inspect Etsy.com pages, capture Etsy pages, or extract Etsy marketplace data.
- Firecrawl must not crawl or scrape Etsy.com. Firecrawl may be used only for non-Etsy external-web research where permitted by the target source.

## 2. Data minimization and retention

- Etsy member content belongs to Etsy members, not to this project.
- Do not persist Etsy member content longer than reasonably necessary to provide the permitted function.
- Product information and/or images displayed by an application must not be more than 6 hours older than the corresponding Etsy.com content.
- Other Etsy content displayed by an application must not be more than 24 hours older than Etsy.com.
- For RQ2 research, prefer ephemeral API cache plus durable **derived aggregate metrics** that do not reproduce member content.
- Do not make long-term archives of titles, descriptions, images, shop stories, profile text, or other member content.
- `research/rq2/raw/` remains local, gitignored, temporary, and must be subject to deletion/expiry controls before live research begins.

## 3. Member rights and privacy

- Respect restrictions Etsy members place on use of their content.
- Do not collect, store, publish, share, transfer, or process personal information about Etsy members unless that member has specifically authorized it.
- Never collect or store Etsy username/password combinations, cookies, session tokens, browser credentials, or equivalent authentication material.
- No private member data is required for RQ2.

## 4. Product information and attribution

- If the application displays Etsy product information and/or images, provide a direct link back to the corresponding Etsy product/content.
- Do not present Etsy member content as project-owned content.
- Do not imply Etsy endorsement, certification, partnership, agency, or affiliation.

Required trademark notice when Etsy marks/API are referenced in the application:

> "Etsy" is a trademark of Etsy, Inc. This application uses the Etsy API but is not endorsed or certified by Etsy, Inc.

The Etsy name/logo/marks must be less prominent than the project's own identity and must not imitate Etsy's branding, signature colors, layout, or trade dress in a confusing way.

## 5. Public application obligations

The public application/review surface must provide:

- a clearly visible contact email;
- a visible privacy policy;
- commercially reasonable terms of service;
- honest, accurate, current application descriptions;
- developer-provided customer/support contact.

Current public contact email approved for this project surface:

`senih@senihbayankulu.com`

## 6. Rate limits and service stability

- Keep request volume reasonable and conservative.
- Default Etsy allowance stated in the supplied terms is 10,000 calls/day; current platform headers/docs must still be treated as authoritative at runtime.
- Honor rate limits and `Retry-After`.
- No aggressive parallelism or behavior that can impair Etsy, its members, or other applications.
- Never bypass API security measures or technical limits.

## 7. Commercial-use boundary

- Do not sell, rent, sublicense, or resell Etsy API access or Etsy member content.
- Do not charge users for access to functionality whose paid value is merely Etsy API integration or a feature Etsy provides its members for free.
- Revenue may come from project-owned products/services or application components that are not simply resold API access/member content.
- Do not use the API primarily to divert traffic from Etsy to another marketplace/service.
- If the planned commercial use is ambiguous, exceeds reasonable limits, or may exceed 10,000 calls/day, stop and seek Etsy guidance before implementation.

## 8. Research-specific controls

For RQ2 and later opportunity research:

**Allowed by project policy**

- Official Etsy Open API calls within granted access.
- Local deterministic normalization and aggregate analysis.
- Short-lived cache needed to perform analysis.
- Persisting aggregate counts, percentiles, concentration metrics, cohort statistics, run metadata, query configuration, and reproducibility metadata when they do not reproduce member content.
- External-web research through Firecrawl only outside Etsy.com and subject to the external source's terms.

**Blocked by project policy**

- Etsy SERP scraping.
- Automated Etsy screenshots for extraction/analysis.
- Chrome DevTools MCP automation against Etsy.com.
- DOM/network/private-endpoint extraction from Etsy.com.
- Reverse engineering hidden Etsy endpoints.
- Long-term raw Etsy content archives.
- Publishing member content without the required rights/links/freshness handling.
- Credential/session extraction.

## 9. Change control

Etsy may change its terms and policies. Before enabling a materially new capability, perform a fresh terms/policy check.

Any proposed change involving one of these areas requires a compliance gate before code is written:

- new Etsy endpoint or scope;
- OAuth/private data;
- write operations;
- messaging/orders/shop management;
- browser automation;
- scraping/crawling;
- content/image display;
- data-retention expansion;
- monetization of API-derived functionality;
- use of Etsy trademarks/logos.

Decision states:

- `TERMS_GATE=PASS`
- `TERMS_GATE=BLOCKED`
- `TERMS_GATE=NEEDS_ETSY_CLARIFICATION`

When uncertain, choose `NEEDS_ETSY_CLARIFICATION` rather than implementing around the restriction.
