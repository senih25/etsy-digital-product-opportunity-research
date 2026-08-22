from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError


DEFAULT_BASE_URL = "https://openapi.etsy.com/v3/application"
DEFAULT_TIMEOUT_SECONDS = 30.0


class EtsyClientError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        request_id: str | None = None,
        retry_after_seconds: float | None = None,
        url: str | None = None,
        method: str | None = None,
        response_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
        self.retry_after_seconds = retry_after_seconds
        self.url = url
        self.method = method
        self.response_text = response_text


@dataclass(frozen=True)
class RequestMetadata:
    method: str
    url: str
    attempt: int
    timeout_seconds: float
    request_id: str | None = None
    retry_after_seconds: float | None = None


def redact_secret_value(text: str | None, secret: str | None) -> str | None:
    if text is None or not secret:
        return text
    return text.replace(secret, "[REDACTED]")


def redact_headers(headers: dict[str, str], *, api_key: str | None = None, oauth_token: str | None = None) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for key, value in headers.items():
        lower_key = key.lower()
        if lower_key == "x-api-key":
            redacted[key] = "[REDACTED]"
        elif lower_key == "authorization" and oauth_token:
            redacted[key] = "Bearer [REDACTED]"
        else:
            redacted[key] = value
    return redacted


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    if value.isdigit():
        return float(value)
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    delta = parsed - datetime.now(timezone.utc)
    return max(delta.total_seconds(), 0.0)


class EtsyClient:
    def __init__(
        self,
        api_key: str,
        *,
        oauth_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        user_agent: str = "etsy-digital-product-opportunity-research/0.1.0",
    ) -> None:
        self.api_key = api_key
        self.oauth_token = oauth_token
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.user_agent = user_agent

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
            "x-api-key": self.api_key,
        }
        if self.oauth_token:
            headers["Authorization"] = f"Bearer {self.oauth_token}"
        return headers

    def _build_url(self, path: str, params: dict[str, Any] | None = None) -> str:
        full_path = f"{self.base_url}/{path.lstrip('/')}"
        if not params:
            return full_path
        query = parse.urlencode({key: value for key, value in params.items() if value is not None})
        return f"{full_path}?{query}"

    def _request_json(self, method: str, path: str, params: dict[str, Any] | None = None) -> tuple[Any, RequestMetadata]:
        url = self._build_url(path, params)
        headers = self._headers()
        last_error: EtsyClientError | None = None

        for attempt in range(1, self.max_retries + 1):
            req = request.Request(url, headers=headers, method=method.upper())
            try:
                with request.urlopen(req, timeout=self.timeout_seconds) as response:
                    body = response.read().decode("utf-8")
                    request_id = response.headers.get("x-request-id") or response.headers.get("request-id")
                    metadata = RequestMetadata(
                        method=method.upper(),
                        url=redact_secret_value(url, self.api_key) or url,
                        attempt=attempt,
                        timeout_seconds=self.timeout_seconds,
                        request_id=request_id,
                    )
                    return json.loads(body), metadata
            except HTTPError as exc:
                response_text = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else None
                request_id = exc.headers.get("x-request-id") if exc.headers else None
                retry_after_seconds = _parse_retry_after(exc.headers.get("Retry-After") if exc.headers else None)
                retriable = exc.code == 429 or 500 <= exc.code < 600
                last_error = EtsyClientError(
                    f"Etsy API request failed with status {exc.code}",
                    status_code=exc.code,
                    request_id=request_id,
                    retry_after_seconds=retry_after_seconds,
                    url=redact_secret_value(url, self.api_key) or url,
                    method=method.upper(),
                    response_text=response_text,
                )
                if not retriable or attempt >= self.max_retries:
                    raise last_error from exc
                delay = retry_after_seconds if retry_after_seconds is not None else self.backoff_factor * (2 ** (attempt - 1))
                time.sleep(delay)
            except URLError as exc:
                last_error = EtsyClientError(
                    f"Etsy API transport failure: {exc.reason}",
                    url=redact_secret_value(url, self.api_key) or url,
                    method=method.upper(),
                )
                if attempt >= self.max_retries:
                    raise last_error from exc
                time.sleep(self.backoff_factor * (2 ** (attempt - 1)))

        if last_error is not None:
            raise last_error
        raise EtsyClientError("Etsy API request failed without a captured error", url=redact_secret_value(url, self.api_key) or url, method=method.upper())

    def get_active_listings(self, **params: Any) -> tuple[Any, RequestMetadata]:
        return self._request_json("GET", "/listings/active", params=params or None)

    def iter_active_listings(self, *, limit: int = 100, **params: Any):
        offset = 0
        while True:
            page_params = dict(params)
            page_params.update({"limit": limit, "offset": offset})
            payload, metadata = self.get_active_listings(**page_params)
            yield payload, metadata
            items = payload.get("results") if isinstance(payload, dict) else None
            if not items or len(items) < limit:
                break
            offset += limit

