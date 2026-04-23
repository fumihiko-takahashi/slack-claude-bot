"""python -m slack_claude_bot エントリーポイント。環境変数だけで起動できる最小構成。"""
import os
import sys

from .bot import SlackClaudeBot
from .db import SessionDB
from .runner import ClaudeRunner


def main() -> None:
    def require(name: str) -> str:
        val = os.environ.get(name)
        if not val:
            print(f"ERROR: 環境変数 {name} が未設定です。", file=sys.stderr)
            sys.exit(1)
        return val

    runner = ClaudeRunner(
        project_dir=require("CLAUDE_PROJECT_DIR"),
        claude_path=os.environ.get("CLAUDE_PATH", "claude"),
        timeout=int(os.environ.get("CLAUDE_TIMEOUT", str(60 * 60 * 3))),
    )
    db = SessionDB(db_path=os.environ.get("SESSION_DB_PATH", "sessions.db"))
    bot = SlackClaudeBot(
        slack_bot_token=require("SLACK_BOT_TOKEN"),
        slack_app_token=require("SLACK_APP_TOKEN"),
        runner=runner,
        db=db,
    )
    bot.start()


if __name__ == "__main__":
    main()
