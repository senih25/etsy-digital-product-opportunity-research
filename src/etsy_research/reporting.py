from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

from .models import FamilyMetrics, QueryMetrics, ResearchRun, ResearchVerdict


def render_executive_summary(
    run: ResearchRun,
    verdict: ResearchVerdict,
    query_metrics: Iterable[QueryMetrics],
    family_metrics: Iterable[FamilyMetrics],
) -> str:
    families = list(family_metrics)
    queries = list(query_metrics)
    lines = [
        "# RQ2 - Etsy API Search Entry Signal",
        "",
        f"Run Date: {run.started_at.isoformat()}",
        f"Git SHA: {run.git_sha or 'unknown'}",
        f"Data Source: {run.api_source}",
        f"Queries: {len(queries)}",
        f"Raw Observations: {sum(query.raw_observation_count for query in queries)}",
        f"Unique Listings: {sum(query.unique_listing_count for query in queries)}",
        f"Unique Shops: {sum(query.unique_shop_count for query in queries)}",
        "",
        "## Entry Signal",
        "",
        verdict.value,
        "",
        "## Marketplace Entry Signal Ranking",
    ]
    for index, family in enumerate(sorted(families, key=lambda item: item.entry_score.score if item.entry_score else 0, reverse=True), start=1):
        lines.append(f"{index}. {family.family}")
    return "\n".join(lines).rstrip() + "\n"


def write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[Mapping[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_query_results_rows(query_metrics: Iterable[QueryMetrics]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for query in query_metrics:
        top20 = query.windows.get("20")
        top50 = query.windows.get("50")
        rows.append(
            {
                "query_id": query.query_id,
                "family": query.family,
                "text": query.text,
                "raw_observation_count": query.raw_observation_count,
                "unique_listing_count": query.unique_listing_count,
                "unique_shop_count": query.unique_shop_count,
                "top20_new_shop_share": None if top20 is None else top20.new_shop_unique_shop_share,
                "top50_unique_new_shops": None if top50 is None else top50.new_shop_unique_shop_count,
                "entry_score": None if query.entry_score is None else query.entry_score.score,
                "verdict": query.verdict,
            }
        )
    return rows


def build_family_summary_rows(family_metrics: Iterable[FamilyMetrics]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for family in family_metrics:
        rows.append(
            {
                "family": family.family,
                "top20_new_shop_share": family.top20_new_shop_share,
                "top50_unique_new_shops": family.top50_unique_new_shops,
                "recent_listing_share": family.recent_listing_share,
                "cr5": family.cr5,
                "entry_score": None if family.entry_score is None else family.entry_score.score,
                "verdict": family.verdict,
            }
        )
    return rows
