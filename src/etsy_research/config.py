from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

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

    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
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


@dataclass(frozen=True)
class EtsyCredentials:
    keystring: str
    shared_secret: str

    @property
    def x_api_key(self) -> str:
        return f"{self.keystring}:{self.shared_secret}"


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


def load_etsy_credentials(environ: Mapping[str, str] | None = None) -> EtsyCredentials | None:
    env = os.environ if environ is None else environ
    keystring = env.get("ETSY_API_KEYSTRING")
    shared_secret = env.get("ETSY_SHARED_SECRET")
    if not keystring or not shared_secret:
        return None
    return EtsyCredentials(keystring=keystring, shared_secret=shared_secret)


def detect_etsy_app_approval_state(environ: Mapping[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ

    approval = env.get("ETSY_APP_APPROVAL")
    if approval is not None:
        value = approval.strip().upper()
        if value == "APPROVED":
            return "APPROVED"
        if value in {"PENDING", "REJECTED"}:
            return value
        if value in {"TRUE", "YES", "1"}:
            return "APPROVED"
        if value in {"FALSE", "NO", "0"}:
            return "PENDING"

    legacy_approval = env.get("ETSY_APP_APPROVED")
    if legacy_approval is not None:
        value = legacy_approval.strip().lower()
        if value in {"true", "yes", "1", "approved"}:
            return "APPROVED"
        if value in {"false", "no", "0", "pending"}:
            return "PENDING"

    return "PENDING"


def detect_etsy_credential_state(environ: Mapping[str, str] | None = None) -> str:
    env = os.environ if environ is None else environ
    keystring = env.get("ETSY_API_KEYSTRING")
    shared_secret = env.get("ETSY_SHARED_SECRET")
    if not keystring and not shared_secret:
        return "BLOCKED_NO_CREDENTIALS"
    if not keystring:
        return "BLOCKED_MISSING_KEYSTRING"
    if not shared_secret:
        return "BLOCKED_MISSING_SHARED_SECRET"
    return "READY"
