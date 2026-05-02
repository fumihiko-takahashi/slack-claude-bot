import re
import threading
from collections.abc import Callable

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .db import SessionDB
from .runner import ClaudeRunner

CommandHandler = Callable[[str, str, str], str | None]


class SlackClaudeBot:
    def __init__(
        self,
        slack_bot_token: str,
        slack_app_token: str,
        runner: ClaudeRunner,
        db: SessionDB,
    ):
        self.app_token = slack_app_token
        self.runner = runner
        self.db = db
        self.app = App(token=slack_bot_token)

        # {trigger_lower: (handler, description)}
        self._commands: dict[str, tuple[CommandHandler, str]] = {}

        self._register_builtin_commands()
        self.app.event("app_mention")(self._on_mention)

    # ------------------------------------------------------------------
    # コマンド登録
    # ------------------------------------------------------------------

    def register_command(
        self,
        trigger: str,
        handler: CommandHandler,
        description: str = "",
        case_sensitive: bool = False,
    ) -> None:
        key = trigger if case_sensitive else trigger.lower()
        self._commands[key] = (handler, description)

    def command(self, trigger: str, description: str = "", case_sensitive: bool = False):
        """デコレータ形式のコマンド登録。"""
        def decorator(fn: CommandHandler) -> CommandHandler:
            self.register_command(trigger, fn, description=description, case_sensitive=case_sensitive)
            return fn
        return decorator

    # ------------------------------------------------------------------
    # 組み込みコマンド
    # ------------------------------------------------------------------

    def _register_builtin_commands(self) -> None:
        def _help(channel, thread_ts, text):
            lines = ["*利用可能なコマンド一覧*\n"]
            for trigger, (_, desc) in sorted(self._commands.items()):
                line = f"`{trigger}`"
                if desc:
                    line += f" — {desc}"
                lines.append(line)
            return "\n".join(lines)

        def _reset(channel, thread_ts, text):
            self.db.release_lock(thread_ts)
            return "🔓 このスレッドのロックを解放しました。再度実行できます。"

        def _reset_all(channel, thread_ts, text):
            self.db.clear_all_locks()
            return "🔓 すべてのスレッドのロックを解放しました。"

        def _compact(channel, thread_ts, text):
            # /compact は Claude Code スラッシュコマンドとして処理
            threading.Thread(
                target=self._execute,
                args=(channel, thread_ts, "/compact"),
            ).start()
            return None  # _execute 内で返答するので、ここでは返さない

        self.register_command("!help",      _help,      description="このヘルプを表示")
        self.register_command("!reset",     _reset,     description="このスレッドのロックを強制解放")
        self.register_command("!reset all", _reset_all, description="すべてのロックを一括解放（管理者向け）")
        self.register_command("!compact",   _compact,   description="会話履歴を圧縮してコンテキストを節約")

    # ------------------------------------------------------------------
    # イベントハンドラ
    # ------------------------------------------------------------------

    def _on_mention(self, event, say):
        channel = event["channel"]
        thread_ts = event.get("thread_ts") or event["ts"]
        text = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()
        text_lower = text.lower()

        # 最長マッチでコマンドを探す（"!reset all" が "!reset" より先にマッチするよう）
        matched_trigger = None
        for trigger in sorted(self._commands, key=len, reverse=True):
            if text_lower == trigger or text_lower.startswith(trigger + " "):
                matched_trigger = trigger
                break

        if matched_trigger is not None:
            handler, _ = self._commands[matched_trigger]
            result = handler(channel, thread_ts, text)
            if result is not None:
                self.app.client.chat_postMessage(
                    channel=channel, thread_ts=thread_ts, text=result
                )
            return

        # 通常メッセージ → 別スレッドで Claude を実行（Slack 3秒 ACK 対策）
        threading.Thread(
            target=self._execute,
            args=(channel, thread_ts, text),
        ).start()

    def _execute(self, channel: str, thread_ts: str, text: str) -> None:
        if not self.db.acquire_lock(thread_ts):
            self.app.client.chat_postMessage(
                channel=channel,
                thread_ts=thread_ts,
                text="⏳ 前の処理が実行中です。しばらくお待ちください。",
            )
            return

        try:
            self.app.client.chat_postMessage(
                channel=channel, thread_ts=thread_ts, text="⚙️ 実行中..."
            )
            session_id = self.db.get_session(thread_ts)
            result, new_session_id, context_usage = self.runner.run(text, session_id)

            if new_session_id:
                self.db.save_session(thread_ts, new_session_id, channel)

            # コンテキスト使用率を返信に追加
            if context_usage is not None:
                result = f"{result}\n\n（コンテキスト使用率: {context_usage}%）"

            self.app.client.chat_postMessage(
                channel=channel, thread_ts=thread_ts, text=result
            )
        finally:
            self.db.release_lock(thread_ts)

    # ------------------------------------------------------------------
    # 起動
    # ------------------------------------------------------------------

    def start(self) -> None:
        self.db.init()
        self.db.clear_all_locks()
        print("Bot starting...")
        SocketModeHandler(self.app, self.app_token).start()
