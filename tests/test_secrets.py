from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_env_example_placeholder_only() -> None:
    content = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "ETSY_APP_APPROVAL=PENDING" in content
    assert "ETSY_API_KEYSTRING=" in content
    assert "ETSY_SHARED_SECRET=" in content
    assert "FIRECRAWL_API_KEY=" in content
    assert "ETSY_API_KEY=" not in content
    assert "sk-" not in content
    assert "BEGIN PRIVATE KEY" not in content


def test_gitignore_and_fixture_safety() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore
    assert ".env.*" in gitignore
    assert "!.env.example" in gitignore
    assert "__pycache__/" in gitignore
    assert ".pytest_cache/" in gitignore
    assert ".venv/" in gitignore
    assert "research/rq2/raw/*" in gitignore
    assert "!research/rq2/raw/.gitkeep" in gitignore

    for fixture_name in ["strong_entry.json", "mixed_entry.json", "incumbent_dominated.json"]:
        content = (ROOT / "tests" / "fixtures" / fixture_name).read_text(encoding="utf-8")
        assert "TEST_ONLY" in content
        assert "sk-" not in content
        assert "xoxb-" not in content
        assert "BEGIN PRIVATE KEY" not in content
