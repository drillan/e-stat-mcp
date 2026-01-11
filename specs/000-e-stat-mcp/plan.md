# Implementation Plan: e-Stat API連携MCPサーバー

**Branch**: `001-e-stat-mcp` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-e-stat-mcp/spec.md`

## Summary

政府統計の総合窓口（e-Stat）が提供する統計データをMCP（Model Context Protocol）を通じてAIアシスタントから利用可能にするMCPサーバーを実装する。MCP Python SDK（FastMCP）を使用し、Pydanticによる厳密なデータバリデーションを行う。

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: mcp[cli]>=1.2.0, pydantic>=2.0, pydantic-settings>=2.0, httpx>=0.27, cachetools>=5.0
**Storage**: N/A（ステートレス、インメモリキャッシュのみ）
**Testing**: pytest
**Target Platform**: Linux/macOS/Windows（STDIO MCPサーバー）
**Project Type**: single
**Performance Goals**: 統計表検索5秒以内、データ取得10秒以内（成功条件より）
**Constraints**: e-Stat APIの制約（一括取得10万件上限、リクエスト100コード上限）
**Scale/Scope**: PoC（単一ユーザー向け、ローカル実行）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

現在のconstitution.mdはテンプレート状態のため、以下の汎用ゲートを適用：

| Gate | Status | Notes |
|------|--------|-------|
| 単一目的の原則 | ✅ PASS | e-Stat API連携という単一目的 |
| TDD | ✅ WILL COMPLY | タスク実行時に適用 |
| 型安全性 | ✅ WILL COMPLY | Pydantic必須 |
| シンプル設計 | ✅ PASS | 最小限の依存関係 |

## Project Structure

### Documentation (this feature)

```text
specs/001-e-stat-mcp/
├── plan.md              # This file
├── research.md          # 技術選定・API調査結果
├── data-model.md        # Pydanticモデル定義
├── quickstart.md        # セットアップ・使用ガイド
├── contracts/           # APIコントラクト
│   └── mcp-tools.yaml   # MCPツール定義
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
└── e_stat_mcp/
    ├── __init__.py
    ├── __main__.py        # エントリーポイント
    ├── server.py          # MCPサーバー定義（FastMCP）
    ├── client.py          # e-Stat APIクライアント
    ├── models/            # Pydanticモデル
    │   ├── __init__.py
    │   ├── api.py         # e-Stat APIレスポンスモデル
    │   ├── tools.py       # MCPツール入出力モデル
    │   └── errors.py      # エラーモデル
    ├── settings.py        # 設定管理（pydantic-settings）
    └── cache.py           # キャッシュ実装（cachetools）

tests/
├── unit/
│   ├── test_models.py     # Pydanticモデルのテスト
│   ├── test_client.py     # APIクライアントのテスト（モック）
│   └── test_cache.py      # キャッシュのテスト
├── integration/
│   └── test_e_stat_api.py # e-Stat API統合テスト
└── contract/
    └── test_mcp_tools.py  # MCPツールコントラクトテスト
```

**Structure Decision**: Singleプロジェクト構造を選択。MCPサーバーは単一パッケージ（`e_stat_mcp`）として実装し、`src/`レイアウトを採用。

## Complexity Tracking

> 特に違反なし。シンプルな構造を維持。

## Design Decisions

### Pydanticバリデーション必須化

**ユーザー要求**: `pydanticによるデータバリデーションを必須にしてください`

**適用範囲**:

1. **e-Stat APIレスポンス**: すべてのAPIレスポンスはPydanticモデルでパース・バリデーション
2. **MCPツール入力**: すべてのツール引数はPydantic BaseModelでバリデーション
3. **MCPツール出力**: すべてのツール戻り値はPydanticモデルでシリアライズ
4. **設定**: pydantic-settingsで環境変数を型安全に管理

**実装ルール**:

- `BaseModel`の`model_validate()`を使用（`parse_obj`は非推奨）
- `Field(...)`で必須フィールドを明示
- `alias`でe-Stat APIのフィールド名（`@id`, `$`等）をマッピング
- バリデーションエラーは`ValidationError`として伝播し、ユーザーに説明的なメッセージを返却

## Generated Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| research.md | specs/001-e-stat-mcp/research.md | 技術選定・API調査 |
| data-model.md | specs/001-e-stat-mcp/data-model.md | Pydanticモデル定義 |
| mcp-tools.yaml | specs/001-e-stat-mcp/contracts/mcp-tools.yaml | MCPツールコントラクト |
| quickstart.md | specs/001-e-stat-mcp/quickstart.md | セットアップガイド |

## Next Steps

`/speckit.tasks`コマンドを実行してtasks.mdを生成し、実装タスクを定義する。
