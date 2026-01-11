"""Contract tests for MCP tools.

These tests verify that the MCP tools conform to the expected interface
as defined in contracts/mcp-tools.yaml.
"""

import os
from collections.abc import Generator
from unittest.mock import patch

import httpx
import pytest
import respx


@pytest.fixture
def mock_env() -> Generator[None]:
    """テスト用の環境変数を設定."""
    with patch.dict(
        os.environ,
        {
            "E_STAT_APP_ID": "test_app_id_12345",
        },
    ):
        yield


class TestSearchStatsTool:
    """search_statsツールのコントラクトテスト."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_stats_returns_list(self, mock_env: None) -> None:
        """search_statsがリストを返すこと."""
        from e_stat_mcp.server import search_stats

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

        results = await search_stats(keyword="人口")

        assert isinstance(results, list)
        assert len(results) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_stats_result_structure(self, mock_env: None) -> None:
        """search_statsの結果が正しい構造を持つこと."""
        from e_stat_mcp.server import search_stats

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

        results = await search_stats(keyword="人口")
        result = results[0]

        # Contract: Each result must have these fields
        assert "table_id" in result
        assert "table_name" in result
        assert "stat_name" in result
        assert "survey_date" in result
        assert "gov_org" in result

        # Contract: All values are strings or None
        assert isinstance(result["table_id"], str)
        assert isinstance(result["table_name"], str)
        assert isinstance(result["stat_name"], str)
        assert result["survey_date"] is None or isinstance(result["survey_date"], str)
        assert isinstance(result["gov_org"], str)


class TestGetStatsDataTool:
    """get_stats_dataツールのコントラクトテスト."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_stats_data_returns_dict(self, mock_env: None) -> None:
        """get_stats_dataが辞書を返すこと."""
        from e_stat_mcp.server import get_stats_data

        mock_response = {
            "GET_STATS_DATA": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
                "STATISTICAL_DATA": {
                    "CLASS_INF": {"CLASS_OBJ": []},
                    "DATA_INF": {"@totalNumber": "1", "VALUE": []},
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await get_stats_data(stats_data_id="0003410379")

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_stats_data_result_structure(self, mock_env: None) -> None:
        """get_stats_dataの結果が正しい構造を持つこと."""
        from e_stat_mcp.server import get_stats_data

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
                            }
                        ]
                    },
                    "DATA_INF": {
                        "@totalNumber": "1",
                        "VALUE": [
                            {
                                "@tab": "001",
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

        result = await get_stats_data(stats_data_id="0003410379")

        # Contract: Result must have these fields
        assert "total_count" in result
        assert "returned_count" in result
        assert "data" in result

        # Contract: Types
        assert isinstance(result["total_count"], int)
        assert isinstance(result["returned_count"], int)
        assert isinstance(result["data"], list)


class TestGetMetaInfoTool:
    """get_meta_infoツールのコントラクトテスト."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_meta_info_returns_list(self, mock_env: None) -> None:
        """get_meta_infoがリストを返すこと."""
        from e_stat_mcp.server import get_meta_info

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
                            "CLASS": [{"@code": "001", "$": "人口"}],
                        }
                    ]
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        results = await get_meta_info(stats_data_id="0003410379")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_meta_info_result_structure(self, mock_env: None) -> None:
        """get_meta_infoの結果が正しい構造を持つこと."""
        from e_stat_mcp.server import get_meta_info

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
                            "CLASS": [{"@code": "001", "$": "人口"}],
                        }
                    ]
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        results = await get_meta_info(stats_data_id="0003410379")
        result = results[0]

        # Contract: Each result must have these fields
        assert "class_id" in result
        assert "class_name" in result
        assert "items" in result

        # Contract: Types
        assert isinstance(result["class_id"], str)
        assert isinstance(result["class_name"], str)
        assert isinstance(result["items"], list)


class TestListDatasetsTool:
    """list_datasetsツールのコントラクトテスト."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_datasets_returns_list(self, mock_env: None) -> None:
        """list_datasetsがリストを返すこと."""
        from e_stat_mcp.server import list_datasets

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

        results = await list_datasets()

        assert isinstance(results, list)

    @pytest.mark.asyncio
    @respx.mock
    async def test_list_datasets_result_structure(self, mock_env: None) -> None:
        """list_datasetsの結果が正しい構造を持つこと."""
        from e_stat_mcp.server import list_datasets

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

        results = await list_datasets()
        result = results[0]

        # Contract: Each result must have these fields
        assert "dataset_id" in result
        assert "dataset_name" in result
        assert "stats_data_id" in result
        assert "is_public" in result

        # Contract: Types
        assert isinstance(result["dataset_id"], str)
        assert isinstance(result["dataset_name"], str)
        assert isinstance(result["stats_data_id"], str)
        assert isinstance(result["is_public"], bool)


class TestGetDatasetDataTool:
    """get_dataset_dataツールのコントラクトテスト."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_dataset_data_returns_dict(self, mock_env: None) -> None:
        """get_dataset_dataが辞書を返すこと."""
        from e_stat_mcp.server import get_dataset_data

        mock_response = {
            "REF_DATASET": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
                "STATISTICAL_DATA": {
                    "CLASS_INF": {"CLASS_OBJ": []},
                    "DATA_INF": {"@totalNumber": "0", "VALUE": []},
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/refDataset").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await get_dataset_data(dataset_id="DS001")

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_dataset_data_result_structure(self, mock_env: None) -> None:
        """get_dataset_dataの結果が正しい構造を持つこと."""
        from e_stat_mcp.server import get_dataset_data

        mock_response = {
            "REF_DATASET": {
                "RESULT": {
                    "STATUS": 0,
                    "ERROR_MSG": "正常に終了しました。",
                    "DATE": "2024-01-01T00:00:00.000+09:00",
                },
                "PARAMETER": {"LANG": "J"},
                "STATISTICAL_DATA": {
                    "CLASS_INF": {"CLASS_OBJ": []},
                    "DATA_INF": {"@totalNumber": "0", "VALUE": []},
                },
            }
        }

        respx.get("https://api.e-stat.go.jp/rest/3.0/app/json/refDataset").mock(
            return_value=httpx.Response(200, json=mock_response)
        )

        result = await get_dataset_data(dataset_id="DS001")

        # Contract: Result must have these fields
        assert "total_count" in result
        assert "returned_count" in result
        assert "data" in result

        # Contract: Types
        assert isinstance(result["total_count"], int)
        assert isinstance(result["returned_count"], int)
        assert isinstance(result["data"], list)
