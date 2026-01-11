"""e-Stat APIクライアント."""

from __future__ import annotations

import hashlib
import logging
from typing import Any, TypeVar

import httpx
from cachetools import TTLCache
from pydantic import BaseModel, ValidationError

from e_stat_mcp.cache import create_cache, get_cache, set_cache
from e_stat_mcp.models.api import (
    ClassInfo,
    DatasetListResponse,
    MetaInfoResponse,
    StatsDataResponse,
    StatsListResponse,
    StatsTable,
)
from e_stat_mcp.models.errors import ApiResult, EStatErrorCode
from e_stat_mcp.models.tools import (
    ClassItemInfo,
    DatasetResult,
    MetaInfoResult,
    SearchStatsResult,
    StatsDataItem,
    StatsDataResult,
)
from e_stat_mcp.settings import Settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class EStatApiError(Exception):
    """e-Stat APIエラー."""

    def __init__(self, message: str, code: EStatErrorCode, parameter: str | None = None) -> None:
        """エラーを初期化.

        Args:
            message: エラーメッセージ
            code: e-Statエラーコード
            parameter: 関連するパラメータ名（オプション）
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.parameter = parameter

    @classmethod
    def from_api_result(cls, result: ApiResult) -> EStatApiError:
        """APIレスポンスからエラーを生成.

        Args:
            result: APIレスポンスの結果部分

        Returns:
            EStatApiError: エラーインスタンス
        """
        code = EStatErrorCode(result.status)
        return cls(message=result.error_msg, code=code)

    def get_user_message(self) -> str:
        """ユーザー向けのエラーメッセージを取得.

        Returns:
            ユーザー向けのエラーメッセージ
        """
        error_messages = {
            EStatErrorCode.AUTH_ERROR: (
                "認証に失敗しました。"
                "環境変数 E_STAT_APP_ID にe-StatのアプリケーションIDを設定してください。"
            ),
            EStatErrorCode.NO_DATA: (
                "該当するデータが見つかりませんでした。検索条件を変更して再度お試しください。"
            ),
            EStatErrorCode.MISSING_PARAM: (
                f"必須パラメータが指定されていません: {self.parameter or 'unknown'}"
            ),
            EStatErrorCode.INVALID_PARAM: (
                f"パラメータ値が不正です: {self.parameter or 'unknown'}"
            ),
            EStatErrorCode.DATA_NOT_FOUND: (
                "指定されたデータが存在しません。統計表IDまたはデータセットIDを確認してください。"
            ),
            EStatErrorCode.NETWORK_ERROR: (
                "ネットワークエラーが発生しました。インターネット接続を確認してください。"
            ),
            EStatErrorCode.SERVER_ERROR: (
                "e-Statサーバーでエラーが発生しました。しばらく待ってから再度お試しください。"
            ),
            EStatErrorCode.VALIDATION_ERROR: ("APIレスポンスの形式が不正です。"),
        }
        return error_messages.get(self.code, self.message)


class EStatClient:
    """e-Stat APIクライアント."""

    def __init__(self, settings: Settings) -> None:
        """クライアントを初期化.

        Args:
            settings: 設定インスタンス
        """
        self._settings = settings
        self._cache: TTLCache[str, Any] = create_cache(
            ttl=settings.cache_ttl_seconds,
            maxsize=settings.cache_max_size,
        )
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """HTTPクライアントを取得（遅延初期化）.

        Returns:
            httpx.AsyncClient: HTTPクライアント
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._settings.request_timeout_seconds),
            )
        return self._client

    async def close(self) -> None:
        """クライアントを閉じる."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _make_cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
        """キャッシュキーを生成.

        Args:
            endpoint: APIエンドポイント
            params: リクエストパラメータ

        Returns:
            キャッシュキー
        """
        sorted_params = sorted(params.items())
        key_str = f"{endpoint}:{sorted_params}"
        return hashlib.md5(key_str.encode()).hexdigest()

    async def _request(
        self,
        endpoint: str,
        params: dict[str, Any],
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """APIリクエストを実行.

        Args:
            endpoint: APIエンドポイント（例: "getStatsList"）
            params: リクエストパラメータ
            use_cache: キャッシュを使用するか

        Returns:
            APIレスポンス（JSONパース済み）

        Raises:
            EStatApiError: API呼び出しに失敗した場合
        """
        cache_key = self._make_cache_key(endpoint, params)

        if use_cache:
            cached = get_cache(self._cache, cache_key)
            if cached is not None:
                logger.debug("Cache hit for %s", endpoint)
                return cached  # type: ignore[no-any-return]

        url = f"{self._settings.e_stat_base_url}/{endpoint}"
        full_params = {"appId": self._settings.e_stat_app_id, **params}

        client = await self._get_client()
        last_error: Exception | None = None

        for attempt in range(self._settings.max_retries):
            try:
                logger.debug("Requesting %s (attempt %d)", endpoint, attempt + 1)
                response = await client.get(url, params=full_params)
                response.raise_for_status()
                data: dict[str, Any] = response.json()

                if use_cache:
                    set_cache(self._cache, cache_key, data)

                return data

            except httpx.HTTPStatusError as e:
                logger.warning(
                    "HTTP error %d for %s (attempt %d)",
                    e.response.status_code,
                    endpoint,
                    attempt + 1,
                )
                last_error = e
                if e.response.status_code >= 400 and e.response.status_code < 500:
                    break
            except httpx.RequestError as e:
                logger.warning("Request error for %s (attempt %d): %s", endpoint, attempt + 1, e)
                last_error = e

        # エラータイプに応じて適切なエラーコードを選択
        error_code: EStatErrorCode
        if isinstance(last_error, httpx.HTTPStatusError):
            status_code = last_error.response.status_code
            if status_code >= 500:
                error_code = EStatErrorCode.SERVER_ERROR
            else:
                error_code = EStatErrorCode.INVALID_PARAM
        else:
            # RequestError（ネットワーク障害、タイムアウト、DNS解決エラー等）
            error_code = EStatErrorCode.NETWORK_ERROR

        msg = f"API request failed: {last_error}"
        raise EStatApiError(
            message=msg,
            code=error_code,
        )

    def _check_result(self, data: dict[str, Any], response_key: str) -> ApiResult:
        """APIレスポンスの結果を確認.

        Args:
            data: APIレスポンス
            response_key: レスポンスのルートキー（例: "GET_STATS_LIST"）

        Returns:
            ApiResult: 結果オブジェクト

        Raises:
            EStatApiError: エラーレスポンスの場合
        """
        response_data = data.get(response_key, {})
        result_data = response_data.get("RESULT", {})
        result = ApiResult.model_validate(result_data)

        if not result.is_success and not result.is_no_data:
            raise EStatApiError.from_api_result(result)

        return result

    def _validate_model(self, model_cls: type[T], data: Any) -> T:
        """モデルをバリデーションし、ValidationErrorをEStatApiErrorに変換.

        Args:
            model_cls: バリデーションするモデルクラス
            data: バリデーションするデータ

        Returns:
            バリデーション済みのモデルインスタンス

        Raises:
            EStatApiError: バリデーションに失敗した場合
        """
        try:
            return model_cls.model_validate(data)
        except ValidationError as e:
            msg = f"APIレスポンスのパースに失敗しました: {e}"
            raise EStatApiError(
                message=msg,
                code=EStatErrorCode.VALIDATION_ERROR,
            ) from e

    async def get_stats_list(
        self,
        keyword: str | None = None,
        stats_code: str | None = None,
        survey_years: str | None = None,
        limit: int = 100,
        start_position: int = 1,
    ) -> list[SearchStatsResult]:
        """統計表を検索.

        Args:
            keyword: 検索キーワード
            stats_code: 政府統計コード
            survey_years: 調査年の範囲（例: "2020-2023"）
            limit: 取得件数上限
            start_position: 取得開始位置

        Returns:
            検索結果のリスト

        Raises:
            EStatApiError: API呼び出しに失敗した場合
        """
        params: dict[str, Any] = {
            "limit": limit,
            "startPosition": start_position,
            "lang": "J",
        }

        if keyword:
            params["searchWord"] = keyword
        if stats_code:
            params["statsCode"] = stats_code
        if survey_years:
            if "-" in survey_years:
                start, end = survey_years.split("-", 1)
                params["surveyYears"] = f"{start}-{end}"
            else:
                params["surveyYears"] = survey_years

        data = await self._request("getStatsList", params)
        self._check_result(data, "GET_STATS_LIST")

        response = self._validate_model(StatsListResponse, data["GET_STATS_LIST"])
        tables = response.get_tables()

        return [self._table_to_result(table) for table in tables]

    def _table_to_result(self, table: StatsTable) -> SearchStatsResult:
        """統計表情報を検索結果に変換.

        Args:
            table: 統計表情報

        Returns:
            検索結果
        """
        return SearchStatsResult(
            table_id=table.id,
            table_name=table.title,
            stat_name=table.stat_name,
            survey_date=table.survey_date,
            gov_org=table.gov_org,
        )

    async def get_meta_info(self, stats_data_id: str) -> list[MetaInfoResult]:
        """メタ情報を取得.

        Args:
            stats_data_id: 統計表ID

        Returns:
            メタ情報のリスト

        Raises:
            EStatApiError: API呼び出しに失敗した場合
        """
        params = {
            "statsDataId": stats_data_id,
            "lang": "J",
        }

        data = await self._request("getMetaInfo", params)
        self._check_result(data, "GET_META_INFO")

        response = self._validate_model(MetaInfoResponse, data["GET_META_INFO"])
        class_objects = response.get_class_objects()

        return [self._class_info_to_result(info) for info in class_objects]

    def _class_info_to_result(self, info: ClassInfo) -> MetaInfoResult:
        """分類情報をメタ情報結果に変換.

        Args:
            info: 分類情報

        Returns:
            メタ情報結果
        """
        items = [
            ClassItemInfo(
                code=item.code,
                name=item.name,
                level=item.level,
                unit=item.unit,
            )
            for item in info.items
        ]
        return MetaInfoResult(
            class_id=info.id,
            class_name=info.name,
            items=items,
        )

    async def get_stats_data(
        self,
        stats_data_id: str,
        cd_tab: str | None = None,
        cd_cat01: str | None = None,
        cd_cat02: str | None = None,
        cd_area: str | None = None,
        cd_time: str | None = None,
        limit: int = 10000,
        start_position: int = 1,
    ) -> StatsDataResult:
        """統計データを取得.

        Args:
            stats_data_id: 統計表ID
            cd_tab: 表章事項コード
            cd_cat01: 分類事項コード01
            cd_cat02: 分類事項コード02
            cd_area: 地域コード
            cd_time: 時間軸コード
            limit: 取得件数上限
            start_position: 取得開始位置

        Returns:
            統計データ結果

        Raises:
            EStatApiError: API呼び出しに失敗した場合
        """
        params: dict[str, Any] = {
            "statsDataId": stats_data_id,
            "limit": limit,
            "startPosition": start_position,
            "lang": "J",
        }

        if cd_tab:
            params["cdTab"] = cd_tab
        if cd_cat01:
            params["cdCat01"] = cd_cat01
        if cd_cat02:
            params["cdCat02"] = cd_cat02
        if cd_area:
            params["cdArea"] = cd_area
        if cd_time:
            params["cdTime"] = cd_time

        data = await self._request("getStatsData", params)
        self._check_result(data, "GET_STATS_DATA")

        response = self._validate_model(StatsDataResponse, data["GET_STATS_DATA"])

        class_map = self._build_class_map(response.get_class_info())
        data_values = response.get_data_values()

        items = [self._value_to_item(v, class_map) for v in data_values]

        total_count = self._get_total_count(response)
        returned_count = len(items)

        # ページネーション計算
        # has_next: 現在位置 + 取得件数 - 1 < 総件数 の場合、次ページあり
        has_next = (start_position + returned_count - 1) < total_count
        next_start_position = start_position + returned_count if has_next else None

        return StatsDataResult(
            total_count=total_count,
            returned_count=returned_count,
            data=items,
            has_next=has_next,
            next_start_position=next_start_position,
        )

    def _build_class_map(self, class_info_list: list[ClassInfo]) -> dict[str, dict[str, str]]:
        """分類コードから名称へのマッピングを構築.

        Args:
            class_info_list: 分類情報のリスト

        Returns:
            分類ID -> {コード -> 名称} のマッピング
        """
        result: dict[str, dict[str, str]] = {}
        for info in class_info_list:
            code_map: dict[str, str] = {}
            for item in info.items:
                code_map[item.code] = item.name
            result[info.id] = code_map
        return result

    def _value_to_item(self, value: Any, class_map: dict[str, dict[str, str]]) -> StatsDataItem:
        """データ値を統計データ項目に変換.

        Args:
            value: データ値
            class_map: 分類コードから名称へのマッピング

        Returns:
            統計データ項目
        """
        from e_stat_mcp.models.api import DataValue

        if not isinstance(value, DataValue):
            value = self._validate_model(DataValue, value)

        tab_map = class_map.get("tab", {})
        tab_name = tab_map.get(value.tab, value.tab)

        category_names: dict[str, str] = {}
        for cat_id in ["cat01", "cat02", "cat03"]:
            cat_code = getattr(value, cat_id, None)
            if cat_code:
                cat_map = class_map.get(cat_id, {})
                category_names[cat_id] = cat_map.get(cat_code, cat_code)

        area_name: str | None = None
        if value.area:
            area_map = class_map.get("area", {})
            area_name = area_map.get(value.area, value.area)

        time_name: str | None = None
        if value.time:
            time_map = class_map.get("time", {})
            time_name = time_map.get(value.time, value.time)

        return StatsDataItem(
            tab_name=tab_name,
            category_names=category_names,
            area_name=area_name,
            time_name=time_name,
            value=value.numeric_value,
            value_raw=value.value,
            unit=value.unit,
        )

    def _get_total_count(self, response: StatsDataResponse) -> int:
        """レスポンスから総データ件数を取得.

        Args:
            response: 統計データレスポンス

        Returns:
            総データ件数
        """
        if not response.statistical_data:
            return 0
        data_inf = response.statistical_data.get("DATA_INF", {})
        if isinstance(data_inf, dict):
            return int(data_inf.get("@totalNumber", len(response.get_data_values())))
        return len(response.get_data_values())

    async def get_datasets(self, stats_data_id: str | None = None) -> list[DatasetResult]:
        """データセット一覧を取得.

        Args:
            stats_data_id: 統計表ID（フィルタ用）

        Returns:
            データセット結果のリスト

        Raises:
            EStatApiError: API呼び出しに失敗した場合
        """
        params: dict[str, Any] = {
            "lang": "J",
        }

        if stats_data_id:
            params["statsDataId"] = stats_data_id

        data = await self._request("refDataset", params)
        self._check_result(data, "REF_DATASET")

        response = self._validate_model(DatasetListResponse, data["REF_DATASET"])
        datasets = response.get_datasets()

        return [
            DatasetResult(
                dataset_id=ds.id,
                dataset_name=ds.dataset_name,
                stats_data_id=ds.stats_data_id,
                is_public=ds.open == "1",
                description=ds.description,
            )
            for ds in datasets
        ]

    async def get_dataset_data(
        self,
        dataset_id: str,
        limit: int = 10000,
        start_position: int = 1,
    ) -> StatsDataResult:
        """データセットのデータを取得.

        Args:
            dataset_id: データセットID
            limit: 取得件数上限
            start_position: 取得開始位置

        Returns:
            統計データ結果

        Raises:
            EStatApiError: API呼び出しに失敗した場合
        """
        params: dict[str, Any] = {
            "dataSetId": dataset_id,
            "limit": limit,
            "startPosition": start_position,
            "lang": "J",
        }

        data = await self._request("refDataset", params, use_cache=False)
        self._check_result(data, "REF_DATASET")

        response = self._validate_model(StatsDataResponse, data["REF_DATASET"])

        class_map = self._build_class_map(response.get_class_info())
        data_values = response.get_data_values()

        items = [self._value_to_item(v, class_map) for v in data_values]

        total_count = self._get_total_count(response)
        returned_count = len(items)

        # ページネーション計算
        # has_next: 現在位置 + 取得件数 - 1 < 総件数 の場合、次ページあり
        has_next = (start_position + returned_count - 1) < total_count
        next_start_position = start_position + returned_count if has_next else None

        return StatsDataResult(
            total_count=total_count,
            returned_count=returned_count,
            data=items,
            has_next=has_next,
            next_start_position=next_start_position,
        )
