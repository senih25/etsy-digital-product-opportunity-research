from __future__ import annotations

from collections.abc import Mapping

from .analyze import calculate_entry_score, classify_verdict
from .models import EntryScoreResult, ResearchVerdict


def score_entry(metrics: Mapping[str, float | None], weights: Mapping[str, int]) -> EntryScoreResult:
    return calculate_entry_score(metrics, weights)


def verdict_from_score(
    *,
    score: float | None,
    top20_new_shop_share: float | None,
    top50_unique_new_shops: int | None,
    live_data_available: bool = True,
) -> ResearchVerdict:
    return classify_verdict(
        score=score,
        top20_new_shop_share=top20_new_shop_share,
        top50_unique_new_shops=top50_unique_new_shops,
        live_data_available=live_data_available,
    )

