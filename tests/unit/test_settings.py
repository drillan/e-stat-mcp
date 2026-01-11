"""Unit tests for Settings model."""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest

from e_stat_mcp.settings import Settings


@pytest.fixture
def clean_env() -> Generator[None]:
    """環境変数をクリーンな状態にするフィクスチャ."""
    env_vars = [
        "E_STAT_APP_ID",
        "E_STAT_BASE_URL",
        "E_STAT_CACHE_TTL_SECONDS",
        "E_STAT_REQUEST_TIMEOUT_SECONDS",
        "E_STAT_MAX_RETRIES",
    ]
    original_values = {k: os.environ.get(k) for k in env_vars}

    for k in env_vars:
        if k in os.environ:
            del os.environ[k]

    yield

    for k, v in original_values.items():
        if v is not None:
            os.environ[k] = v
        elif k in os.environ:
            del os.environ[k]


class TestSettingsValidation:
    """Settingsモデルのバリデーションテスト."""

    def test_valid_settings_from_env(self, clean_env: None) -> None:
        """環境変数から有効な設定を読み込めること."""
        with patch.dict(
            os.environ,
            {
                "E_STAT_APP_ID": "test_app_id_12345",
            },
        ):
            settings = Settings()
            assert settings.e_stat_app_id == "test_app_id_12345"
            assert settings.e_stat_base_url == "https://api.e-stat.go.jp/rest/3.0/app/json"
            assert settings.cache_ttl_seconds == 3600
            assert settings.request_timeout_seconds == 30
            assert settings.max_retries == 3

    def test_custom_settings_from_env(self, clean_env: None) -> None:
        """カスタム設定値を環境変数から読み込めること."""
        with patch.dict(
            os.environ,
            {
                "E_STAT_APP_ID": "custom_app_id",
                "E_STAT_BASE_URL": "https://custom.api.example.com",
                "E_STAT_CACHE_TTL_SECONDS": "7200",
                "E_STAT_REQUEST_TIMEOUT_SECONDS": "60",
                "E_STAT_MAX_RETRIES": "5",
            },
        ):
            settings = Settings()
            assert settings.e_stat_app_id == "custom_app_id"
            assert settings.e_stat_base_url == "https://custom.api.example.com"
            assert settings.cache_ttl_seconds == 7200
            assert settings.request_timeout_seconds == 60
            assert settings.max_retries == 5

    def test_missing_app_id_raises_error(self, clean_env: None) -> None:
        """必須のapp_idが未設定の場合、エラーが発生すること."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("e_stat_app_id",)
        assert errors[0]["type"] == "missing"

    def test_invalid_cache_ttl_type(self, clean_env: None) -> None:
        """cache_ttlに不正な型を指定した場合、エラーが発生すること."""
        from pydantic import ValidationError

        with patch.dict(
            os.environ,
            {
                "E_STAT_APP_ID": "test_app_id",
                "E_STAT_CACHE_TTL_SECONDS": "not_a_number",
            },
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any(e["loc"] == ("e_stat_cache_ttl_seconds",) for e in errors)

    def test_empty_app_id_raises_error(self, clean_env: None) -> None:
        """空のapp_idを指定した場合、エラーが発生すること."""
        from pydantic import ValidationError

        with patch.dict(
            os.environ,
            {
                "E_STAT_APP_ID": "",
            },
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            errors = exc_info.value.errors()
            assert any(e["loc"] == ("e_stat_app_id",) for e in errors)
