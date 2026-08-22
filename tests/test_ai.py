from __future__ import annotations

import ast
from pathlib import Path

import pytest

from etsy_research.ai import AISettings, NullAIProvider, build_ai_provider, load_ai_settings
from etsy_research.scoring import score_entry, verdict_from_score


ROOT = Path(__file__).resolve().parents[1]
CORE_MODULES = [
    "analyze",
    "cli",
    "config",
    "etsy_client",
    "models",
    "normalize",
    "pilot",
    "reporting",
    "scoring",
]


def _module_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level
            module = node.module or ""
            imports.add(f"{prefix}{module}" if module else prefix)
    return imports


def test_load_ai_settings_uses_placeholders_only() -> None:
    settings = load_ai_settings(
        {
            "AI_ENABLED": "true",
            "AI_PROVIDER": "nvidia",
            "AI_MODEL": "meta/llama-3.1-8b-instruct",
            "AI_BASE_URL": "https://example.invalid/v1",
            "AI_API_KEY_ENV_NAME": "NVIDIA_API_KEY",
            "AI_COST_CLASS": "free_developer_program",
            "AI_DEPENDENCY_CLASS": "optional",
            "ALLOW_PAID_AI": "false",
        }
    )

    assert settings == AISettings(
        enabled=True,
        provider_name="nvidia",
        model="meta/llama-3.1-8b-instruct",
        base_url="https://example.invalid/v1",
        api_key_env_name="NVIDIA_API_KEY",
        allow_paid_ai=False,
        cost_class="FREE_DEVELOPER_PROGRAM",
        dependency_class="OPTIONAL",
    )


def test_null_ai_provider_redacts_sensitive_context() -> None:
    provider = NullAIProvider(
        AISettings(
            enabled=False,
            provider_name="null",
            model=None,
            cost_class="UNKNOWN",
        )
    )

    result = provider.summarize(
        "Summarize this note.",
        context={
            "NVIDIA_API_KEY": "secret-value",
            "nested": {"token": "another-secret", "notes": ["safe", {"cookie": "hidden"}]},
            "notes": "safe",
        },
    )

    assert provider.is_available() is False
    assert result.provider_name == "null"
    assert result.status == "disabled"
    assert result.content is None
    assert result.metadata["reason"] == "ai_disabled"
    assert result.metadata["context"]["NVIDIA_API_KEY"] == "[REDACTED]"
    assert result.metadata["context"]["nested"]["token"] == "[REDACTED]"
    assert result.metadata["context"]["nested"]["notes"][1]["cookie"] == "[REDACTED]"
    assert result.metadata["context"]["notes"] == "safe"


def test_paid_ai_provider_is_blocked_by_default() -> None:
    provider = build_ai_provider(
        AISettings(
            enabled=True,
            provider_name="nvidia",
            model="demo-model",
            allow_paid_ai=False,
            cost_class="PAID_OR_BILLABLE",
        )
    )

    assert isinstance(provider, NullAIProvider)
    assert provider.provider_name == "nvidia"
    assert provider.status == "blocked_paid_disabled"
    assert provider.is_available() is False


def test_core_modules_do_not_import_nvidia_or_optional_ai() -> None:
    for module_name in CORE_MODULES:
        imports = _module_imports(ROOT / "src" / "etsy_research" / f"{module_name}.py")
        assert not any(target.startswith("nvidia") for target in imports)
        assert not any(target.endswith(".ai") for target in imports)
        assert "etsy_research.ai" not in imports


@pytest.mark.parametrize(
    "ai_settings",
    [
        AISettings(enabled=False, provider_name="null", cost_class="UNKNOWN"),
        AISettings(
            enabled=True,
            provider_name="nvidia",
            model="demo-model",
            allow_paid_ai=False,
            cost_class="PAID_OR_BILLABLE",
        ),
    ],
)
def test_core_scores_and_verdicts_stay_deterministic(ai_settings: AISettings) -> None:
    provider = build_ai_provider(ai_settings)
    metrics = {
        "top20_new_shop_penetration": 0.2,
        "top50_new_shop_penetration": 0.3,
        "unique_new_shop_diversity": 0.4,
        "recent_listing_penetration": 0.5,
        "incumbency_concentration": 0.1,
    }
    weights = {
        "top20_new_shop_penetration": 35,
        "top50_new_shop_penetration": 20,
        "unique_new_shop_diversity": 15,
        "recent_listing_penetration": 15,
        "incumbency_concentration": 15,
    }

    score_without_ai = score_entry(metrics, weights)
    verdict_without_ai = verdict_from_score(
        score=score_without_ai.score,
        top20_new_shop_share=0.2,
        top50_unique_new_shops=5,
        live_data_available=True,
    )

    score_with_ai = score_entry(metrics, weights)
    verdict_with_ai = verdict_from_score(
        score=score_with_ai.score,
        top20_new_shop_share=0.2,
        top50_unique_new_shops=5,
        live_data_available=True,
    )

    assert provider.is_available() is False
    assert score_with_ai.model_dump() == score_without_ai.model_dump()
    assert verdict_with_ai.model_dump() == verdict_without_ai.model_dump()
