# e-Stat API 仕様

e-Stat API の概要と本プロジェクトで使用するエンドポイントを解説します。

## e-Stat とは

[e-Stat](https://www.e-stat.go.jp/) は、日本の政府統計ポータルサイトです。
各府省が公表する統計データを一元的に提供しています。

## API 概要

| 項目 | 内容 |
|------|------|
| ベースURL | `https://api.e-stat.go.jp/rest/3.0/app/json` |
| 認証 | アプリケーションID（クエリパラメータ） |
| フォーマット | JSON |
| 利用制限 | なし（過度なアクセスは制限される可能性） |

## 使用するエンドポイント

### getStatsList（統計表一覧取得）

統計表を検索します。

| パラメータ | 説明 |
|-----------|------|
| `appId` | アプリケーションID（必須） |
| `searchWord` | 検索キーワード |
| `statsCode` | 政府統計コード |
| `surveyYears` | 調査年（例: "2020", "2020-2023"） |
| `limit` | 取得件数上限 |
| `startPosition` | 取得開始位置 |

### getStatsData（統計データ取得）

統計表からデータを取得します。

| パラメータ | 説明 |
|-----------|------|
| `appId` | アプリケーションID（必須） |
| `statsDataId` | 統計表ID（必須） |
| `cdTab` | 表章事項コード |
| `cdCat01` | 分類事項コード01 |
| `cdCat02` | 分類事項コード02 |
| `cdArea` | 地域コード |
| `cdTime` | 時間軸コード |
| `limit` | 取得件数上限 |
| `startPosition` | 取得開始位置 |

### getMetaInfo（メタ情報取得）

統計表の構造（分類項目など）を取得します。

| パラメータ | 説明 |
|-----------|------|
| `appId` | アプリケーションID（必須） |
| `statsDataId` | 統計表ID（必須） |

### refDataset（データセット参照）

公開データセットの一覧・データを取得します。

| パラメータ | 説明 |
|-----------|------|
| `appId` | アプリケーションID（必須） |
| `statsDataId` | 統計表ID（フィルタ用、任意） |
| `datasetId` | データセットID（データ取得時） |

## レスポンス構造

### 共通構造

```json
{
  "GET_STATS_LIST": {
    "RESULT": {
      "STATUS": 0,
      "ERROR_MSG": "正常に終了しました。",
      "DATE": "2024-01-01T00:00:00.000+09:00"
    },
    "PARAMETER": {...},
    "DATALIST_INF": {...}
  }
}
```

### ステータスコード

| コード | 意味 |
|--------|------|
| 0 | 成功 |
| 1 | 該当データなし |
| 100 | 認証エラー |
| 101 | 必須パラメータ不足 |
| 102 | パラメータ値が不正 |
| 300 | データが存在しない |

## API 制約

- 1回のリクエストで取得できる最大件数: 100,000件
- レート制限: 明確な制限はないが、過度なアクセスは控える

## 公式ドキュメント

- [e-Stat API 仕様書（Version 3.0）](https://www.e-stat.go.jp/api/api-info/e-stat-manual3-0)
- [e-Stat API 利用ガイド](https://www.e-stat.go.jp/api/)

## アプリケーションIDの取得

1. [e-Stat](https://www.e-stat.go.jp/) でユーザー登録
2. マイページにログイン
3. 「API」→「アプリケーションIDの取得」
4. 必要事項を入力してIDを取得

## 関連リンク

- [e-Stat トップページ](https://www.e-stat.go.jp/)
- [政府統計コード一覧](https://www.e-stat.go.jp/stat-search/database?page=1&statdisp_id=0003000001)
