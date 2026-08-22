from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .models import QueryDefinition


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def config_dir() -> Path:
    return repo_root() / "config"


def load_local_env(path: Path | None = None) -> None:
    env_path = path or (repo_root() / ".env")
    if not env_path.is_file():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


class QuerySetConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    queries: list[QueryDefinition] = Field(default_factory=list)


class ReviewCohort(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    min: int
    max: int | None = None


class EntryScoreWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top20_new_shop_penetration: int
    top50_new_shop_penetration: int
    unique_new_shop_diversity: int
    recent_listing_penetration: int
    incumbency_concentration: int


class GateThreshold(BaseModel):
    model_config = ConfigDict(extra="forbid")

    top20_new_shop_share_min: float | None = None
    top20_new_shop_share_max: float | None = None
    top50_unique_new_shops_min: int | None = None
    top50_unique_new_shops_max: int | None = None
    entry_score_min: float | None = None
    entry_score_max: float | None = None


class ThresholdConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    review_cohorts: list[ReviewCohort] = Field(default_factory=list)
    primary_entry_review_max: int
    secondary_entry_review_max: int
    rank_windows: list[int] = Field(default_factory=list)
    entry_score_weights: EntryScoreWeights
    go_gate: GateThreshold
    no_go_gate: GateThreshold


@dataclass(frozen=True)
class ConfigBundle:
    queries: QuerySetConfig
    thresholds: ThresholdConfig


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_query_config(path: Path | None = None) -> QuerySetConfig:
    config_path = path or (config_dir() / "queries.json")
    return QuerySetConfig.model_validate(_load_json(config_path))


def load_threshold_config(path: Path | None = None) -> ThresholdConfig:
    config_path = path or (config_dir() / "thresholds.json")
    return ThresholdConfig.model_validate(_load_json(config_path))


def load_config_bundle(
    queries_path: Path | None = None,
    thresholds_path: Path | None = None,
) -> ConfigBundle:
    return ConfigBundle(
        queries=load_query_config(queries_path),
        thresholds=load_threshold_config(thresholds_path),
    )

