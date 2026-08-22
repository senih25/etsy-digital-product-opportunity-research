# RQ2 Shop Maturity Model

## Claim

Representation of low-maturity shops within Etsy Open API keyword-relevance results.

This is a diagnostic model only. It does not change GO / CONDITIONAL_GO / NO_GO thresholds or score weights.

## Canonical shop fields

Official shop enrichment uses only the verified `getShop` fields below.

- `shop_id`
- `shop_name`
- `review_count`
- `review_average`
- `transaction_sold_count`
- `created_timestamp`
- `listing_active_count`
- `digital_listing_count`
- `num_favorers`

Metadata tracked with the canonical record:

- `source_endpoint`
- `retrieved_at`

Missing values remain `null`. They are never coerced to zero.

## Diagnostic buckets

### Review cohorts

- `A`: 0-25 reviews
- `B`: 26-100 reviews
- `C`: 101-500 reviews
- `D`: 501-2000 reviews
- `E`: 2001+ reviews

### Sales maturity buckets

- `0-100`
- `101-500`
- `501-2000`
- `2001-10000`
- `10001+`

### Shop-age buckets

The age buckets are deterministic and use day-based cutoffs for repeatability:

- `<6 months` -> under 183 days
- `6-12 months` -> 183 to 364 days
- `1-2 years` -> 365 to 729 days
- `2-5 years` -> 730 to 1824 days
- `5+ years` -> 1825+ days

## Helper semantics

Implemented helpers:

- `assign_review_cohort()`
- `assign_sales_maturity_bucket()`
- `assign_shop_age_bucket()`
- `calculate_low_review_shop_share()`
- `calculate_low_sales_shop_share()`
- `calculate_young_shop_share()`
- `calculate_unique_low_maturity_shop_count()`
- `calculate_review_median()`
- `calculate_sales_median()`
- `calculate_shop_age_median_days()`

Rules:

- Missing values are excluded from denominators.
- Shares return `None` when no evaluable values exist.
- Counts return `None` when no evaluable values exist and `0` only when the evaluable set exists but none qualify.
- Shop-age calculations use an explicit reference time when provided.

## Join behavior

The enrichment path is deterministic:

1. `findAllListingsActive`
2. observations
3. extract `shop_id`
4. unique sorted shop IDs
5. `getShop` once per unique shop
6. canonical shop parse
7. deterministic join back onto the canonical listing set

If a shop lookup fails, the shop remains missing rather than being replaced with fabricated zero values.

## Score stability

- Existing score weights are unchanged.
- GO / CONDITIONAL_GO / NO_GO thresholds are unchanged.
- Review, sales, and age dimensions are diagnostic only until live pilot evidence is available.

## Verification status

- Tests cover review cohort boundaries, sales bucket boundaries, shop-age bucket boundaries, dedupe, partial enrichment failure, and fixture verdict stability.
- Live request count remains zero in this task.

