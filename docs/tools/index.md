# MCPツールリファレンス

e-Stat MCP サーバーが提供する5つのツールを解説します。

## ツール一覧

| ツール | 説明 |
|--------|------|
| [search_stats](search-stats.md) | キーワードや政府統計コードで統計表を検索 |
| [get_stats_data](get-stats-data.md) | 統計表IDからデータを取得 |
| [get_meta_info](get-meta-info.md) | 統計表のメタ情報（分類項目など）を取得 |
| [list_datasets](list-datasets.md) | 公開データセットの一覧を取得 |
| [get_dataset_data](get-dataset-data.md) | データセットIDからデータを取得 |

## 基本的なワークフロー

統計データを取得する典型的な流れを示します。

```{mermaid}
flowchart TB
    subgraph "Step 1: 検索"
        A[search_stats] --> B[table_id を取得]
    end

    subgraph "Step 2: 構造確認"
        B --> C[get_meta_info]
        C --> D[分類コードを確認]
    end

    subgraph "Step 3: データ取得"
        D --> E[get_stats_data]
        E --> F[統計データ]
    end
```

### ワークフロー例

1. **検索**: `search_stats` でキーワード検索し、目的の統計表の `table_id` を取得
2. **構造確認**: `get_meta_info` でメタ情報を取得し、分類項目やコードを確認
3. **データ取得**: `get_stats_data` で実際のデータを取得（必要に応じてフィルタ条件を指定）

## データセット経由のワークフロー

公開データセットを使う場合の流れです。

```{mermaid}
flowchart TB
    A[list_datasets] --> B[dataset_id を取得]
    B --> C[get_dataset_data]
    C --> D[統計データ]
```

データセットは、よく使われるデータを事前に整理したものです。フィルタ条件が事前設定されているため、`get_stats_data` より簡単に使えます。

## 共通パラメータ

### ページネーション

多くのツールで以下のパラメータが使えます：

| パラメータ | 型 | デフォルト | 説明 |
|-----------|------|----------|------|
| `limit` | int | ツールによる | 取得件数上限（最大 100,000） |
| `start_position` | int | 1 | 取得開始位置 |

大量データを取得する場合は、`start_position` を変更しながら繰り返し呼び出します。

### レスポンスの共通構造

データ取得系ツールは以下の構造で結果を返します：

```json
{
  "total_count": 12345,
  "returned_count": 100,
  "data": [...]
}
```

- `total_count`: 条件に一致するデータの総件数
- `returned_count`: 今回返却した件数
- `data`: データの配列

## エラーハンドリング

ツールはエラー時に詳細なメッセージを返します。

| エラー種別 | 説明 | 対処法 |
|-----------|------|--------|
| 認証エラー | アプリケーションIDが無効 | E_STAT_APP_ID を確認 |
| パラメータエラー | 必須パラメータが不足 | パラメータを確認 |
| データなし | 条件に一致するデータがない | 検索条件を緩和 |
| ネットワークエラー | API接続に失敗 | しばらく待って再試行 |

詳細は [エラーコード一覧](../appendix/error-codes.md) を参照してください。

## 次のステップ

各ツールの詳細ドキュメント：

- [search_stats](search-stats.md) - 統計表検索
- [get_stats_data](get-stats-data.md) - データ取得
- [get_meta_info](get-meta-info.md) - メタ情報取得
- [list_datasets](list-datasets.md) - データセット一覧
- [get_dataset_data](get-dataset-data.md) - データセットデータ取得
