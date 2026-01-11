# e-Stat MCP サーバー

日本の政府統計ポータルサイト [e-Stat](https://www.e-stat.go.jp/) のAPIに接続するMCP (Model Context Protocol) サーバーです。

Claude Code や Claude Desktop から e-Stat の統計データを検索・取得できます。

## 機能

| ツール | 説明 |
|--------|------|
| `search_stats` | キーワードや政府統計コードで統計表を検索 |
| `get_stats_data` | 統計表IDを指定して統計データを取得 |
| `get_meta_info` | 統計表のメタ情報（分類項目など）を取得 |
| `list_datasets` | 公開データセットの一覧を取得 |
| `get_dataset_data` | データセットIDを指定してデータを取得 |

## 前提条件

- Python 3.13以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー
- e-Stat アプリケーションID（[e-Stat API](https://www.e-stat.go.jp/api/) から取得）

## セットアップ

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. 環境変数の設定

e-Stat のアプリケーションIDを環境変数に設定します。

```bash
export E_STAT_APP_ID="あなたのアプリケーションID"
```

または `.env` ファイルを作成:

```bash
echo "E_STAT_APP_ID=あなたのアプリケーションID" > .env
```

### 3. Claude Code での利用

プロジェクトディレクトリで Claude Code を起動すると、自動的にMCPサーバーが読み込まれます。

```bash
claude
```

`/mcp` コマンドでツールが認識されていることを確認:

```
Tools for e-stat-mcp (5 tools)
  1. search_stats
  2. get_stats_data
  3. get_meta_info
  4. list_datasets
  5. get_dataset_data
```

## 使用例

### 統計表の検索

```
国勢調査の人口に関する統計表を検索してください
```

```
「労働力調査」に関する統計表を5件検索してください
```

### メタ情報の確認

```
統計表ID 0003410379 のメタ情報を取得してください
```

### 統計データの取得

```
人口に関する統計表を1件検索し、そのメタ情報を確認してから、最初の10件のデータを取得してください
```

### データセットの活用

```
公開データセットの一覧を取得して、どのようなデータが利用可能か教えてください
```

### 実践的な分析

```
2020年の国勢調査から都道府県別人口データを取得して、上位5都道府県を教えてください
```

## 設定オプション

以下の環境変数で動作をカスタマイズできます。

| 環境変数 | デフォルト値 | 説明 |
|----------|--------------|------|
| `E_STAT_APP_ID` | (必須) | e-Stat アプリケーションID |
| `E_STAT_BASE_URL` | `https://api.e-stat.go.jp/rest/3.0/app/json` | API ベースURL |
| `E_STAT_CACHE_TTL_SECONDS` | `3600` | キャッシュ有効期間（秒） |
| `E_STAT_REQUEST_TIMEOUT_SECONDS` | `30` | リクエストタイムアウト（秒） |
| `E_STAT_MAX_RETRIES` | `3` | 最大リトライ回数 |

## 開発

### テストの実行

```bash
# ユニットテスト
uv run pytest -m "not integration"

# 統合テスト（要 E_STAT_APP_ID）
uv run pytest -m integration

# カバレッジ付き
uv run pytest --cov=e_stat_mcp
```

### コード品質チェック

```bash
# Linter
uv run ruff check src/ tests/

# フォーマッター
uv run ruff format src/ tests/

# 型チェック
uv run mypy src/
```

### 全チェック実行

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest
```

## ドキュメント

詳細なドキュメントは `docs/` ディレクトリにあります。

```bash
# ドキュメントのビルド
cd docs && uv run sphinx-build -M html . _build

# ブラウザで確認
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
```

ドキュメントの内容:

- **ユーザーガイド**: インストール、設定、使用例
- **MCP ツールリファレンス**: 各ツールの詳細な仕様
- **開発者ガイド**: アーキテクチャ、データモデル、コントリビューション
- **API リファレンス**: Python モジュールの自動生成ドキュメント

## ライセンス

MIT License

## 関連リンク

- [e-Stat API 仕様](https://www.e-stat.go.jp/api/api-info/e-stat-manual3-0)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
