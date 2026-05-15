# Changelog

## [0.4.0] - 2026-05-15

### Added
- Add Codex CLI support via `CodexRunner`
- Add `BOT_RUNNER=claude|codex` runner selection
- Add Codex environment options for workdir, model, sandbox, approval, timeout, extra args, and Codex home
- Store sessions per Slack thread and runner provider so Claude and Codex sessions do not conflict

### Changed
- Generalize Slack bot runner typing so custom runners can implement the same `run()` interface
- Make `!compact` Claude-only and return an unsupported message for Codex
- Pass Codex global options before the `exec` subcommand for CLI compatibility
- Prepend the Codex binary directory to `PATH` when running Codex, helping systemd find Node.js
- Default Codex CLI startup to bypass approvals and sandboxing for unattended systemd runs

### Documentation
- Document Codex setup, configuration, systemd deployment, and internal session handling in English and Japanese

## [0.3.0] - 2026-05-02

### Added
- Dynamic context window size detection based on model ID
- `ClaudeRunner._get_context_window_size()` method to determine window size (200K or 1M) from model ID

### Changed
- Context usage calculation now uses actual model context window size instead of hardcoded 200K
- Supports 1M context window for Claude Opus 4.7, Opus 4.6, and Sonnet 4.6

## [0.2.0] - 2026-05-02

### Added
- Display context usage percentage in Slack replies
- Add `ClaudeRunner._get_context_usage()` method to calculate usage from transcript files

## [0.1.1] - 2026-04-24

### Fixed
- Added `__main__.py` to enable `python -m slack_claude_bot` execution for systemd deployment

## [0.1.0] - 2026-04-23

### Added
- Initial release
- `SlackClaudeBot` — Main class based on Slack Bolt
- `ClaudeRunner` — Executes Claude Code CLI via subprocess
- `SessionDB` — Session and lock management with SQLite
- Built-in commands: `!help`, `!reset`, `!reset all`, `!compact`
- Custom command extension via `register_command()` / `@bot.command()`
- CLI entry point (`python -m slack_claude_bot` / `slack-claude-bot`)
