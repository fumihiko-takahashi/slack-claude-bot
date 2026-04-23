# slack-claude-bot

Slack bot that proxies messages to [Claude Code](https://claude.ai/code) CLI with session management, lock control, and extensible command system.

## Features

- Thread-scoped session continuity (Claude Code `--resume`)
- Concurrent-execution lock per thread
- Built-in commands: `!help`, `!reset`, `!reset all`, `!compact`
- Custom command registration via `register_command()` or `@bot.command()` decorator

## Installation

```bash
pip install git+https://github.com/fumihiko-takahashi/slack-claude-bot.git
```

## Quick Start

### Environment variables only (CLI)

```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
export CLAUDE_PROJECT_DIR=~/.claude/projects/my-project
export CLAUDE_PATH=/usr/local/bin/claude   # optional, default: "claude"
export SESSION_DB_PATH=sessions.db         # optional
export CLAUDE_TIMEOUT=10800               # optional, seconds (default: 3h)

python -m slack_claude_bot
# or
slack-claude-bot
```

### Programmatic usage with custom commands

```python
import os
from slack_claude_bot import SlackClaudeBot, ClaudeRunner, SessionDB

runner = ClaudeRunner(
    project_dir="~/.claude/projects/my-project",
    claude_path="/usr/local/bin/claude",
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
| `!reset` | スレッドのロックを強制解放 |
| `!reset all` | すべてのロックを一括解放 |
| `!compact` | 会話履歴を圧縮（`/compact` に相当） |

## Custom Command API

```python
# デコレータ形式
@bot.command("!foo", description="説明文（!help に表示）")
def handle_foo(channel: str, thread_ts: str, text: str) -> str | None:
    return "返答テキスト"  # None を返すと返答しない

# 関数形式
bot.register_command("!bar", handle_bar, description="説明文")
```

## Slack App Setup

Required scopes: `app_mentions:read`, `chat:write`  
Required event subscriptions: `app_mention`  
Socket Mode: enabled

## Requirements

- Python 3.10+
- Claude Code CLI (`claude` command)
- `slack-bolt >= 1.20`
