# Deployment

[日本語版](deployment_ja.md)

## systemd (Linux / GCE)

### Create the service file

```ini
# /etc/systemd/system/slack-claude-bot.service

[Unit]
Description=Slack Claude Bot
After=network.target

[Service]
User=your-username
WorkingDirectory=/home/your-username/your-project
Environment="SLACK_BOT_TOKEN=xoxb-..."
Environment="SLACK_APP_TOKEN=xapp-..."
Environment="CLAUDE_PROJECT_DIR=/home/your-username/.claude/projects/-home-your-username-your-project"
Environment="CLAUDE_PATH=/home/your-username/.local/bin/claude"
Environment="SESSION_DB_PATH=/home/your-username/your-project/sessions.db"
ExecStart=/home/your-username/your-project/.venv/bin/python -m slack_claude_bot
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> **Note**: Do not write just `claude` for `CLAUDE_PATH`. systemd does not inherit the shell PATH, which causes a `No such file or directory` error. Confirm the full path with `which claude` first.

To use Codex CLI, replace the Claude-specific environment variables with:

```ini
Environment="BOT_RUNNER=codex"
Environment="CODEX_WORKDIR=/home/your-username/your-project"
Environment="CODEX_PATH=/home/your-username/.local/bin/codex"
Environment="PATH=/home/your-username/.local/bin:/usr/local/bin:/usr/bin:/bin"
Environment="CODEX_DANGEROUS_BYPASS=true"
```

If `CODEX_PATH` points into an nvm or other Node.js-managed directory, include that directory in `PATH`. Codex CLI may use a `/usr/bin/env node` shebang, and systemd's default `PATH` may not find `node`.

This library passes Codex global options as `codex --ask-for-approval never exec ...`. Some Codex versions reject the `codex exec --ask-for-approval never ...` order.

Codex sandboxing can fail under systemd with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, so CLI startup defaults `CODEX_DANGEROUS_BYPASS=true` for unattended runs.

### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable slack-claude-bot
sudo systemctl start slack-claude-bot
```

### View logs

```bash
sudo journalctl -u slack-claude-bot -f
```

### Stop and disable

```bash
sudo systemctl stop slack-claude-bot
sudo systemctl disable slack-claude-bot
```

---

## Programmatic entry point

When using custom commands, point `ExecStart` at a script like this instead of `-m slack_claude_bot`:

```python
# main.py
import os
from slack_claude_bot import SlackClaudeBot, ClaudeRunner, CodexRunner, SessionDB

if os.environ.get("BOT_RUNNER") == "codex":
    runner = CodexRunner(
        workdir=os.environ.get("CODEX_WORKDIR", os.getcwd()),
        codex_path=os.environ.get("CODEX_PATH", "codex"),
    )
else:
    runner = ClaudeRunner(
        project_dir=os.environ["CLAUDE_PROJECT_DIR"],
        claude_path=os.environ.get("CLAUDE_PATH", "claude"),
    )
db = SessionDB(db_path=os.environ.get("SESSION_DB_PATH", "sessions.db"))
bot = SlackClaudeBot(
    slack_bot_token=os.environ["SLACK_BOT_TOKEN"],
    slack_app_token=os.environ["SLACK_APP_TOKEN"],
    runner=runner,
    db=db,
)

# Add project-specific commands here
# @bot.command("!status", description="Show status")
# def handle_status(channel, thread_ts, text):
#     return "Running"

bot.start()
```
