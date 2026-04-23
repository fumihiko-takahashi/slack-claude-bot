# slack-claude-bot

A Python library that forwards Slack mentions and thread replies to the [Claude Code](https://claude.ai/code) CLI. Maintains conversation history per thread and prevents concurrent execution with a per-thread lock.

[日本語版 README はこちら](README_ja.md)

## Features

- Thread-scoped session continuity via Claude Code `--resume`
- Per-thread exclusive lock (prevents parallel execution)
- Built-in commands: `!help` / `!reset` / `!reset all` / `!compact`
- Custom command extension via `register_command()` or `@bot.command()` decorator

## ⚠️ Security Notice

This library runs Claude Code with `--dangerously-skip-permissions`, which **bypasses all confirmation prompts** for file writes, command execution, and other potentially destructive actions.

**Only use this in environments where both of the following are true:**

- The instance is dedicated to this bot (not a shared server)
- Every member of the Slack workspace is trusted

Do not expose this bot to public or untrusted Slack workspaces.

## Installation & Setup

### Step 1 — Create a Slack App

1. Go to https://api.slack.com/apps → "Create New App" → "From scratch"
2. **OAuth & Permissions** → Bot Token Scopes → add `app_mentions:read`, `chat:write`, `channels:history`
3. **Socket Mode** → Enable → generate an App-Level Token (scope: `connections:write`) → save the `xapp-...` token
4. **Event Subscriptions** → Enable → Subscribe to bot events → add `app_mention`
5. **OAuth & Permissions** → Install to Workspace → save the `xoxb-...` Bot Token

> You need two tokens: `SLACK_BOT_TOKEN` (`xoxb-...`) and `SLACK_APP_TOKEN` (`xapp-...`).  
> If you see `xoxe.xoxp-...` instead, you are looking at a User Token — the Bot Token is on a separate row.  
> See [docs/slack-app-setup.md](docs/slack-app-setup.md) for details.

### Step 2 — Install the library

```bash
pip install git+ssh://git@github.com/fumihiko-takahashi/slack-claude-bot.git
```

### Step 3 — Configure environment variables

```bash
# Find your Claude Code session directory
ls ~/.claude/projects/
# e.g. -home-alice-myproject

# Find the full path to the claude binary
which claude
# e.g. /home/alice/.local/bin/claude

export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
export CLAUDE_PROJECT_DIR=~/.claude/projects/-home-alice-myproject
export CLAUDE_PATH=/home/alice/.local/bin/claude
```

> `CLAUDE_PROJECT_DIR`: the working directory path with `/` replaced by `-` under `~/.claude/projects/`.  
> `CLAUDE_PATH`: always use the full path — environments like systemd do not inherit the shell PATH.  
> See [docs/configuration.md](docs/configuration.md) for all options.

### Step 4 — Run

```bash
python -m slack_claude_bot
# or
slack-claude-bot
```

Mention the bot in any channel it has been invited to and it will reply in the thread.  
For persistent deployment via systemd, see [docs/deployment.md](docs/deployment.md).

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
