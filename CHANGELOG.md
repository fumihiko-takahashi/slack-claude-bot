# Changelog

## [0.1.1] - 2026-04-24

### Fixed
- Added `__main__.py` to enable `python -m slack_claude_bot` execution for systemd deployment

## [0.1.0] - 2026-04-23

### Added
- Initial release
- `SlackClaudeBot` — Slack Bolt ベースのメインクラス
- `ClaudeRunner` — Claude Code CLI を subprocess で実行
- `SessionDB` — SQLite によるセッション・ロック管理
- 組み込みコマンド: `!help`, `!reset`, `!reset all`, `!compact`
- `register_command()` / `@bot.command()` によるカスタムコマンド拡張
- CLI エントリーポイント (`python -m slack_claude_bot` / `slack-claude-bot`)
