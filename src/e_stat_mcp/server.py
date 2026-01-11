"""e-Stat MCP サーバー."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from e_stat_mcp.client import EStatApiError, EStatClient
from e_stat_mcp.models.tools import (
    GetDatasetDataRequest,
    GetMetaInfoRequest,
    GetStatsDataRequest,
    ListDatasetsRequest,
    SearchStatsRequest,
)
from e_stat_mcp.settings import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_server: FastMCP) -> AsyncIterator[dict[str, EStatClient]]:
    """サーバーのライフサイクルを管理.

    Args:
        _server: FastMCPサーバーインスタンス（未使用）

    Yields:
        コンテキストデータ（EStatClientを含む）
    """
    settings = get_settings()
    client = EStatClient(settings)
    logger.info("e-Stat MCP server starting up")
    try:
        yield {"client": client}
    finally:
        await client.close()
        logger.info("e-Stat MCP server shutting down")


# MCPサーバーインスタンスを作成
mcp = FastMCP(
    "e-stat-mcp",
    dependencies=["e_stat_mcp"],
    lifespan=lifespan,
)


@mcp.tool()
async def search_stats(
    keyword: str | None = None,
    stats_code: str | None = None,
    survey_years: str | None = None,
    limit: int = 100,
    start_position: int = 1,
) -> list[dict[str, str | None]]:
    """統計表を検索します.

    Args:
        keyword: 検索キーワード（統計表名、作成機関名などから検索）
        stats_code: 政府統計コード（例: "00200521"は国勢調査）
        survey_years: 調査年の範囲（例: "2020" または "2020-2023"）
        limit: 取得件数上限（デフォルト: 100、最大: 100000）
        start_position: 取得開始位置（デフォルト: 1）

    Returns:
        検索結果のリスト。各要素には以下が含まれます:
        - table_id: 統計表ID（get_stats_dataで使用）
        - table_name: 統計表名称
        - stat_name: 政府統計名称
        - survey_date: 調査年月
        - gov_org: 作成機関

    Raises:
        EStatApiError: API呼び出しに失敗した場合
    """
    request = SearchStatsRequest(
        keyword=keyword,
        stats_code=stats_code,
        survey_years=survey_years,
        limit=limit,
        start_position=start_position,
    )

    try:
        settings = get_settings()
        client = EStatClient(settings)
        try:
            results = await client.get_stats_list(
                keyword=request.keyword,
                stats_code=request.stats_code,
                survey_years=request.survey_years,
                limit=request.limit,
                start_position=request.start_position,
            )
            return [
                {
                    "table_id": r.table_id,
                    "table_name": r.table_name,
                    "stat_name": r.stat_name,
                    "survey_date": r.survey_date,
                    "gov_org": r.gov_org,
                }
                for r in results
            ]
        finally:
            await client.close()
    except EStatApiError as e:
        logger.error("search_stats failed: %s", e.get_user_message())
        raise


@mcp.tool()
async def get_stats_data(
    stats_data_id: str,
    cd_tab: str | None = None,
    cd_cat01: str | None = None,
    cd_cat02: str | None = None,
    cd_area: str | None = None,
    cd_time: str | None = None,
    limit: int = 10000,
    start_position: int = 1,
) -> dict[str, int | list[dict[str, str | float | dict[str, str] | None]]]:
    """統計データを取得します.

    Args:
        stats_data_id: 統計表ID（search_statsで取得したtable_id）
        cd_tab: 表章事項コード（get_meta_infoで取得可能）
        cd_cat01: 分類事項コード01
        cd_cat02: 分類事項コード02
        cd_area: 地域コード
        cd_time: 時間軸コード
        limit: 取得件数上限（デフォルト: 10000）
        start_position: 取得開始位置

    Returns:
        統計データ結果:
        - total_count: 総データ件数
        - returned_count: 今回返却した件数
        - data: 統計データのリスト

    Raises:
        EStatApiError: API呼び出しに失敗した場合
    """
    request = GetStatsDataRequest(
        stats_data_id=stats_data_id,
        cd_tab=cd_tab,
        cd_cat01=cd_cat01,
        cd_cat02=cd_cat02,
        cd_area=cd_area,
        cd_time=cd_time,
        limit=limit,
        start_position=start_position,
    )

    try:
        settings = get_settings()
        client = EStatClient(settings)
        try:
            result = await client.get_stats_data(
                stats_data_id=request.stats_data_id,
                cd_tab=request.cd_tab,
                cd_cat01=request.cd_cat01,
                cd_cat02=request.cd_cat02,
                cd_area=request.cd_area,
                cd_time=request.cd_time,
                limit=request.limit,
                start_position=request.start_position,
            )
            return {
                "total_count": result.total_count,
                "returned_count": result.returned_count,
                "data": [
                    {
                        "tab_name": item.tab_name,
                        "category_names": item.category_names,
                        "area_name": item.area_name,
                        "time_name": item.time_name,
                        "value": item.value,
                        "value_raw": item.value_raw,
                        "unit": item.unit,
                    }
                    for item in result.data
                ],
            }
        finally:
            await client.close()
    except EStatApiError as e:
        logger.error("get_stats_data failed: %s", e.get_user_message())
        raise


@mcp.tool()
async def get_meta_info(
    stats_data_id: str,
) -> list[dict[str, str | list[dict[str, str | None]]]]:
    """統計表のメタ情報を取得します.

    Args:
        stats_data_id: 統計表ID

    Returns:
        メタ情報のリスト。各要素には以下が含まれます:
        - class_id: 分類ID（例: "tab", "cat01", "area", "time"）
        - class_name: 分類名（例: "表章事項", "地域"）
        - items: 分類項目のリスト
            - code: コード
            - name: 名称
            - level: 階層レベル（オプション）
            - unit: 単位（オプション）

    Raises:
        EStatApiError: API呼び出しに失敗した場合
    """
    request = GetMetaInfoRequest(stats_data_id=stats_data_id)

    try:
        settings = get_settings()
        client = EStatClient(settings)
        try:
            results = await client.get_meta_info(request.stats_data_id)
            return [
                {
                    "class_id": r.class_id,
                    "class_name": r.class_name,
                    "items": [
                        {
                            "code": item.code,
                            "name": item.name,
                            "level": item.level,
                            "unit": item.unit,
                        }
                        for item in r.items
                    ],
                }
                for r in results
            ]
        finally:
            await client.close()
    except EStatApiError as e:
        logger.error("get_meta_info failed: %s", e.get_user_message())
        raise


@mcp.tool()
async def list_datasets(
    stats_data_id: str | None = None,
) -> list[dict[str, str | bool | None]]:
    """公開データセットの一覧を取得します.

    Args:
        stats_data_id: 統計表ID（指定すると特定の統計表に関連するデータセットのみ取得）

    Returns:
        データセットのリスト。各要素には以下が含まれます:
        - dataset_id: データセットID（get_dataset_dataで使用）
        - dataset_name: データセット名
        - stats_data_id: 対象統計表ID
        - is_public: 公開状態
        - description: 説明（オプション）

    Raises:
        EStatApiError: API呼び出しに失敗した場合
    """
    request = ListDatasetsRequest(stats_data_id=stats_data_id)

    try:
        settings = get_settings()
        client = EStatClient(settings)
        try:
            results = await client.get_datasets(request.stats_data_id)
            return [
                {
                    "dataset_id": r.dataset_id,
                    "dataset_name": r.dataset_name,
                    "stats_data_id": r.stats_data_id,
                    "is_public": r.is_public,
                    "description": r.description,
                }
                for r in results
            ]
        finally:
            await client.close()
    except EStatApiError as e:
        logger.error("list_datasets failed: %s", e.get_user_message())
        raise


@mcp.tool()
async def get_dataset_data(
    dataset_id: str,
    limit: int = 10000,
    start_position: int = 1,
) -> dict[str, int | list[dict[str, str | float | dict[str, str] | None]]]:
    """データセットのデータを取得します.

    Args:
        dataset_id: データセットID（list_datasetsで取得）
        limit: 取得件数上限（デフォルト: 10000）
        start_position: 取得開始位置

    Returns:
        統計データ結果:
        - total_count: 総データ件数
        - returned_count: 今回返却した件数
        - data: 統計データのリスト

    Raises:
        EStatApiError: API呼び出しに失敗した場合
    """
    request = GetDatasetDataRequest(
        dataset_id=dataset_id,
        limit=limit,
        start_position=start_position,
    )

    try:
        settings = get_settings()
        client = EStatClient(settings)
        try:
            result = await client.get_dataset_data(
                dataset_id=request.dataset_id,
                limit=request.limit,
                start_position=request.start_position,
            )
            return {
                "total_count": result.total_count,
                "returned_count": result.returned_count,
                "data": [
                    {
                        "tab_name": item.tab_name,
                        "category_names": item.category_names,
                        "area_name": item.area_name,
                        "time_name": item.time_name,
                        "value": item.value,
                        "value_raw": item.value_raw,
                        "unit": item.unit,
                    }
                    for item in result.data
                ],
            }
        finally:
            await client.close()
    except EStatApiError as e:
        logger.error("get_dataset_data failed: %s", e.get_user_message())
        raise


def run_server() -> None:
    """MCPサーバーを起動."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 設定の検証（起動時にエラーを早期検出）
    try:
        settings = get_settings()
        logger.info("e-Stat MCP server configured with base URL: %s", settings.e_stat_base_url)
    except Exception as e:
        logger.error("Failed to load settings: %s", e)
        raise

    mcp.run()
