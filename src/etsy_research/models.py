from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _ResearchBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ResearchRun(_ResearchBaseModel):
    research_run_id: str
    started_at: datetime
    completed_at: datetime | None = None
    query_set_version: str
    script_version: str
    git_sha: str | None = None
    api_source: str
    buyer_country_context: str | None = None
    language_context: str | None = None


class QueryDefinition(_ResearchBaseModel):
    id: str
    family: str
    text: str
    enabled: bool = True


class RawObservation(_ResearchBaseModel):
    research_run_id: str
    query_id: str
    query_family: str
    query_text: str
    retrieved_at: datetime
    source: str
    api_position: int
    api_rank: int
    listing_id: str
    shop_id: str | None = None
    title: str | None = None
    description: str | None = None
    price_amount: float | None = None
    price_currency: str | None = None
    taxonomy_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    raw_source_ref: str | None = None


class CanonicalListing(_ResearchBaseModel):
    listing_id: str
    shop_id: str | None = None
    title: str | None = None
    description: str | None = None
    price_amount: float | None = None
    price_currency: str | None = None
    taxonomy_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    raw_observation_ids: list[str] = Field(default_factory=list)
    query_ids: list[str] = Field(default_factory=list)
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None


class CanonicalShop(_ResearchBaseModel):
    shop_id: str
    shop_name: str | None = None
    review_count: int | None = None
    review_average: float | None = None
    transaction_sold_count: int | None = Field(default=None, alias="sales_count")
    created_timestamp: datetime | None = Field(default=None, alias="shop_created_at")
    listing_active_count: int | None = Field(default=None, alias="active_listing_count")
    digital_listing_count: int | None = None
    num_favorers: int | None = None
    source_endpoint: str | None = None
    retrieved_at: datetime | None = None
    maturity_source: str
    listing_ids: list[str] = Field(default_factory=list)

    @property
    def sales_count(self) -> int | None:
        return self.transaction_sold_count

    @property
    def shop_created_at(self) -> datetime | None:
        return self.created_timestamp

    @property
    def active_listing_count(self) -> int | None:
        return self.listing_active_count


class PriceSummary(_ResearchBaseModel):
    count: int = 0
    minimum: float | None = None
    p25: float | None = None
    median: float | None = None
    p75: float | None = None
    maximum: float | None = None
    currency: str | None = None


class RankWindowMetrics(_ResearchBaseModel):
    window_size: int
    observation_count: int = 0
    unique_listing_count: int = 0
    unique_shop_count: int = 0
    new_shop_listing_count: int = 0
    new_shop_unique_shop_count: int = 0
    new_shop_listing_share: float | None = None
    new_shop_unique_shop_share: float | None = None
    recent_listing_count: int = 0
    recent_listing_share: float | None = None
    incumbent_unique_shop_count: int = 0
    cr5: float | None = None
    cr10: float | None = None
    median_reviews: float | None = None
    price_summary: PriceSummary | None = None
    missing_metrics: list[str] = Field(default_factory=list)


class EntryScoreResult(_ResearchBaseModel):
    score: float
    metric_values: dict[str, float | None] = Field(default_factory=dict)
    normalized_metric_values: dict[str, float] = Field(default_factory=dict)
    weights: dict[str, int] = Field(default_factory=dict)
    available_weight_total: int = 0
    missing_metrics: list[str] = Field(default_factory=list)


class QueryMetrics(_ResearchBaseModel):
    query_id: str
    family: str
    text: str
    raw_observation_count: int = 0
    unique_listing_count: int = 0
    unique_shop_count: int = 0
    duplicate_observation_count: int = 0
    missing_shop_count: int = 0
    missing_review_count: int = 0
    windows: dict[str, RankWindowMetrics] = Field(default_factory=dict)
    price_summary: PriceSummary | None = None
    entry_score: EntryScoreResult | None = None
    verdict: str | None = None
    missing_metrics: list[str] = Field(default_factory=list)


class FamilyMetrics(_ResearchBaseModel):
    family: str
    query_ids: list[str] = Field(default_factory=list)
    query_count: int = 0
    total_raw_observations: int = 0
    total_unique_listings: int = 0
    total_unique_shops: int = 0
    top20_new_shop_share: float | None = None
    top50_unique_new_shops: int | None = None
    recent_listing_share: float | None = None
    cr5: float | None = None
    cr10: float | None = None
    price_summary: PriceSummary | None = None
    entry_score: EntryScoreResult | None = None
    verdict: str | None = None
    confidence: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    missing_metrics: list[str] = Field(default_factory=list)


class ResearchVerdict(_ResearchBaseModel):
    value: Literal["GO", "CONDITIONAL_GO", "NO_GO", "BLOCKED_LIVE_DATA"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"] | None = None
    reason: str | None = None
    live_data_available: bool = True
    missing_metrics: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
