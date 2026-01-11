# 変更履歴

e-Stat MCP サーバーの変更履歴です。

## [0.1.0] - 2026-01-07

### 追加

- 初期リリース
- MCP サーバー基盤（FastMCP）
- e-Stat API クライアント
- 5つの MCP ツール
  - `search_stats`: 統計表検索
  - `get_stats_data`: 統計データ取得
  - `get_meta_info`: メタ情報取得
  - `list_datasets`: データセット一覧取得
  - `get_dataset_data`: データセットデータ取得
- TTL キャッシュによるレスポンスキャッシング
- 指数バックオフリトライ
- Pydantic によるデータバリデーション
- 環境変数による設定管理
- 包括的なテストスイート（単体・統合・コントラクト）
- Sphinx ドキュメント

### 修正

- ClassItem モデルが `@name` と `$` の両形式に対応（PR #3）

---

## バージョニング

このプロジェクトは [Semantic Versioning](https://semver.org/lang/ja/) に従います。

- **MAJOR**: 互換性のない API 変更
- **MINOR**: 後方互換性のある機能追加
- **PATCH**: 後方互換性のあるバグ修正

## 破壊的変更の方針

- MAJOR バージョンアップ時のみ破壊的変更を行います
- 破壊的変更は事前に非推奨（deprecation）警告を出します
- 移行ガイドを提供します
