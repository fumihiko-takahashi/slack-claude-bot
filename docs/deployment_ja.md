# デプロイ・常駐化

[English version](deployment.md)

## systemd による常駐化（Linux / GCE 推奨）

### サービスファイルの作成

```ini
# /etc/systemd/system/slack-claude-bot.service

[Unit]
Description=Slack Claude Bot
After=network.target

[Service]
User=your-username
WorkingDirectory=/home/your-username/your-project
Environment="SLACK_BOT_TOKEN=xoxb-..."
Environment="SLACK_APP_TOKEN=xapp-..."
Environment="CLAUDE_PROJECT_DIR=/home/your-username/.claude/projects/-home-your-username-your-project"
Environment="CLAUDE_PATH=/home/your-username/.local/bin/claude"
Environment="SESSION_DB_PATH=/home/your-username/your-project/sessions.db"
ExecStart=/home/your-username/your-project/.venv/bin/python -m slack_claude_bot
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> **注意**: `CLAUDE_PATH` に `claude` とだけ書くと systemd の起動時に PATH が引き継がれず失敗する。  
> `which claude` でフルパスを確認してから指定すること。

### 起動・有効化

```bash
sudo systemctl daemon-reload
sudo systemctl enable slack-claude-bot
sudo systemctl start slack-claude-bot
```

### ログの確認

```bash
sudo journalctl -u slack-claude-bot -f
```

### 停止・無効化

```bash
sudo systemctl stop slack-claude-bot
sudo systemctl disable slack-claude-bot
```

---

## プログラム利用時のエントリーポイント例

カスタムコマンドを追加する場合は、`-m slack_claude_bot` の代わりに以下のようなスクリプトを `ExecStart` に指定する：

```python
# main.py
import os
from slack_claude_bot import SlackClaudeBot, ClaudeRunner, SessionDB

runner = ClaudeRunner(
    project_dir=os.environ["CLAUDE_PROJECT_DIR"],
    claude_path=os.environ.get("CLAUDE_PATH", "claude"),
)
db = SessionDB(db_path=os.environ.get("SESSION_DB_PATH", "sessions.db"))
bot = SlackClaudeBot(
    slack_bot_token=os.environ["SLACK_BOT_TOKEN"],
    slack_app_token=os.environ["SLACK_APP_TOKEN"],
    runner=runner,
    db=db,
)

# プロジェクト固有のカスタムコマンドをここに追加
# @bot.command("!status", description="現在のステータスを表示")
# def handle_status(channel, thread_ts, text):
#     return "正常稼働中"

bot.start()
```
