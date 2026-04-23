import glob
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

    def run(self, instruction: str, session_id: str | None = None) -> tuple[str, str | None]:
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
            return output or "（出力なし）", session_id
        except subprocess.TimeoutExpired:
            if not session_id:
                session_id = self._latest_session_id()
            return (
                f"⏱ タイムアウト（{self.timeout}秒）しました。続きから再開するには返信してください。",
                session_id,
            )
        except Exception as e:
            return f"エラー: {e}", session_id
