from __future__ import annotations

import json
from pathlib import Path

import pytest

from etsy_research.analyze import build_query_metrics, classify_verdict
from etsy_research.config import load_threshold_config
from etsy_research.models import CanonicalShop, RawObservation


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _build_query_metrics(name: str):
    payload = _load_fixture(name)
    thresholds = load_threshold_config()
    observations = [RawObservation.model_validate(item) for item in payload["raw_observations"]]
    shops = [CanonicalShop.model_validate(item) for item in payload["shops"]]
    query = payload["query"]
    return build_query_metrics(
        query_id=query["id"],
        family=query["family"],
        text=query["text"],
        observations=observations,
        shops=shops,
        rank_windows=thresholds.rank_windows,
        score_weights=thresholds.entry_score_weights.model_dump(),
        primary_entry_review_max=thresholds.primary_entry_review_max,
        live_data_available=True,
    )


@pytest.mark.parametrize(
    ("fixture_name", "expected"),
    [
        ("strong_entry.json", "GO"),
        ("mixed_entry.json", "CONDITIONAL_GO"),
        ("incumbent_dominated.json", "NO_GO"),
    ],
)
def test_fixture_verdicts(fixture_name: str, expected: str) -> None:
    metrics = _build_query_metrics(fixture_name)
    assert metrics.verdict == expected


def test_missing_metric_normalization() -> None:
    result = classify_verdict(
        score=80,
        top20_new_shop_share=0.5,
        top50_unique_new_shops=6,
        live_data_available=False,
    )
    assert result.value == "BLOCKED_LIVE_DATA"

