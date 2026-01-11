"""Unit tests for e-Stat API client."""

import os
from collections.abc import Generator
from unittest.mock import patch

import httpx
import pytest
import respx

from e_stat_mcp.client import EStatApiError, EStatClient, _calculate_pagination
from e_stat_mcp.models.errors import EStatErrorCode
from e_stat_mcp.settings import Settings


class TestCalculatePagination:
    """_calculate_pagination関数のテスト."""

    def test_has_next_true(self) -> None:
        """次ページがある場合にTrueを返すこと."""
        has_next, next_pos = _calculate_pagination(
            start_position=1, returned_count=10000, total_count=25000
        )
        assert has_next is True
        assert next_pos == 10001

    def test_has_next_false_at_end(self) -> None:
        """最終ページの場合にFalseを返すこと."""
        has_next, next_pos = _calculate_pagination(
            start_position=1, returned_count=5000, total_count=5000
        )
        assert has_next is False
        assert next_pos is None

    def test_has_next_false_beyond_end(self) -> None:
        """データが総数を超えた場合にFalseを返すこと."""
        has_next, next_pos = _calculate_pagination(
            start_position=10001, returned_count=5000, total_count=15000
        )
        assert has_next is False
        assert next_pos is None

    def test_returned_count_zero_prevents_infinite_loop(self) -> None:
        """returned_count=0の場合はFalseを返すこと（無限ループ防止）."""
        has_next, next_pos = _calculate_pagination(
            start_position=1, returned_count=0, total_count=25000
        )
        assert has_next is False
        assert next_pos is None

    def test_middle_page(self) -> None:
        """中間ページで正しく計算されること."""
        has_next, next_pos = _calculate_pagination(
            start_position=10001, returned_count=10000, total_count=25000
        )
        assert has_next is True
        assert next_pos == 20001

    def test_exactly_at_limit(self) -> None:
        """ちょうどlimitでデータが終わる場合."""
        # start_position=20001, returned=5000, total=25000
        # 20001 + 5000 - 1 = 25000 == total_count → has_next=False
        has_next, next_pos = _calculate_pagination(
            start_position=20001, returned_count=5000, total_count=25000
        )
        assert has_next is False
        assert next_pos is None


@pytest.fixture
def mock_settings() -> Generator[Settings]:
    """モック設定を作成."""
    with patch.dict(
        os.environ,
        {
            "E_STAT_APP_ID": "test_app_id_12345",
            "E_STAT_BASE_URL": "https://api.e-stat.go.jp/rest/3.0/app/json",
            "E_STAT_CACHE_TTL_SECONDS": "3600",
            "E_STAT_REQUEST_TIMEOUT_SECONDS": "30",
            "E_STAT_MAX_RETRIES": "3",
            "E_STAT_CACHE_MAX_SIZE": "1000",
        },
    ):
        yield Settings()


class TestEStatApiError:
    """EStatApiErrorのテスト."""

    def test_create_error(self) -> None:
        """エラーを作成できること."""
        error = EStatApiError(
            message="Authentication failed",
            code=EStatErrorCode.AUTH_ERROR,
        )
        assert error.message == "Authentication failed"
        assert error.code == EStatErrorCode.AUTH_ERROR
        assert error.parameter is None

    def test_create_error_with_parameter(self) -> None:
        """パラメータ付きでエラーを作成できること."""
        error = EStatApiError(
            message="Invalid parameter",
            code=EStatErrorCode.INVALID_PARAM,
            parameter="statsDataId",
        )
        assert error.message == "Invalid parameter"
        assert error.code == EStatErrorCode.INVALID_PARAM
        assert error.parameter == "statsDataId"

    def test_get_user_message_auth_error(self) -> None:
        """認証エラーのユーザー向けメッセージを取得できること."""
        error = EStatApiError(
            message="Auth failed",
            code=EStatErrorCode.AUTH_ERROR,
        )
        message = error.get_user_message()
        assert "認証に失敗しました" in message
        assert "E_STAT_APP_ID" in message

    def test_get_user_message_no_data(self) -> None:
        """データなしエラーのユーザー向けメッセージを取得できること."""
        error = EStatApiError(
            message="No data",
            code=EStatErrorCode.NO_DATA,
        )
        message = error.get_user_message()
        assert "該当するデータが見つかりませんでした" in message

    def test_get_user_message_missing_param(self) -> None:
        """パラメータ不足エラーのユーザー向けメッセージを取得できること."""
        error = EStatApiError(
            message="Missing param",
            code=EStatErrorCode.MISSING_PARAM,
            parameter="statsDataId",
        )
        message = error.get_user_message()
        assert "必須パラメータが指定されていません" in message
        assert "statsDataId" in message

    def test_get_user_message_invalid_param(self) -> None:
        """不正パラメータエラーのユーザー向けメッセージを取得できること."""
        error = EStatApiError(
            message="Invalid param",
            code=EStatErrorCode.INVALID_PARAM,
            parameter="cdTime",
        )
        message = error.get_user_message()
        assert "パラメータ値が不正です" in message
        assert "cdTime" in message

    def test_get_user_message_data_not_found(self) -> None:
        """データ未発見エラーのユーザー向けメッセージを取得できること."""
        error = EStatApiError(
            message="Data not found",
            code=EStatErrorCode.DATA_NOT_FOUND,
        )
        message = error.get_user_message()
        assert "指定されたデータが存在しません" in message


class TestEStatClient:
    """EStatClientのテスト."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_settings: Settings) -> None:
        """クライアントを初期化できること."""
        client = EStatClient(mock_settings)
        assert client._settings == mock_settings
        assert client._client is None
        await client.close()

    @pytest.mark.asyncio
    async def test_client_lazy_http_initialization(self, mock_settings: Settings) -> None:
        """HTTPクライアントが遅延初期化されること."""
        client = EStatClient(mock_settings)
        assert client._client is None

        http_client = await client._get_client()
        assert http_client is not None
        assert client._client is not None

        await client.close()
        assert client._client is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_stats_list_success(self, mock_settings: Settings) -> None:
        """統計表リストを取得できること."""
        mock_response = {
            "GET_STATS_LIST": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
                "DATALIST_INF": {
                    "TABLE_INF": [
                        {
                            "@id": "0003410379",
                            "STAT_NAME": "国勢調査",
                            "GOV_ORG": "総務省",
                            "TITLE": "男女別人口",
                            "SURVEY_DATE": "202010",
                        }
                    ]
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = EStatClient(mock_settings)
        results = await client.get_stats_list(keyword="人口")

        assert len(results) == 1
        assert results[0].table_id == "0003410379"
        assert results[0].stat_name == "国勢調査"
        assert results[0].gov_org == "総務省"
        assert results[0].table_name == "男女別人口"

        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_stats_list_no_data(self, mock_settings: Settings) -> None:
        """検索結果がない場合、空リストを返すこと."""
        mock_response = {
            "GET_STATS_LIST": {
                "RESULT": {
                    "STATUS": 1,
                    "ERROR_MSG": "該当データなし",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = EStatClient(mock_settings)
        results = await client.get_stats_list(keyword="存在しないデータ")

        assert len(results) == 0

        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_stats_list_auth_error(self, mock_settings: Settings) -> None:
        """認証エラーの場合、EStatApiErrorを発生させること."""
        mock_response = {
            "GET_STATS_LIST": {
                "RESULT": {
                    "STATUS": 100,
                    "ERROR_MSG": "アプリケーションIDが不正です",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = EStatClient(mock_settings)

        with pytest.raises(EStatApiError) as exc_info:
            await client.get_stats_list(keyword="人口")

        assert exc_info.value.code == EStatErrorCode.AUTH_ERROR

        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_cache_hit(self, mock_settings: Settings) -> None:
        """同じリクエストはキャッシュから返されること."""
        mock_response = {
            "GET_STATS_LIST": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
                "DATALIST_INF": {
                    "TABLE_INF": [
                        {
                            "@id": "0003410379",
                            "STAT_NAME": "国勢調査",
                            "GOV_ORG": "総務省",
                            "TITLE": "男女別人口",
                        }
                    ]
                },
            }
        }

        route = respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = EStatClient(mock_settings)

        # First request - should hit API
        results1 = await client.get_stats_list(keyword="人口")
        assert len(results1) == 1
        assert route.call_count == 1

        # Second request - should hit cache
        results2 = await client.get_stats_list(keyword="人口")
        assert len(results2) == 1
        assert route.call_count == 1  # Still 1 - cache hit

        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_meta_info_success(self, mock_settings: Settings) -> None:
        """メタ情報を取得できること."""
        mock_response = {
            "GET_META_INFO": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
                "CLASS_INF": {
                    "CLASS_OBJ": [
                        {
                            "@id": "tab",
                            "@name": "表章事項",
                            "CLASS": [
                                {"@code": "001", "$": "人口"},
                                {"@code": "002", "$": "面積"},
                            ],
                        }
                    ]
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = EStatClient(mock_settings)
        results = await client.get_meta_info("0003410379")

        assert len(results) == 1
        assert results[0].class_id == "tab"
        assert results[0].class_name == "表章事項"
        assert len(results[0].items) == 2
        assert results[0].items[0].code == "001"
        assert results[0].items[0].name == "人口"

        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_stats_data_success(self, mock_settings: Settings) -> None:
        """統計データを取得できること."""
        mock_response = {
            "GET_STATS_DATA": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
                "STATISTICAL_DATA": {
                    "CLASS_INF": {
                        "CLASS_OBJ": [
                            {
                                "@id": "tab",
                                "@name": "表章事項",
                                "CLASS": [{"@code": "001", "$": "人口"}],
                            },
                            {
                                "@id": "area",
                                "@name": "地域",
                                "CLASS": [{"@code": "00000", "$": "全国"}],
                            },
                        ]
                    },
                    "DATA_INF": {
                        "@totalNumber": "1",
                        "VALUE": [
                            {
                                "@tab": "001",
                                "@area": "00000",
                                "@unit": "人",
                                "$": "126000000",
                            }
                        ],
                    },
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = EStatClient(mock_settings)
        result = await client.get_stats_data("0003410379")

        assert result.total_count == 1
        assert result.returned_count == 1
        assert len(result.data) == 1
        assert result.data[0].tab_name == "人口"
        assert result.data[0].area_name == "全国"
        assert result.data[0].value == 126000000.0
        assert result.data[0].unit == "人"

        await client.close()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_datasets_success(self, mock_settings: Settings) -> None:
        """データセット一覧を取得できること."""
        mock_response = {
            "REF_DATASET": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
                "DATALIST_INF": {
                    "DATASET_INF": [
                        {
                            "@id": "DS001",
                            "STATS_DATA_ID": "0003410379",
                            "DATASET_NAME": "人口データセット",
                            "OPEN": "1",
                        }
                    ]
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/refDataset").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        client = EStatClient(mock_settings)
        results = await client.get_datasets()

        assert len(results) == 1
        assert results[0].dataset_id == "DS001"
        assert results[0].dataset_name == "人口データセット"
        assert results[0].stats_data_id == "0003410379"
        assert results[0].is_public is True

        await client.close()
