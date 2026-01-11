# エラー処理

e-Stat MCP サーバーのエラー処理パターンを解説します。

## エラー処理フロー

```{mermaid}
flowchart TD
    A[API Response] --> B{JSON Parse}
    B -->|Success| C{Check STATUS}
    B -->|Failure| D[NETWORK_ERROR]

    C -->|0| E[Success - Return Data]
    C -->|1| F[NO_DATA - Return Empty]
    C -->|100| G[AUTH_ERROR]
    C -->|101| H[MISSING_PARAM]
    C -->|102| I[INVALID_PARAM]
    C -->|300| J[DATA_NOT_FOUND]

    G --> K[User Message]
    H --> K
    I --> K
    J --> K
    D --> K

    K --> L[EStatApiError]
```

## エラーコード体系

### e-Stat API エラー（0-300）

| コード | 名前 | 説明 | 対処法 |
|--------|------|------|--------|
| 0 | SUCCESS | 成功 | - |
| 1 | NO_DATA | 該当データなし | 検索条件を変更 |
| 100 | AUTH_ERROR | 認証エラー | E_STAT_APP_ID を確認 |
| 101 | MISSING_PARAM | 必須パラメータ不足 | パラメータを確認 |
| 102 | INVALID_PARAM | パラメータ値が不正 | 値の形式を確認 |
| 300 | DATA_NOT_FOUND | データが存在しない | 統計表IDを確認 |

### クライアント側エラー（900-）

| コード | 名前 | 説明 | 対処法 |
|--------|------|------|--------|
| 900 | NETWORK_ERROR | ネットワークエラー | 接続を確認、再試行 |
| 901 | SERVER_ERROR | サーバーエラー | しばらく待って再試行 |
| 902 | VALIDATION_ERROR | バリデーションエラー | APIレスポンスの形式確認 |

## EStatApiError クラス

カスタム例外クラスでエラー情報を管理：

```python
class EStatApiError(Exception):
    def __init__(
        self,
        code: EStatErrorCode,
        message: str,
        parameter: str | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.parameter = parameter
        super().__init__(message)

    def get_user_message(self) -> str:
        """ユーザー向けの分かりやすいメッセージを生成"""
        messages = {
            EStatErrorCode.AUTH_ERROR: (
                "認証に失敗しました。"
                "E_STAT_APP_ID が正しく設定されているか確認してください。"
            ),
            EStatErrorCode.MISSING_PARAM: (
                f"必須パラメータが不足しています: {self.parameter}"
            ),
            EStatErrorCode.INVALID_PARAM: (
                f"パラメータの値が不正です: {self.parameter}"
            ),
            EStatErrorCode.DATA_NOT_FOUND: (
                "指定されたデータが見つかりませんでした。"
                "統計表IDを確認してください。"
            ),
            EStatErrorCode.NETWORK_ERROR: (
                "e-Stat APIへの接続に失敗しました。"
                "ネットワーク接続を確認してください。"
            ),
            EStatErrorCode.SERVER_ERROR: (
                "e-Stat APIでサーバーエラーが発生しました。"
                "しばらく待ってから再試行してください。"
            ),
        }
        return messages.get(self.code, self.message)
```

## エラー処理パターン

### API レスポンスの処理

```python
async def _request(
    self,
    endpoint: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    try:
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except httpx.NetworkError as e:
        raise EStatApiError(
            code=EStatErrorCode.NETWORK_ERROR,
            message=str(e),
        )
    except httpx.HTTPStatusError as e:
        raise EStatApiError(
            code=EStatErrorCode.SERVER_ERROR,
            message=f"HTTP {e.response.status_code}",
        )

    # API レスポンスのステータスコードを確認
    result = data.get("GET_STATS_LIST", {}).get("RESULT", {})
    status = result.get("STATUS", 0)

    if status == EStatErrorCode.SUCCESS:
        return data
    elif status == EStatErrorCode.NO_DATA:
        return data  # 空のデータとして処理
    else:
        raise EStatApiError(
            code=EStatErrorCode(status),
            message=result.get("ERROR_MSG", "Unknown error"),
        )
```

### サーバー層でのエラー変換

```python
@mcp.tool()
async def search_stats(
    keyword: str | None = None,
    # ...
) -> list[SearchStatsResult]:
    try:
        response = await client.get_stats_list(keyword=keyword, ...)
        # 結果を変換して返す
    except EStatApiError as e:
        # ユーザー向けメッセージで再raise
        raise McpError(e.get_user_message())
```

## リトライ処理

### 対象となるエラー

- ネットワークエラー（タイムアウト、接続失敗）
- サーバーエラー（5xx）

### 対象外のエラー

- 認証エラー（リトライしても成功しない）
- パラメータエラー（入力を修正が必要）

### 実装

```python
async def _request_with_retry(
    self,
    endpoint: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    last_error: Exception | None = None

    for attempt in range(self._max_retries):
        try:
            return await self._request(endpoint, params)
        except EStatApiError as e:
            if e.code in (EStatErrorCode.NETWORK_ERROR, EStatErrorCode.SERVER_ERROR):
                last_error = e
                wait_time = 2 ** attempt  # 指数バックオフ: 1, 2, 4, 8...
                await asyncio.sleep(wait_time)
            else:
                raise  # リトライ対象外のエラー

    raise last_error or EStatApiError(
        code=EStatErrorCode.NETWORK_ERROR,
        message="Maximum retries exceeded",
    )
```

## バリデーションエラー

Pydantic バリデーションエラーの処理：

```python
try:
    response = StatsListResponse.model_validate(data)
except ValidationError as e:
    raise EStatApiError(
        code=EStatErrorCode.VALIDATION_ERROR,
        message=f"APIレスポンスの形式が不正です: {e}",
    )
```

## ユーザー向けエラーメッセージ

エラーメッセージは以下の原則で設計：

1. **何が起きたか**: 問題の説明
2. **なぜ起きたか**: 原因の推測（可能な場合）
3. **どうすればいいか**: 対処法の提案

```python
# 良い例
"認証に失敗しました。E_STAT_APP_ID が正しく設定されているか確認してください。"

# 悪い例
"Error 100"
```

## デバッグ

### ログの確認

MCP サーバーのログは以下で確認できます：

- **macOS**: `~/Library/Logs/Claude/mcp*.log`
- **Windows**: `%USERPROFILE%\AppData\Local\Claude\logs\mcp*.log`

### 手動テスト

```python
import asyncio
from e_stat_mcp.client import EStatClient
from e_stat_mcp.settings import get_settings

async def test():
    settings = get_settings()
    client = EStatClient(settings)
    try:
        result = await client.get_stats_list(keyword="人口")
        print(result)
    except EStatApiError as e:
        print(f"Error: {e.code} - {e.get_user_message()}")
    finally:
        await client.close()

asyncio.run(test())
```

## 次のステップ

- [エラーコード一覧](../appendix/error-codes.md) - 全エラーコードの詳細
- [コントリビューション](contributing.md) - エラー処理の改善に貢献
