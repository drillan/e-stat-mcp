# list_datasets

公開データセットの一覧を取得するツールです。

## 概要

e-Stat で公開されているデータセットの一覧を取得します。データセットは、よく使われる統計データを事前にフィルタ・整理したものです。

## パラメータ

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|------|------|----------|------|
| `stats_data_id` | str | 任意 | null | 統計表IDでフィルタ |

## 戻り値

データセット情報のリスト。各要素は以下の構造です：

| フィールド | 型 | 説明 |
|-----------|------|------|
| `dataset_id` | str | データセットID（get_dataset_data で使用） |
| `dataset_name` | str | データセット名 |
| `stats_data_id` | str | 対象統計表ID |
| `is_public` | bool | 公開状態 |
| `description` | str | 説明（任意） |

## 使用例

### 全データセットの一覧

```
公開データセットの一覧を取得してください
```

→ `list_datasets()`

レスポンス例：
```
1. dataset_id: DS001
   dataset_name: 都道府県別人口（2020年）
   stats_data_id: 0003410379
   is_public: true
   description: 国勢調査2020年の都道府県別人口

2. dataset_id: DS002
   dataset_name: 完全失業率推移
   stats_data_id: 0003215423
   is_public: true
   description: 労働力調査の完全失業率時系列データ
...
```

### 特定統計表のデータセット

```
統計表ID「0003410379」に関連するデータセットを確認してください
```

→ `list_datasets(stats_data_id="0003410379")`

## データセットと get_stats_data の違い

| 項目 | get_stats_data | get_dataset_data |
|------|---------------|------------------|
| 取得元 | 統計表（生データ） | データセット（整理済み） |
| フィルタ | 自分で指定 | 事前設定済み |
| 柔軟性 | 高い | 低い |
| 手軽さ | 低い（コード確認が必要） | 高い |

```{tip}
目的のデータがデータセットにあれば、`get_dataset_data` を使う方が簡単です。
```

## ワークフロー

```{mermaid}
flowchart TD
    A[list_datasets] --> B{目的のデータセットがある?}
    B -->|ある| C[get_dataset_data]
    B -->|ない| D[search_stats]
    D --> E[get_meta_info]
    E --> F[get_stats_data]
    C --> G[統計データ]
    F --> G
```

## エラーケース

### データセットなし

指定した統計表IDにデータセットがない場合：

```
指定された統計表ID「XXXX」に関連するデータセットは見つかりませんでした。
```

## 関連ツール

- [get_dataset_data](get-dataset-data.md) - データセットIDでデータを取得
- [get_stats_data](get-stats-data.md) - 統計表から直接データを取得
