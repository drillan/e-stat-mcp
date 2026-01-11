# アーキテクチャ

e-Stat MCP サーバーのシステムアーキテクチャを解説します。

## 全体構成

```{mermaid}
graph TB
    subgraph "Claude Code / Desktop"
        MCP[MCP Client]
    end

    subgraph "e-Stat MCP Server"
        Server["server.py<br/>FastMCP Server"]
        Client["client.py<br/>EStatClient"]
        Cache["cache.py<br/>TTLCache"]
        Models["models/<br/>Pydantic Models"]
        Settings["settings.py<br/>Configuration"]
    end

    subgraph "External"
        API["e-Stat API<br/>REST JSON"]
    end

    MCP <-->|STDIO| Server
    Server --> Client
    Client --> Cache
    Client --> Models
    Client --> Settings
    Client <-->|HTTPS| API
    Server --> Models
```

## レイヤー構造

### サーバーレイヤー（server.py）

MCP プロトコルを処理し、ツールを公開します。

- FastMCP を使用したサーバー定義
- 5つのツール関数（`search_stats`, `get_stats_data` など）
- ライフサイクル管理（初期化・終了処理）
- 入力バリデーションと出力整形

### クライアントレイヤー（client.py）

e-Stat API との通信を担当します。

- httpx による非同期 HTTP 通信
- TTL キャッシュによるレスポンスキャッシング
- 自動リトライ（ネットワークエラー、サーバーエラー時）
- Pydantic モデルによるレスポンスパース

### モデルレイヤー（models/）

データ構造を定義します。

- `api.py`: e-Stat API レスポンスモデル
- `tools.py`: MCP ツール入出力モデル
- `errors.py`: エラーコード・エラーモデル

### インフラレイヤー

- `settings.py`: 環境変数からの設定読み込み
- `cache.py`: キャッシュユーティリティ

## リクエストフロー

```{mermaid}
sequenceDiagram
    participant U as User (Claude)
    participant S as MCP Server
    participant C as EStatClient
    participant CH as Cache
    participant A as e-Stat API

    U->>S: search_stats(keyword="人口")
    S->>S: SearchStatsRequest バリデーション
    S->>C: get_stats_list()
    C->>CH: キャッシュ確認
    alt キャッシュヒット
        CH-->>C: キャッシュされたレスポンス
    else キャッシュミス
        C->>A: GET /getStatsList
        A-->>C: JSON レスポンス
        C->>C: Pydantic モデルでバリデーション
        C->>CH: キャッシュに保存
    end
    C-->>S: StatsListResponse
    S->>S: SearchStatsResult に変換
    S-->>U: 検索結果
```

## キャッシュ戦略

### TTL キャッシュ

- `cachetools.TTLCache` を使用
- デフォルト TTL: 3600秒（1時間）
- 最大エントリ数: 1000

### キャッシュキー

MD5 ハッシュを使用してキャッシュキーを生成：

```python
def _make_cache_key(endpoint: str, params: dict[str, Any]) -> str:
    sorted_params = sorted(params.items())
    key_str = f"{endpoint}:{sorted_params}"
    return hashlib.md5(key_str.encode()).hexdigest()
```

### キャッシュ対象

- すべての e-Stat API レスポンス
- 統計データは頻繁に更新されないため、長めの TTL でも問題なし

## リトライ戦略

### 自動リトライ

ネットワークエラー・サーバーエラー時は自動でリトライを行います。
リトライ回数は `E_STAT_MAX_RETRIES` 環境変数で設定可能です（デフォルト: 3回）。

### リトライ対象

- ネットワークエラー（接続タイムアウトなど）
- サーバーエラー（5xx）

### リトライ対象外

- 認証エラー（100）
- パラメータエラー（101, 102）
- データなし（1）

## 設定管理

### pydantic-settings

環境変数からの設定読み込みに `pydantic-settings` を使用：

```python
class Settings(BaseSettings):
    e_stat_app_id: str
    e_stat_base_url: str = "https://api.e-stat.go.jp/rest/3.0/app/json"
    e_stat_cache_ttl_seconds: int = 3600
    # ...

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
```

### シングルトンパターン

設定は `@lru_cache` でシングルトン化：

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

## MCP 統合

### FastMCP

[FastMCP](https://github.com/jlowin/fastmcp) を使用してサーバーを定義：

```python
mcp = FastMCP("e-stat-mcp")

@mcp.tool()
async def search_stats(
    keyword: str | None = None,
    # ...
) -> list[SearchStatsResult]:
    """統計表を検索します。"""
    # ...
```

### STDIO 通信

Claude Code / Desktop との通信は標準入出力（STDIO）で行われます：

```python
def run_server() -> None:
    mcp.run(transport="stdio")
```

### ライフサイクル

```python
@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    # 初期化
    settings = get_settings()
    client = EStatClient(settings)

    yield AppContext(client=client)

    # クリーンアップ
    await client.close()
```

## テスト戦略

### 単体テスト

- `respx` で HTTP をモック
- 外部依存なしで高速実行
- すべてのエッジケースをカバー

### 統合テスト

- 実際の e-Stat API を使用
- `pytest.mark.integration` でマーク
- CI では環境変数が設定されている場合のみ実行

### コントラクトテスト

- MCP ツールの入出力仕様を検証
- `pytest.mark.contract` でマーク

## 拡張ポイント

### 新しいツールの追加

`server.py` に `@mcp.tool()` デコレータで追加：

```python
@mcp.tool()
async def new_tool(param: str) -> Result:
    """新しいツールの説明"""
    # 実装
```

### 新しい API エンドポイント

1. `client.py` にメソッドを追加
2. `models/api.py` にレスポンスモデルを追加
3. `models/tools.py` に入出力モデルを追加
4. `server.py` にツール関数を追加

## 次のステップ

- [データモデル](data-models.md) - Pydantic モデルの詳細
- [エラー処理](error-handling.md) - エラーハンドリングパターン
