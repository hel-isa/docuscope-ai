import importlib

import pytest

from app import config as config_module


def _reload_config():
    return importlib.reload(config_module)


@pytest.fixture(autouse=True)
def _restore_config_after_test():
    """app/config.py reads env vars at import time; reloading it inside a
    test only reflects the change while monkeypatch's env vars are set. Once
    monkeypatch tears down (restoring the real environment), reload again so
    later tests never see state left over from this module's reload calls."""
    yield
    _reload_config()


def test_defaults_hold_when_env_unset(monkeypatch) -> None:
    for var in [
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_MODEL",
        "AI_ENABLED",
        "MAX_FILE_SIZE_BYTES",
        "REVIEW_CONFIDENCE_THRESHOLD",
    ]:
        monkeypatch.delenv(var, raising=False)

    cfg = _reload_config()

    assert cfg.ANTHROPIC_API_KEY is None
    assert cfg.AI_ENABLED is True
    assert cfg.REVIEW_CONFIDENCE_THRESHOLD == 0.75
    assert cfg.MAX_FILE_SIZE_BYTES == 50_000_000


def test_env_values_are_picked_up(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    monkeypatch.setenv("AI_ENABLED", "false")
    monkeypatch.setenv("MAX_FILE_SIZE_BYTES", "1234")
    monkeypatch.setenv("REVIEW_CONFIDENCE_THRESHOLD", "0.5")

    cfg = _reload_config()

    assert cfg.ANTHROPIC_API_KEY == "test-key-123"
    assert cfg.ANTHROPIC_MODEL == "claude-sonnet-5"
    assert cfg.AI_ENABLED is False
    assert cfg.MAX_FILE_SIZE_BYTES == 1234
    assert cfg.REVIEW_CONFIDENCE_THRESHOLD == 0.5


def test_empty_api_key_is_treated_as_unset(monkeypatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")

    cfg = _reload_config()

    assert cfg.ANTHROPIC_API_KEY is None


def test_malformed_numeric_env_var_fails_fast_with_clear_message(monkeypatch) -> None:
    """
    These values gate security-relevant limits — a typo (e.g. a stray unit
    suffix) must fail loudly at startup, not silently fall back to a default
    that might be weaker than the operator intended.
    """
    monkeypatch.setenv("ANTHROPIC_TIMEOUT_SECONDS", "20s")

    with pytest.raises(ValueError, match="ANTHROPIC_TIMEOUT_SECONDS"):
        _reload_config()
