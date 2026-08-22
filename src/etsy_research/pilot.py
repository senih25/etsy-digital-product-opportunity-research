from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Iterable, Sequence

from .etsy_client import EtsyClient, EtsyClientError
from .models import CanonicalShop, QueryDefinition, RawObservation
from .normalize import normalize_listing_id


PILOT_QUERY_TEXTS = (
    "etsy profit calculator",
    "handmade pricing calculator",
    "etsy bookkeeping spreadsheet",
    "etsy seller spreadsheet",
)


def select_representative_pilot_queries(queries: Sequence[QueryDefinition]) -> list[QueryDefinition]:
    by_text = {query.text: query for query in queries if query.enabled}
    selected: list[QueryDefinition] = []
    for text in PILOT_QUERY_TEXTS:
        query = by_text.get(text)
        if query is not None:
            selected.append(query)
    return selected


def classify_capability_status(
    *,
    direct: bool | None = None,
    official_enrichment: bool | None = None,
) -> str:
    if direct is True:
        return "AVAILABLE_DIRECTLY"
    if official_enrichment is True:
        return "AVAILABLE_VIA_OFFICIAL_ENRICHMENT"
    if direct is False and official_enrichment is False:
        return "NOT_AVAILABLE"
    return "UNKNOWN"


def collect_unique_shop_ids(observations: Sequence[RawObservation]) -> list[str]:
    shop_ids = {observation.shop_id for observation in observations if observation.shop_id}
    return sorted(shop_ids)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=UTC)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
            return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)
        except ValueError:
            return None
    return None


def _parse_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(value)]


def _first_present(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return None


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_price(record: dict[str, Any]) -> tuple[float | None, str | None]:
    price_value = record.get("price")
    if isinstance(price_value, dict):
        amount = price_value.get("amount") or price_value.get("amount_total") or price_value.get("value")
        currency = price_value.get("currency_code") or price_value.get("currency") or record.get("currency_code")
        try:
            return (None if amount is None else float(amount), None if currency is None else str(currency))
        except (TypeError, ValueError):
            return None, None
    amount = record.get("price_amount")
    currency = record.get("price_currency") or record.get("currency_code") or record.get("currency")
    try:
        parsed_amount = None if amount is None else float(amount)
    except (TypeError, ValueError):
        parsed_amount = None
    return parsed_amount, None if currency is None else str(currency)


def _nested_dict(record: dict[str, Any], key: str) -> dict[str, Any]:
    value = record.get(key)
    return value if isinstance(value, dict) else {}


def parse_active_listing_record(
    record: dict[str, Any],
    *,
    research_run_id: str,
    query: QueryDefinition,
    retrieved_at: datetime,
    source: str,
    api_position: int,
    api_rank: int,
    raw_source_ref: str | None = None,
) -> RawObservation:
    nested_listing = _nested_dict(record, "listing")
    nested_shop = _nested_dict(record, "shop")
    listing_id = normalize_listing_id(
        record.get("listing_id")
        or record.get("listingId")
        or record.get("id")
        or nested_listing.get("listing_id")
    )
    if listing_id is None:
        raise ValueError("Missing listing_id in active listing record")

    shop_id = normalize_listing_id(
        record.get("shop_id")
        or record.get("shopId")
        or nested_listing.get("shop_id")
        or nested_shop.get("shop_id")
    )
    title = record.get("title") or record.get("name")
    description = record.get("description")
    price_amount, price_currency = _parse_price(record)
    taxonomy_id = (
        record.get("taxonomy_id")
        or record.get("taxonomyId")
        or record.get("taxonomy_node_id")
        or record.get("taxonomy")
    )
    created_at = _parse_datetime(
        record.get("created_at")
        or record.get("createdTimestamp")
        or record.get("creation_tsz")
        or record.get("listing_created_at")
    )
    updated_at = _parse_datetime(
        record.get("updated_at")
        or record.get("update_tsz")
        or record.get("listing_updated_at")
    )
    tags = _parse_tags(record.get("tags"))
    url = record.get("url") or record.get("listing_url") or record.get("listingUrl")

    return RawObservation(
        research_run_id=research_run_id,
        query_id=query.id,
        query_family=query.family,
        query_text=query.text,
        retrieved_at=retrieved_at,
        source=source,
        api_position=api_position,
        api_rank=api_rank,
        listing_id=listing_id,
        shop_id=shop_id,
        title=None if title is None else str(title),
        description=None if description is None else str(description),
        price_amount=price_amount,
        price_currency=price_currency,
        taxonomy_id=None if taxonomy_id is None else str(taxonomy_id),
        created_at=created_at,
        updated_at=updated_at,
        tags=tags,
        url=None if url is None else str(url),
        raw_source_ref=raw_source_ref,
    )


def parse_active_listing_page(
    payload: dict[str, Any],
    *,
    research_run_id: str,
    query: QueryDefinition,
    retrieved_at: datetime,
    source: str,
) -> list[RawObservation]:
    results = payload.get("results")
    if not isinstance(results, list):
        return []
    observations: list[RawObservation] = []
    for index, record in enumerate(results, start=1):
        if not isinstance(record, dict):
            continue
        observations.append(
            parse_active_listing_record(
                record,
                research_run_id=research_run_id,
                query=query,
                retrieved_at=retrieved_at,
                source=source,
                api_position=index,
                api_rank=index,
                raw_source_ref=f"{query.id}:{index}",
            )
        )
    return observations


def parse_shop_record(
    record: dict[str, Any],
    *,
    requested_shop_id: str | None = None,
    retrieved_at: datetime,
    source_endpoint: str = "getShop",
) -> CanonicalShop:
    shop_id = normalize_listing_id(
        _first_present(record, "shop_id", "shopId", "user_id", "userId", requested_shop_id or "")
    )
    if shop_id is None:
        raise ValueError("Missing shop_id in shop record")

    return CanonicalShop(
        shop_id=shop_id,
        shop_name=None if (shop_name := _first_present(record, "shop_name", "shopName", "login_name")) is None else str(shop_name),
        review_count=_parse_int(_first_present(record, "review_count")),
        review_average=_parse_float(_first_present(record, "review_average")),
        transaction_sold_count=_parse_int(_first_present(record, "transaction_sold_count", "sales_count")),
        created_timestamp=_parse_datetime(_first_present(record, "created_timestamp", "create_date", "shop_created_at")),
        listing_active_count=_parse_int(_first_present(record, "listing_active_count", "active_listing_count")),
        digital_listing_count=_parse_int(_first_present(record, "digital_listing_count")),
        num_favorers=_parse_int(_first_present(record, "num_favorers")),
        source_endpoint=source_endpoint,
        retrieved_at=retrieved_at,
        maturity_source=source_endpoint,
        listing_ids=[],
    )


def fetch_official_shops(
    client: EtsyClient,
    shop_ids: Sequence[str],
    *,
    retrieved_at: datetime | None = None,
) -> tuple[list[CanonicalShop], list[str]]:
    unique_shop_ids = sorted({normalize_listing_id(shop_id) for shop_id in shop_ids if normalize_listing_id(shop_id)})
    timestamp = retrieved_at or datetime.now(UTC)
    enriched_shops: list[CanonicalShop] = []
    failed_shop_ids: list[str] = []

    for shop_id in unique_shop_ids:
        try:
            payload, _metadata = client.get_shop(shop_id)
        except EtsyClientError:
            failed_shop_ids.append(shop_id)
            continue
        if not isinstance(payload, dict):
            failed_shop_ids.append(shop_id)
            continue
        try:
            enriched_shops.append(
                parse_shop_record(
                    payload,
                    requested_shop_id=shop_id,
                    retrieved_at=timestamp,
                    source_endpoint="getShop",
                )
            )
        except ValueError:
            failed_shop_ids.append(shop_id)

    return enriched_shops, failed_shop_ids
