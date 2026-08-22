from __future__ import annotations

from datetime import UTC, datetime

from etsy_research.models import CanonicalShop, RawObservation
from etsy_research.normalize import build_canonical_listings, build_canonical_shops, normalize_listing_id


def _observation(*, query_id: str, listing_id: str, shop_id: str, rank: int) -> RawObservation:
    return RawObservation(
        research_run_id="run-1",
        query_id=query_id,
        query_family="FAMILY_A_ETSY_PROFIT",
        query_text="etsy profit calculator",
        retrieved_at=datetime(2026, 8, 22, tzinfo=UTC),
        source="etsy_open_api_v3",
        api_position=rank,
        api_rank=rank,
        listing_id=listing_id,
        shop_id=shop_id,
        title=f"Listing {listing_id}",
        price_amount=19.99,
        price_currency="USD",
        taxonomy_id="123",
        created_at=datetime(2026, 8, 1, tzinfo=UTC),
        updated_at=datetime(2026, 8, 2, tzinfo=UTC),
        tags=["calculator"],
        raw_source_ref=f"{query_id}:{rank}",
    )


def test_normalize_listing_id() -> None:
    assert normalize_listing_id(" 123 ") == "123"
    assert normalize_listing_id(123) == "123"
    assert normalize_listing_id(None) is None


def test_duplicate_listing_and_cross_query_preservation() -> None:
    observations = [
        _observation(query_id="q1", listing_id="111", shop_id="shop-a", rank=1),
        _observation(query_id="q2", listing_id="111", shop_id="shop-a", rank=2),
        _observation(query_id="q1", listing_id="222", shop_id="shop-a", rank=3),
    ]

    listings, duplicate_count = build_canonical_listings(observations)
    assert len(observations) == 3
    assert len(listings) == 2
    assert duplicate_count == 1

    listing_111 = next(item for item in listings if item.listing_id == "111")
    assert listing_111.query_ids == ["q1", "q2"]
    assert listing_111.raw_observation_ids == ["q1:1", "q2:2"]


def test_unique_shop_aggregation() -> None:
    observations = [
        _observation(query_id="q1", listing_id="111", shop_id="shop-a", rank=1),
        _observation(query_id="q1", listing_id="222", shop_id="shop-a", rank=2),
    ]

    listings, _ = build_canonical_listings(observations)
    shops = build_canonical_shops(
        listings,
        shops=[
            CanonicalShop(
                shop_id="shop-a",
                shop_name="Shop A",
                review_count=42,
                sales_count=100,
                shop_created_at=datetime(2024, 1, 1, tzinfo=UTC),
                active_listing_count=1,
                maturity_source="fixture",
            )
        ],
    )
    assert len(shops) == 1
    assert shops[0].listing_ids == ["111", "222"]
    assert shops[0].active_listing_count == 1
    assert shops[0].review_count == 42
