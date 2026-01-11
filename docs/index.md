# e-Stat MCP サーバー ドキュメント

日本の政府統計ポータルサイト [e-Stat](https://www.e-stat.go.jp/) のAPIに接続するMCP (Model Context Protocol) サーバーです。

Claude Code や Claude Desktop から e-Stat の統計データを検索・取得できます。

## 主な機能

- **統計表検索** (`search_stats`): キーワードや政府統計コードで統計表を検索
- **統計データ取得** (`get_stats_data`): 統計表IDからデータを取得
- **メタ情報取得** (`get_meta_info`): 統計表の分類情報を取得
- **データセット一覧** (`list_datasets`): 公開データセットを一覧表示
- **データセットデータ取得** (`get_dataset_data`): データセットIDからデータを取得

## 対象読者

**エンドユーザー向け** ([ユーザーガイド](user-guide/index.md))
: Claude Code や Claude Desktop で統計データを活用したい方向け。セットアップから使用例まで解説します。

**開発者向け** ([開発者ガイド](developer-guide/index.md))
: コードを理解・拡張したい方向け。アーキテクチャ、データモデル、APIリファレンスを提供します。

## クイックスタート

```bash
# 1. 依存関係のインストール
uv sync

# 2. 環境変数の設定
export E_STAT_APP_ID="あなたのアプリケーションID"

# 3. Claude Code で利用開始
claude
```

詳細は [クイックスタート](user-guide/quickstart.md) を参照してください。

## 目次

```{toctree}
:maxdepth: 2
:caption: ユーザーガイド

user-guide/index
user-guide/quickstart
user-guide/installation
user-guide/configuration
user-guide/usage-examples
```

```{toctree}
:maxdepth: 2
:caption: MCPツールリファレンス

tools/index
tools/search-stats
tools/get-stats-data
tools/get-meta-info
tools/list-datasets
tools/get-dataset-data
```

```{toctree}
:maxdepth: 2
:caption: 開発者ガイド

developer-guide/index
developer-guide/architecture
developer-guide/data-models
developer-guide/error-handling
developer-guide/contributing
```

```{toctree}
:maxdepth: 2
:caption: APIリファレンス

api/index
api/server
api/client
api/models
api/settings
api/cache
```

```{toctree}
:maxdepth: 1
:caption: 付録

appendix/e-stat-api
appendix/error-codes
appendix/changelog
```

## 関連リンク

- [e-Stat API 仕様](https://www.e-stat.go.jp/api/api-info/e-stat-manual3-0)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [GitHub リポジトリ](https://github.com/drillan/e-stat-mcp)
