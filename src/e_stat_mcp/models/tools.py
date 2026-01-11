"""MCPツール入出力モデル定義."""

from pydantic import BaseModel, Field


class SearchStatsRequest(BaseModel):
    """統計表検索リクエスト."""

    keyword: str | None = Field(None, description="検索キーワード")
    stats_code: str | None = Field(None, description="政府統計コード")
    survey_years: str | None = Field(None, description="調査年（開始-終了）")
    limit: int = Field(default=100, ge=1, le=100000, description="取得件数上限")
    start_position: int = Field(default=1, ge=1, description="取得開始位置")


class SearchStatsResult(BaseModel):
    """統計表検索結果."""

    table_id: str = Field(..., description="統計表ID")
    table_name: str = Field(..., description="統計表名称")
    stat_name: str = Field(..., description="政府統計名称")
    survey_date: str | None = Field(None, description="調査年月")
    gov_org: str = Field(..., description="作成機関")


class GetStatsDataRequest(BaseModel):
    """統計データ取得リクエスト."""

    stats_data_id: str = Field(..., description="統計表ID")
    cd_tab: str | None = Field(None, description="表章事項コード")
    cd_cat01: str | None = Field(None, description="分類事項コード01")
    cd_cat02: str | None = Field(None, description="分類事項コード02")
    cd_area: str | None = Field(None, description="地域コード")
    cd_time: str | None = Field(None, description="時間軸コード")
    limit: int = Field(default=10000, ge=1, le=100000, description="取得件数上限")
    start_position: int = Field(default=1, ge=1, description="取得開始位置")


class StatsDataItem(BaseModel):
    """統計データ項目."""

    tab_name: str = Field(..., description="表章事項名")
    category_names: dict[str, str] = Field(default_factory=dict, description="分類項目名")
    area_name: str | None = Field(None, description="地域名")
    time_name: str | None = Field(None, description="時点名")
    value: float | None = Field(None, description="統計値（数値）")
    value_raw: str = Field(..., description="統計値（生値）")
    unit: str | None = Field(None, description="単位")


class GetMetaInfoRequest(BaseModel):
    """メタ情報取得リクエスト."""

    stats_data_id: str = Field(..., description="統計表ID")


class ClassItemInfo(BaseModel):
    """分類項目情報."""

    code: str = Field(..., description="コード")
    name: str = Field(..., description="名称")
    level: str | None = Field(None, description="階層レベル")
    unit: str | None = Field(None, description="単位")


class MetaInfoResult(BaseModel):
    """メタ情報結果."""

    class_id: str = Field(..., description="分類ID")
    class_name: str = Field(..., description="分類名")
    items: list[ClassItemInfo] = Field(..., description="分類項目リスト")


class ListDatasetsRequest(BaseModel):
    """データセット一覧取得リクエスト."""

    stats_data_id: str | None = Field(None, description="統計表ID（フィルタ用）")


class DatasetResult(BaseModel):
    """データセット結果."""

    dataset_id: str = Field(..., description="データセットID")
    dataset_name: str = Field(..., description="データセット名")
    stats_data_id: str = Field(..., description="対象統計表ID")
    is_public: bool = Field(..., description="公開状態")
    description: str | None = Field(None, description="説明")


class GetDatasetDataRequest(BaseModel):
    """データセットデータ取得リクエスト."""

    dataset_id: str = Field(..., description="データセットID")
    limit: int = Field(default=10000, ge=1, le=100000, description="取得件数上限")
    start_position: int = Field(default=1, ge=1, description="取得開始位置")


class StatsDataResult(BaseModel):
    """統計データ取得結果."""

    total_count: int = Field(..., description="総データ件数")
    returned_count: int = Field(..., description="今回返却した件数")
    data: list[StatsDataItem] = Field(..., description="統計データリスト")
