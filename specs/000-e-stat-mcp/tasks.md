# Tasks: e-Stat API連携MCPサーバー

**Input**: Design documents from `/specs/001-e-stat-mcp/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/mcp-tools.yaml ✅

**Tests**: テスト駆動開発（TDD）に従い、各フェーズでテストを先に作成する。

**Organization**: タスクはユーザーストーリー単位でグループ化し、独立した実装とテストを可能にする。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 所属するユーザーストーリー（US1, US2, US3, US4, US5）

## Path Conventions

- **Single project**: `src/e_stat_mcp/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: プロジェクトの初期化と基本構造の作成

- [X] T001 Create project structure per implementation plan (`src/e_stat_mcp/`, `tests/`)
- [X] T002 Initialize Python project with uv and dependencies in pyproject.toml
- [X] T003 [P] Configure ruff (linting/formatting) in pyproject.toml
- [X] T004 [P] Configure mypy (type checking) in pyproject.toml
- [X] T005 [P] Configure pytest in pyproject.toml
- [X] T006 Create package `__init__.py` files in src/e_stat_mcp/ and src/e_stat_mcp/models/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: すべてのユーザーストーリーの前提となるコアインフラストラクチャ

**⚠️ CRITICAL**: このフェーズが完了するまで、ユーザーストーリーの作業は開始できない

### Tests for Foundational

- [X] T007 [P] Unit test for Settings model in tests/unit/test_settings.py
- [X] T008 [P] Unit test for API response models in tests/unit/test_models_api.py
- [X] T009 [P] Unit test for error models in tests/unit/test_models_errors.py
- [X] T010 [P] Unit test for cache module in tests/unit/test_cache.py

### Implementation for Foundational

- [X] T011 [P] Create Settings model with pydantic-settings in src/e_stat_mcp/settings.py
- [X] T012 [P] Create API result models (ApiResult, EStatErrorCode, EStatError) in src/e_stat_mcp/models/errors.py
- [X] T013 [P] Create StatsTable and StatsListResponse models in src/e_stat_mcp/models/api.py
- [X] T014 [P] Create ClassItem, ClassInfo, MetaInfoResponse models in src/e_stat_mcp/models/api.py
- [X] T015 [P] Create DataValue, StatsDataResponse models in src/e_stat_mcp/models/api.py
- [X] T016 [P] Create DatasetInfo, DatasetListResponse models in src/e_stat_mcp/models/api.py
- [X] T017 Create cache module with TTLCache in src/e_stat_mcp/cache.py
- [X] T018 Create base e-Stat API client with httpx in src/e_stat_mcp/client.py (HTTP connection, auth, retry, timeout)
- [X] T019 Export models from src/e_stat_mcp/models/__init__.py

**Checkpoint**: 基盤準備完了 - ユーザーストーリーの実装を並列で開始可能

---

## Phase 3: User Story 5 - APIキーの設定 (Priority: P1) 🎯 MVP

**Goal**: ユーザーがe-StatアプリケーションIDをMCPサーバーに設定してAPIを利用できる

**Independent Test**: アプリケーションIDを設定し、APIリクエストが正常に認証されることを確認

**Why First**: 他のすべてのAPI機能が認証に依存するため、最初に実装

### Tests for User Story 5

- [X] T020 [P] [US5] Unit test for Settings validation (valid/invalid/missing appId) in tests/unit/test_settings.py (extend)
- [X] T021 [P] [US5] Integration test for API authentication in tests/integration/test_e_stat_api.py

### Implementation for User Story 5

- [X] T022 [US5] Implement Settings loading and validation in src/e_stat_mcp/settings.py (extend with get_settings())
- [X] T023 [US5] Implement authentication error handling in src/e_stat_mcp/client.py (auth error → descriptive message)
- [X] T024 [US5] Implement missing appId error handling in src/e_stat_mcp/client.py
- [X] T025 [US5] Create MCP server entry point with Settings in src/e_stat_mcp/server.py
- [X] T026 [US5] Create __main__.py entry point in src/e_stat_mcp/__main__.py

**Checkpoint**: 設定完了 - MCPサーバーが起動し、認証が動作する

---

## Phase 4: User Story 1 - 統計データの検索 (Priority: P1)

**Goal**: キーワードで統計表を検索し、一覧を取得できる

**Independent Test**: キーワードを指定して統計表を検索し、統計表ID・名称・調査年等の一覧が返却される

### Tests for User Story 1

- [X] T027 [P] [US1] Unit test for SearchStatsRequest/SearchStatsResult models in tests/unit/test_models_tools.py
- [X] T028 [P] [US1] Contract test for search_stats tool in tests/contract/test_mcp_tools.py
- [X] T029 [US1] Integration test for getStatsList API in tests/integration/test_e_stat_api.py (extend)

### Implementation for User Story 1

- [X] T030 [P] [US1] Create SearchStatsRequest, SearchStatsResult models in src/e_stat_mcp/models/tools.py
- [X] T031 [US1] Implement getStatsList API call in src/e_stat_mcp/client.py
- [X] T032 [US1] Add caching for getStatsList in src/e_stat_mcp/client.py
- [X] T033 [US1] Implement search_stats MCP tool in src/e_stat_mcp/server.py

**Checkpoint**: 検索機能完了 - キーワードで統計表を検索可能

---

## Phase 5: User Story 2 - 統計データの取得 (Priority: P1)

**Goal**: 統計表IDを指定して統計データ（数値データ）を取得できる

**Independent Test**: 統計表IDを指定してデータを取得し、表章事項・分類事項・数値データが構造化された形式で返却される

### Tests for User Story 2

- [X] T034 [P] [US2] Unit test for GetStatsDataRequest/StatsDataItem models in tests/unit/test_models_tools.py (extend)
- [X] T035 [P] [US2] Contract test for get_stats_data tool in tests/contract/test_mcp_tools.py (extend)
- [X] T036 [US2] Integration test for getStatsData API in tests/integration/test_e_stat_api.py (extend)

### Implementation for User Story 2

- [X] T037 [P] [US2] Create GetStatsDataRequest, StatsDataItem models in src/e_stat_mcp/models/tools.py (extend)
- [X] T038 [US2] Implement getStatsData API call in src/e_stat_mcp/client.py
- [X] T039 [US2] Add caching for getStatsData in src/e_stat_mcp/client.py
- [X] T040 [US2] Implement data transformation (code → name mapping) in src/e_stat_mcp/client.py
- [X] T041 [US2] Implement get_stats_data MCP tool in src/e_stat_mcp/server.py

**Checkpoint**: データ取得機能完了 - 統計表IDを指定してデータを取得可能

---

## Phase 6: User Story 3 - 統計表のメタ情報取得 (Priority: P2)

**Goal**: 統計表の詳細情報（どのような項目・分類があるか等）を事前に確認できる

**Independent Test**: 統計表IDを指定してメタ情報を取得し、表章事項・分類事項・地域事項等の情報が返却される

### Tests for User Story 3

- [X] T042 [P] [US3] Unit test for GetMetaInfoRequest/MetaInfoResult models in tests/unit/test_models_tools.py (extend)
- [X] T043 [P] [US3] Contract test for get_meta_info tool in tests/contract/test_mcp_tools.py (extend)
- [X] T044 [US3] Integration test for getMetaInfo API in tests/integration/test_e_stat_api.py (extend)

### Implementation for User Story 3

- [X] T045 [P] [US3] Create GetMetaInfoRequest, ClassItemInfo, MetaInfoResult models in src/e_stat_mcp/models/tools.py (extend)
- [X] T046 [US3] Implement getMetaInfo API call in src/e_stat_mcp/client.py
- [X] T047 [US3] Add caching for getMetaInfo in src/e_stat_mcp/client.py
- [X] T048 [US3] Implement get_meta_info MCP tool in src/e_stat_mcp/server.py

**Checkpoint**: メタ情報取得機能完了 - 統計表の構造を事前確認可能

---

## Phase 7: User Story 4 - 公開データセットの参照 (Priority: P2)

**Goal**: 公開データセットを参照し、それを使って効率的に統計データを取得できる

**Independent Test**: 公開データセットの一覧を取得し、データセットIDを使って統計データを取得できる

### Tests for User Story 4

- [X] T049 [P] [US4] Unit test for ListDatasetsRequest/DatasetResult models in tests/unit/test_models_tools.py (extend)
- [X] T050 [P] [US4] Contract test for list_datasets/get_dataset_data tools in tests/contract/test_mcp_tools.py (extend)
- [X] T051 [US4] Integration test for refDataset API in tests/integration/test_e_stat_api.py (extend)

### Implementation for User Story 4

- [X] T052 [P] [US4] Create ListDatasetsRequest, DatasetResult models in src/e_stat_mcp/models/tools.py (extend)
- [X] T053 [US4] Implement refDataset API call (list datasets) in src/e_stat_mcp/client.py
- [X] T054 [US4] Implement refDataset API call (get dataset data) in src/e_stat_mcp/client.py
- [X] T055 [US4] Add caching for refDataset in src/e_stat_mcp/client.py
- [X] T056 [US4] Implement list_datasets MCP tool in src/e_stat_mcp/server.py
- [X] T057 [US4] Implement get_dataset_data MCP tool in src/e_stat_mcp/server.py

**Checkpoint**: データセット参照機能完了 - 公開データセットを活用可能

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 複数のユーザーストーリーに影響する改善

- [X] T058 Add logging configuration in src/e_stat_mcp/server.py
- [X] T059 [P] Improve error messages for all API errors in src/e_stat_mcp/client.py
- [X] T060 [P] Add pagination handling for large result sets in src/e_stat_mcp/client.py
- [ ] T061 Run and verify quickstart.md scenarios manually
- [X] T062 Run full quality check: `uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし - 即座に開始可能
- **Foundational (Phase 2)**: Setup完了後 - すべてのユーザーストーリーをブロック
- **User Story 5 (Phase 3)**: Foundational完了後 - 認証基盤
- **User Story 1 (Phase 4)**: Foundational完了後 - US5と並列可能だが、認証テストのためUS5を先に推奨
- **User Story 2 (Phase 5)**: Foundational完了後 - US1と独立
- **User Story 3 (Phase 6)**: Foundational完了後 - US2から分類コードを使うためUS2と連携するが独立してテスト可能
- **User Story 4 (Phase 7)**: Foundational完了後 - 独立
- **Polish (Phase 8)**: すべてのユーザーストーリー完了後

### User Story Dependencies

- **User Story 5 (P1)**: Foundational完了後すぐに開始 - 他のストーリーの前提
- **User Story 1 (P1)**: US5完了後 - 認証が動作することが前提
- **User Story 2 (P1)**: US5完了後 - US1と並列可能（ただしUS1で見つけたIDを使うのが典型的なフロー）
- **User Story 3 (P2)**: US5完了後 - US2と並列可能
- **User Story 4 (P2)**: US5完了後 - US3と並列可能

### Within Each User Story

- テストを先に作成し、FAILすることを確認（TDD Red Phase）
- モデル → クライアント → サーバー（ツール）の順で実装
- ストーリー完了後に次の優先度へ移行

### Parallel Opportunities

- Setup内: T003, T004, T005 は並列実行可能
- Foundational内: T007-T010（テスト）、T011-T016（モデル）は並列実行可能
- US1, US2, US3, US4 はFoundational完了後、並列で開始可能（ただしUS5が先に完了していることを推奨）
- 各ストーリー内の[P]タスクは並列実行可能

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for SearchStatsRequest/SearchStatsResult in tests/unit/test_models_tools.py"
Task: "Contract test for search_stats tool in tests/contract/test_mcp_tools.py"

# Launch all models together:
Task: "Create SearchStatsRequest, SearchStatsResult in src/e_stat_mcp/models/tools.py"
```

---

## Implementation Strategy

### MVP First (User Story 5 + 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - すべてのストーリーをブロック)
3. Complete Phase 3: User Story 5 (設定・認証)
4. Complete Phase 4: User Story 1 (検索)
5. **STOP and VALIDATE**: US5 + US1を独立テスト
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational 完了 → 基盤準備完了
2. US5 追加 → 独立テスト → 認証動作確認
3. US1 追加 → 独立テスト → 検索機能デモ（MVP!）
4. US2 追加 → 独立テスト → データ取得機能デモ
5. US3 追加 → 独立テスト → メタ情報取得機能デモ
6. US4 追加 → 独立テスト → データセット参照機能デモ
7. 各ストーリーは既存機能を壊さずに価値を追加

### Recommended Execution Order (Single Developer)

1. Phase 1 → Phase 2 → Phase 3 (US5) → Phase 4 (US1) → **MVP達成**
2. Phase 5 (US2) → Phase 6 (US3) → **コアAPI完了**
3. Phase 7 (US4) → Phase 8 → **全機能完了**

---

## Summary

| Phase | Story | Task Count | Parallel Tasks |
|-------|-------|------------|----------------|
| Phase 1: Setup | - | 6 | 3 |
| Phase 2: Foundational | - | 13 | 10 |
| Phase 3: US5 | 設定 | 7 | 2 |
| Phase 4: US1 | 検索 | 7 | 3 |
| Phase 5: US2 | データ取得 | 8 | 3 |
| Phase 6: US3 | メタ情報 | 7 | 3 |
| Phase 7: US4 | データセット | 9 | 3 |
| Phase 8: Polish | - | 5 | 2 |
| **Total** | | **62** | **29** |

### MVP Scope

- Phase 1-4 完了時点（Setup + Foundational + US5 + US1）= 33タスク
- 統計表の検索機能が動作するMCPサーバー

---

## Notes

- [P]タスク = 異なるファイル、依存関係なし
- [Story]ラベル = 特定のユーザーストーリーへのトレーサビリティ
- 各ユーザーストーリーは独立して完了・テスト可能
- 実装前にテストがFAILすることを確認（TDD）
- タスクまたは論理グループごとにコミット
- 任意のチェックポイントで停止し、ストーリーを独立検証可能
- 避けること: 曖昧なタスク、同一ファイルの競合、独立性を損なうストーリー間依存
