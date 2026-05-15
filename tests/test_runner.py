import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from slack_claude_bot import ClaudeRunner, CodexRunner


@pytest.fixture
def project_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_run_success(project_dir):
    runner = ClaudeRunner(project_dir=project_dir, claude_path="claude")
    mock_proc = MagicMock()
    mock_proc.stdout = "hello"

    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        output, session_id, context_usage = runner.run("say hello")

    assert output == "hello"
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "--dangerously-skip-permissions" in args
    assert "say hello" in args


def test_run_with_session(project_dir):
    runner = ClaudeRunner(project_dir=project_dir)
    mock_proc = MagicMock()
    mock_proc.stdout = "ok"

    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        output, session_id, context_usage = runner.run("do something", session_id="sess-123")

    args = mock_run.call_args[0][0]
    assert "--resume" in args
    assert "sess-123" in args


def test_run_timeout(project_dir):
    import subprocess
    runner = ClaudeRunner(project_dir=project_dir, timeout=1)

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 1)):
        output, _, _ = runner.run("slow task")

    assert "タイムアウト" in output


def test_run_empty_output(project_dir):
    runner = ClaudeRunner(project_dir=project_dir)
    mock_proc = MagicMock()
    mock_proc.stdout = "   "

    with patch("subprocess.run", return_value=mock_proc):
        output, _, _ = runner.run("silent task")

    assert output == "（出力なし）"


def test_codex_run_success(project_dir):
    runner = CodexRunner(
        workdir=project_dir,
        codex_path="codex",
        codex_home=os.path.join(project_dir, "empty-codex-home"),
    )
    mock_proc = MagicMock()
    mock_proc.stdout = "hello from codex"

    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        output, session_id, context_usage = runner.run("say hello")

    assert output == "hello from codex"
    assert session_id is None
    assert context_usage is None
    args = mock_run.call_args[0][0]
    assert args[0] == "codex"
    assert args.index("--sandbox") < args.index("exec")
    assert args.index("--ask-for-approval") < args.index("exec")
    assert "--sandbox" in args
    assert "workspace-write" in args
    assert "--ask-for-approval" in args
    assert "never" in args
    assert "say hello" in args
    assert mock_run.call_args.kwargs["cwd"] == project_dir


def test_codex_run_with_session(project_dir):
    runner = CodexRunner(workdir=project_dir)
    mock_proc = MagicMock()
    mock_proc.stdout = "ok"

    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        output, session_id, context_usage = runner.run("do something", session_id="sess-123")

    assert output == "ok"
    assert session_id == "sess-123"
    assert context_usage is None
    args = mock_run.call_args[0][0]
    assert args[0] == "codex"
    assert args[-4] == "--output-last-message"
    assert "exec" in args
    assert "resume" in args
    assert args.index("exec") < args.index("resume")
    assert "sess-123" in args
    assert "do something" in args
    assert args.index("--sandbox") < args.index("exec")
    assert args.index("--ask-for-approval") < args.index("exec")


def test_codex_run_prepends_codex_bin_to_path(project_dir):
    codex_path = os.path.join(project_dir, "bin", "codex")
    runner = CodexRunner(
        workdir=project_dir,
        codex_path=codex_path,
        codex_home=os.path.join(project_dir, "empty-codex-home"),
    )
    mock_proc = MagicMock()
    mock_proc.stdout = "ok"

    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        runner.run("do something")

    env = mock_run.call_args.kwargs["env"]
    assert env["PATH"].split(os.pathsep)[0] == os.path.dirname(codex_path)


def test_codex_extra_args_are_after_exec(project_dir):
    runner = CodexRunner(
        workdir=project_dir,
        extra_args=["--skip-git-repo-check"],
        codex_home=os.path.join(project_dir, "empty-codex-home"),
    )
    mock_proc = MagicMock()
    mock_proc.stdout = "ok"

    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        runner.run("do something")

    args = mock_run.call_args[0][0]
    assert args.index("exec") < args.index("--skip-git-repo-check")
    assert args.index("--skip-git-repo-check") < args.index("--output-last-message")


def test_codex_run_reads_latest_session_id(project_dir):
    codex_home = os.path.join(project_dir, "codex-home")
    session_dir = os.path.join(codex_home, "sessions", "2026", "05", "15")
    os.makedirs(session_dir)
    session_file = os.path.join(session_dir, "rollout.jsonl")
    with open(session_file, "w", encoding="utf-8") as f:
        f.write('{"type":"session_meta","payload":{"id":"codex-session-123"}}\n')

    runner = CodexRunner(workdir=project_dir, codex_home=codex_home)
    mock_proc = MagicMock()
    mock_proc.stdout = "ok"

    with patch("subprocess.run", return_value=mock_proc):
        output, session_id, context_usage = runner.run("do something")

    assert output == "ok"
    assert session_id == "codex-session-123"
    assert context_usage is None
