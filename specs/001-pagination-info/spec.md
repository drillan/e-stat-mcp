# Feature Specification: ページネーション情報の追加

**Feature Branch**: `001-pagination-info`
**Created**: 2026-01-11
**Status**: Draft
**Input**: GitHub Issue #1: "10万件上限に対応したページネーション情報の追加"
**Base Spec**: `specs/000-e-stat-mcp/spec.md`

## Overview

e-Stat APIはデータ取得件数の上限が10万件に設定されている。現在の実装では`total_count`と`returned_count`を返しているが、LLMが次のリクエストを理解しやすくするための情報が不足している。本機能追加により、ページネーションを使いやすくし、大量データ取得時のユーザー体験を改善する。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - ページネーションによる連続データ取得 (Priority: P1)

ユーザーとして、大量データを取得する際に、次のページが存在するかと次の開始位置を明確に知りたい。

**Why this priority**: 10万件上限を超えるデータの取得はよくあるユースケースであり、LLMが自動的にページングを理解できることが重要。

**Independent Test**: 総件数がlimitを超えるデータを取得し、`has_next`と`next_start_position`が正しく返却されることを確認する。

**Acceptance Scenarios**:

1. **Given** 総件数がlimitを超えるデータを取得する状態, **When** `get_stats_data`でデータを取得する, **Then** `has_next=true`と正しい`next_start_position`が返却される
2. **Given** 総件数がlimit以下のデータを取得する状態, **When** `get_stats_data`でデータを取得する, **Then** `has_next=false`と`next_start_position=None`が返却される
3. **Given** `has_next=true`のレスポンスを受け取った状態, **When** `next_start_position`を使って次のリクエストを送信する, **Then** 続きのデータが取得できる
4. **Given** 総件数がlimitを超えるデータセットを取得する状態, **When** `get_dataset_data`でデータを取得する, **Then** `has_next`と`next_start_position`が正しく返却される

---

### Edge Cases

| ケース | 挙動 | 期待値 |
|--------|------|--------|
| 最終ページ取得時 | `has_next=false`, `next_start_position=None` | 次ページなしを明示 |
| 空の結果 | `has_next=false`, `next_start_position=None`, `returned_count=0` | 次ページなし |
| ちょうどlimit件 | 次ページの有無を`total_count`と比較して判定 | 正確な判定 |

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `get_stats_data`のレスポンスに`has_next: bool`フィールドを追加しなければならない
- **FR-002**: `get_stats_data`のレスポンスに`next_start_position: int | None`フィールドを追加しなければならない
- **FR-003**: `get_dataset_data`のレスポンスに`has_next: bool`フィールドを追加しなければならない
- **FR-004**: `get_dataset_data`のレスポンスに`next_start_position: int | None`フィールドを追加しなければならない
- **FR-005**: `has_next`は`(start_position + returned_count - 1) < total_count`で計算しなければならない
- **FR-006**: `next_start_position`は`has_next`がtrueの場合のみ`start_position + returned_count`を返却し、falseの場合は`None`を返却しなければならない
- **FR-007**: `get_stats_data`と`get_dataset_data`のdocstringにページネーションの使用例を含む詳細な案内を記載しなければならない

### Key Entities

- **StatsDataResult**: 統計データ取得のレスポンスモデル
  - `total_count: int` - 総件数
  - `returned_count: int` - 今回返却した件数
  - `data: list[StatsDataItem]` - 統計データリスト
  - `has_next: bool` - 次ページ存在フラグ（追加）
  - `next_start_position: int | None` - 次ページ開始位置（追加）

### Modified Files

- `src/e_stat_mcp/models/tools.py` - StatsDataResultモデル拡張
- `src/e_stat_mcp/server.py` - レスポンス計算ロジック追加、docstring改善
- `tests/unit/test_models_tools.py` - モデルテスト追加
- `tests/contract/test_mcp_tools.py` - コントラクトテスト更新

## Assumptions

- 既存の`StatsDataResult`モデルが存在し、`total_count`、`returned_count`、`data`フィールドを持つ
- `start_position`パラメータはデフォルト値1を持つ（1-indexed）
- e-Stat APIの10万件上限は変更されない

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `StatsDataResult`に`has_next`と`next_start_position`フィールドが追加されている
- **SC-002**: 次ページ情報が正しく計算されている（ユニットテストでカバー）
- **SC-003**: docstringにページネーションの使用方法が記載されている
- **SC-004**: 全テストがパスする
- **SC-005**: 型チェック（mypy）がパスする
