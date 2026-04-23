# slack-claude-bot

Slack のメンション・スレッド返信を [Claude Code](https://claude.ai/code) CLI に転送する Python ライブラリ。スレッドごとに会話履歴を保持し、同時実行を排他制御する。

[English README](README.md)

## Features

- スレッドスコープのセッション継続（Claude Code `--resume`）
- スレッドごとの排他ロック（並列実行防止）
- 組み込みコマンド: `!help` / `!reset` / `!reset all` / `!compact`
- `register_command()` / `@bot.command()` によるカスタムコマンド拡張

## ⚠️ セキュリティに関する注意

このライブラリは Claude Code を `--dangerously-skip-permissions` で実行します。これにより、ファイル書き込みやコマンド実行などの操作における**確認プロンプトがすべてスキップ**されます。

**以下の条件をどちらも満たす環境でのみ使用してください：**

- このbotの専用インスタンスであること（共有サーバーでないこと）
- Slack ワークスペースのメンバー全員を信頼できること

パブリックなワークスペースや不特定多数が参加するワークスペースでは使用しないでください。

## インストール

```bash
pip install git+ssh://git@github.com/fumihiko-takahashi/slack-claude-bot.git
```

## クイックスタート

### 環境変数のみで起動（CLI）

```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
export CLAUDE_PROJECT_DIR=~/.claude/projects/-home-alice-myproject
export CLAUDE_PATH=/home/alice/.local/bin/claude   # フルパス推奨
export SESSION_DB_PATH=sessions.db                 # 省略可
export CLAUDE_TIMEOUT=10800                        # 省略可（デフォルト: 3時間）

python -m slack_claude_bot
# または
slack-claude-bot
```

### カスタムコマンドを追加する場合

```python
import os
from slack_claude_bot import SlackClaudeBot, ClaudeRunner, SessionDB

runner = ClaudeRunner(
    project_dir=os.environ["CLAUDE_PROJECT_DIR"],
    claude_path=os.environ.get("CLAUDE_PATH", "claude"),
)
db = SessionDB(db_path="sessions.db")
bot = SlackClaudeBot(
    slack_bot_token=os.environ["SLACK_BOT_TOKEN"],
    slack_app_token=os.environ["SLACK_APP_TOKEN"],
    runner=runner,
    db=db,
)

@bot.command("!status", description="現在のステータスを表示")
def handle_status(channel, thread_ts, text):
    return "ステータス: 正常稼働中"

bot.start()
```

## 組み込みコマンド

| コマンド | 説明 |
|---|---|
| `!help` | コマンド一覧を表示 |
| `!reset` | このスレッドのロックを強制解放 |
| `!reset all` | すべてのロックを一括解放 |
| `!compact` | 会話履歴を圧縮（`/compact` に相当） |

## カスタムコマンド API

```python
# デコレータ形式
@bot.command("!foo", description="説明文（!help に自動掲載）")
def handle_foo(channel: str, thread_ts: str, text: str) -> str | None:
    return "返答テキスト"  # None を返すと返答しない

# 関数形式
bot.register_command("!bar", handle_bar, description="説明文")
```

## 動作要件

- Python 3.10+
- Claude Code CLI（`claude` コマンド）
- `slack-bolt >= 1.20`

## ドキュメント

| ドキュメント | 英語 | 日本語 |
|---|---|---|
| Slack App のセットアップ | [docs/slack-app-setup.md](docs/slack-app-setup.md) | [docs/slack-app-setup_ja.md](docs/slack-app-setup_ja.md) |
| 設定リファレンス | [docs/configuration.md](docs/configuration.md) | [docs/configuration_ja.md](docs/configuration_ja.md) |
| デプロイ・常駐化 | [docs/deployment.md](docs/deployment.md) | [docs/deployment_ja.md](docs/deployment_ja.md) |
| 内部実装の詳細 | [docs/internals.md](docs/internals.md) | [docs/internals_ja.md](docs/internals_ja.md) |
