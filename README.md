# slack-claude-bot

A Python library that forwards Slack mentions and thread replies to the [Claude Code](https://claude.ai/code) CLI. Maintains conversation history per thread and prevents concurrent execution with a per-thread lock.

[日本語版 README はこちら](README_ja.md)

## Features

- Thread-scoped session continuity via Claude Code `--resume`
- Per-thread exclusive lock (prevents parallel execution)
- Built-in commands: `!help` / `!reset` / `!reset all` / `!compact`
- Custom command extension via `register_command()` or `@bot.command()` decorator

## Installation

```bash
pip install git+ssh://git@github.com/fumihiko-takahashi/slack-claude-bot.git
```

## Quick Start

### Environment variables only (CLI)

```bash
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
export CLAUDE_PROJECT_DIR=~/.claude/projects/-home-alice-myproject
export CLAUDE_PATH=/home/alice/.local/bin/claude   # full path recommended
export SESSION_DB_PATH=sessions.db                 # optional
export CLAUDE_TIMEOUT=10800                        # optional, seconds (default: 3h)

python -m slack_claude_bot
# or
slack-claude-bot
```

### Adding custom commands

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

@bot.command("!status", description="Show current status")
def handle_status(channel, thread_ts, text):
    return "Status: running"

bot.start()
```

## Built-in Commands

| Command | Description |
|---|---|
| `!help` | List available commands |
| `!reset` | Force-release the lock for this thread |
| `!reset all` | Force-release all locks |
| `!compact` | Compact conversation history (equivalent to `/compact`) |

## Custom Command API

```python
# Decorator style
@bot.command("!foo", description="Shown in !help")
def handle_foo(channel: str, thread_ts: str, text: str) -> str | None:
    return "response text"  # return None to send no reply

# Function style
bot.register_command("!bar", handle_bar, description="description")
```

## Requirements

- Python 3.10+
- Claude Code CLI (`claude` command)
- `slack-bolt >= 1.20`

## Documentation

| Document | English | Japanese |
|---|---|---|
| Slack App Setup | [docs/slack-app-setup.md](docs/slack-app-setup.md) | [docs/slack-app-setup_ja.md](docs/slack-app-setup_ja.md) |
| Configuration Reference | [docs/configuration.md](docs/configuration.md) | [docs/configuration_ja.md](docs/configuration_ja.md) |
| Deployment | [docs/deployment.md](docs/deployment.md) | [docs/deployment_ja.md](docs/deployment_ja.md) |
| Internals | [docs/internals.md](docs/internals.md) | [docs/internals_ja.md](docs/internals_ja.md) |
