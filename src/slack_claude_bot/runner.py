import glob
import json
import os
import subprocess


class ClaudeRunner:
    def __init__(
        self,
        project_dir: str,
        claude_path: str = "claude",
        timeout: int = 60 * 60 * 3,
        extra_args: list[str] | None = None,
    ):
        self.project_dir = os.path.expanduser(project_dir)
        self.claude_path = claude_path
        self.timeout = timeout
        self.extra_args = extra_args or []

    def _latest_session_id(self) -> str | None:
        files = glob.glob(f"{self.project_dir}/*.jsonl")
        if not files:
            return None
        latest = max(files, key=os.path.getmtime)
        return os.path.basename(latest).replace(".jsonl", "")

    def _get_context_usage(self, session_id: str | None) -> float | None:
        """トランスクリプトファイルから最新のコンテキスト使用率を計算"""
        if not session_id:
            return None

        transcript_path = f"{self.project_dir}/{session_id}.jsonl"
        if not os.path.exists(transcript_path):
            return None

        try:
            # 最後の行から逆順に読んで、最新のusage情報を見つける
            with open(transcript_path, "rb") as f:
                # ファイルの最後から読む
                f.seek(0, 2)
                file_size = f.tell()
                buffer_size = min(file_size, 100000)  # 最後の100KB程度を読む
                f.seek(max(0, file_size - buffer_size))
                lines = f.read().decode("utf-8").splitlines()

            # 最新のusage情報を探す（逆順）
            for line in reversed(lines):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if "message" in data and "usage" in data["message"]:
                        usage = data["message"]["usage"]
                        input_tokens = usage.get("input_tokens", 0)
                        cache_creation = usage.get("cache_creation_input_tokens", 0)
                        cache_read = usage.get("cache_read_input_tokens", 0)

                        # context_window_sizeのデフォルトは200,000トークン
                        total_input = input_tokens + cache_creation + cache_read
                        context_window_size = 200000
                        used_percentage = (total_input / context_window_size) * 100
                        return round(used_percentage, 1)
                except json.JSONDecodeError:
                    continue

            return None
        except Exception:
            return None

    def run(self, instruction: str, session_id: str | None = None) -> tuple[str, str | None, float | None]:
        cmd = [self.claude_path, "--print", "--dangerously-skip-permissions"]
        cmd += self.extra_args

        if session_id:
            cmd += ["--resume", session_id]

        cmd.append(instruction)

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            output = proc.stdout.strip()
            if not session_id:
                session_id = self._latest_session_id()
            context_usage = self._get_context_usage(session_id)
            return output or "（出力なし）", session_id, context_usage
        except subprocess.TimeoutExpired:
            if not session_id:
                session_id = self._latest_session_id()
            context_usage = self._get_context_usage(session_id)
            return (
                f"⏱ タイムアウト（{self.timeout}秒）しました。続きから再開するには返信してください。",
                session_id,
                context_usage,
            )
        except Exception as e:
            return f"エラー: {e}", session_id, None
