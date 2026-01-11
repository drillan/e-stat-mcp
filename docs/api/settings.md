# settings モジュール

設定管理を担当するモジュールです。

## 概要

`e_stat_mcp.settings` モジュールは pydantic-settings を使用して
環境変数からの設定読み込みを行います。

## 設定項目

| 環境変数 | 型 | デフォルト | 説明 |
|----------|------|----------|------|
| `E_STAT_APP_ID` | str | 必須 | e-Stat アプリケーションID |
| `E_STAT_BASE_URL` | str | `https://api.e-stat.go.jp/rest/3.0/app/json` | API ベースURL |
| `E_STAT_CACHE_TTL_SECONDS` | int | 3600 | キャッシュ TTL（秒） |
| `E_STAT_REQUEST_TIMEOUT_SECONDS` | int | 30 | リクエストタイムアウト（秒） |
| `E_STAT_MAX_RETRIES` | int | 3 | 最大リトライ回数 |
| `E_STAT_CACHE_MAX_SIZE` | int | 1000 | キャッシュ最大エントリ数 |

## 使用例

```python
from e_stat_mcp.settings import get_settings

# シングルトンで設定を取得
settings = get_settings()

print(f"App ID: {settings.e_stat_app_id}")
print(f"Cache TTL: {settings.e_stat_cache_ttl_seconds}s")
print(f"Timeout: {settings.e_stat_request_timeout_seconds}s")
```

## .env ファイル

`.env` ファイルを使用して設定を管理できます：

```bash
E_STAT_APP_ID=your_application_id
E_STAT_CACHE_TTL_SECONDS=3600
E_STAT_REQUEST_TIMEOUT_SECONDS=30
E_STAT_MAX_RETRIES=3
```

## API ドキュメント

```{eval-rst}
.. automodule:: e_stat_mcp.settings
   :members:
   :undoc-members:
   :show-inheritance:
```
