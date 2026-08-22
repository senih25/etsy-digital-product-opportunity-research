"""Provider-neutral advisory AI boundary.

Core Etsy research code does not import this module. It exists so optional AI
helpers can be added later without making NVIDIA, paid AI, or any other model
provider part of the deterministic research path.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

__all__ = [
    "AIProvider",
    "AIResult",
    "AISettings",
    "NullAIProvider",
    "build_ai_provider",
    "load_ai_settings",
]

_SENSITIVE_KEY_PARTS = ("api_key", "apikey", "secret", "token", "password", "cookie", "session", "credential")


@dataclass(frozen=True)
class AISettings:
    enabled: bool = False
    provider_name: str = "null"
    model: str | None = None
    base_url: str | None = None
    api_key_env_name: str = "NVIDIA_API_KEY"
    allow_paid_ai: bool = False
    cost_class: str = "UNKNOWN"
    dependency_class: str = "OPTIONAL"


@dataclass(frozen=True)
class AIResult:
    provider_name: str
    model: str | None
    status: str
    content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProvider(Protocol):
    provider_name: str

    def is_available(self) -> bool:
        ...

    def summarize(self, input_text: str, *, context: Mapping[str, Any] | None = None) -> AIResult:
        ...


def _env_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _redact_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _redact_context(value)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_value(item) for item in value)
    return value


def _redact_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    if not context:
        return {}

    redacted: dict[str, Any] = {}
    for key, value in context.items():
        key_text = str(key).lower()
        if any(part in key_text for part in _SENSITIVE_KEY_PARTS):
            redacted[str(key)] = "[REDACTED]"
        else:
            redacted[str(key)] = _redact_value(value)
    return redacted


def _normalize_provider_name(value: str | None) -> str:
    if value is None:
        return "null"
    normalized = value.strip().lower()
    return normalized or "null"


def _normalize_cost_class(value: str | None) -> str:
    if value is None:
        return "UNKNOWN"
    normalized = value.strip().upper()
    return normalized or "UNKNOWN"


def _normalize_dependency_class(value: str | None) -> str:
    if value is None:
        return "OPTIONAL"
    normalized = value.strip().upper()
    return normalized or "OPTIONAL"


@dataclass(frozen=True)
class NullAIProvider:
    settings: AISettings = field(default_factory=AISettings)
    status: str = "disabled"
    provider_name: str = "null"

    def is_available(self) -> bool:
        return False

    def summarize(self, input_text: str, *, context: Mapping[str, Any] | None = None) -> AIResult:
        del input_text
        reason_by_status = {
            "disabled": "ai_disabled",
            "blocked_paid_disabled": "paid_ai_blocked_by_policy",
            "blocked_trial_only": "trial_only_blocked_by_policy",
            "unavailable": "optional_ai_provider_unavailable",
        }
        return AIResult(
            provider_name=self.provider_name,
            model=self.settings.model,
            status=self.status,
            content=None,
            metadata={
                "reason": reason_by_status.get(self.status, "optional_ai_provider_unavailable"),
                "enabled": self.settings.enabled,
                "provider_name": self.provider_name,
                "base_url": self.settings.base_url,
                "api_key_env_name": self.settings.api_key_env_name,
                "allow_paid_ai": self.settings.allow_paid_ai,
                "cost_class": self.settings.cost_class,
                "dependency_class": self.settings.dependency_class,
                "context": _redact_context(context),
            },
        )


def load_ai_settings(environ: Mapping[str, str] | None = None) -> AISettings:
    env = os.environ if environ is None else environ
    return AISettings(
        enabled=_env_bool(env.get("AI_ENABLED"), default=False),
        provider_name=_normalize_provider_name(env.get("AI_PROVIDER")),
        model=env.get("AI_MODEL") or None,
        base_url=env.get("AI_BASE_URL") or None,
        api_key_env_name=env.get("AI_API_KEY_ENV_NAME", "NVIDIA_API_KEY").strip() or "NVIDIA_API_KEY",
        allow_paid_ai=_env_bool(env.get("ALLOW_PAID_AI"), default=False),
        cost_class=_normalize_cost_class(env.get("AI_COST_CLASS")),
        dependency_class=_normalize_dependency_class(env.get("AI_DEPENDENCY_CLASS")),
    )


def build_ai_provider(settings: AISettings | None = None) -> AIProvider:
    resolved = settings or load_ai_settings()
    provider_name = _normalize_provider_name(resolved.provider_name)
    cost_class = _normalize_cost_class(resolved.cost_class)

    if not resolved.enabled or provider_name == "null":
        return NullAIProvider(settings=resolved, status="disabled", provider_name="null")
    if cost_class == "PAID_OR_BILLABLE" and not resolved.allow_paid_ai:
        return NullAIProvider(settings=resolved, status="blocked_paid_disabled", provider_name=provider_name)
    if cost_class == "TRIAL_ONLY":
        return NullAIProvider(settings=resolved, status="blocked_trial_only", provider_name=provider_name)
    return NullAIProvider(settings=resolved, status="unavailable", provider_name=provider_name)
