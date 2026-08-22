# Etsy OpenAPI Spec Audit

## Scope

This audit covers the Etsy Open API v3 endpoints used by RQ2 read-only search and shop enrichment:

- `findAllListingsActive`
- `getShop`

No live Etsy marketplace API calls were made.

## A. `findAllListingsActive`

| Item | Verified value |
|---|---|
| Operation ID | `findAllListingsActive` |
| Method | `GET` |
| Path | `/v3/application/listings/active` |
| Authentication | `api_key` |
| OAuth | Not required for this endpoint |
| Query params | `keywords` |
| Query params | `limit` |
| Query params | `offset` |
| Query params | `sort_on` |
| Query params | `sort_order` |
| `keywords` | string, default `null` |
| `limit` | integer `1..100`, default `25` |
| `offset` | integer `>= 0`, default `0` |
| `sort_on` | string, default `created`, enum `created`, `price`, `updated`, `score` |
| `sort_order` | string, default `desc`, enum `asc`, `ascending`, `desc`, `descending`, `up`, `down` |
| Sort note | `sort_order` only applies when combined with a search option such as `keywords`; without it, results are newest-first by default |
| Response model | JSON object with `count` and `results` |
| Pagination behavior | `offset` skips records; `limit` caps page size; the endpoint returns paged search results ordered by the selected sort |

## B. `getShop`

| Item | Verified value |
|---|---|
| Operation ID | `getShop` |
| Method | `GET` |
| Path | `/v3/application/shops/{shop_id}` |
| Authentication | `api_key` |
| OAuth | Not required for this endpoint |
| Response schema | Shop object with official shop metadata fields |

### Verified field availability

The following fields are documented in the official response samples and were verified as available for `getShop`:

- `shop_id`
- `shop_name`
- `review_count`
- `review_average`
- `transaction_sold_count`
- `created_timestamp`
- `listing_active_count`
- `digital_listing_count`
- `num_favorers`

## Notes

- The reference page also shows additional shop fields such as `user_id`, `create_date`, `title`, `announcement`, `login_name`, and policy fields.
- Those extra fields are not part of the canonical shop payload for this project unless explicitly needed.
- `getShop` is read-only and does not require seller OAuth for this RQ2 workflow.

