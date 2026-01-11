"""Integration tests for e-Stat API.

Note: These tests require a valid E_STAT_APP_ID environment variable.
They are marked as integration tests and can be skipped with:
    pytest -m "not integration"
"""

import os

import pytest

from e_stat_mcp.client import EStatApiError, EStatClient
from e_stat_mcp.models.errors import EStatErrorCode
from e_stat_mcp.settings import Settings


@pytest.fixture
def integration_settings() -> Settings:
    """統合テスト用の設定を作成.

    環境変数 E_STAT_APP_ID が設定されていない場合はスキップ.
    """
    app_id = os.environ.get("E_STAT_APP_ID")
    if not app_id:
        pytest.skip("E_STAT_APP_ID environment variable not set")

    return Settings()


@pytest.mark.integration
class TestEStatApiAuthentication:
    """e-Stat API認証のテスト."""

    @pytest.mark.asyncio
    async def test_valid_app_id_authenticates_successfully(
        self, integration_settings: Settings
    ) -> None:
        """有効なアプリケーションIDで認証が成功すること."""
        client = EStatClient(integration_settings)

        try:
            # Simple search should work with valid app ID
            results = await client.get_stats_list(keyword="人口", limit=1)
            # Should not raise an auth error
            assert isinstance(results, list)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_invalid_app_id_returns_auth_error(self) -> None:
        """無効なアプリケーションIDで認証エラーが発生すること."""
        from unittest.mock import patch

        with patch.dict(
            os.environ,
            {
                "E_STAT_APP_ID": "invalid_app_id_12345",
            },
        ):
            from e_stat_mcp.settings import Settings

            settings = Settings()
            client = EStatClient(settings)

            try:
                with pytest.raises(EStatApiError) as exc_info:
                    await client.get_stats_list(keyword="人口")

                assert exc_info.value.code == EStatErrorCode.AUTH_ERROR
                user_message = exc_info.value.get_user_message()
                assert "認証に失敗しました" in user_message
            finally:
                await client.close()


@pytest.mark.integration
class TestEStatApiSearch:
    """e-Stat API検索のテスト."""

    @pytest.mark.asyncio
    async def test_search_stats_returns_results(self, integration_settings: Settings) -> None:
        """キーワード検索で統計表リストを取得できること."""
        client = EStatClient(integration_settings)

        try:
            results = await client.get_stats_list(keyword="国勢調査", limit=5)

            assert len(results) > 0
            for result in results:
                assert result.table_id
                assert result.table_name
                assert result.stat_name
                assert result.gov_org
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_search_stats_with_no_results(self, integration_settings: Settings) -> None:
        """該当データがない場合、空リストを返すこと."""
        client = EStatClient(integration_settings)

        try:
            results = await client.get_stats_list(keyword="xyznonexistentkeyword12345")
            assert isinstance(results, list)
            assert len(results) == 0
        finally:
            await client.close()


@pytest.mark.integration
class TestEStatApiMetaInfo:
    """e-Stat APIメタ情報取得のテスト."""

    @pytest.mark.asyncio
    async def test_get_meta_info_returns_class_info(self, integration_settings: Settings) -> None:
        """メタ情報を取得できること."""
        client = EStatClient(integration_settings)

        try:
            # First, find a valid stats data ID
            search_results = await client.get_stats_list(keyword="国勢調査", limit=1)
            if not search_results:
                pytest.skip("No stats data found for testing")

            stats_data_id = search_results[0].table_id

            # Get meta info
            meta_results = await client.get_meta_info(stats_data_id)

            assert len(meta_results) > 0
            for meta in meta_results:
                assert meta.class_id
                assert meta.class_name
                assert isinstance(meta.items, list)
        finally:
            await client.close()


@pytest.mark.integration
class TestEStatApiStatsData:
    """e-Stat API統計データ取得のテスト."""

    @pytest.mark.asyncio
    async def test_get_stats_data_returns_values(self, integration_settings: Settings) -> None:
        """統計データを取得できること."""
        client = EStatClient(integration_settings)

        try:
            # First, find a valid stats data ID
            search_results = await client.get_stats_list(keyword="国勢調査", limit=1)
            if not search_results:
                pytest.skip("No stats data found for testing")

            stats_data_id = search_results[0].table_id

            # Get stats data with limit
            result = await client.get_stats_data(stats_data_id, limit=10)

            assert result.returned_count > 0
            assert len(result.data) > 0
            for item in result.data:
                assert item.tab_name
                assert item.value_raw
        finally:
            await client.close()
