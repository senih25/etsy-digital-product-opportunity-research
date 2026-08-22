from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime, timedelta
from statistics import median
from typing import Iterable, Mapping, Sequence

from .models import CanonicalShop, EntryScoreResult, PriceSummary, QueryMetrics, RankWindowMetrics, ResearchVerdict, RawObservation


def _as_shop_lookup(shops: Sequence[CanonicalShop] | Mapping[str, CanonicalShop] | None) -> dict[str, CanonicalShop]:
    if shops is None:
        return {}
    if isinstance(shops, Mapping):
        return {str(key): value for key, value in shops.items()}
    return {shop.shop_id: shop for shop in shops}


def _dedupe_and_sort_observations(observations: Sequence[RawObservation]) -> list[RawObservation]:
    ordered: list[RawObservation] = sorted(
        observations,
        key=lambda item: (item.api_rank, item.api_position, item.listing_id),
    )
    seen: set[str] = set()
    deduped: list[RawObservation] = []
    for observation in ordered:
        if observation.listing_id in seen:
            continue
        seen.add(observation.listing_id)
        deduped.append(observation)
    return deduped


def assign_review_cohort(review_count: int | None, cohorts: Sequence[Mapping[str, int | None]] | None = None) -> str | None:
    if review_count is None:
        return None
    cohort_defs = list(cohorts or [])
    if not cohort_defs:
        cohort_defs = [
            {"id": "A", "min": 0, "max": 25},
            {"id": "B", "min": 26, "max": 100},
            {"id": "C", "min": 101, "max": 500},
            {"id": "D", "min": 501, "max": 2000},
            {"id": "E", "min": 2001, "max": None},
        ]
    for cohort in cohort_defs:
        lower = cohort["min"]
        upper = cohort.get("max")
        if review_count >= lower and (upper is None or review_count <= upper):
            return str(cohort["id"])
    return None


def _window_slice(observations: Sequence[RawObservation], window_size: int) -> list[RawObservation]:
    return _dedupe_and_sort_observations(observations)[:window_size]


def calculate_new_shop_share(
    observations: Sequence[RawObservation],
    shops: Sequence[CanonicalShop] | Mapping[str, CanonicalShop] | None,
    *,
    primary_entry_review_max: int = 100,
    window_size: int | None = None,
) -> dict[str, float | int | None]:
    shop_lookup = _as_shop_lookup(shops)
    window = _window_slice(observations, window_size or len(observations))
    if not window:
        return {
            "new_shop_listing_count": 0,
            "listing_count": 0,
            "new_shop_listing_share": None,
        }

    new_shop_listing_count = 0
    for observation in window:
        shop = shop_lookup.get(observation.shop_id or "")
        if shop is not None and shop.review_count is not None and shop.review_count <= primary_entry_review_max:
            new_shop_listing_count += 1

    listing_count = len(window)
    return {
        "new_shop_listing_count": new_shop_listing_count,
        "listing_count": listing_count,
        "new_shop_listing_share": new_shop_listing_count / listing_count if listing_count else None,
    }


def calculate_unique_shop_penetration(
    observations: Sequence[RawObservation],
    shops: Sequence[CanonicalShop] | Mapping[str, CanonicalShop] | None,
    *,
    primary_entry_review_max: int = 100,
    window_size: int | None = None,
) -> dict[str, float | int | None]:
    shop_lookup = _as_shop_lookup(shops)
    window = _window_slice(observations, window_size or len(observations))
    unique_shop_ids = [observation.shop_id for observation in window if observation.shop_id]
    unique_shop_ids = list(dict.fromkeys(unique_shop_ids))
    unique_shop_count = len(unique_shop_ids)
    if not unique_shop_count:
        return {
            "unique_shop_count": 0,
            "new_shop_unique_shop_count": 0,
            "new_shop_unique_shop_share": None,
        }

    new_shop_unique_shop_count = 0
    for shop_id in unique_shop_ids:
        shop = shop_lookup.get(shop_id)
        if shop is not None and shop.review_count is not None and shop.review_count <= primary_entry_review_max:
            new_shop_unique_shop_count += 1

    return {
        "unique_shop_count": unique_shop_count,
        "new_shop_unique_shop_count": new_shop_unique_shop_count,
        "new_shop_unique_shop_share": new_shop_unique_shop_count / unique_shop_count,
    }


def calculate_recent_listing_share(
    observations: Sequence[RawObservation],
    *,
    window_size: int | None = None,
    as_of: datetime | None = None,
    recent_listing_days: int = 180,
) -> dict[str, float | int | None]:
    window = _window_slice(observations, window_size or len(observations))
    if not window:
        return {"recent_listing_count": 0, "listing_count": 0, "recent_listing_share": None}

    reference = as_of
    if reference is None:
        timestamps = [observation.retrieved_at for observation in window if observation.retrieved_at is not None]
        reference = max(timestamps) if timestamps else datetime.now(UTC)
    cutoff = reference - timedelta(days=recent_listing_days)

    recent_listing_count = 0
    for observation in window:
        if observation.created_at is not None and observation.created_at >= cutoff:
            recent_listing_count += 1

    listing_count = len(window)
    return {
        "recent_listing_count": recent_listing_count,
        "listing_count": listing_count,
        "recent_listing_share": recent_listing_count / listing_count if listing_count else None,
    }


def calculate_cr5(observations: Sequence[RawObservation], *, window_size: int | None = None) -> float | None:
    window = _window_slice(observations, window_size or len(observations))
    if not window:
        return None
    counts = Counter(observation.shop_id for observation in window if observation.shop_id)
    if not counts:
        return None
    total = sum(counts.values())
    top_five = sum(count for _, count in counts.most_common(5))
    return top_five / total if total else None


def calculate_cr10(observations: Sequence[RawObservation], *, window_size: int | None = None) -> float | None:
    window = _window_slice(observations, window_size or len(observations))
    if not window:
        return None
    counts = Counter(observation.shop_id for observation in window if observation.shop_id)
    if not counts:
        return None
    total = sum(counts.values())
    top_ten = sum(count for _, count in counts.most_common(10))
    return top_ten / total if total else None


def calculate_price_summary(values: Sequence[float | int | None], *, currency: str | None = None) -> PriceSummary:
    numeric_values = sorted(float(value) for value in values if value is not None)
    if not numeric_values:
        return PriceSummary(count=0, currency=currency)

    def percentile(percent: float) -> float:
        if len(numeric_values) == 1:
            return numeric_values[0]
        position = (len(numeric_values) - 1) * percent
        lower_index = int(position)
        upper_index = min(lower_index + 1, len(numeric_values) - 1)
        lower_value = numeric_values[lower_index]
        upper_value = numeric_values[upper_index]
        interpolation = position - lower_index
        return lower_value + (upper_value - lower_value) * interpolation

    return PriceSummary(
        count=len(numeric_values),
        minimum=numeric_values[0],
        p25=percentile(0.25),
        median=median(numeric_values),
        p75=percentile(0.75),
        maximum=numeric_values[-1],
        currency=currency,
    )


def calculate_rank_window_metrics(
    observations: Sequence[RawObservation],
    shops: Sequence[CanonicalShop] | Mapping[str, CanonicalShop] | None,
    window_size: int,
    *,
    primary_entry_review_max: int = 100,
    recent_listing_days: int = 180,
    as_of: datetime | None = None,
) -> RankWindowMetrics:
    shop_lookup = _as_shop_lookup(shops)
    window = _window_slice(observations, window_size)
    unique_listing_count = len(window)
    unique_shop_ids = list(dict.fromkeys(observation.shop_id for observation in window if observation.shop_id))
    unique_shop_count = len(unique_shop_ids)
    currency_values = [observation.price_currency for observation in window if observation.price_currency]
    currency = currency_values[0] if len(set(currency_values)) == 1 and currency_values else None

    new_shop_listing_count = 0
    missing_review_count = 0
    review_values: list[int] = []
    listing_prices: list[float | int | None] = []
    for observation in window:
        listing_prices.append(observation.price_amount)
        shop = shop_lookup.get(observation.shop_id or "")
        if shop is None or shop.review_count is None:
            missing_review_count += 1
            continue
        review_values.append(shop.review_count)
        if shop.review_count <= primary_entry_review_max:
            new_shop_listing_count += 1

    new_shop_unique_shop_count = 0
    for shop_id in unique_shop_ids:
        shop = shop_lookup.get(shop_id)
        if shop is not None and shop.review_count is not None and shop.review_count <= primary_entry_review_max:
            new_shop_unique_shop_count += 1

    recent_listing_metrics = calculate_recent_listing_share(
        window,
        window_size=window_size,
        as_of=as_of,
        recent_listing_days=recent_listing_days,
    )
    price_summary = calculate_price_summary(listing_prices, currency=currency)
    cr5 = calculate_cr5(window)
    cr10 = calculate_cr10(window)
    missing_metrics: list[str] = []
    if not review_values:
        missing_metrics.append("review_count")
    if recent_listing_metrics["recent_listing_share"] is None:
        missing_metrics.append("recent_listing_share")
    if price_summary.count == 0:
        missing_metrics.append("price_summary")

    return RankWindowMetrics(
        window_size=window_size,
        observation_count=unique_listing_count,
        unique_listing_count=unique_listing_count,
        unique_shop_count=unique_shop_count,
        new_shop_listing_count=new_shop_listing_count,
        new_shop_unique_shop_count=new_shop_unique_shop_count,
        new_shop_listing_share=new_shop_listing_count / unique_listing_count if unique_listing_count else None,
        new_shop_unique_shop_share=new_shop_unique_shop_count / unique_shop_count if unique_shop_count else None,
        recent_listing_count=int(recent_listing_metrics["recent_listing_count"] or 0),
        recent_listing_share=recent_listing_metrics["recent_listing_share"],
        incumbent_unique_shop_count=max(unique_shop_count - new_shop_unique_shop_count, 0),
        cr5=cr5,
        cr10=cr10,
        median_reviews=median(review_values) if review_values else None,
        price_summary=price_summary if price_summary.count else None,
        missing_metrics=missing_metrics,
    )


def calculate_entry_score(
    metric_values: Mapping[str, float | None],
    weights: Mapping[str, int],
) -> EntryScoreResult:
    normalized_metric_values: dict[str, float] = {}
    available_weight_total = 0
    weighted_sum = 0.0
    missing_metrics: list[str] = []

    for metric_name, weight in weights.items():
        value = metric_values.get(metric_name)
        if value is None:
            missing_metrics.append(metric_name)
            continue
        normalized_value = max(0.0, min(1.0, float(value)))
        normalized_metric_values[metric_name] = normalized_value
        available_weight_total += weight
        weighted_sum += normalized_value * weight

    score = weighted_sum / available_weight_total * 100 if available_weight_total else 0.0
    return EntryScoreResult(
        score=score,
        metric_values=dict(metric_values),
        normalized_metric_values=normalized_metric_values,
        weights=dict(weights),
        available_weight_total=available_weight_total,
        missing_metrics=missing_metrics,
    )


def classify_verdict(
    *,
    score: float | None,
    top20_new_shop_share: float | None,
    top50_unique_new_shops: int | None,
    live_data_available: bool = True,
) -> ResearchVerdict:
    if not live_data_available:
        return ResearchVerdict(
            value="BLOCKED_LIVE_DATA",
            confidence="LOW",
            reason="Real live Etsy data is not available yet.",
            live_data_available=False,
        )

    if score is None or top20_new_shop_share is None or top50_unique_new_shops is None:
        return ResearchVerdict(
            value="CONDITIONAL_GO",
            confidence="LOW",
            reason="At least one required metric is missing.",
            missing_metrics=[
                metric_name
                for metric_name, metric_value in {
                    "score": score,
                    "top20_new_shop_share": top20_new_shop_share,
                    "top50_unique_new_shops": top50_unique_new_shops,
                }.items()
                if metric_value is None
            ],
        )

    if score >= 65 and top20_new_shop_share >= 0.15 and top50_unique_new_shops >= 5:
        return ResearchVerdict(
            value="GO",
            confidence="MEDIUM",
            reason="Visibility signals meet the initial GO hypothesis.",
        )

    if score < 40 and top20_new_shop_share < 0.05 and top50_unique_new_shops <= 2:
        return ResearchVerdict(
            value="NO_GO",
            confidence="MEDIUM",
            reason="Visibility is dominated by incumbents under the initial hypothesis.",
        )

    return ResearchVerdict(
        value="CONDITIONAL_GO",
        confidence="MEDIUM",
        reason="Signals are mixed or incomplete under the initial hypothesis.",
    )


def build_query_metrics(
    *,
    query_id: str,
    family: str,
    text: str,
    observations: Sequence[RawObservation],
    shops: Sequence[CanonicalShop] | Mapping[str, CanonicalShop] | None,
    rank_windows: Sequence[int],
    score_weights: Mapping[str, int],
    primary_entry_review_max: int = 100,
    recent_listing_days: int = 180,
    as_of: datetime | None = None,
    live_data_available: bool = True,
) -> QueryMetrics:
    deduped = _dedupe_and_sort_observations(observations)
    shop_lookup = _as_shop_lookup(shops)
    listings_with_shop = [observation for observation in deduped if observation.shop_id]
    currency_values = [observation.price_currency for observation in deduped if observation.price_currency]
    currency = currency_values[0] if len(set(currency_values)) == 1 and currency_values else None
    price_summary = calculate_price_summary([observation.price_amount for observation in deduped], currency=currency)

    windows: dict[str, RankWindowMetrics] = {}
    for window_size in rank_windows:
        windows[str(window_size)] = calculate_rank_window_metrics(
            deduped,
            shop_lookup,
            window_size,
            primary_entry_review_max=primary_entry_review_max,
            recent_listing_days=recent_listing_days,
            as_of=as_of,
        )

    top20 = windows.get("20")
    top50 = windows.get("50")
    entry_metric_values = {
        "top20_new_shop_penetration": top20.new_shop_unique_shop_share if top20 else None,
        "top50_new_shop_penetration": top50.new_shop_unique_shop_share if top50 else None,
        "unique_new_shop_diversity": (
            min(1.0, (top50.new_shop_unique_shop_count if top50 else 0) / 5.0) if top50 is not None else None
        ),
        "recent_listing_penetration": top20.recent_listing_share if top20 else None,
        "incumbency_concentration": (1.0 - top20.cr5) if top20 and top20.cr5 is not None else None,
    }
    entry_score = calculate_entry_score(entry_metric_values, score_weights)
    verdict = classify_verdict(
        score=entry_score.score,
        top20_new_shop_share=top20.new_shop_unique_shop_share if top20 else None,
        top50_unique_new_shops=top50.new_shop_unique_shop_count if top50 else None,
        live_data_available=live_data_available,
    )

    missing_metrics = sorted(set(entry_score.missing_metrics + [metric for window in windows.values() for metric in window.missing_metrics]))
    return QueryMetrics(
        query_id=query_id,
        family=family,
        text=text,
        raw_observation_count=len(observations),
        unique_listing_count=len(deduped),
        unique_shop_count=len({observation.shop_id for observation in listings_with_shop if observation.shop_id}),
        duplicate_observation_count=max(len(observations) - len(deduped), 0),
        missing_shop_count=sum(1 for observation in deduped if observation.shop_id is None),
        missing_review_count=sum(1 for observation in deduped if observation.shop_id is None or shop_lookup.get(observation.shop_id or "") is None or shop_lookup.get(observation.shop_id or "").review_count is None),
        windows=windows,
        price_summary=price_summary if price_summary.count else None,
        entry_score=entry_score,
        verdict=verdict.value,
        missing_metrics=missing_metrics,
    )
