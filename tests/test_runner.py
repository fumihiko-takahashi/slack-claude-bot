import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from slack_claude_bot import ClaudeRunner


@pytest.fixture
def project_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_run_success(project_dir):
    runner = ClaudeRunner(project_dir=project_dir, claude_path="claude")
    mock_proc = MagicMock()
    mock_proc.stdout = "hello"

    with patch("subprocess.run", return_value=mock_proc) as mock_run:
        output, session_id = runner.run("say hello")

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
        runner.run("do something", session_id="sess-123")

    args = mock_run.call_args[0][0]
    assert "--resume" in args
    assert "sess-123" in args


def test_run_timeout(project_dir):
    import subprocess
    runner = ClaudeRunner(project_dir=project_dir, timeout=1)

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("claude", 1)):
        output, _ = runner.run("slow task")

    assert "タイムアウト" in output


def test_run_empty_output(project_dir):
    runner = ClaudeRunner(project_dir=project_dir)
    mock_proc = MagicMock()
    mock_proc.stdout = "   "

    with patch("subprocess.run", return_value=mock_proc):
        output, _ = runner.run("silent task")

    assert output == "（出力なし）"
