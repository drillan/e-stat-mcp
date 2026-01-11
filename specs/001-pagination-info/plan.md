# Implementation Plan: ページネーション情報の追加

**Branch**: `001-pagination-info` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: GitHub Issue #1: "10万件上限に対応したページネーション情報の追加"
**Base Implementation**: `specs/000-e-stat-mcp/`

## Summary

e-Stat APIの10万件上限に対応するため、`StatsDataResult`モデルに`has_next`と`next_start_position`フィールドを追加し、LLMが自動的にページングを理解できるようにする。対象ツールは`get_stats_data`と`get_dataset_data`の2つ。

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: mcp[cli]>=1.2.0, pydantic>=2.0
**Storage**: N/A（既存実装への増分変更）
**Testing**: pytest
**Target Platform**: Linux/macOS/Windows（STDIO MCPサーバー）
**Project Type**: single（既存プロジェクトへの機能追加）
**Performance Goals**: 計算ロジックは既存レスポンスに含まれるため、追加オーバーヘッドなし
**Constraints**: 後方互換性を考慮（新フィールドの追加のみ、既存フィールドは変更なし）
**Scale/Scope**: 小規模機能追加（4ファイル変更）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Pydantic-First（型安全性） | PASS | `has_next: bool`, `next_start_position: int \| None`をPydanticモデルに追加 |
| Test-Driven Development | WILL COMPLY | モデルテストを先に作成し、Red-Green-Refactorで実装 |
| Explicit Error Handling | N/A | エラー処理の変更なし |
| Single Responsibility | PASS | models/tools.pyはデータ構造、server.pyはツール定義のみ |

## Project Structure

### Documentation (this feature)

```text
specs/001-pagination-info/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (modified files)

```text
src/e_stat_mcp/
├── models/
│   └── tools.py         # StatsDataResultモデル拡張
└── server.py            # レスポンス計算ロジック追加、docstring改善

tests/
├── unit/
│   └── test_models_tools.py  # モデルテスト追加
└── contract/
    └── test_mcp_tools.py     # コントラクトテスト更新
```

**Structure Decision**: 既存プロジェクト構造を維持。変更は4ファイルのみ。

## Complexity Tracking

> 特に違反なし。最小限の変更でシンプルに維持。

## Design Decisions

### 1. フィールド設計

**決定**: `has_next: bool`と`next_start_position: int | None`を`StatsDataResult`に追加

**根拠**:
- LLMが次のアクションを判断しやすい明示的なフィールド
- `next_start_position`は次ページがある場合のみ値を持ち、ない場合はNone
- 既存の`total_count`と`returned_count`はそのまま維持（後方互換性）

### 2. 計算ロジック

**決定**:
- `has_next = (start_position + returned_count - 1) < total_count`
- `next_start_position = start_position + returned_count` (has_nextがtrueの場合のみ)

**根拠**:
- e-Stat APIは1-indexed（start_positionの初期値は1）
- 標準的なページネーション計算式

### 3. docstring改善

**決定**: `get_stats_data`と`get_dataset_data`のdocstringにページネーション使用例を追加

**根拠**:
- LLMがツール説明から自動的にページングを理解できる
- 具体的な使用例を含めることで、次のアクションが明確になる

## Generated Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| spec.md | specs/001-pagination-info/spec.md | Feature specification |
| research.md | specs/001-pagination-info/research.md | 技術調査（最小限） |
| data-model.md | specs/001-pagination-info/data-model.md | モデル変更定義 |

## Next Steps

`/speckit.tasks`コマンドを実行してtasks.mdを生成し、実装タスクを定義する。
