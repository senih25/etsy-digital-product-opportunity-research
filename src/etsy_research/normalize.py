from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable

from .models import CanonicalListing, CanonicalShop, RawObservation


def normalize_listing_id(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _dedupe_key(observation: RawObservation) -> str:
    return normalize_listing_id(observation.listing_id) or observation.raw_source_ref or observation.query_id


def build_canonical_listings(
    observations: Iterable[RawObservation],
) -> tuple[list[CanonicalListing], int]:
    canonical: dict[str, CanonicalListing] = {}
    duplicate_observation_count = 0

    for observation in observations:
        listing_id = normalize_listing_id(observation.listing_id)
        if listing_id is None:
            continue

        existing = canonical.get(listing_id)
        if existing is None:
            canonical[listing_id] = CanonicalListing(
                listing_id=listing_id,
                shop_id=observation.shop_id,
                title=observation.title,
                description=observation.description,
                price_amount=observation.price_amount,
                price_currency=observation.price_currency,
                taxonomy_id=observation.taxonomy_id,
                created_at=observation.created_at,
                updated_at=observation.updated_at,
                tags=list(observation.tags),
                url=observation.url,
                raw_observation_ids=[observation.raw_source_ref or f"{observation.query_id}:{observation.api_rank}"],
                query_ids=[observation.query_id],
                first_seen_at=observation.retrieved_at,
                last_seen_at=observation.retrieved_at,
            )
            continue

        duplicate_observation_count += 1
        if existing.shop_id is None:
            existing.shop_id = observation.shop_id
        if existing.title is None:
            existing.title = observation.title
        if existing.description is None:
            existing.description = observation.description
        if existing.price_amount is None:
            existing.price_amount = observation.price_amount
        if existing.price_currency is None:
            existing.price_currency = observation.price_currency
        if existing.taxonomy_id is None:
            existing.taxonomy_id = observation.taxonomy_id
        if existing.created_at is None:
            existing.created_at = observation.created_at
        if existing.updated_at is None:
            existing.updated_at = observation.updated_at
        if not existing.tags and observation.tags:
            existing.tags = list(observation.tags)
        if existing.url is None:
            existing.url = observation.url
        if observation.raw_source_ref:
            existing.raw_observation_ids.append(observation.raw_source_ref)
        else:
            existing.raw_observation_ids.append(f"{observation.query_id}:{observation.api_rank}")
        if observation.query_id not in existing.query_ids:
            existing.query_ids.append(observation.query_id)
        if existing.first_seen_at is None or observation.retrieved_at < existing.first_seen_at:
            existing.first_seen_at = observation.retrieved_at
        if existing.last_seen_at is None or observation.retrieved_at > existing.last_seen_at:
            existing.last_seen_at = observation.retrieved_at

    return list(canonical.values()), duplicate_observation_count


def build_canonical_shops(
    listings: Iterable[CanonicalListing],
    shops: Iterable[CanonicalShop] | None = None,
) -> list[CanonicalShop]:
    shop_map: dict[str, CanonicalShop] = {}

    for shop in shops or []:
        shop_map[shop.shop_id] = shop.model_copy(deep=True)

    for listing in listings:
        if listing.shop_id is None:
            continue
        shop = shop_map.get(listing.shop_id)
        if shop is None:
            shop = CanonicalShop(
                shop_id=listing.shop_id,
                shop_name=None,
                review_count=None,
                sales_count=None,
                shop_created_at=None,
                active_listing_count=None,
                maturity_source="derived",
                listing_ids=[],
            )
            shop_map[listing.shop_id] = shop
        if listing.listing_id not in shop.listing_ids:
            shop.listing_ids.append(listing.listing_id)
        if shop.active_listing_count is None or len(shop.listing_ids) > shop.active_listing_count:
            shop.active_listing_count = len(shop.listing_ids)
        if shop.maturity_source == "derived" and listing.shop_id:
            shop.maturity_source = "derived_from_listings"

    return list(shop_map.values())

