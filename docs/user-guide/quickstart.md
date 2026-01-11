# クイックスタート

5分で e-Stat MCP サーバーを動作させる手順です。

## 前提条件チェック

以下がインストールされていることを確認してください：

- [ ] Python 3.13 以上
- [ ] [uv](https://docs.astral.sh/uv/) パッケージマネージャー
- [ ] e-Stat アプリケーションID

```{note}
e-Stat アプリケーションIDは [e-Stat API](https://www.e-stat.go.jp/api/) でユーザー登録後に取得できます。
```

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/drillan/e-stat-mcp.git
cd e-stat-mcp
```

### 2. 依存関係のインストール

```bash
uv sync
```

### 3. 環境変数の設定

方法1: 環境変数を直接設定

```bash
export E_STAT_APP_ID="あなたのアプリケーションID"
```

方法2: `.env` ファイルを作成

```bash
echo "E_STAT_APP_ID=あなたのアプリケーションID" > .env
```

### 4. Claude Code で利用開始

プロジェクトディレクトリで Claude Code を起動：

```bash
claude
```

`/mcp` コマンドでツールが認識されていることを確認：

```
Tools for e-stat-mcp (5 tools)
  1. search_stats
  2. get_stats_data
  3. get_meta_info
  4. list_datasets
  5. get_dataset_data
```

## 動作確認

Claude に以下のように依頼してみてください：

```
「人口」に関する統計表を3件検索してください
```

検索結果が表示されれば、セットアップ完了です。

## Claude Desktop での利用

Claude Desktop で使用する場合は、設定ファイルを編集します。

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "e-stat": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/e-stat-mcp",
        "run",
        "python",
        "-m",
        "e_stat_mcp"
      ],
      "env": {
        "E_STAT_APP_ID": "あなたのアプリケーションID"
      }
    }
  }
}
```

```{warning}
`/path/to/e-stat-mcp` は実際のプロジェクトパスに置き換えてください。
```

Claude Desktop を再起動して設定を反映します。

## トラブルシューティング

### 認証エラーが発生する

```
エラー: 認証に失敗しました。アプリケーションIDを確認してください。
```

→ `E_STAT_APP_ID` 環境変数が正しく設定されているか確認してください。

### サーバーが見つからない

1. Claude を完全に再起動
2. 設定ファイルのパスが絶対パスか確認
3. サーバー単体起動を確認：
   ```bash
   uv run python -m e_stat_mcp
   ```

### ログの確認

- **macOS**: `~/Library/Logs/Claude/mcp*.log`
- **Windows**: `%USERPROFILE%\AppData\Local\Claude\logs\mcp*.log`

## 次のステップ

- [設定](configuration.md) - 詳細な設定オプション
- [使用例](usage-examples.md) - 実践的なユースケース
- [MCPツールリファレンス](../tools/index.md) - 各ツールの詳細
