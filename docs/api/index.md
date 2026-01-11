# APIリファレンス

e-Stat MCP サーバーの Python API リファレンスです。

このセクションはソースコードの docstring から自動生成されています。

## モジュール一覧

| モジュール | 説明 |
|-----------|------|
| [server](server.md) | MCP サーバー定義、ツール関数 |
| [client](client.md) | e-Stat API クライアント |
| [models](models.md) | Pydantic データモデル |
| [settings](settings.md) | 設定管理 |
| [cache](cache.md) | キャッシュユーティリティ |

## パッケージ構造

```
e_stat_mcp/
├── __init__.py          # パッケージ初期化
├── __main__.py          # エントリーポイント
├── server.py            # MCPサーバー
├── client.py            # APIクライアント
├── settings.py          # 設定
├── cache.py             # キャッシュ
└── models/
    ├── __init__.py      # モデルエクスポート
    ├── api.py           # APIレスポンスモデル
    ├── tools.py         # ツール入出力モデル
    └── errors.py        # エラーモデル
```

## 使用例

### クライアントの直接使用

```python
import asyncio
from e_stat_mcp.client import EStatClient
from e_stat_mcp.settings import get_settings

async def main():
    settings = get_settings()
    client = EStatClient(settings)

    try:
        results = await client.get_stats_list(keyword="人口")
        for result in results:
            print(f"{result.table_id}: {result.table_name}")
    finally:
        await client.close()

asyncio.run(main())
```

### モデルの使用

```python
from e_stat_mcp.models import SearchStatsResult, StatsDataItem

# 検索結果の作成
result = SearchStatsResult(
    table_id="0003410379",
    table_name="都道府県別人口",
    stat_name="国勢調査",
    survey_date="2020年",
    gov_org="総務省",
)

print(result.model_dump_json(indent=2))
```

## 次のステップ

各モジュールの詳細ドキュメント：

- [server](server.md) - MCP サーバー
- [client](client.md) - API クライアント
- [models](models.md) - データモデル
