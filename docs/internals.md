# Internals

[日本語版](internals_ja.md)

## Why `--dangerously-skip-permissions` is required

Claude Code normally shows a confirmation prompt in the terminal before writing files or running commands:

```
Do you want to run this command?
  python experiment.py
❯ Yes  No
```

When invoked via subprocess, stdin is not connected to a terminal, so this prompt blocks indefinitely. The `--dangerously-skip-permissions` flag skips all such prompts.

This library is designed for personal use on a dedicated instance where the Slack workspace members are trusted. Use with caution in shared environments.

---

## Session Management

### Thread-to-session mapping

Slack's `thread_ts` (thread timestamp) is used as the key to map to a Claude Code `session_id` stored in SQLite.

```
Slack thread_ts  ↔  Claude Code session_id
   "1234567890"  →  "abc12345-..."
```

When a reply arrives in an existing thread, `--resume <session_id>` continues the conversation.

### How session IDs are obtained

The `--session-id` flag has the following constraints (discovered through testing):

- `--session-id` alone (new session) → error
- `--session-id` combined with `--resume` → error (`--fork-session` required)

The correct approach: start a new session with no flags, then retrieve the session ID from the newest `.jsonl` file under `~/.claude/projects/{project_dir}/` after the run completes.

```python
def _latest_session_id(self):
    files = glob.glob(f"{self.project_dir}/*.jsonl")
    latest = max(files, key=os.path.getmtime)
    return os.path.basename(latest).replace(".jsonl", "")
```

---

## Lock Mechanism

A `locks` table in SQLite prevents the same thread from spawning multiple Claude processes concurrently. The exclusive constraint relies on `thread_ts` being a `PRIMARY KEY` — a duplicate `INSERT` raises `IntegrityError`, which is treated as a lock failure.

Stale locks (older than the runner timeout + 30 min buffer) are automatically deleted at the next `acquire_lock` call. Locks are also cleared on startup via `clear_all_locks()` to recover from crashes.

---

## Timeout Behavior

`subprocess.run()` calls `process.kill()` on timeout, so Claude's process is terminated immediately — it does not continue running in the background.

Even after a timeout, the session ID is retrieved and saved so that the next message can resume the conversation via `--resume`:

```python
except subprocess.TimeoutExpired:
    if not session_id:
        session_id = self._latest_session_id()
    return "⏱ Timed out. Reply to this thread to resume.", session_id
```
