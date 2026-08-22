from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from .analyze import build_query_metrics
from .config import detect_etsy_credential_state, load_config_bundle, load_etsy_credentials, load_local_env
from .etsy_client import EtsyClient, EtsyClientError
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
    state = detect_etsy_credential_state()
    if state != "READY":
        print(state)
        return 2

    credentials = load_etsy_credentials()
    assert credentials is not None
    client = EtsyClient(credentials.keystring, credentials.shared_secret)
    try:
        payload, metadata = client.find_all_listings_active(limit=1, offset=0)
    except EtsyClientError as exc:
        response_text = (exc.response_text or "").lower()
        if exc.status_code in {401, 403} and ("pending approval" in response_text or "not approved" in response_text):
            print("BLOCKED_APP_NOT_APPROVED")
            return 2
        if exc.status_code in {401, 403}:
            print("AUTH_FAILED")
            return 3
        print("AUTH_FAILED")
        return 3

    payload = {
        "status": "PASS",
        "api_source": "Etsy Open API v3",
        "base_url": "https://openapi.etsy.com/v3/application",
        "endpoint": "/listings/active",
        "operation": "findAllListingsActive",
        "auth": "x-api-key = keystring:shared_secret",
        "oauth_required": False,
        "request_metadata": asdict(metadata),
        "rank_windows": bundle.thresholds.rank_windows,
        "results_type": type(payload).__name__,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def run_rq2_command() -> int:
    load_local_env()
    state = detect_etsy_credential_state()
    if state != "READY":
        print(state)
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
