"""設定管理モジュール."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MCPサーバー設定.

    環境変数から設定を読み込む。
    環境変数名: E_STAT_APP_ID, E_STAT_BASE_URL, E_STAT_CACHE_TTL_SECONDS など
    """

    e_stat_app_id: str = Field(..., description="e-StatアプリケーションID（必須）")
    e_stat_base_url: str = Field(
        default="https://api.e-stat.go.jp/rest/3.0/app/json",
        description="e-Stat API ベースURL",
    )
    e_stat_cache_ttl_seconds: int = Field(
        default=3600,
        description="キャッシュTTL（秒）",
    )
    e_stat_request_timeout_seconds: int = Field(
        default=30,
        description="リクエストタイムアウト（秒）",
    )
    e_stat_max_retries: int = Field(
        default=3,
        description="最大リトライ回数",
    )
    e_stat_cache_max_size: int = Field(
        default=1000,
        description="キャッシュの最大エントリ数",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("e_stat_app_id")
    @classmethod
    def validate_app_id_not_empty(cls, v: str) -> str:
        """アプリケーションIDが空でないことを検証."""
        if not v.strip():
            msg = "e_stat_app_id must not be empty"
            raise ValueError(msg)
        return v

    @property
    def cache_ttl_seconds(self) -> int:
        """キャッシュTTL（秒）."""
        return self.e_stat_cache_ttl_seconds

    @property
    def request_timeout_seconds(self) -> int:
        """リクエストタイムアウト（秒）."""
        return self.e_stat_request_timeout_seconds

    @property
    def max_retries(self) -> int:
        """最大リトライ回数."""
        return self.e_stat_max_retries

    @property
    def cache_max_size(self) -> int:
        """キャッシュの最大エントリ数."""
        return self.e_stat_cache_max_size


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得.

    Returns:
        Settings: 設定インスタンス

    Raises:
        ValidationError: 必須の設定が未設定の場合
    """
    return Settings()
