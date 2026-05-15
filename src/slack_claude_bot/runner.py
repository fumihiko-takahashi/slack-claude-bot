import glob
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Protocol


class Runner(Protocol):
    provider: str

    def run(self, instruction: str, session_id: str | None = None) -> tuple[str, str | None, float | None]:
        ...


class ClaudeRunner:
    provider = "claude"

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

    def _get_context_window_size(self, model_id: str) -> int:
        """モデルIDからコンテキストウィンドウサイズを取得"""
        if not model_id:
            return 200000  # デフォルト

        # 1M context window models
        if model_id in ['claude-opus-4-7', 'claude-opus-4-6', 'claude-sonnet-4-6']:
            return 1000000

        # 200K context window models (default)
        return 200000

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
                        model_id = data["message"].get("model", "")

                        input_tokens = usage.get("input_tokens", 0)
                        cache_creation = usage.get("cache_creation_input_tokens", 0)
                        cache_read = usage.get("cache_read_input_tokens", 0)

                        # モデルに応じたcontext window sizeを取得
                        total_input = input_tokens + cache_creation + cache_read
                        context_window_size = self._get_context_window_size(model_id)
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
class CodexRunner:
    provider = "codex"

    def __init__(
        self,
        workdir: str,
        codex_path: str = "codex",
        timeout: int = 60 * 60 * 3,
        model: str | None = None,
        sandbox: str | None = "workspace-write",
        approval: str | None = "never",
        dangerously_bypass: bool = False,
        extra_args: list[str] | None = None,
        codex_home: str | None = None,
    ):
        self.workdir = os.path.abspath(os.path.expanduser(workdir))
        self.codex_path = codex_path
        self.timeout = timeout
        self.model = model
        self.sandbox = sandbox
        self.approval = approval
        self.dangerously_bypass = dangerously_bypass
        self.extra_args = extra_args or []
        self.codex_home = os.path.abspath(os.path.expanduser(codex_home or os.environ.get("CODEX_HOME", "~/.codex")))

    def _global_args(self) -> list[str]:
        args: list[str] = []
        if self.model:
            args += ["--model", self.model]
        if self.dangerously_bypass:
            args.append("--dangerously-bypass-approvals-and-sandbox")
        else:
            if self.sandbox:
                args += ["--sandbox", self.sandbox]
            if self.approval:
                args += ["--ask-for-approval", self.approval]

        return args

    def _subprocess_env(self) -> dict[str, str]:
        env = os.environ.copy()
        codex_dir = os.path.dirname(self.codex_path)
        if codex_dir:
            current_path = env.get("PATH", "")
            paths = current_path.split(os.pathsep) if current_path else []
            if codex_dir not in paths:
                env["PATH"] = os.pathsep.join([codex_dir, current_path]) if current_path else codex_dir
        return env

    def _latest_session_id(self, since: float | None = None) -> str | None:
        sessions_dir = Path(self.codex_home) / "sessions"
        if not sessions_dir.exists():
            return None

        files = list(sessions_dir.glob("**/*.jsonl"))
        if since is not None:
            recent_files = [f for f in files if f.stat().st_mtime >= since]
            files = recent_files or files
        if not files:
            return None

        latest = max(files, key=lambda f: f.stat().st_mtime)
        try:
            with latest.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if data.get("type") == "session_meta":
                        return data.get("payload", {}).get("id")
        except Exception:
            return None
        return None

    def run(self, instruction: str, session_id: str | None = None) -> tuple[str, str | None, float | None]:
        started_at = time.time()
        output_path = None

        if session_id:
            cmd = [self.codex_path]
            cmd += self._global_args()
            cmd += ["exec", "resume"]
            cmd += self.extra_args
            cmd += ["--output-last-message"]
        else:
            cmd = [self.codex_path]
            cmd += self._global_args()
            cmd += ["exec"]
            cmd += self.extra_args
            cmd += ["--output-last-message"]

        try:
            with tempfile.NamedTemporaryFile(prefix="slack-codex-", suffix=".txt", delete=False) as f:
                output_path = f.name

            cmd.append(output_path)
            if session_id:
                cmd += [session_id, instruction]
            else:
                cmd.append(instruction)

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.workdir,
                env=self._subprocess_env(),
            )

            output = ""
            if output_path and os.path.exists(output_path):
                with open(output_path, encoding="utf-8") as f:
                    output = f.read().strip()
            if not output:
                output = proc.stdout.strip()
            if not session_id:
                session_id = self._latest_session_id(started_at)
            return output or "（出力なし）", session_id, None
        except subprocess.TimeoutExpired:
            if not session_id:
                session_id = self._latest_session_id(started_at)
            return (
                f"⏱ タイムアウト（{self.timeout}秒）しました。続きから再開するには返信してください。",
                session_id,
                None,
            )
        except Exception as e:
            return f"エラー: {e}", session_id, None
        finally:
            if output_path and os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except OSError:
                    pass
