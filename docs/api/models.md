# models パッケージ

Pydantic データモデルを定義するパッケージです。

## 概要

`e_stat_mcp.models` パッケージは3つのモジュールで構成されます：

| モジュール | 説明 |
|-----------|------|
| `api` | e-Stat API レスポンスモデル |
| `tools` | MCP ツール入出力モデル |
| `errors` | エラーコード・エラーモデル |

## api モジュール

e-Stat API からのレスポンスをパースするモデルです。

### 主なモデル

- `ApiResult`: API レスポンスの結果部分
- `StatsTable`: 統計表情報
- `ClassInfo`, `ClassItem`: 分類情報
- `DataValue`: 統計データ値
- `StatsListResponse`, `MetaInfoResponse`, `StatsDataResponse`: レスポンス全体

```{eval-rst}
.. automodule:: e_stat_mcp.models.api
   :members:
   :undoc-members:
   :show-inheritance:
```

## tools モジュール

MCP ツールの入出力を定義するモデルです。

### リクエストモデル

- `SearchStatsRequest`: 統計表検索リクエスト
- `GetStatsDataRequest`: 統計データ取得リクエスト
- `GetMetaInfoRequest`: メタ情報取得リクエスト
- `ListDatasetsRequest`: データセット一覧リクエスト
- `GetDatasetDataRequest`: データセットデータ取得リクエスト

### 結果モデル

- `SearchStatsResult`: 統計表検索結果
- `StatsDataResult`, `StatsDataItem`: 統計データ取得結果
- `MetaInfoResult`, `ClassItemInfo`: メタ情報取得結果
- `DatasetResult`: データセット情報

```{eval-rst}
.. automodule:: e_stat_mcp.models.tools
   :members:
   :undoc-members:
   :show-inheritance:
```

## errors モジュール

エラーコードとエラーモデルを定義します。

### 主な要素

- `EStatErrorCode`: e-Stat API エラーコード（IntEnum）
- `ApiResult`: API レスポンスの結果部分

```{eval-rst}
.. automodule:: e_stat_mcp.models.errors
   :members:
   :undoc-members:
   :show-inheritance:
```
