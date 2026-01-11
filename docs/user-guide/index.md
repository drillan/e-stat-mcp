# ユーザーガイド

このセクションでは、e-Stat MCP サーバーのセットアップから実際の使用方法までを解説します。

## 概要

e-Stat MCP サーバーを使用すると、Claude Code や Claude Desktop から日本の政府統計データにアクセスできます。

```{mermaid}
flowchart LR
    A[あなた] --> B[Claude]
    B --> C[e-Stat MCP サーバー]
    C --> D[e-Stat API]
    D --> E[(政府統計データ)]
```

## このセクションの内容

- [クイックスタート](quickstart.md) - 5分で始める
- [インストール](installation.md) - 詳細なセットアップ手順
- [設定](configuration.md) - 環境変数とオプション
- [使用例](usage-examples.md) - 実践的なユースケース

## 前提条件

始める前に、以下を準備してください：

1. **Python 3.13 以上**
2. **[uv](https://docs.astral.sh/uv/)** パッケージマネージャー
3. **e-Stat アプリケーションID** - [e-Stat API](https://www.e-stat.go.jp/api/) で取得

## 次のステップ

初めての方は [クイックスタート](quickstart.md) から始めることをお勧めします。
