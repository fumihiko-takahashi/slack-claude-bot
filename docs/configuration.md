# Configuration Reference

[日本語版](configuration_ja.md)

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SLACK_BOT_TOKEN` | ✅ | — | Bot Token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | ✅ | — | App-level Token (`xapp-...`) |
| `CLAUDE_PROJECT_DIR` | ✅ | — | Directory where Claude Code stores session files |
| `CLAUDE_PATH` | — | `claude` | Full path to the Claude Code CLI binary |
| `SESSION_DB_PATH` | — | `sessions.db` | Path to the SQLite database file |
| `CLAUDE_TIMEOUT` | — | `10800` | Timeout in seconds (default: 3 hours) |

---

## How to Find CLAUDE_PROJECT_DIR

Claude Code stores session files under `~/.claude/projects/`. The directory name is the working directory path with `/` replaced by `-`.

```bash
ls ~/.claude/projects/
# e.g. -home-alice-myproject
```

If the project directory is `/home/alice/myproject`:

```
CLAUDE_PROJECT_DIR=~/.claude/projects/-home-alice-myproject
```

---

## How to Find CLAUDE_PATH

```bash
which claude
# e.g. /home/alice/.local/bin/claude
```

Using just `claude` (without a full path) will fail in environments that do not inherit the shell PATH, such as systemd or cron.  
Always specify the full path.

---

## ClaudeRunner Options (programmatic use)

```python
ClaudeRunner(
    project_dir="~/.claude/projects/-home-alice-myproject",  # equivalent to CLAUDE_PROJECT_DIR
    claude_path="/home/alice/.local/bin/claude",             # equivalent to CLAUDE_PATH
    timeout=10800,                                           # equivalent to CLAUDE_TIMEOUT
    extra_args=["--model", "claude-opus-4-6"],               # additional flags (optional)
)
```
