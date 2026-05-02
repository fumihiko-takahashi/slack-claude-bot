# Changelog

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
