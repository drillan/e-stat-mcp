# Data Model: ページネーション情報の追加

**Feature Branch**: `001-pagination-info`
**Date**: 2026-01-11

## Model Changes

### StatsDataResult（変更）

**ファイル**: `src/e_stat_mcp/models/tools.py`

#### 現在の定義

```python
class StatsDataResult(BaseModel):
    """統計データ取得結果."""

    total_count: int = Field(..., description="総データ件数")
    returned_count: int = Field(..., description="今回返却した件数")
    data: list[StatsDataItem] = Field(..., description="統計データリスト")
```

#### 変更後の定義

```python
class StatsDataResult(BaseModel):
    """統計データ取得結果.

    ページネーション:
        データが複数ページにわたる場合、has_nextがTrueになります。
        次のページを取得するには、next_start_positionの値を
        start_positionパラメータに指定して再度呼び出してください。
    """

    total_count: int = Field(..., description="総データ件数")
    returned_count: int = Field(..., description="今回返却した件数")
    data: list[StatsDataItem] = Field(..., description="統計データリスト")
    has_next: bool = Field(..., description="次ページが存在するかどうか")
    next_start_position: int | None = Field(
        None,
        description="次回使用すべきstart_position（次ページがない場合はNone）",
    )
```

### フィールド詳細

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `total_count` | `int` | Yes | 総データ件数 |
| `returned_count` | `int` | Yes | 今回返却した件数 |
| `data` | `list[StatsDataItem]` | Yes | 統計データリスト |
| `has_next` | `bool` | Yes | 次ページが存在するかどうか（**新規**） |
| `next_start_position` | `int \| None` | Yes | 次回使用すべきstart_position（**新規**） |

### 計算ロジック

`StatsDataResult`の生成時に以下の計算を行う:

```python
def create_stats_data_result(
    total_count: int,
    returned_count: int,
    data: list[StatsDataItem],
    start_position: int = 1,
) -> StatsDataResult:
    """StatsDataResultを生成する.

    Args:
        total_count: 総データ件数
        returned_count: 今回返却した件数
        data: 統計データリスト
        start_position: 取得開始位置（デフォルト: 1）

    Returns:
        ページネーション情報を含むStatsDataResult
    """
    has_next = (start_position + returned_count - 1) < total_count
    next_start_position = start_position + returned_count if has_next else None

    return StatsDataResult(
        total_count=total_count,
        returned_count=returned_count,
        data=data,
        has_next=has_next,
        next_start_position=next_start_position,
    )
```

## Validation Rules

### has_next

- `True`: 次のページが存在する
- `False`: これが最後のページ

### next_start_position

- `has_next=True`の場合: 次のリクエストで使用すべき`start_position`の値
- `has_next=False`の場合: `None`

### 境界条件

| ケース | total_count | start_position | returned_count | has_next | next_start_position |
|--------|-------------|----------------|----------------|----------|---------------------|
| 最初のページ（続きあり） | 25000 | 1 | 10000 | True | 10001 |
| 2ページ目（続きあり） | 25000 | 10001 | 10000 | True | 20001 |
| 最終ページ | 25000 | 20001 | 5000 | False | None |
| 1ページで完結 | 5000 | 1 | 5000 | False | None |
| 空の結果 | 0 | 1 | 0 | False | None |
| ちょうどlimit件 | 10000 | 1 | 10000 | False | None |

## JSON Schema

```json
{
  "type": "object",
  "properties": {
    "total_count": {
      "type": "integer",
      "description": "総データ件数"
    },
    "returned_count": {
      "type": "integer",
      "description": "今回返却した件数"
    },
    "data": {
      "type": "array",
      "items": { "$ref": "#/$defs/StatsDataItem" },
      "description": "統計データリスト"
    },
    "has_next": {
      "type": "boolean",
      "description": "次ページが存在するかどうか"
    },
    "next_start_position": {
      "type": ["integer", "null"],
      "description": "次回使用すべきstart_position（次ページがない場合はnull）"
    }
  },
  "required": ["total_count", "returned_count", "data", "has_next", "next_start_position"]
}
```

## Example Responses

### 次ページあり

```json
{
  "total_count": 150000,
  "returned_count": 10000,
  "data": [...],
  "has_next": true,
  "next_start_position": 10001
}
```

### 最終ページ

```json
{
  "total_count": 150000,
  "returned_count": 5000,
  "data": [...],
  "has_next": false,
  "next_start_position": null
}
```

### 1ページで完結

```json
{
  "total_count": 500,
  "returned_count": 500,
  "data": [...],
  "has_next": false,
  "next_start_position": null
}
```
