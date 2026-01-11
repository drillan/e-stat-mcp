# 開発者ガイド

このセクションでは、e-Stat MCP サーバーの内部構造と拡張方法を解説します。

## 概要

e-Stat MCP サーバーは以下の技術スタックで構築されています：

| カテゴリ | 技術 |
|---------|------|
| 言語 | Python 3.13+ |
| MCPフレームワーク | FastMCP |
| HTTPクライアント | httpx |
| データバリデーション | Pydantic v2 |
| 設定管理 | pydantic-settings |
| キャッシュ | cachetools |

## このセクションの内容

- [アーキテクチャ](architecture.md) - システム全体の設計
- [データモデル](data-models.md) - Pydantic モデルの解説
- [エラー処理](error-handling.md) - エラーハンドリングパターン
- [コントリビューション](contributing.md) - プロジェクトへの貢献方法

## プロジェクト構造

```
e-stat-mcp/
├── src/e_stat_mcp/
│   ├── __init__.py          # パッケージ初期化
│   ├── __main__.py          # エントリーポイント
│   ├── server.py            # MCPサーバー定義
│   ├── client.py            # e-Stat APIクライアント
│   ├── settings.py          # 設定管理
│   ├── cache.py             # キャッシュユーティリティ
│   └── models/
│       ├── __init__.py      # モデルエクスポート
│       ├── api.py           # APIレスポンスモデル
│       ├── tools.py         # MCPツール入出力モデル
│       └── errors.py        # エラーモデル
│
├── tests/
│   ├── unit/                # 単体テスト
│   ├── integration/         # 統合テスト
│   └── contract/            # コントラクトテスト
│
├── docs/                    # ドキュメント（このサイト）
├── specs/                   # 仕様書
└── pyproject.toml           # プロジェクト設定
```

## 設計原則

### 型安全性

- すべての関数、メソッド、変数に型アノテーション
- mypy strict モードで静的型チェック
- Pydantic によるランタイムバリデーション

### テスト駆動開発

- 単体テスト: 外部依存なし（モック使用）
- 統合テスト: 実際の e-Stat API を使用
- コントラクトテスト: MCP ツール仕様の検証

### エラー処理

- 明示的なエラー処理（暗黙のフォールバックなし）
- ユーザー向けの分かりやすいエラーメッセージ
- 詳細なエラーコード体系

## 開発環境のセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/drillan/e-stat-mcp.git
cd e-stat-mcp

# 開発用依存関係を含めてインストール
uv sync --all-extras

# テストの実行
uv run pytest

# コード品質チェック
uv run ruff check . && uv run ruff format --check . && uv run mypy .
```

## 次のステップ

- [アーキテクチャ](architecture.md) - システム設計を理解
- [APIリファレンス](../api/index.md) - コードの詳細ドキュメント
