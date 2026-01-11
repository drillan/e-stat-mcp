# Research: e-Stat API連携MCPサーバー

**Branch**: `001-e-stat-mcp` | **Date**: 2026-01-07

## 技術選定

### MCP Python SDK

**Decision**: `mcp[cli]` パッケージを使用（FastMCPクラス）

**Rationale**:
- Anthropic公式のPython SDKであり、フル仕様を実装
- FastMCPクラスにより型ヒントとdocstringからツール定義を自動生成
- Pydanticモデルとのネイティブ連携をサポート
- uvによるプロジェクト管理との親和性が高い

**Alternatives considered**:
- TypeScript SDK: Node.js環境が必要、Pythonプロジェクトとの整合性低
- 自前実装: 仕様準拠の保証が困難、メンテナンスコスト増

### データバリデーション

**Decision**: Pydanticを必須とし、すべての入出力データをバリデーション

**Rationale**:
- MCPのFastMCPはPydantic BaseModelとネイティブに連携
- 型安全性を確保し、APIレスポンスの構造を保証
- ランタイムバリデーションによりe-Stat APIの不正レスポンスを早期検出
- ドキュメント自動生成（JSON Schema）が可能

**Alternatives considered**:
- dataclasses: バリデーション機能なし、型安全性が不十分
- TypedDict: ランタイムバリデーションなし
- attrs: Pydanticほどエコシステムが充実していない

### HTTPクライアント

**Decision**: `httpx` を使用

**Rationale**:
- async/await対応でMCPの非同期ツールと相性が良い
- リトライ、タイムアウト設定が容易
- 型ヒントが充実

**Alternatives considered**:
- requests: 同期のみ、非同期対応が弱い
- aiohttp: 十分だが、httpxの方がAPIがシンプル

### キャッシュ

**Decision**: `cachetools` によるインメモリTTLキャッシュ

**Rationale**:
- 軽量でPoC向け
- TTL（Time-To-Live）設定が容易
- 外部依存なし（Redis等不要）

**Alternatives considered**:
- Redis: オーバースペック、運用負荷増
- ファイルキャッシュ: 複雑性増、パフォーマンス不明

## e-Stat API 3.0仕様

### エンドポイント

| API | URL（JSON形式） | HTTPメソッド |
|-----|-----------------|--------------|
| getStatsList | `https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList` | GET |
| getMetaInfo | `https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo` | GET |
| getStatsData | `https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData` | GET |
| refDataset | `https://api.e-stat.go.jp/rest/3.0/app/json/refDataset` | GET |

### 認証

- パラメータ名: `appId`
- 取得方法: e-Statでユーザー登録後、アプリケーションIDを発行

### レスポンス構造

```json
{
  "GET_STATS_LIST": {
    "RESULT": {
      "STATUS": 0,
      "ERROR_MSG": "正常に終了しました",
      "DATE": "2026-01-07T12:00:00.000+09:00"
    },
    "PARAMETER": { ... },
    "DATALIST_INF": { ... }
  }
}
```

- XML属性は`@`プレフィックス
- テキスト値は`$`キー

### エラーコード

| コード | HTTPステータス | 説明 |
|--------|----------------|------|
| 0 | 200 | 正常終了 |
| 1 | 200 | 該当データなし |
| 100 | 403 | 認証エラー |
| 101 | 400 | 必須パラメータ未指定 |
| 102 | 400 | パラメータ値不正 |
| 300 | 400 | 指定データ存在しない |

### 制約

- カンマ区切りコード指定: 最大100個
- 一括取得行数上限: 100,000件
- デフォルト取得件数: 10,000件（limit省略時）

## MCP実装パターン

### ツール定義

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP(name="e-stat", json_response=True)

class SearchResult(BaseModel):
    table_id: str
    table_name: str
    survey_year: str

@mcp.tool()
async def search_stats(keyword: str) -> list[SearchResult]:
    """キーワードで統計表を検索"""
    ...
```

### ログ出力

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# STDIOトランスポート使用時はstdoutに書かない
logger.info("Processing request")  # OK
print("Debug")  # NG - JSON-RPCメッセージを破壊
```

### 設定管理

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    e_stat_app_id: str
    cache_ttl_seconds: int = 3600

    class Config:
        env_file = ".env"
```

## トランスポート選択

**Decision**: STDIO（開発・PoC用）

**Rationale**:
- Claude for Desktop / Claude Codeとの統合が最も簡単
- 設定がシンプル（コマンドとパスのみ）

**注意**: 本番環境ではHTTP/SSEトランスポートを検討

## 依存関係まとめ

| パッケージ | バージョン | 用途 |
|-----------|-----------|------|
| mcp[cli] | >= 1.2.0 | MCPサーバー実装 |
| pydantic | >= 2.0 | データバリデーション |
| pydantic-settings | >= 2.0 | 設定管理 |
| httpx | >= 0.27 | HTTPクライアント |
| cachetools | >= 5.0 | インメモリキャッシュ |

## Sources

- [MCP Python SDK (GitHub)](https://github.com/modelcontextprotocol/python-sdk)
- [Build an MCP server](https://modelcontextprotocol.io/docs/develop/build-server)
- [e-Stat API 3.0マニュアル](https://www.e-stat.go.jp/api/api-info/e-stat-manual3-0)
