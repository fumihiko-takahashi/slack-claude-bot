# Configuration Reference

[日本語版](configuration_ja.md)

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SLACK_BOT_TOKEN` | ✅ | — | Bot Token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | ✅ | — | App-level Token (`xapp-...`) |
| `BOT_RUNNER` | — | `claude` | Runner to use. `claude` or `codex` |
| `CLAUDE_PROJECT_DIR` | ✅ when `BOT_RUNNER=claude` | — | Directory where Claude Code stores session files |
| `CLAUDE_PATH` | — | `claude` | Full path to the Claude Code CLI binary |
| `CLAUDE_TIMEOUT` | — | `10800` | Timeout in seconds (default: 3 hours) |
| `CLAUDE_EXTRA_ARGS` | — | — | Extra arguments passed to Claude Code CLI |
| `CODEX_WORKDIR` | — | current directory | Working directory where Codex runs |
| `CODEX_PATH` | — | `codex` | Full path to the Codex CLI binary |
| `CODEX_TIMEOUT` | — | `CLAUDE_TIMEOUT` or `10800` | Codex timeout in seconds |
| `CODEX_MODEL` | — | — | Codex model |
| `CODEX_SANDBOX` | — | `workspace-write` | Codex sandbox mode |
| `CODEX_APPROVAL` | — | `never` | Codex approval policy |
| `CODEX_DANGEROUS_BYPASS` | — | `true` | Set `true` to bypass Codex approvals and sandboxing |
| `CODEX_EXTRA_ARGS` | — | — | Extra arguments passed to `codex exec` / `codex exec resume` |
| `CODEX_HOME` | — | `~/.codex` | Directory used to read Codex session files |
| `SESSION_DB_PATH` | — | `sessions.db` | Path to the SQLite database file |

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

---

## CodexRunner Options (programmatic use)

```python
CodexRunner(
    workdir="/home/alice/myproject",           # equivalent to CODEX_WORKDIR
    codex_path="/home/alice/.local/bin/codex", # equivalent to CODEX_PATH
    timeout=10800,                             # equivalent to CODEX_TIMEOUT
    model="gpt-5.2",                           # equivalent to CODEX_MODEL (optional)
    sandbox="workspace-write",                 # equivalent to CODEX_SANDBOX
    approval="never",                          # equivalent to CODEX_APPROVAL
    dangerously_bypass=False,                  # equivalent to CODEX_DANGEROUS_BYPASS
    extra_args=["--skip-git-repo-check"],      # additional flags (optional)
)
```

For CLI startup, `CODEX_DANGEROUS_BYPASS` defaults to `true` because unattended systemd runs commonly cannot use Codex's sandbox. Programmatic `CodexRunner` defaults to `False` unless explicitly set.

When `CODEX_PATH` is an absolute path, its bin directory is prepended to `PATH` for the Codex subprocess. This helps Codex CLIs with a `/usr/bin/env node` shebang find `node` under systemd's narrow default `PATH`.
