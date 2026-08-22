# Research Methodology

Canonical detailed methodology: [research/rq2/methodology.md](research/rq2/methodology.md)

This summary exists for the public review surface.

## Research question

Can new or low-review Etsy shops earn first-page visibility in functional digital product categories such as fee calculators, pricing calculators, bookkeeping workbooks, and seller tools?

## Unit of observation

- raw observation: one query result row as observed through the research pipeline
- canonical listing: one unique Etsy listing, deduped by `listing_id`
- canonical shop: one unique shop, aggregated across listings

## Cohorts

- A: 0-25 reviews
- B: 26-100 reviews
- C: 101-500 reviews
- D: 501-2000 reviews
- E: 2001+ reviews

Primary entry cohort: `<= 100` reviews.
Secondary entry cohort: `<= 500` reviews.

## Rank windows

Analyze visibility within top 10, top 20, top 50, and top 100 results.

## Concentration

Use simple shop concentration metrics:

- `CR5`: share of listings controlled by the top 5 shops
- `CR10`: share of listings controlled by the top 10 shops

## Entry score

The initial market entry score is a weighted average of five normalized signals:

- top 20 new-shop penetration
- top 50 new-shop penetration
- unique new-shop diversity
- recent listing penetration
- low incumbency concentration

Missing metrics are excluded from the denominator and the remaining weights are renormalized.

## Thresholds

The GO / CONDITIONAL_GO / NO_GO thresholds in `config/thresholds.json` are project hypotheses, not validated market truth.

## Limitations

- Etsy ranking algorithm is opaque
- personalization and location can change visibility
- ads and sponsored listings may distort rank
- API rank is not the same as browser-visible SERP rank
- review, sales, and freshness fields may be incomplete
- listing visibility does not imply revenue or conversion
- the same shop can appear multiple times and dominate the page
