# データモデル

e-Stat MCP サーバーで使用する Pydantic モデルを解説します。

## モデル分類

モデルは3つのカテゴリに分類されます：

| カテゴリ | ファイル | 役割 |
|---------|---------|------|
| APIレスポンス | `models/api.py` | e-Stat API からのレスポンスをパース |
| ツール入出力 | `models/tools.py` | MCP ツールの入出力を定義 |
| エラー | `models/errors.py` | エラーコード・エラー情報を管理 |

## クラス図

```{mermaid}
classDiagram
    class ApiResult {
        +int status
        +str error_msg
        +str date
        +is_success() bool
        +is_no_data() bool
    }

    class StatsTable {
        +str id
        +str stat_name
        +str gov_org
        +str title
        +str survey_date
    }

    class ClassInfo {
        +str id
        +str name
        +list~ClassItem~ items
    }

    class ClassItem {
        +str code
        +str name
        +str level
        +str unit
    }

    class DataValue {
        +str tab
        +str cat01
        +str area
        +str time
        +str value
        +numeric_value() float
    }

    class SearchStatsResult {
        +str table_id
        +str table_name
        +str stat_name
        +str survey_date
        +str gov_org
    }

    class StatsDataItem {
        +str tab_name
        +dict category_names
        +str area_name
        +str time_name
        +float value
        +str value_raw
        +str unit
    }

    ClassInfo "1" --> "*" ClassItem
    StatsTable ..> SearchStatsResult : transforms to
    DataValue ..> StatsDataItem : transforms to
```

## API レスポンスモデル

### ApiResult

API レスポンスの結果部分を表します：

```python
class ApiResult(BaseModel):
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

### StatsTable

統計表情報を表します：

```python
class StatsTable(BaseModel):
    id: str = Field(..., alias="@id")
    stat_name: str = Field(..., description="政府統計名称")
    gov_org: str = Field(..., description="作成機関名")
    title: str = Field(..., description="統計表名称")
    survey_date: str | None = Field(None, description="調査年月")
    # ...
```

### ClassItem（分類項目）

e-Stat API は分類項目を2つの形式で返します：

```json
// 形式1: @name を使用
{"@code": "001", "@name": "人口", "@level": "1"}

// 形式2: $ を使用
{"@code": "001", "$": "人口", "@level": "1"}
```

両方の形式に対応するため、`model_validator` で正規化：

```python
class ClassItem(BaseModel):
    code: str = Field(..., alias="@code")
    name: str = Field(..., description="分類項目名称")
    level: str | None = Field(None, alias="@level")
    unit: str | None = Field(None, alias="@unit")
    parent_code: str | None = Field(None, alias="@parentCode")

    @model_validator(mode="before")
    @classmethod
    def normalize_name_field(cls, data: Any) -> Any:
        """@nameまたは$フィールドをnameに正規化.

        Raises:
            ValueError: @nameも$もnameも存在しない場合
        """
        if not isinstance(data, dict):
            return data

        if "name" not in data:
            if "@name" in data:
                data["name"] = data["@name"]
            elif "$" in data:
                data["name"] = data["$"]
            else:
                msg = "ClassItem requires '@name', '$', or 'name' field"
                raise ValueError(msg)
        return data
```

### DataValue

統計データ値を表します：

```python
class DataValue(BaseModel):
    tab: str = Field(..., alias="@tab")
    cat01: str | None = Field(None, alias="@cat01")
    area: str | None = Field(None, alias="@area")
    time: str | None = Field(None, alias="@time")
    value: str = Field(..., alias="$")
    unit: str | None = Field(None, alias="@unit")

    @property
    def numeric_value(self) -> float | None:
        """欠損値を処理して数値に変換"""
        if self.value in ["-", "...", "x", "*", "…"]:
            return None
        try:
            return float(self.value.replace(",", ""))
        except ValueError:
            return None
```

## ツール入出力モデル

### リクエストモデル

```python
class SearchStatsRequest(BaseModel):
    keyword: str | None = Field(None, description="検索キーワード")
    stats_code: str | None = Field(None, description="政府統計コード")
    survey_years: str | None = Field(None, description="調査年の範囲")
    limit: int = Field(default=100, ge=1, le=100000)
    start_position: int = Field(default=1, ge=1)
```

### 結果モデル

```python
class SearchStatsResult(BaseModel):
    table_id: str = Field(..., description="統計表ID")
    table_name: str = Field(..., description="統計表名称")
    stat_name: str = Field(..., description="政府統計名称")
    survey_date: str | None = Field(None, description="調査年月")
    gov_org: str = Field(..., description="作成機関")
```

## エラーモデル

### EStatErrorCode

e-Stat API のエラーコード：

```python
class EStatErrorCode(IntEnum):
    SUCCESS = 0           # 成功
    NO_DATA = 1           # 該当データなし
    AUTH_ERROR = 100      # 認証エラー
    MISSING_PARAM = 101   # 必須パラメータ不足
    INVALID_PARAM = 102   # パラメータ値が不正
    DATA_NOT_FOUND = 300  # データが存在しない
    NETWORK_ERROR = 900   # ネットワークエラー（クライアント側）
    SERVER_ERROR = 901    # サーバーエラー（クライアント側）
    VALIDATION_ERROR = 902 # バリデーションエラー（クライアント側）
```

### EStatApiError

API エラーを表すカスタム例外：

```python
class EStatApiError(Exception):
    def __init__(
        self,
        code: EStatErrorCode,
        message: str,
        parameter: str | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.parameter = parameter
        super().__init__(message)

    def get_user_message(self) -> str:
        """ユーザー向けメッセージを生成"""
        # ...
```

## バリデーションパターン

### 単一値/リストの正規化

e-Stat API は要素が1つの場合、配列ではなくオブジェクトを返すことがあります：

```json
// 1件の場合
{"TABLE_INF": {"@id": "001", ...}}

// 複数件の場合
{"TABLE_INF": [{"@id": "001", ...}, {"@id": "002", ...}]}
```

モデルで自動正規化：

```python
@field_validator("table_inf", mode="before")
@classmethod
def normalize_table_inf(cls, v: Any) -> list[dict[str, Any]]:
    if isinstance(v, dict):
        return [v]
    return v
```

### エイリアスの使用

e-Stat API のフィールド名は JSON キーと Python 変数名が異なるため、エイリアスを使用：

```python
class StatsTable(BaseModel):
    id: str = Field(..., alias="@id")  # @id → id
    stat_name: str = Field(..., alias="STAT_NAME")  # STAT_NAME → stat_name
```

## データ変換フロー

```{mermaid}
flowchart LR
    A[e-Stat API<br/>JSON Response] --> B[API Model<br/>StatsTable]
    B --> C[Tool Model<br/>SearchStatsResult]
    C --> D[MCP Response<br/>JSON]
```

1. **APIレスポンス** → **APIモデル**: `model_validate()` でパース・バリデーション
2. **APIモデル** → **ツールモデル**: サーバー層で変換
3. **ツールモデル** → **MCPレスポンス**: Pydantic の `model_dump()` でシリアライズ

## 次のステップ

- [エラー処理](error-handling.md) - エラーハンドリングパターン
- [APIリファレンス](../api/models.md) - モデルの詳細ドキュメント
