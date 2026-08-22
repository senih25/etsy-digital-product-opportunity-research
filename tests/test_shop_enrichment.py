from __future__ import annotations

from datetime import UTC, datetime

import pytest

from etsy_research.etsy_client import EtsyClient, EtsyClientError, RequestMetadata
from etsy_research.models import RawObservation
from etsy_research.normalize import build_canonical_listings, build_canonical_shops
from etsy_research.pilot import collect_unique_shop_ids, fetch_official_shops, parse_shop_record


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


def test_collect_unique_shop_ids_is_sorted_and_deduped() -> None:
    observations = [
        _observation(query_id="q2", listing_id="222", shop_id="shop-b", rank=2),
        _observation(query_id="q1", listing_id="111", shop_id="shop-a", rank=1),
        _observation(query_id="q3", listing_id="333", shop_id="shop-b", rank=3),
    ]

    assert collect_unique_shop_ids(observations) == ["shop-a", "shop-b"]


def test_parse_shop_record_keeps_missing_fields_null() -> None:
    retrieved_at = datetime(2026, 8, 22, tzinfo=UTC)
    shop = parse_shop_record(
        {"shop_id": "shop-a", "shop_name": "Shop A"},
        requested_shop_id="shop-a",
        retrieved_at=retrieved_at,
    )

    assert shop.shop_id == "shop-a"
    assert shop.shop_name == "Shop A"
    assert shop.review_count is None
    assert shop.transaction_sold_count is None
    assert shop.created_timestamp is None
    assert shop.listing_active_count is None
    assert shop.digital_listing_count is None
    assert shop.num_favorers is None
    assert shop.source_endpoint == "getShop"
    assert shop.retrieved_at == retrieved_at


def test_parse_shop_record_parses_official_fields() -> None:
    retrieved_at = datetime(2026, 8, 22, tzinfo=UTC)
    shop = parse_shop_record(
        {
            "shop_id": 123,
            "shop_name": "Shop 123",
            "review_count": "42",
            "review_average": "4.8",
            "transaction_sold_count": "900",
            "created_timestamp": 1_725_148_800,
            "listing_active_count": "12",
            "digital_listing_count": 4,
            "num_favorers": "18",
        },
        requested_shop_id="123",
        retrieved_at=retrieved_at,
    )

    assert shop.shop_id == "123"
    assert shop.shop_name == "Shop 123"
    assert shop.review_count == 42
    assert shop.review_average == pytest.approx(4.8)
    assert shop.transaction_sold_count == 900
    assert shop.created_timestamp == datetime(2024, 9, 1, tzinfo=UTC)
    assert shop.listing_active_count == 12
    assert shop.digital_listing_count == 4
    assert shop.num_favorers == 18


def test_fetch_official_shops_dedupes_and_handles_partial_failure() -> None:
    class FakeClient(EtsyClient):
        def __init__(self) -> None:
            super().__init__("keystring", "shared-secret", max_retries=1, backoff_factor=0.0)
            self.calls: list[str] = []

        def get_shop(self, shop_id: str | int):
            shop_id_text = str(shop_id)
            self.calls.append(shop_id_text)
            if shop_id_text == "shop-b":
                raise EtsyClientError("boom", status_code=500)
            return (
                {
                    "shop_id": shop_id_text,
                    "shop_name": f"Shop {shop_id_text[-1]}",
                    "review_count": 10,
                    "transaction_sold_count": 100,
                    "created_timestamp": 1_725_148_800,
                    "listing_active_count": 1,
                    "digital_listing_count": 1,
                    "num_favorers": 5,
                },
                RequestMetadata(method="GET", url="https://example.invalid", attempt=1, timeout_seconds=30.0),
            )

    client = FakeClient()
    retrieved_at = datetime(2026, 8, 22, tzinfo=UTC)
    observations = [
        _observation(query_id="q1", listing_id="111", shop_id="shop-b", rank=1),
        _observation(query_id="q2", listing_id="222", shop_id="shop-a", rank=2),
        _observation(query_id="q3", listing_id="333", shop_id="shop-a", rank=3),
    ]
    listings, _ = build_canonical_listings(observations)

    enriched_shops, failed_shop_ids = fetch_official_shops(client, [obs.shop_id for obs in observations if obs.shop_id], retrieved_at=retrieved_at)
    canonical_shops = build_canonical_shops(listings, shops=enriched_shops)

    assert client.calls == ["shop-a", "shop-b"]
    assert failed_shop_ids == ["shop-b"]
    assert [shop.shop_id for shop in enriched_shops] == ["shop-a"]

    shop_a = next(shop for shop in canonical_shops if shop.shop_id == "shop-a")
    shop_b = next(shop for shop in canonical_shops if shop.shop_id == "shop-b")

    assert shop_a.review_count == 10
    assert shop_a.source_endpoint == "getShop"
    assert shop_a.retrieved_at == retrieved_at
    assert shop_a.listing_ids == ["222", "333"]

    assert shop_b.review_count is None
    assert shop_b.transaction_sold_count is None
    assert shop_b.created_timestamp is None
    assert shop_b.listing_ids == ["111"]
