from __future__ import annotations

from datetime import UTC, datetime

import pytest

from etsy_research.config import load_query_config
from etsy_research.pilot import (
    classify_capability_status,
    parse_active_listing_page,
    parse_active_listing_record,
    select_representative_pilot_queries,
)


def test_select_representative_pilot_queries() -> None:
    queries = load_query_config().queries
    selected = select_representative_pilot_queries(queries)

    assert [query.text for query in selected] == [
        "etsy profit calculator",
        "handmade pricing calculator",
        "etsy bookkeeping spreadsheet",
        "etsy seller spreadsheet",
    ]


def test_parse_active_listing_record() -> None:
    query = load_query_config().queries[0]
    record = {
        "listing_id": 123,
        "shop_id": 456,
        "title": "Profit Calculator",
        "description": "A calculator listing",
        "price": {"amount": "19.99", "currency_code": "USD"},
        "taxonomy_id": "1001",
        "created_at": "2026-08-20T12:00:00Z",
        "updated_at": "2026-08-21T12:00:00Z",
        "tags": ["calculator", "profit"],
        "url": "https://example.invalid/listing/123",
    }

    observation = parse_active_listing_record(
        record,
        research_run_id="run-1",
        query=query,
        retrieved_at=datetime(2026, 8, 22, tzinfo=UTC),
        source="etsy_open_api_v3",
        api_position=1,
        api_rank=1,
        raw_source_ref="q1:1",
    )

    assert observation.listing_id == "123"
    assert observation.shop_id == "456"
    assert observation.title == "Profit Calculator"
    assert observation.description == "A calculator listing"
    assert observation.price_amount == 19.99
    assert observation.price_currency == "USD"
    assert observation.taxonomy_id == "1001"
    assert observation.tags == ["calculator", "profit"]
    assert observation.raw_source_ref == "q1:1"


def test_parse_active_listing_page() -> None:
    query = load_query_config().queries[0]
    payload = {
        "results": [
            {
                "listing_id": "1",
                "shop_id": "2",
                "title": "Listing",
                "price_amount": 9.99,
                "price_currency": "USD",
                "tags": "alpha, beta",
            }
        ]
    }

    observations = parse_active_listing_page(
        payload,
        research_run_id="run-1",
        query=query,
        retrieved_at=datetime(2026, 8, 22, tzinfo=UTC),
        source="etsy_open_api_v3",
    )

    assert len(observations) == 1
    assert observations[0].tags == ["alpha", "beta"]
    assert observations[0].api_position == 1
    assert observations[0].api_rank == 1


@pytest.mark.parametrize(
    ("direct", "official_enrichment", "expected"),
    [
        (True, None, "AVAILABLE_DIRECTLY"),
        (None, True, "AVAILABLE_VIA_OFFICIAL_ENRICHMENT"),
        (False, False, "NOT_AVAILABLE"),
        (None, None, "UNKNOWN"),
    ],
)
def test_capability_audit_classification(
    direct: bool | None,
    official_enrichment: bool | None,
    expected: str,
) -> None:
    assert classify_capability_status(direct=direct, official_enrichment=official_enrichment) == expected

