"""Unit tests for cache module."""

import time

from e_stat_mcp.cache import create_cache, get_cache, set_cache


class TestCacheModule:
    """キャッシュモジュールのテスト."""

    def test_create_cache_with_default_ttl(self) -> None:
        """デフォルトTTLでキャッシュを作成できること."""
        cache = create_cache()
        assert cache is not None
        assert cache.maxsize == 1000
        assert cache.ttl == 3600

    def test_create_cache_with_custom_ttl(self) -> None:
        """カスタムTTLでキャッシュを作成できること."""
        cache = create_cache(ttl=7200, maxsize=500)
        assert cache.maxsize == 500
        assert cache.ttl == 7200

    def test_set_and_get_cache(self) -> None:
        """キャッシュに値を設定して取得できること."""
        cache = create_cache()
        key = "test_key"
        value = {"data": "test_value"}

        set_cache(cache, key, value)
        result = get_cache(cache, key)

        assert result == value

    def test_get_cache_miss(self) -> None:
        """キャッシュミス時にNoneを返すこと."""
        cache = create_cache()
        result = get_cache(cache, "nonexistent_key")
        assert result is None

    def test_cache_expiration(self) -> None:
        """TTL経過後にキャッシュが期限切れになること."""
        cache = create_cache(ttl=0.1)  # 100ms TTL
        key = "expiring_key"
        value = {"data": "expiring_value"}

        set_cache(cache, key, value)
        assert get_cache(cache, key) == value

        time.sleep(0.15)  # Wait for expiration
        assert get_cache(cache, key) is None

    def test_cache_key_generation(self) -> None:
        """異なるキーで異なる値を保存できること."""
        cache = create_cache()

        set_cache(cache, "key1", {"value": 1})
        set_cache(cache, "key2", {"value": 2})

        assert get_cache(cache, "key1") == {"value": 1}
        assert get_cache(cache, "key2") == {"value": 2}

    def test_cache_overwrite(self) -> None:
        """同じキーで値を上書きできること."""
        cache = create_cache()
        key = "overwrite_key"

        set_cache(cache, key, {"version": 1})
        assert get_cache(cache, key) == {"version": 1}

        set_cache(cache, key, {"version": 2})
        assert get_cache(cache, key) == {"version": 2}
