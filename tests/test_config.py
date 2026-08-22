from __future__ import annotations

from etsy_research.config import load_query_config, load_threshold_config


def test_query_schema() -> None:
    config = load_query_config()
    assert config.version == "rq2-query-set-v1"
    assert len(config.queries) == 16
    assert all(query.enabled for query in config.queries)
    assert {query.family for query in config.queries} == {
        "FAMILY_A_ETSY_PROFIT",
        "FAMILY_B_HANDMADE_PRICING",
        "FAMILY_C_BOOKKEEPING",
        "FAMILY_D_SELLER_OPERATIONS",
    }


def test_threshold_schema() -> None:
    thresholds = load_threshold_config()
    assert thresholds.version == "rq2-thresholds-v1"
    assert [cohort.id for cohort in thresholds.review_cohorts] == ["A", "B", "C", "D", "E"]
    assert thresholds.primary_entry_review_max == 100
    assert thresholds.secondary_entry_review_max == 500
    assert thresholds.rank_windows == [10, 20, 50, 100]
    assert thresholds.go_gate.top20_new_shop_share_min == 0.15
    assert thresholds.go_gate.top50_unique_new_shops_min == 5
    assert thresholds.go_gate.entry_score_min == 65
    assert thresholds.no_go_gate.top20_new_shop_share_max == 0.05
    assert thresholds.no_go_gate.top50_unique_new_shops_max == 2
    assert thresholds.no_go_gate.entry_score_max == 40

