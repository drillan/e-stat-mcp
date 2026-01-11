# インストール

e-Stat MCP サーバーの詳細なインストール手順です。

## システム要件

| 項目 | 要件 |
|------|------|
| Python | 3.13 以上 |
| パッケージマネージャー | [uv](https://docs.astral.sh/uv/) |
| OS | Linux, macOS, Windows |

## e-Stat アプリケーションIDの取得

1. [e-Stat](https://www.e-stat.go.jp/) にアクセス
2. ユーザー登録（無料）
3. [マイページ](https://www.e-stat.go.jp/mypage/) にログイン
4. 「API」→「アプリケーションIDの取得」
5. 必要事項を入力してIDを取得

```{note}
アプリケーションIDは即時発行されます。メモしておいてください。
```

## uv のインストール

まだ uv をインストールしていない場合：

**macOS / Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

詳細は [uv 公式ドキュメント](https://docs.astral.sh/uv/getting-started/installation/) を参照してください。

## プロジェクトのセットアップ

### リポジトリのクローン

```bash
git clone https://github.com/drillan/e-stat-mcp.git
cd e-stat-mcp
```

### 依存関係のインストール

```bash
uv sync
```

開発用依存関係も含める場合：

```bash
uv sync --all-extras
```

## 環境変数の設定

### 方法1: 環境変数を直接設定

**bash / zsh**:
```bash
export E_STAT_APP_ID="あなたのアプリケーションID"
```

**fish**:
```fish
set -x E_STAT_APP_ID "あなたのアプリケーションID"
```

**PowerShell**:
```powershell
$env:E_STAT_APP_ID = "あなたのアプリケーションID"
```

### 方法2: .env ファイルを使用

プロジェクトルートに `.env` ファイルを作成：

```bash
E_STAT_APP_ID=あなたのアプリケーションID
```

```{warning}
`.env` ファイルには機密情報が含まれます。Git にコミットしないよう `.gitignore` に含まれていることを確認してください。
```

## インストールの確認

サーバーが正常に起動するか確認：

```bash
uv run python -m e_stat_mcp
```

エラーなく起動すれば成功です（Ctrl+C で終了）。

## Claude Code との連携

プロジェクトディレクトリに `.mcp.json` が含まれているため、特別な設定なしに Claude Code から利用できます。

```bash
cd e-stat-mcp
claude
```

## Claude Desktop との連携

設定ファイルを編集します。

### macOS

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "e-stat": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yourname/path/to/e-stat-mcp",
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

### Windows

`%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "e-stat": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\yourname\\path\\to\\e-stat-mcp",
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

### Linux

`~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "e-stat": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/yourname/path/to/e-stat-mcp",
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

設定後、Claude Desktop を再起動してください。

## 次のステップ

- [設定](configuration.md) - 詳細な設定オプション
- [クイックスタート](quickstart.md) - 動作確認
