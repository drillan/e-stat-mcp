# Tasks: ページネーション情報の追加

**Input**: Design documents from `/specs/001-pagination-info/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: 本機能はTDDアプローチを採用。テストを先に作成し、失敗を確認後に実装。

**Organization**: 単一ユーザーストーリー（P1）のため、シンプルな構成。既存プロジェクトへの増分変更。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: 本機能は既存プロジェクトへの増分変更のため、新規セットアップは不要

**Note**: 既存の `src/e_stat_mcp/` および `tests/` 構造を使用

**Checkpoint**: セットアップ不要 - 次のフェーズへ進む

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 本機能は既存モデル・サーバーへの変更のため、新規基盤構築は不要

**Note**: 既存の `StatsDataResult` モデルと `server.py` のツール定義を直接変更

**Checkpoint**: 基盤準備完了 - ユーザーストーリー実装を開始可能

---

## Phase 3: User Story 1 - ページネーションによる連続データ取得 (Priority: P1)

**Goal**: 大量データ取得時に、次のページが存在するかと次の開始位置を明確に返却する

**Independent Test**: 総件数がlimitを超えるデータを取得し、`has_next`と`next_start_position`が正しく返却されることを確認

### Tests for User Story 1 (TDD: Red Phase)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T001 [P] [US1] モデルテスト作成: `has_next=True`のケース in tests/unit/test_models_tools.py
- [X] T002 [P] [US1] モデルテスト作成: `has_next=False`のケース in tests/unit/test_models_tools.py
- [X] T003 [P] [US1] モデルテスト作成: 境界条件（空結果、ちょうどlimit件）in tests/unit/test_models_tools.py
- [X] T004 [P] [US1] コントラクトテスト更新: `get_stats_data`のページネーションフィールド検証 in tests/contract/test_mcp_tools.py
- [X] T005 [P] [US1] コントラクトテスト更新: `get_dataset_data`のページネーションフィールド検証 in tests/contract/test_mcp_tools.py

### Implementation for User Story 1 (TDD: Green Phase)

- [X] T006 [US1] `StatsDataResult`モデルに`has_next: bool`フィールド追加 in src/e_stat_mcp/models/tools.py
- [X] T007 [US1] `StatsDataResult`モデルに`next_start_position: int | None`フィールド追加 in src/e_stat_mcp/models/tools.py
- [X] T008 [US1] `StatsDataResult`のdocstring更新（ページネーション説明追加）in src/e_stat_mcp/models/tools.py
- [X] T009 [US1] `get_stats_data`ツールにページネーション計算ロジック追加 in src/e_stat_mcp/server.py
- [X] T010 [US1] `get_dataset_data`ツールにページネーション計算ロジック追加 in src/e_stat_mcp/server.py
- [X] T011 [US1] `get_stats_data`のdocstringにページネーション使用例追加 in src/e_stat_mcp/server.py
- [X] T012 [US1] `get_dataset_data`のdocstringにページネーション使用例追加 in src/e_stat_mcp/server.py

**Checkpoint**: User Story 1完了 - 全テストがパスし、ページネーション情報が正しく返却される

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: 品質確認と最終検証

- [X] T013 型チェック実行: `uv run mypy .` でエラーがないことを確認
- [X] T014 Lint実行: `uv run ruff check .` でエラーがないことを確認
- [X] T015 フォーマット確認: `uv run ruff format --check .` で整形済みであることを確認
- [X] T016 全テスト実行: `uv run pytest` で全テストがパスすることを確認（既存の無関係なテスト2件の失敗を除く）

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: スキップ（既存プロジェクト）
- **Phase 2 (Foundational)**: スキップ（既存インフラ使用）
- **Phase 3 (User Story 1)**: 即座に開始可能
- **Phase 4 (Polish)**: Phase 3完了後に実行

### Within User Story 1

1. **テスト作成 (T001-T005)**: 並列実行可能（異なるテストケース）
2. **テスト失敗確認**: 全テストが失敗することを確認（Red Phase）
3. **モデル変更 (T006-T008)**: 順次実行（同一ファイル）
4. **サーバー変更 (T009-T012)**: T006-T008完了後、順次実行（同一ファイル）
5. **テスト成功確認**: 全テストがパスすることを確認（Green Phase）

### Parallel Opportunities

```bash
# テスト作成は並列実行可能（異なるテストケース）:
Task T001: モデルテスト - has_next=True
Task T002: モデルテスト - has_next=False
Task T003: モデルテスト - 境界条件
Task T004: コントラクトテスト - get_stats_data
Task T005: コントラクトテスト - get_dataset_data

# 品質チェックは並列実行可能:
Task T013: mypy
Task T014: ruff check
Task T015: ruff format --check
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. テスト作成（T001-T005）→ 失敗確認
2. モデル変更（T006-T008）
3. サーバー変更（T009-T012）
4. テスト成功確認
5. 品質チェック（T013-T016）

### Incremental Delivery

本機能は単一ユーザーストーリーのため、Phase 3完了で機能完成。

---

## Summary

| カテゴリ | タスク数 |
|---------|---------|
| テスト作成 | 5 |
| 実装 | 7 |
| 品質チェック | 4 |
| **合計** | **16** |

### User Story Coverage

| ユーザーストーリー | タスク数 | タスクID |
|------------------|---------|---------|
| US1 - ページネーションによる連続データ取得 | 12 | T001-T012 |

### Files Modified

| ファイル | 変更内容 |
|----------|----------|
| `src/e_stat_mcp/models/tools.py` | `StatsDataResult`に2フィールド追加、docstring更新 |
| `src/e_stat_mcp/server.py` | 計算ロジック追加、docstring改善 |
| `tests/unit/test_models_tools.py` | モデルテスト追加 |
| `tests/contract/test_mcp_tools.py` | コントラクトテスト更新 |

---

## Notes

- [P] tasks = 異なるファイルまたはテストケース、依存関係なし
- [US1] = User Story 1に属するタスク
- TDDアプローチ: テスト作成 → 失敗確認 → 実装 → 成功確認
- 既存プロジェクトへの増分変更のため、Setup/Foundationalフェーズはスキップ
- 品質チェック（mypy, ruff, pytest）は必須
