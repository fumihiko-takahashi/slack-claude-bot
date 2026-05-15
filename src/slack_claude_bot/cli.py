"""python -m slack_claude_bot エントリーポイント。環境変数だけで起動できる最小構成。"""
import os
import shlex
import sys

from .bot import SlackClaudeBot
from .db import SessionDB
from .runner import ClaudeRunner, CodexRunner


def main() -> None:
    def require(name: str) -> str:
        val = os.environ.get(name)
        if not val:
            print(f"ERROR: 環境変数 {name} が未設定です。", file=sys.stderr)
            sys.exit(1)
        return val

    runner_name = os.environ.get("BOT_RUNNER", "claude").lower()
    if runner_name == "claude":
        runner = ClaudeRunner(
            project_dir=require("CLAUDE_PROJECT_DIR"),
            claude_path=os.environ.get("CLAUDE_PATH", "claude"),
            timeout=int(os.environ.get("CLAUDE_TIMEOUT", str(60 * 60 * 3))),
            extra_args=shlex.split(os.environ.get("CLAUDE_EXTRA_ARGS", "")),
        )
    elif runner_name == "codex":
        runner = CodexRunner(
            workdir=os.environ.get("CODEX_WORKDIR", os.getcwd()),
            codex_path=os.environ.get("CODEX_PATH", "codex"),
            timeout=int(os.environ.get("CODEX_TIMEOUT", os.environ.get("CLAUDE_TIMEOUT", str(60 * 60 * 3)))),
            model=os.environ.get("CODEX_MODEL"),
            sandbox=os.environ.get("CODEX_SANDBOX", "workspace-write"),
            approval=os.environ.get("CODEX_APPROVAL", "never"),
            dangerously_bypass=os.environ.get("CODEX_DANGEROUS_BYPASS", "true").lower() in {"1", "true", "yes"},
            extra_args=shlex.split(os.environ.get("CODEX_EXTRA_ARGS", "")),
            codex_home=os.environ.get("CODEX_HOME"),
        )
    else:
        print("ERROR: 環境変数 BOT_RUNNER は 'claude' または 'codex' を指定してください。", file=sys.stderr)
        sys.exit(1)
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
