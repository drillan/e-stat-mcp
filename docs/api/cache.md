# cache モジュール

キャッシュユーティリティを提供するモジュールです。

## 概要

`e_stat_mcp.cache` モジュールは `cachetools.TTLCache` のシンプルなラッパーを提供します。

## 主な関数

| 関数 | 説明 |
|------|------|
| `create_cache` | TTL キャッシュを作成 |
| `get_cache` | キャッシュから値を取得 |
| `set_cache` | キャッシュに値を設定 |

## 使用例

```python
from e_stat_mcp.cache import create_cache, get_cache, set_cache

# キャッシュを作成（TTL: 3600秒、最大1000エントリ）
cache = create_cache(ttl=3600, maxsize=1000)

# 値を設定
set_cache(cache, "key1", {"data": "value"})

# 値を取得
value = get_cache(cache, "key1")
if value is not None:
    print(f"Cache hit: {value}")
else:
    print("Cache miss")
```

## キャッシュの特徴

- **TTL ベース**: 設定した時間が経過すると自動的に無効化
- **サイズ制限**: 最大エントリ数を超えると古いものから削除（LRU）
- **スレッドセーフではない**: 単一スレッドでの使用を想定

## API ドキュメント

```{eval-rst}
.. automodule:: e_stat_mcp.cache
   :members:
   :undoc-members:
   :show-inheritance:
```
