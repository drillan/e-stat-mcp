# get_dataset_data

データセットからデータを取得するツールです。

## 概要

データセットIDを指定して、統計データを取得します。データセットは事前にフィルタ条件が設定されているため、`get_stats_data` よりシンプルに使えます。

## パラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|------|------|----------|------|
| `dataset_id` | str | **必須** | - | データセットID（list_datasets で取得） |
| `limit` | int | 任意 | 10,000 | 取得件数上限（最大: 100,000） |
| `start_position` | int | 任意 | 1 | 取得開始位置 |

## 戻り値

```json
{
  "total_count": 12345,
  "returned_count": 100,
  "data": [...]
}
```

戻り値の構造は `get_stats_data` と同じです。

### data の各要素

| フィールド | 型 | 説明 |
|-----------|------|------|
| `tab_name` | str | 表章事項名 |
| `category_names` | dict | 分類項目名 |
| `area_name` | str | 地域名 |
| `time_name` | str | 時点名 |
| `value` | float | 統計値（数値、欠損の場合は null） |
| `value_raw` | str | 統計値（生の文字列） |
| `unit` | str | 単位 |

## 使用例

### データセットからデータ取得

```
データセットID「DS001」からデータを取得してください
```

→ `get_dataset_data(dataset_id="DS001")`

レスポンス例：
```
total_count: 47
returned_count: 47

1. 表章事項: 人口（総数）
   地域: 北海道
   時点: 2020年
   値: 5,224,614 人

2. 表章事項: 人口（総数）
   地域: 青森県
   時点: 2020年
   値: 1,237,984 人
...
```

### ワークフロー例

```
公開データセットから「人口」に関するデータを取得してください：
1. データセット一覧を取得
2. 人口関連のデータセットを選択
3. データを取得
```

## get_stats_data との比較

### get_dataset_data を使う場合

```
データセットID「DS001」からデータを取得
```

→ 1ステップでデータ取得

### get_stats_data を使う場合

```
1. search_stats で統計表IDを検索
2. get_meta_info でコードを確認
3. get_stats_data でフィルタ条件を指定してデータ取得
```

→ 3ステップ必要

```{tip}
目的のデータがデータセットにあれば、`get_dataset_data` の方が効率的です。
```

## 大量データの取得

データセットにも大量のデータが含まれる場合があります。その場合はページネーションを使用：

```
データセットID「DS001」の全データを取得してください。
ページネーションを使用して、全件取得してください。
```

1回目: `get_dataset_data(dataset_id="DS001", limit=10000, start_position=1)`
2回目: `get_dataset_data(dataset_id="DS001", limit=10000, start_position=10001)`
...

## エラーケース

### データセットが存在しない

```
指定されたデータセットID「XXXX」が見つかりません。
list_datasets で正しいIDを確認してください。
```

### データなし

データセットが空の場合：

```json
{
  "total_count": 0,
  "returned_count": 0,
  "data": []
}
```

## 関連ツール

- [list_datasets](list-datasets.md) - データセットIDを検索
- [get_stats_data](get-stats-data.md) - 統計表から直接データを取得（より柔軟）
