from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from etsy_research.analyze import (
    assign_review_cohort,
    calculate_cr10,
    calculate_cr5,
    calculate_entry_score,
    calculate_price_summary,
    calculate_rank_window_metrics,
    calculate_recent_listing_share,
)
from etsy_research.models import CanonicalShop, RawObservation


def _shop(shop_id: str, review_count: int | None) -> CanonicalShop:
    return CanonicalShop(
        shop_id=shop_id,
        shop_name=shop_id,
        review_count=review_count,
        sales_count=review_count,
        shop_created_at=datetime(2024, 1, 1, tzinfo=UTC),
        active_listing_count=None,
        maturity_source="fixture",
    )


def _obs(rank: int, shop_id: str, *, created_at: datetime | None = None, price: float | None = None) -> RawObservation:
    return RawObservation(
        research_run_id="run-1",
        query_id="q1",
        query_family="FAMILY_A_ETSY_PROFIT",
        query_text="etsy profit calculator",
        retrieved_at=datetime(2026, 8, 22, tzinfo=UTC),
        source="etsy_open_api_v3",
        api_position=rank,
        api_rank=rank,
        listing_id=f"listing-{rank}",
        shop_id=shop_id,
        title=f"Listing {rank}",
        price_amount=price if price is not None else float(rank),
        price_currency="USD",
        taxonomy_id="123",
        created_at=created_at,
        updated_at=datetime(2026, 8, 22, tzinfo=UTC),
        tags=["calculator"],
        raw_source_ref=f"q1:{rank}",
    )


@pytest.mark.parametrize(
    ("review_count", "expected"),
    [
        (25, "A"),
        (26, "B"),
        (100, "B"),
        (101, "C"),
        (500, "C"),
        (501, "D"),
        (2000, "D"),
        (2001, "E"),
    ],
)
def test_assign_review_cohort_boundaries(review_count: int, expected: str) -> None:
    assert assign_review_cohort(review_count) == expected


@pytest.mark.parametrize("window_size, expected_count", [(10, 10), (20, 20), (50, 50), (100, 100)])
def test_rank_windows(window_size: int, expected_count: int) -> None:
    shops = [_shop(f"shop-{index}", 10 if index < 5 else 1000) for index in range(12)]
    observations = [_obs(rank=index + 1, shop_id=f"shop-{index % 12}") for index in range(120)]
    metrics = calculate_rank_window_metrics(observations, shops, window_size)
    assert metrics.observation_count == expected_count
    assert metrics.unique_listing_count == expected_count
    if window_size == 10:
        assert metrics.unique_shop_count == 10
    elif window_size == 20:
        assert metrics.unique_shop_count == 12
    elif window_size == 50:
        assert metrics.unique_shop_count == 12
    elif window_size == 100:
        assert metrics.unique_shop_count == 12


def test_concentration_calculation() -> None:
    shops = [
        _shop("shop-a", 10),
        _shop("shop-b", 10),
        _shop("shop-c", 10),
        _shop("shop-d", 1000),
        _shop("shop-e", 1000),
        _shop("shop-f", 1000),
    ]
    observations = [
        _obs(1, "shop-a"),
        _obs(2, "shop-a"),
        _obs(3, "shop-a"),
        _obs(4, "shop-b"),
        _obs(5, "shop-b"),
        _obs(6, "shop-c"),
        _obs(7, "shop-c"),
        _obs(8, "shop-d"),
        _obs(9, "shop-e"),
        _obs(10, "shop-f"),
    ]
    assert calculate_cr5(observations) == pytest.approx(0.9)
    assert calculate_cr10(observations) == pytest.approx(1.0)
    metrics = calculate_rank_window_metrics(observations, shops, 10)
    assert metrics.cr5 == pytest.approx(0.9)
    assert metrics.cr10 == pytest.approx(1.0)


def test_recent_listing_bucket() -> None:
    as_of = datetime(2026, 8, 22, tzinfo=UTC)
    observations = [
        _obs(1, "shop-a", created_at=as_of - timedelta(days=30)),
        _obs(2, "shop-b", created_at=as_of - timedelta(days=179)),
        _obs(3, "shop-c", created_at=as_of - timedelta(days=181)),
        _obs(4, "shop-d", created_at=as_of - timedelta(days=400)),
    ]
    metrics = calculate_recent_listing_share(observations, as_of=as_of)
    assert metrics["recent_listing_share"] == pytest.approx(0.5)


def test_price_percentile() -> None:
    summary = calculate_price_summary([10, 20, 30, 40, 50], currency="USD")
    assert summary.count == 5
    assert summary.minimum == 10.0
    assert summary.p25 == 20.0
    assert summary.median == 30.0
    assert summary.p75 == 40.0
    assert summary.maximum == 50.0


def test_missing_metric_handling() -> None:
    result = calculate_entry_score(
        {
            "top20_new_shop_penetration": 0.5,
            "top50_new_shop_penetration": None,
            "unique_new_shop_diversity": 1.0,
            "recent_listing_penetration": 0.5,
            "incumbency_concentration": 0.5,
        },
        {
            "top20_new_shop_penetration": 35,
            "top50_new_shop_penetration": 20,
            "unique_new_shop_diversity": 15,
            "recent_listing_penetration": 15,
            "incumbency_concentration": 15,
        },
    )
    assert result.available_weight_total == 80
    assert "top50_new_shop_penetration" in result.missing_metrics
    assert 0 < result.score < 100

