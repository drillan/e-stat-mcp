# server モジュール

MCP サーバー定義とツール関数を提供します。

## 概要

`e_stat_mcp.server` モジュールは FastMCP を使用して MCP サーバーを定義し、
5つのツール関数を公開します。

## ツール関数

| 関数 | 説明 |
|------|------|
| `search_stats` | 統計表を検索 |
| `get_stats_data` | 統計データを取得 |
| `get_meta_info` | メタ情報を取得 |
| `list_datasets` | データセット一覧を取得 |
| `get_dataset_data` | データセットデータを取得 |

## API ドキュメント

```{eval-rst}
.. automodule:: e_stat_mcp.server
   :members:
   :undoc-members:
   :show-inheritance:
```
