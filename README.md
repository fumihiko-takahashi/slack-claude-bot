# slack-claude-bot

Slack のメンション・スレッド返信を [Claude Code](https://claude.ai/code) CLI に転送する Python ライブラリ。スレッドごとに会話履歴を保持し、同時実行を排他制御する。

## Features

- スレッドスコープのセッション継続（Claude Code `--resume`）
- スレッドごとの排他ロック（並列実行防止）
- 組み込みコマンド: `!help` / `!reset` / `!reset all` / `!compact`
- `register_command()` / `@bot.command()` によるカスタムコマンド拡張

## Installation

```bash
pip install git+ssh://git@github.com/fumihiko-takahashi/slack-claude-bot.git
```

## Quick Start

### 環境変数のみで起動（CLI）

```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
export CLAUDE_PROJECT_DIR=~/.claude/projects/-home-alice-myproject
export CLAUDE_PATH=/home/alice/.local/bin/claude   # フルパス推奨
export SESSION_DB_PATH=sessions.db                 # 省略可
export CLAUDE_TIMEOUT=10800                        # 省略可（デフォルト: 3h）

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

## Built-in Commands

| Command | Description |
|---|---|
| `!help` | コマンド一覧を表示 |
| `!reset` | このスレッドのロックを強制解放 |
| `!reset all` | すべてのロックを一括解放 |
| `!compact` | 会話履歴を圧縮（`/compact` に相当） |

## Custom Command API

```python
# デコレータ形式
@bot.command("!foo", description="説明文（!help に自動掲載）")
def handle_foo(channel: str, thread_ts: str, text: str) -> str | None:
    return "返答テキスト"  # None を返すと返答しない

# 関数形式
bot.register_command("!bar", handle_bar, description="説明文")
```

## Requirements

- Python 3.10+
- Claude Code CLI（`claude` コマンド）
- `slack-bolt >= 1.20`

## Documentation

- [Slack App のセットアップ](docs/slack-app-setup.md) — App 作成・Token 取得手順、混乱しがちなトークン種別の説明
- [設定リファレンス](docs/configuration.md) — 環境変数一覧、`CLAUDE_PROJECT_DIR` / `CLAUDE_PATH` の確認方法
- [デプロイ・常駐化](docs/deployment.md) — systemd サービスファイルの設定、ログ確認・停止手順
- [内部実装の詳細](docs/internals.md) — セッション管理・ロック機構・`--dangerously-skip-permissions` の背景
