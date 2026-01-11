# 設定

e-Stat MCP サーバーの設定オプションを解説します。

## 環境変数一覧

| 環境変数 | 必須 | デフォルト値 | 説明 |
|----------|------|--------------|------|
| `E_STAT_APP_ID` | **必須** | - | e-Stat アプリケーションID |
| `E_STAT_BASE_URL` | 任意 | `https://api.e-stat.go.jp/rest/3.0/app/json` | API ベースURL |
| `E_STAT_CACHE_TTL_SECONDS` | 任意 | `3600` | キャッシュ有効期間（秒） |
| `E_STAT_REQUEST_TIMEOUT_SECONDS` | 任意 | `30` | リクエストタイムアウト（秒） |
| `E_STAT_MAX_RETRIES` | 任意 | `3` | 最大リトライ回数 |
| `E_STAT_CACHE_MAX_SIZE` | 任意 | `1000` | キャッシュ最大エントリ数 |

## .env ファイルの例

```bash
# 必須設定
E_STAT_APP_ID=your_application_id_here

# オプション設定
E_STAT_CACHE_TTL_SECONDS=3600
E_STAT_REQUEST_TIMEOUT_SECONDS=30
E_STAT_MAX_RETRIES=3
E_STAT_CACHE_MAX_SIZE=1000
```

## 各設定の詳細

### E_STAT_APP_ID（必須）

e-Stat API を使用するために必要なアプリケーションIDです。

```bash
E_STAT_APP_ID=abcd1234-5678-efgh-ijkl-mnop90123456
```

[e-Stat API](https://www.e-stat.go.jp/api/) でユーザー登録後に取得できます。

### E_STAT_BASE_URL

API のベースURLです。通常は変更不要です。

```bash
E_STAT_BASE_URL=https://api.e-stat.go.jp/rest/3.0/app/json
```

### E_STAT_CACHE_TTL_SECONDS

API レスポンスのキャッシュ有効期間（秒）です。

```bash
# 1時間（デフォルト）
E_STAT_CACHE_TTL_SECONDS=3600

# 24時間
E_STAT_CACHE_TTL_SECONDS=86400

# キャッシュを無効化（0は非推奨）
E_STAT_CACHE_TTL_SECONDS=1
```

```{tip}
統計データは頻繁に更新されないため、長めのキャッシュ時間を設定しても問題ありません。
```

### E_STAT_REQUEST_TIMEOUT_SECONDS

API リクエストのタイムアウト時間（秒）です。

```bash
# 30秒（デフォルト）
E_STAT_REQUEST_TIMEOUT_SECONDS=30

# 大量データ取得時は長めに設定
E_STAT_REQUEST_TIMEOUT_SECONDS=60
```

### E_STAT_MAX_RETRIES

ネットワークエラー時の最大リトライ回数です。

```bash
# 3回（デフォルト）
E_STAT_MAX_RETRIES=3

# リトライを減らす
E_STAT_MAX_RETRIES=1
```

リトライは指数バックオフで行われます（1秒、2秒、4秒...）。

### E_STAT_CACHE_MAX_SIZE

メモリ内キャッシュの最大エントリ数です。

```bash
# 1000エントリ（デフォルト）
E_STAT_CACHE_MAX_SIZE=1000

# メモリを節約する場合
E_STAT_CACHE_MAX_SIZE=100
```

## ユースケース別設定例

### 開発環境

短いキャッシュ時間で頻繁にデータを確認：

```bash
E_STAT_APP_ID=your_app_id
E_STAT_CACHE_TTL_SECONDS=300
E_STAT_REQUEST_TIMEOUT_SECONDS=30
```

### 本番環境

長めのキャッシュで安定運用：

```bash
E_STAT_APP_ID=your_app_id
E_STAT_CACHE_TTL_SECONDS=86400
E_STAT_REQUEST_TIMEOUT_SECONDS=60
E_STAT_MAX_RETRIES=5
E_STAT_CACHE_MAX_SIZE=2000
```

### メモリ制限がある環境

キャッシュを控えめに：

```bash
E_STAT_APP_ID=your_app_id
E_STAT_CACHE_TTL_SECONDS=600
E_STAT_CACHE_MAX_SIZE=100
```

## 設定の確認

設定が正しく読み込まれているか確認するには、Python から直接確認できます：

```bash
uv run python -c "from e_stat_mcp.settings import get_settings; s = get_settings(); print(f'Cache TTL: {s.e_stat_cache_ttl_seconds}s')"
```

## 次のステップ

- [使用例](usage-examples.md) - 実践的なユースケース
- [MCPツールリファレンス](../tools/index.md) - 各ツールの詳細
