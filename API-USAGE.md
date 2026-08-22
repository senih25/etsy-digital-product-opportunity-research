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

Rate-limit practices:

- conservative requests
- retry/backoff
- `Retry-After` handling
- no aggressive parallelism
- no scraping fallback for data already available via the official API

Official docs:

- https://developers.etsy.com/documentation/essentials/requests
- https://developers.etsy.com/documentation/reference
