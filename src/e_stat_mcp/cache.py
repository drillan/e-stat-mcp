"""キャッシュモジュール."""

from typing import Any

from cachetools import TTLCache


def create_cache(ttl: float = 3600, maxsize: int = 1000) -> TTLCache[str, Any]:
    """TTLキャッシュを作成.

    Args:
        ttl: Time-To-Live（秒）。デフォルトは1時間。
        maxsize: キャッシュの最大サイズ。デフォルトは1000エントリ。

    Returns:
        TTLCache: キャッシュインスタンス
    """
    return TTLCache(maxsize=maxsize, ttl=ttl)


def get_cache(cache: TTLCache[str, Any], key: str) -> Any | None:
    """キャッシュから値を取得.

    Args:
        cache: キャッシュインスタンス
        key: キャッシュキー

    Returns:
        キャッシュされた値。存在しない場合はNone。
    """
    return cache.get(key)


def set_cache(cache: TTLCache[str, Any], key: str, value: Any) -> None:
    """キャッシュに値を設定.

    Args:
        cache: キャッシュインスタンス
        key: キャッシュキー
        value: キャッシュする値
    """
    cache[key] = value
