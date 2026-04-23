# Slack App のセットアップ

[English version](slack-app-setup.md)

## 1. App の作成

https://api.slack.com/apps にアクセスし、"Create New App" → "From scratch" を選択。

## 2. Bot Token Scopes の設定

"OAuth & Permissions" → "Bot Token Scopes" に以下を追加：

| Scope | 用途 |
|---|---|
| `app_mentions:read` | メンションの受信 |
| `chat:write` | メッセージの送信 |
| `channels:history` | パブリックチャンネルの履歴読み取り |
| `groups:history` | プライベートチャンネルも使う場合 |

## 3. Socket Mode の有効化

"Socket Mode" → Enable Socket Mode を ON にし、App-Level Token を生成する。

- Token Name: 任意（例: `socket-token`）
- Scope: `connections:write`
- 生成された `xapp-...` トークンをメモしておく

## 4. Event Subscriptions の設定

"Event Subscriptions" → Enable Events を ON → "Subscribe to bot events" に `app_mention` を追加。

## 5. ワークスペースへのインストール

"OAuth & Permissions" → "Install to Workspace" を実行。  
生成された Bot User OAuth Token (`xoxb-...`) をメモしておく。

---

## トークンの種類と混乱しがちな点

このライブラリで使うトークンは2種類だけ：

| 環境変数 | プレフィックス | 取得場所 |
|---|---|---|
| `SLACK_BOT_TOKEN` | `xoxb-...` | "OAuth & Permissions" → "Bot User OAuth Token" |
| `SLACK_APP_TOKEN` | `xapp-...` | "Basic Information" → "App-Level Tokens" |

### `xoxe.xoxp-...` が表示された場合

Token Rotation が有効になっている User Token を見ている。Bot Token は同じページの別の行にある。  
Token Rotation が不要であれば "OAuth & Permissions" → "Advanced" から無効化できる。個人用途では不要な機能。
