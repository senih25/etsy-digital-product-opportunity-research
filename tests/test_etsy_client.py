from __future__ import annotations

from collections.abc import Callable
from email.message import Message
from io import BytesIO
from urllib.error import HTTPError

import pytest

from etsy_research.etsy_client import EtsyClient, RequestMetadata


class _FakeResponse:
    def __init__(self, payload: bytes, headers: dict[str, str] | None = None) -> None:
        self._payload = payload
        self.headers = headers or {}

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


class _RecordingClient(EtsyClient):
    def __init__(self) -> None:
        super().__init__("keystring", "shared-secret", max_retries=1, backoff_factor=0.0)
        self.calls: list[tuple[str, str, dict[str, object] | None]] = []

    def _request_json(self, method: str, path: str, params: dict[str, object] | None = None):
        self.calls.append((method, path, params))
        return {"results": []}, RequestMetadata(method=method, url="https://example.invalid", attempt=1, timeout_seconds=30.0)


def test_find_all_listings_active_supports_keywords_limit_offset() -> None:
    client = _RecordingClient()
    client.find_all_listings_active(limit=25, offset=50, keywords="etsy profit calculator")

    assert client.calls == [
        (
            "GET",
            "/listings/active",
            {"limit": 25, "offset": 50, "keywords": "etsy profit calculator"},
        )
    ]


def test_get_shop_uses_shop_path() -> None:
    client = _RecordingClient()
    client.get_shop("12345")

    assert client.calls == [
        (
            "GET",
            "/shops/12345",
            None,
        )
    ]


def test_iter_active_listings_paginates_until_short_page() -> None:
    class PaginatingClient(EtsyClient):
        def __init__(self) -> None:
            super().__init__("keystring", "shared-secret", max_retries=1, backoff_factor=0.0)
            self.calls: list[dict[str, object] | None] = []

        def find_all_listings_active(self, **params: object):
            self.calls.append(params)
            offset = int(params["offset"])
            if offset == 0:
                return {"results": [1, 2]}, RequestMetadata(method="GET", url="https://example.invalid", attempt=1, timeout_seconds=30.0)
            return {"results": [3]}, RequestMetadata(method="GET", url="https://example.invalid", attempt=1, timeout_seconds=30.0)

    client = PaginatingClient()
    pages = list(client.iter_active_listings(limit=2, keywords="pricing"))

    assert len(pages) == 2
    assert client.calls == [
        {"limit": 2, "offset": 0, "keywords": "pricing"},
        {"limit": 2, "offset": 2, "keywords": "pricing"},
    ]


def test_retry_after_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    client = EtsyClient("keystring", "shared-secret", max_retries=2, backoff_factor=0.0)
    attempts = {"count": 0}

    def fake_urlopen(req, timeout):
        attempts["count"] += 1
        if attempts["count"] == 1:
            headers = Message()
            headers.add_header("Retry-After", "0")
            raise HTTPError(req.full_url, 429, "Too Many Requests", headers, BytesIO(b'{"error":"rate limit"}'))
        return _FakeResponse(b'{"results":[]}', {"x-request-id": "request-1"})

    monkeypatch.setattr("etsy_research.etsy_client.request.urlopen", fake_urlopen)
    monkeypatch.setattr("etsy_research.etsy_client.time.sleep", lambda _: None)

    payload, metadata = client.find_all_listings_active(limit=1, offset=0)

    assert payload == {"results": []}
    assert metadata.attempt == 2
    assert attempts["count"] == 2


def test_auth_rejection_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    client = EtsyClient("keystring", "shared-secret", max_retries=3, backoff_factor=0.0)

    def fake_urlopen(req, timeout):
        headers = Message()
        raise HTTPError(req.full_url, 403, "Forbidden", headers, BytesIO(b"application pending approval"))

    monkeypatch.setattr("etsy_research.etsy_client.request.urlopen", fake_urlopen)
    monkeypatch.setattr("etsy_research.etsy_client.time.sleep", lambda _: None)

    with pytest.raises(Exception) as excinfo:
        client.find_all_listings_active(limit=1, offset=0)

    assert "status 403" in str(excinfo.value)
