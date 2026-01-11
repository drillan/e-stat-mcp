# client モジュール

e-Stat API との通信を担当するクライアントモジュールです。

## 概要

`e_stat_mcp.client` モジュールは以下を提供します：

- `EStatClient`: e-Stat API クライアント
- `EStatApiError`: API エラー例外

## 主な機能

- 非同期 HTTP 通信（httpx）
- TTL キャッシュによるレスポンスキャッシング
- 自動リトライ（ネットワークエラー、サーバーエラー時）
- Pydantic モデルによるレスポンスバリデーション

## 使用例

```python
import asyncio
from e_stat_mcp.client import EStatClient
from e_stat_mcp.settings import get_settings

async def main():
    settings = get_settings()
    client = EStatClient(settings)

    try:
        # 統計表を検索
        results = await client.get_stats_list(keyword="人口", limit=5)
        for result in results:
            print(f"{result.table_id}: {result.table_name}")

        # メタ情報を取得
        meta_results = await client.get_meta_info("0003410379")
        for meta in meta_results:
            print(f"{meta.class_id}: {meta.class_name}")

    finally:
        await client.close()

asyncio.run(main())
```

## API ドキュメント

```{eval-rst}
.. automodule:: e_stat_mcp.client
   :members:
   :undoc-members:
   :show-inheritance:
```
