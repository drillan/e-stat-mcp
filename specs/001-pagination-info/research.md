# Research: ページネーション情報の追加

**Feature Branch**: `001-pagination-info`
**Date**: 2026-01-11

## Overview

本機能は既存実装への増分変更であり、新しい技術選定は不要。e-Stat APIのページネーション仕様と既存実装の確認のみ。

## 1. e-Stat APIページネーション仕様

### 確認結果

e-Stat API 3.0のページネーションパラメータ:

| パラメータ | 説明 | デフォルト |
|-----------|------|-----------|
| `limit` | 取得件数上限 | 10,000（最大100,000） |
| `startPosition` | 取得開始位置 | 1（1-indexed） |

### レスポンスフィールド

APIレスポンスに含まれるページネーション関連情報:

```json
{
  "GET_STATS_DATA": {
    "RESULT": {
      "TOTAL_NUMBER": 150000,     // 総件数
      "FROM_NUMBER": 1,           // 開始位置
      "TO_NUMBER": 10000          // 終了位置
    }
  }
}
```

### 計算式の検証

- `returned_count = TO_NUMBER - FROM_NUMBER + 1`
- `has_next = (start_position + returned_count - 1) < total_count`
  - 例: start_position=1, returned_count=10000, total_count=150000
  - `(1 + 10000 - 1) = 10000 < 150000` → `has_next = true`
- `next_start_position = start_position + returned_count`
  - 例: `1 + 10000 = 10001`

## 2. 既存実装の確認

### StatsDataResult（現在）

```python
class StatsDataResult(BaseModel):
    """統計データ取得結果."""
    total_count: int = Field(..., description="総データ件数")
    returned_count: int = Field(..., description="今回返却した件数")
    data: list[StatsDataItem] = Field(..., description="統計データリスト")
```

### 変更後

```python
class StatsDataResult(BaseModel):
    """統計データ取得結果."""
    total_count: int = Field(..., description="総データ件数")
    returned_count: int = Field(..., description="今回返却した件数")
    data: list[StatsDataItem] = Field(..., description="統計データリスト")
    has_next: bool = Field(..., description="次ページが存在するかどうか")
    next_start_position: int | None = Field(
        None,
        description="次回使用すべきstart_position（次ページがない場合はNone）"
    )
```

## 3. 影響範囲

### 変更が必要なファイル

| ファイル | 変更内容 |
|----------|----------|
| `src/e_stat_mcp/models/tools.py` | `StatsDataResult`に2フィールド追加 |
| `src/e_stat_mcp/server.py` | `get_stats_data`, `get_dataset_data`のレスポンス計算とdocstring改善 |
| `tests/unit/test_models_tools.py` | モデルのユニットテスト追加 |
| `tests/contract/test_mcp_tools.py` | コントラクトテスト更新 |

### 変更が不要なファイル

- `src/e_stat_mcp/client.py` - APIクライアントは既に`total_count`と`returned_count`を返却
- `src/e_stat_mcp/models/api.py` - APIレスポンスモデルの変更なし

## 4. 後方互換性

### 考慮事項

- 新フィールドの追加のみ（既存フィールドの変更なし）
- JSONシリアライズ時に新フィールドが追加される
- 既存のMCPクライアントは新フィールドを無視するか、追加情報として利用可能

### 結論

後方互換性の問題なし。

## Decisions Summary

| 決定事項 | 選択 | 根拠 |
|----------|------|------|
| フィールド設計 | `has_next: bool` + `next_start_position: int \| None` | LLMが理解しやすい明示的なフィールド |
| 計算ロジック | 標準計算式 | e-Stat APIは1-indexed |
| 後方互換性 | 維持 | 新フィールド追加のみ |
