# e-Stat MCP Server Constitution

## Core Principles

### I. Pydantic-First (型安全性)
すべてのデータ構造はPydantic BaseModelで定義する。
- MUST: APIレスポンス、ツール入出力はすべてPydanticモデルでバリデーション
- MUST: 型エラーは実行前にmypyで検出
- SHOULD: `Any`型の使用を避け、具体的な型を使用

### II. Test-Driven Development (NON-NEGOTIABLE)
TDD必須: テスト作成 → ユーザー承認 → テスト失敗 → 実装
- MUST: Red-Green-Refactorサイクルを厳守
- MUST: 各ユーザーストーリーは独立してテスト可能

### III. Explicit Error Handling
暗黙的なフォールバック禁止。
- MUST: データ取得失敗時は例外を発生させる
- MUST: エラーメッセージはユーザーが次のアクションを理解できる内容
- MUST NOT: デフォルト値での自動補完

### IV. Single Responsibility
各モジュールは単一の責務を持つ。
- client.py: e-Stat API通信のみ
- server.py: MCPツール定義のみ
- models/: データ構造定義のみ

## Quality Gates

- コミット前: `uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest`
- すべてのゲートをパスしなければコミット禁止

## Governance

Constitution違反はCRITICALとして扱い、実装前に解決必須。

**Version**: 1.0.0 | **Ratified**: 2026-01-07
