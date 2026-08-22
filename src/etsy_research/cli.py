from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .analyze import build_query_metrics
from .config import load_config_bundle, load_local_env
from .models import CanonicalShop, RawObservation


def _load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_shops(payload: dict[str, Any]) -> list[CanonicalShop]:
    return [CanonicalShop.model_validate(item) for item in payload.get("shops", [])]


def _build_observations(payload: dict[str, Any]) -> list[RawObservation]:
    return [RawObservation.model_validate(item) for item in payload.get("raw_observations", [])]


def validate_config_command() -> int:
    bundle = load_config_bundle()
    payload = {
        "status": "PASS",
        "queries": {
            "version": bundle.queries.version,
            "count": len(bundle.queries.queries),
        },
        "thresholds": {
            "version": bundle.thresholds.version,
            "rank_windows": bundle.thresholds.rank_windows,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def analyze_fixture_command(path: Path) -> int:
    bundle = load_config_bundle()
    payload = _load_fixture(path)
    shops = _build_shops(payload)
    observations = _build_observations(payload)
    query_meta = payload.get("query", {})
    query_metrics = build_query_metrics(
        query_id=query_meta.get("id", path.stem),
        family=query_meta.get("family", "TEST_ONLY"),
        text=query_meta.get("text", path.stem.replace("_", " ")),
        observations=observations,
        shops=shops,
        rank_windows=bundle.thresholds.rank_windows,
        score_weights=bundle.thresholds.entry_score_weights.model_dump(),
        primary_entry_review_max=bundle.thresholds.primary_entry_review_max,
        recent_listing_days=180,
        live_data_available=True,
    )
    result = {
        "fixture": path.name,
        "status": "PASS",
        "query_metrics": query_metrics.model_dump(mode="json"),
        "verdict": query_metrics.verdict,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def preflight_command() -> int:
    load_local_env()
    bundle = load_config_bundle()
    api_key = os.getenv("ETSY_API_KEY")
    if not api_key:
        print("BLOCKED_NO_ETSY_API_KEY")
        return 2
    payload = {
        "status": "PASS",
        "api_source": "Etsy Open API v3",
        "base_url": "https://openapi.etsy.com/v3/application",
        "endpoint": "/listings/active",
        "auth": "x-api-key",
        "oauth_required": False,
        "rank_windows": bundle.thresholds.rank_windows,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def run_rq2_command() -> int:
    load_local_env()
    api_key = os.getenv("ETSY_API_KEY")
    if not api_key:
        print("BLOCKED_NO_ETSY_API_KEY")
        return 2
    print("READY_FOR_LIVE_PILOT")
    return 0


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="etsy_research.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-config")

    analyze_parser = subparsers.add_parser("analyze-fixture")
    analyze_parser.add_argument("path", type=Path)

    subparsers.add_parser("preflight")
    subparsers.add_parser("run-rq2")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-config":
        return validate_config_command()
    if args.command == "analyze-fixture":
        return analyze_fixture_command(args.path)
    if args.command == "preflight":
        return preflight_command()
    if args.command == "run-rq2":
        return run_rq2_command()

    parser.error("unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
