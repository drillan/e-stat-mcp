# コントリビューション

e-Stat MCP サーバーへの貢献方法を解説します。

## 開発環境のセットアップ

### 必要なツール

- Python 3.13 以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー
- Git

### セットアップ手順

```bash
# リポジトリをフォーク & クローン
git clone https://github.com/YOUR_USERNAME/e-stat-mcp.git
cd e-stat-mcp

# 開発用依存関係を含めてインストール
uv sync --all-extras

# 環境変数を設定（テスト用）
export E_STAT_APP_ID="your_app_id"
```

## コーディング規約

### スタイルガイド

以下のツールでコード品質を管理：

| ツール | 用途 |
|--------|------|
| ruff | Linter & Formatter |
| mypy | 静的型チェック |

### コード品質チェック

```bash
# Linter
uv run ruff check .

# Linter（自動修正）
uv run ruff check --fix .

# フォーマッター
uv run ruff format .

# 型チェック
uv run mypy .

# すべてのチェック
uv run ruff check . && uv run ruff format --check . && uv run mypy .
```

### 型アノテーション

すべての関数、メソッド、変数に型アノテーションを付与：

```python
# 良い例
def search_stats(
    keyword: str | None = None,
    limit: int = 100,
) -> list[SearchStatsResult]:
    ...

# 悪い例
def search_stats(keyword=None, limit=100):
    ...
```

### Docstring

Google スタイルの docstring を使用：

```python
def search_stats(
    keyword: str | None = None,
    limit: int = 100,
) -> list[SearchStatsResult]:
    """統計表を検索します。

    Args:
        keyword: 検索キーワード。
        limit: 取得件数上限。

    Returns:
        検索結果のリスト。

    Raises:
        EStatApiError: API呼び出しに失敗した場合。
    """
    ...
```

## テスト

### テストの実行

```bash
# すべてのテスト
uv run pytest

# 単体テストのみ
uv run pytest -m "not integration and not contract"

# 統合テスト（要 E_STAT_APP_ID）
uv run pytest -m integration

# コントラクトテスト
uv run pytest -m contract

# カバレッジ付き
uv run pytest --cov=e_stat_mcp --cov-report=html
```

### テストの構成

```
tests/
├── unit/                # 単体テスト（モック使用）
│   ├── test_cache.py
│   ├── test_client.py
│   ├── test_models_api.py
│   ├── test_models_errors.py
│   ├── test_models_tools.py
│   └── test_settings.py
├── integration/         # 統合テスト（実API使用）
│   └── test_e_stat_api.py
└── contract/           # コントラクトテスト
    └── test_mcp_tools.py
```

### テストの書き方

```python
import pytest
from e_stat_mcp.models.api import StatsTable

class TestStatsTable:
    """StatsTable モデルのテスト"""

    def test_parse_valid_data(self) -> None:
        """正常なデータをパースできること"""
        data = {
            "@id": "0003410379",
            "STAT_NAME": "国勢調査",
            "GOV_ORG": "総務省",
            "TITLE": "都道府県別人口",
        }
        table = StatsTable.model_validate(data)
        assert table.id == "0003410379"
        assert table.stat_name == "国勢調査"

    def test_parse_missing_required_field(self) -> None:
        """必須フィールドが欠けている場合にエラーになること"""
        data = {"@id": "0003410379"}
        with pytest.raises(ValidationError):
            StatsTable.model_validate(data)
```

## プルリクエスト

### ブランチ命名規則

- 機能追加: `feature/description`
- バグ修正: `fix/description`
- ドキュメント: `docs/description`
- リファクタリング: `refactor/description`

### コミットメッセージ

```
<type>: <description>

[optional body]
```

タイプ:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `refactor`: リファクタリング
- `test`: テスト
- `chore`: その他

例:
```
feat: add pagination support to search_stats

- Add limit and start_position parameters
- Update tests for new parameters
```

### PR の作成

1. フォークからブランチを作成
2. 変更を実装
3. テストを追加・更新
4. すべてのチェックをパス
5. PR を作成

```bash
# ブランチを作成
git checkout -b feature/new-feature

# 変更をコミット
git add .
git commit -m "feat: add new feature"

# プッシュ
git push origin feature/new-feature

# GitHub で PR を作成
```

### PR チェックリスト

- [ ] すべてのテストがパス
- [ ] `ruff check` がパス
- [ ] `ruff format --check` がパス
- [ ] `mypy` がパス
- [ ] ドキュメントを更新（必要な場合）
- [ ] 変更内容を説明

## 新機能の追加

### 1. 仕様の確認

`specs/` ディレクトリで仕様を確認または作成。

### 2. テストの作成

TDD（テスト駆動開発）を推奨：

```python
def test_new_feature() -> None:
    """新機能のテスト"""
    # まずテストを書く（失敗する）
    result = new_feature()
    assert result == expected
```

### 3. 実装

テストがパスするように実装。

### 4. ドキュメント

必要に応じてドキュメントを更新：

- API の場合: docstring を記載（autodoc で自動生成される）
- ツールの場合: `docs/tools/` にドキュメントを追加

## 質問・サポート

- **Issue**: バグ報告や機能リクエスト
- **Discussion**: 質問や議論

## ライセンス

貢献されたコードは MIT License の下で公開されます。
