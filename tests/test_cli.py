from __future__ import annotations

import json

import pytest

from etsy_research.cli import estimate_rq2_budget_command


def test_estimate_rq2_budget_command(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = estimate_rq2_budget_command()
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["status"] == "PASS"
    assert payload["search_calls"] == 16
    assert payload["unique_shop_calls"] == 1600
    assert payload["total_estimated_calls"] == 1616
    assert payload["QPD_LIMIT"] == 5000
    assert payload["estimated_usage_percentage"] == pytest.approx(32.32)
