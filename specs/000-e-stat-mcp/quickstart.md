# Quickstart: e-Stat API連携MCPサーバー

**Branch**: `001-e-stat-mcp` | **Date**: 2026-01-07

## 前提条件

1. Python 3.13以上
2. uv（パッケージマネージャー）
3. e-StatのアプリケーションID（[e-Stat](https://www.e-stat.go.jp/)でユーザー登録後に取得）

## セットアップ

### 1. 依存関係のインストール

```bash
cd /home/driller/work/e-stat-mcp
uv add "mcp[cli]>=1.2.0" "pydantic>=2.0" "pydantic-settings>=2.0" "httpx>=0.27" "cachetools>=5.0"
```

### 2. 環境設定

`.env`ファイルを作成：

```bash
# .env
E_STAT_APP_ID=your_application_id_here
E_STAT_CACHE_TTL_SECONDS=3600
E_STAT_REQUEST_TIMEOUT_SECONDS=30
E_STAT_MAX_RETRIES=3
```

### 3. サーバーの起動確認

```bash
uv run python -m e_stat_mcp
```

## Claude for Desktopとの統合

`~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）または
`%APPDATA%\Claude\claude_desktop_config.json`（Windows）に以下を追加：

```json
{
  "mcpServers": {
    "e-stat": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/driller/work/e-stat-mcp",
        "run",
        "python",
        "-m",
        "e_stat_mcp"
      ],
      "env": {
        "E_STAT_APP_ID": "your_application_id_here"
      }
    }
  }
}
```

Claudeを再起動して設定を反映。

## 使用例

### 統計表の検索

```
「人口に関する統計を探して」
```

→ `search_stats`ツールが呼び出され、人口関連の統計表一覧が返却される。

### 統計データの取得

```
「統計表ID 0003348423 のデータを取得して」
```

→ `get_stats_data`ツールが呼び出され、統計データが返却される。

### メタ情報の確認

```
「統計表ID 0003348423 の構造を教えて」
```

→ `get_meta_info`ツールが呼び出され、分類情報が返却される。

## トラブルシューティング

### 認証エラー

```
エラー: 認証に失敗しました。アプリケーションIDを確認してください。
```

→ `E_STAT_APP_ID`環境変数が正しく設定されているか確認。

### サーバーが見つからない

1. Claudeを完全に再起動
2. 設定ファイルのパスが絶対パスか確認
3. `uv run python -m e_stat_mcp`でサーバーが単体起動するか確認

### ログの確認

- macOS: `~/Library/Logs/Claude/mcp*.log`
- Windows: `%USERPROFILE%\AppData\Local\Claude\logs\mcp*.log`

## 開発者向け

### テストの実行

```bash
uv run python -m pytest tests/ -v
```

### 型チェック

```bash
uv run python -m mypy src/
```

### コードフォーマット

```bash
uv run python -m ruff check . --fix
uv run python -m ruff format .
```

## プロジェクト構造

```
e-stat-mcp/
├── src/
│   └── e_stat_mcp/
│       ├── __init__.py
│       ├── __main__.py      # エントリーポイント
│       ├── server.py        # MCPサーバー定義
│       ├── client.py        # e-Stat APIクライアント
│       ├── models/          # Pydanticモデル
│       │   ├── __init__.py
│       │   ├── api.py       # e-Stat APIレスポンスモデル
│       │   ├── tools.py     # MCPツール入出力モデル
│       │   └── errors.py    # エラーモデル
│       ├── settings.py      # 設定管理
│       └── cache.py         # キャッシュ実装
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── .env
└── pyproject.toml
```
