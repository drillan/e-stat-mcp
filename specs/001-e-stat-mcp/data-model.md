# Data Model: e-Stat API連携MCPサーバー

**Branch**: `001-e-stat-mcp` | **Date**: 2026-01-07

## 概要

すべてのデータ構造はPydantic BaseModelで定義し、ランタイムバリデーションを必須とする。

## 設定モデル

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """MCPサーバー設定"""
    e_stat_app_id: str  # e-StatアプリケーションID（必須）
    e_stat_base_url: str = "https://api.e-stat.go.jp/rest/3.0/app/json"
    cache_ttl_seconds: int = 3600  # キャッシュTTL（秒）
    request_timeout_seconds: int = 30  # リクエストタイムアウト
    max_retries: int = 3  # 最大リトライ回数

    model_config = {"env_file": ".env", "env_prefix": "E_STAT_"}
```

## e-Stat APIレスポンスモデル

### 共通レスポンス構造

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ApiResult(BaseModel):
    """APIレスポンスの結果部分"""
    status: int = Field(..., alias="STATUS")
    error_msg: str = Field(..., alias="ERROR_MSG")
    date: str = Field(..., alias="DATE")

    @property
    def is_success(self) -> bool:
        return self.status == 0

    @property
    def is_no_data(self) -> bool:
        return self.status == 1
```

### 統計表情報（getStatsList）

```python
class StatsTable(BaseModel):
    """統計表情報"""
    id: str = Field(..., alias="@id", description="統計表ID")
    stat_name: str = Field(..., alias="STAT_NAME", description="政府統計名称")
    gov_org: str = Field(..., alias="GOV_ORG", description="作成機関名")
    statistics_name: Optional[str] = Field(None, alias="STATISTICS_NAME")
    title: str = Field(..., alias="TITLE", description="統計表名称")
    cycle: Optional[str] = Field(None, alias="CYCLE", description="調査周期")
    survey_date: Optional[str] = Field(None, alias="SURVEY_DATE", description="調査年月")
    open_date: Optional[str] = Field(None, alias="OPEN_DATE", description="公開日")
    small_area: Optional[int] = Field(None, alias="SMALL_AREA", description="小地域フラグ")
    main_category: Optional[str] = Field(None, alias="MAIN_CATEGORY", description="大分類")
    sub_category: Optional[str] = Field(None, alias="SUB_CATEGORY", description="小分類")
    overall_total_number: Optional[int] = Field(None, alias="OVERALL_TOTAL_NUMBER")
    updated_date: Optional[str] = Field(None, alias="UPDATED_DATE")
    description: Optional[str] = Field(None, alias="DESCRIPTION")

class StatsListResponse(BaseModel):
    """getStatsListレスポンス"""
    result: ApiResult = Field(..., alias="RESULT")
    parameter: dict = Field(..., alias="PARAMETER")
    datalist_inf: Optional[dict] = Field(None, alias="DATALIST_INF")

    def get_tables(self) -> list[StatsTable]:
        """統計表リストを取得"""
        if not self.datalist_inf:
            return []
        table_inf = self.datalist_inf.get("TABLE_INF", [])
        if isinstance(table_inf, dict):
            table_inf = [table_inf]
        return [StatsTable.model_validate(t) for t in table_inf]
```

### メタ情報（getMetaInfo）

```python
class ClassItem(BaseModel):
    """分類項目

    e-Stat APIは分類項目を2つの形式で返す:
    1. {'@code': '...', '@name': '...', '@level': '...'} - @name形式
    2. {'@code': '...', '$': '...', '@level': '...'} - $形式

    両方の形式に対応するため、model_validatorで事前に正規化する。
    """
    code: str = Field(..., alias="@code")
    name: str = Field(..., description="分類項目名称（@nameまたは$から取得）")
    level: Optional[str] = Field(None, alias="@level")
    unit: Optional[str] = Field(None, alias="@unit")
    parent_code: Optional[str] = Field(None, alias="@parentCode")

class ClassInfo(BaseModel):
    """分類情報"""
    id: str = Field(..., alias="@id")
    name: str = Field(..., alias="@name")
    items: list[ClassItem] = Field(default_factory=list, alias="CLASS")

class MetaInfoResponse(BaseModel):
    """getMetaInfoレスポンス"""
    result: ApiResult = Field(..., alias="RESULT")
    parameter: dict = Field(..., alias="PARAMETER")
    class_inf: Optional[dict] = Field(None, alias="CLASS_INF")

    def get_class_objects(self) -> list[ClassInfo]:
        """分類情報リストを取得"""
        if not self.class_inf:
            return []
        class_obj = self.class_inf.get("CLASS_OBJ", [])
        if isinstance(class_obj, dict):
            class_obj = [class_obj]
        return [ClassInfo.model_validate(c) for c in class_obj]
```

### 統計データ（getStatsData）

```python
class DataValue(BaseModel):
    """統計データ値"""
    tab: str = Field(..., alias="@tab", description="表章事項コード")
    cat01: Optional[str] = Field(None, alias="@cat01", description="分類事項コード01")
    cat02: Optional[str] = Field(None, alias="@cat02", description="分類事項コード02")
    cat03: Optional[str] = Field(None, alias="@cat03", description="分類事項コード03")
    area: Optional[str] = Field(None, alias="@area", description="地域コード")
    time: Optional[str] = Field(None, alias="@time", description="時間軸コード")
    unit: Optional[str] = Field(None, alias="@unit", description="単位")
    value: str = Field(..., alias="$", description="統計値")

    @property
    def numeric_value(self) -> Optional[float]:
        """数値に変換（変換不可の場合はNone）"""
        try:
            # "-"や"..."等の欠損値を処理
            if self.value in ["-", "...", "x", "*", "…"]:
                return None
            return float(self.value.replace(",", ""))
        except (ValueError, AttributeError):
            return None

class StatsDataResponse(BaseModel):
    """getStatsDataレスポンス"""
    result: ApiResult = Field(..., alias="RESULT")
    parameter: dict = Field(..., alias="PARAMETER")
    statistical_data: Optional[dict] = Field(None, alias="STATISTICAL_DATA")

    def get_data_values(self) -> list[DataValue]:
        """データ値リストを取得"""
        if not self.statistical_data:
            return []
        data_inf = self.statistical_data.get("DATA_INF", {})
        value_list = data_inf.get("VALUE", [])
        if isinstance(value_list, dict):
            value_list = [value_list]
        return [DataValue.model_validate(v) for v in value_list]

    def get_class_info(self) -> list[ClassInfo]:
        """関連する分類情報を取得"""
        if not self.statistical_data:
            return []
        class_inf = self.statistical_data.get("CLASS_INF", {})
        class_obj = class_inf.get("CLASS_OBJ", [])
        if isinstance(class_obj, dict):
            class_obj = [class_obj]
        return [ClassInfo.model_validate(c) for c in class_obj]
```

### データセット（refDataset）

```python
class DatasetInfo(BaseModel):
    """データセット情報"""
    id: str = Field(..., alias="@id", description="データセットID")
    stats_data_id: str = Field(..., alias="STATS_DATA_ID", description="統計表ID")
    dataset_name: str = Field(..., alias="DATASET_NAME", description="データセット名")
    open: Optional[str] = Field(None, alias="OPEN", description="公開状態")
    created: Optional[str] = Field(None, alias="CREATED", description="作成日時")
    updated: Optional[str] = Field(None, alias="UPDATED", description="更新日時")
    description: Optional[str] = Field(None, alias="DESCRIPTION")

class DatasetListResponse(BaseModel):
    """refDatasetレスポンス（一覧）"""
    result: ApiResult = Field(..., alias="RESULT")
    parameter: dict = Field(..., alias="PARAMETER")
    datalist_inf: Optional[dict] = Field(None, alias="DATALIST_INF")

    def get_datasets(self) -> list[DatasetInfo]:
        """データセットリストを取得"""
        if not self.datalist_inf:
            return []
        dataset_inf = self.datalist_inf.get("DATASET_INF", [])
        if isinstance(dataset_inf, dict):
            dataset_inf = [dataset_inf]
        return [DatasetInfo.model_validate(d) for d in dataset_inf]
```

## MCPツール入出力モデル

### 統計表検索

```python
class SearchStatsRequest(BaseModel):
    """統計表検索リクエスト"""
    keyword: Optional[str] = Field(None, description="検索キーワード")
    stats_code: Optional[str] = Field(None, description="政府統計コード")
    survey_years: Optional[str] = Field(None, description="調査年（開始-終了）")
    limit: int = Field(default=100, ge=1, le=100000, description="取得件数上限")
    start_position: int = Field(default=1, ge=1, description="取得開始位置")

class SearchStatsResult(BaseModel):
    """統計表検索結果"""
    table_id: str = Field(..., description="統計表ID")
    table_name: str = Field(..., description="統計表名称")
    stat_name: str = Field(..., description="政府統計名称")
    survey_date: Optional[str] = Field(None, description="調査年月")
    gov_org: str = Field(..., description="作成機関")
```

### 統計データ取得

```python
class GetStatsDataRequest(BaseModel):
    """統計データ取得リクエスト"""
    stats_data_id: str = Field(..., description="統計表ID")
    cd_tab: Optional[str] = Field(None, description="表章事項コード")
    cd_cat01: Optional[str] = Field(None, description="分類事項コード01")
    cd_cat02: Optional[str] = Field(None, description="分類事項コード02")
    cd_area: Optional[str] = Field(None, description="地域コード")
    cd_time: Optional[str] = Field(None, description="時間軸コード")
    limit: int = Field(default=10000, ge=1, le=100000, description="取得件数上限")
    start_position: int = Field(default=1, ge=1, description="取得開始位置")

class StatsDataItem(BaseModel):
    """統計データ項目"""
    tab_name: str = Field(..., description="表章事項名")
    category_names: dict[str, str] = Field(default_factory=dict, description="分類項目名")
    area_name: Optional[str] = Field(None, description="地域名")
    time_name: Optional[str] = Field(None, description="時点名")
    value: Optional[float] = Field(None, description="統計値（数値）")
    value_raw: str = Field(..., description="統計値（生値）")
    unit: Optional[str] = Field(None, description="単位")
```

### メタ情報取得

```python
class GetMetaInfoRequest(BaseModel):
    """メタ情報取得リクエスト"""
    stats_data_id: str = Field(..., description="統計表ID")

class ClassItemInfo(BaseModel):
    """分類項目情報"""
    code: str = Field(..., description="コード")
    name: str = Field(..., description="名称")
    level: Optional[str] = Field(None, description="階層レベル")
    unit: Optional[str] = Field(None, description="単位")

class MetaInfoResult(BaseModel):
    """メタ情報結果"""
    class_id: str = Field(..., description="分類ID")
    class_name: str = Field(..., description="分類名")
    items: list[ClassItemInfo] = Field(..., description="分類項目リスト")
```

### データセット参照

```python
class ListDatasetsRequest(BaseModel):
    """データセット一覧取得リクエスト"""
    stats_data_id: Optional[str] = Field(None, description="統計表ID（フィルタ用）")

class DatasetResult(BaseModel):
    """データセット結果"""
    dataset_id: str = Field(..., description="データセットID")
    dataset_name: str = Field(..., description="データセット名")
    stats_data_id: str = Field(..., description="対象統計表ID")
    is_public: bool = Field(..., description="公開状態")
    description: Optional[str] = Field(None, description="説明")
```

## エラーモデル

```python
from enum import IntEnum

class EStatErrorCode(IntEnum):
    """e-Statエラーコード"""
    SUCCESS = 0
    NO_DATA = 1
    AUTH_ERROR = 100
    MISSING_PARAM = 101
    INVALID_PARAM = 102
    DATA_NOT_FOUND = 300

class EStatError(BaseModel):
    """e-Statエラー情報"""
    code: EStatErrorCode
    message: str
    parameter: Optional[str] = None

    @classmethod
    def from_api_result(cls, result: ApiResult) -> Optional["EStatError"]:
        """APIレスポンスからエラーを生成"""
        if result.is_success:
            return None
        return cls(
            code=EStatErrorCode(result.status),
            message=result.error_msg,
        )
```

## バリデーションルール

### 必須バリデーション

1. **APIレスポンス**: すべてのe-Stat APIレスポンスは対応するPydanticモデルでパース
2. **ツール入力**: すべてのMCPツール引数はリクエストモデルでバリデーション
3. **ツール出力**: すべてのMCPツール戻り値は結果モデルでシリアライズ

### バリデーション失敗時の処理

```python
from pydantic import ValidationError

async def validate_response(response_data: dict, model_class: type) -> BaseModel:
    """APIレスポンスをバリデーション"""
    try:
        return model_class.model_validate(response_data)
    except ValidationError as e:
        raise EStatApiError(
            message=f"Invalid API response: {e}",
            code=EStatErrorCode.INVALID_PARAM,
        )
```

## 状態遷移

### APIリクエストフロー

```
[リクエストモデル] → [バリデーション] → [HTTPリクエスト]
                                              ↓
[結果モデル] ← [バリデーション] ← [APIレスポンス]
```

### エラーハンドリングフロー

```
[APIレスポンス]
      ↓
[ステータスコード確認]
      ↓
   0: [正常処理] → [データモデルへパース]
   1: [該当なし] → [空リスト返却]
 100: [認証エラー] → [設定確認を促すメッセージ]
 101: [パラメータエラー] → [必須項目を説明]
 その他: [汎用エラー] → [エラーメッセージ転送]
```
