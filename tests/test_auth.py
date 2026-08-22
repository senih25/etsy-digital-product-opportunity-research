from __future__ import annotations

from contextlib import nullcontext

import pytest

from etsy_research.cli import preflight_command
from etsy_research.config import detect_etsy_credential_state, load_etsy_credentials
from etsy_research.etsy_client import EtsyClient, EtsyClientError, RequestMetadata, compose_x_api_key, redact_headers


def test_credential_composition() -> None:
    assert compose_x_api_key("keystring", "shared-secret") == "keystring:shared-secret"
    client = EtsyClient("keystring", "shared-secret")
    assert client._headers()["x-api-key"] == "keystring:shared-secret"


def test_redaction_masks_credentials() -> None:
    headers = {
        "x-api-key": "keystring:shared-secret",
        "Authorization": "Bearer 12345678.token",
    }
    redacted = redact_headers(headers, api_keystring="keystring", shared_secret="shared-secret", oauth_token="12345678.token")
    assert redacted["x-api-key"] == "[REDACTED]"
    assert redacted["Authorization"] == "Bearer [REDACTED]"


def test_redaction_masks_authorization_without_token_hint() -> None:
    headers = {"Authorization": "Bearer 12345678.token"}
    redacted = redact_headers(headers)
    assert redacted["Authorization"] == "[REDACTED]"


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        ({}, "BLOCKED_NO_CREDENTIALS"),
        ({"ETSY_API_KEYSTRING": "keystring"}, "BLOCKED_MISSING_SHARED_SECRET"),
        ({"ETSY_SHARED_SECRET": "shared-secret"}, "BLOCKED_MISSING_KEYSTRING"),
        ({"ETSY_API_KEYSTRING": "keystring", "ETSY_SHARED_SECRET": "shared-secret"}, "READY"),
    ],
)
def test_detect_credential_state(environ: dict[str, str], expected: str) -> None:
    assert detect_etsy_credential_state(environ) == expected


def test_load_credentials_returns_none_when_incomplete() -> None:
    assert load_etsy_credentials({}) is None
    assert load_etsy_credentials({"ETSY_API_KEYSTRING": "keystring"}) is None
    assert load_etsy_credentials({"ETSY_SHARED_SECRET": "shared-secret"}) is None


def test_explicit_empty_env_mapping_is_respected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ETSY_API_KEYSTRING", "process-keystring")
    monkeypatch.setenv("ETSY_SHARED_SECRET", "process-shared-secret")

    assert load_etsy_credentials({}) is None
    assert detect_etsy_credential_state({}) == "BLOCKED_NO_CREDENTIALS"


def test_preflight_missing_credentials(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.delenv("ETSY_API_KEYSTRING", raising=False)
    monkeypatch.delenv("ETSY_SHARED_SECRET", raising=False)

    exit_code = preflight_command()
    out = capsys.readouterr().out.strip()

    assert exit_code == 2
    assert out == "BLOCKED_NO_CREDENTIALS"


def test_preflight_missing_shared_secret(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("ETSY_API_KEYSTRING", "keystring")
    monkeypatch.delenv("ETSY_SHARED_SECRET", raising=False)

    exit_code = preflight_command()
    out = capsys.readouterr().out.strip()

    assert exit_code == 2
    assert out == "BLOCKED_MISSING_SHARED_SECRET"


def test_preflight_missing_keystring(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.delenv("ETSY_API_KEYSTRING", raising=False)
    monkeypatch.setenv("ETSY_SHARED_SECRET", "shared-secret")

    exit_code = preflight_command()
    out = capsys.readouterr().out.strip()

    assert exit_code == 2
    assert out == "BLOCKED_MISSING_KEYSTRING"


def test_preflight_app_not_approved(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("ETSY_API_KEYSTRING", "keystring")
    monkeypatch.setenv("ETSY_SHARED_SECRET", "shared-secret")

    def fake_find_all_listings_active(self: EtsyClient, **_: object) -> tuple[object, RequestMetadata]:
        raise EtsyClientError(
            "Etsy API request failed with status 403",
            status_code=403,
            response_text="application pending approval",
        )

    monkeypatch.setattr(EtsyClient, "find_all_listings_active", fake_find_all_listings_active)

    exit_code = preflight_command()
    out = capsys.readouterr().out.strip()

    assert exit_code == 2
    assert out == "BLOCKED_APP_NOT_APPROVED"


def test_preflight_auth_failed(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("ETSY_API_KEYSTRING", "keystring")
    monkeypatch.setenv("ETSY_SHARED_SECRET", "shared-secret")

    def fake_find_all_listings_active(self: EtsyClient, **_: object) -> tuple[object, RequestMetadata]:
        raise EtsyClientError("Etsy API request failed with status 401", status_code=401, response_text="unauthorized")

    monkeypatch.setattr(EtsyClient, "find_all_listings_active", fake_find_all_listings_active)

    exit_code = preflight_command()
    out = capsys.readouterr().out.strip()

    assert exit_code == 3
    assert out == "AUTH_FAILED"


def test_preflight_success(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("ETSY_API_KEYSTRING", "keystring")
    monkeypatch.setenv("ETSY_SHARED_SECRET", "shared-secret")

    def fake_find_all_listings_active(self: EtsyClient, **_: object) -> tuple[object, RequestMetadata]:
        return (
            {"results": []},
            RequestMetadata(method="GET", url="https://example.invalid", attempt=1, timeout_seconds=30.0),
        )

    monkeypatch.setattr(EtsyClient, "find_all_listings_active", fake_find_all_listings_active)

    exit_code = preflight_command()
    out = capsys.readouterr().out

    assert exit_code == 0
    assert '"status": "PASS"' in out
    assert '"operation": "findAllListingsActive"' in out
    assert '"x-api-key = keystring:shared_secret"' in out
