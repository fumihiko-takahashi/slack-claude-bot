# 設定リファレンス

[English version](configuration.md)

## 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
|---|---|---|---|
| `SLACK_BOT_TOKEN` | ✅ | — | `xoxb-...` 形式の Bot Token |
| `SLACK_APP_TOKEN` | ✅ | — | `xapp-...` 形式の App-level Token |
| `CLAUDE_PROJECT_DIR` | ✅ | — | Claude Code のセッションファイルが保存されるディレクトリ |
| `CLAUDE_PATH` | — | `claude` | Claude Code CLI のフルパス |
| `SESSION_DB_PATH` | — | `sessions.db` | SQLite ファイルのパス |
| `CLAUDE_TIMEOUT` | — | `10800` | タイムアウト秒数（デフォルト: 3時間） |

---

## CLAUDE_PROJECT_DIR の確認方法

Claude Code はセッションファイルを `~/.claude/projects/` 以下に保存する。  
ディレクトリ名は作業ディレクトリのパスの `/` を `-` に変換したもの。

```bash
ls ~/.claude/projects/
# 例: -home-alice-myproject
```

プロジェクトディレクトリが `/home/alice/myproject` の場合：

```
CLAUDE_PROJECT_DIR=~/.claude/projects/-home-alice-myproject
```

---

## CLAUDE_PATH の確認方法

```bash
which claude
# 例: /home/alice/.local/bin/claude
```

`claude` とだけ指定すると systemd や cron など PATH を引き継がない環境で `No such file or directory` になる。  
フルパスを指定しておくのが確実。

---

## ClaudeRunner のオプション（プログラム利用時）

```python
ClaudeRunner(
    project_dir="~/.claude/projects/-home-alice-myproject",  # CLAUDE_PROJECT_DIR に相当
    claude_path="/home/alice/.local/bin/claude",             # CLAUDE_PATH に相当
    timeout=10800,                                           # CLAUDE_TIMEOUT に相当
    extra_args=["--model", "claude-opus-4-6"],               # 追加フラグ（任意）
)
```
