"""Test __main__.py module execution"""
import subprocess
import sys


def test_main_module_import():
    """Test that the __main__.py can be imported"""
    result = subprocess.run(
        [sys.executable, "-c", "import slack_claude_bot.__main__"],
        capture_output=True,
        text=True,
    )
    # Should import without error (but will fail due to missing env vars if run)
    assert result.returncode == 0


def test_main_module_execution_requires_env():
    """Test that running as module fails with proper error when env vars missing"""
    import os
    env = os.environ.copy()
    # Remove any Slack/Claude env vars that might be set
    for key in list(env.keys()):
        if key.startswith(("SLACK_", "CLAUDE_")):
            del env[key]

    result = subprocess.run(
        [sys.executable, "-m", "slack_claude_bot"],
        capture_output=True,
        text=True,
        timeout=2,
        env=env,
    )
    # Should fail due to missing required env vars
    assert result.returncode == 1
    # Should show error about missing env var
    assert "環境変数" in result.stderr or "ERROR" in result.stderr
