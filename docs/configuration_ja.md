# 設定リファレンス

[English version](configuration.md)

## 環境変数

| 変数名 | 必須 | デフォルト | 説明 |
|---|---|---|---|
| `SLACK_BOT_TOKEN` | ✅ | — | `xoxb-...` 形式の Bot Token |
| `SLACK_APP_TOKEN` | ✅ | — | `xapp-...` 形式の App-level Token |
| `BOT_RUNNER` | — | `claude` | 使用する runner。`claude` または `codex` |
| `CLAUDE_PROJECT_DIR` | `BOT_RUNNER=claude` の時 ✅ | — | Claude Code のセッションファイルが保存されるディレクトリ |
| `CLAUDE_PATH` | — | `claude` | Claude Code CLI のフルパス |
| `CLAUDE_TIMEOUT` | — | `10800` | タイムアウト秒数（デフォルト: 3時間） |
| `CLAUDE_EXTRA_ARGS` | — | — | Claude Code CLI に渡す追加引数 |
| `CODEX_WORKDIR` | — | カレントディレクトリ | Codex を実行する作業ディレクトリ |
| `CODEX_PATH` | — | `codex` | Codex CLI のフルパス |
| `CODEX_TIMEOUT` | — | `CLAUDE_TIMEOUT` または `10800` | Codex 実行のタイムアウト秒数 |
| `CODEX_MODEL` | — | — | Codex のモデル指定 |
| `CODEX_SANDBOX` | — | `workspace-write` | Codex の sandbox モード |
| `CODEX_APPROVAL` | — | `never` | Codex の approval policy |
| `CODEX_DANGEROUS_BYPASS` | — | `true` | `true` で Codex の承認とサンドボックスをバイパス |
| `CODEX_EXTRA_ARGS` | — | — | `codex exec` / `codex exec resume` に渡す追加引数 |
| `CODEX_HOME` | — | `~/.codex` | Codex のセッションファイルを読むディレクトリ |
| `SESSION_DB_PATH` | — | `sessions.db` | SQLite ファイルのパス |

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

---

## CodexRunner のオプション（プログラム利用時）

```python
CodexRunner(
    workdir="/home/alice/myproject",           # CODEX_WORKDIR に相当
    codex_path="/home/alice/.local/bin/codex", # CODEX_PATH に相当
    timeout=10800,                             # CODEX_TIMEOUT に相当
    model="gpt-5.2",                           # CODEX_MODEL に相当（任意）
    sandbox="workspace-write",                 # CODEX_SANDBOX に相当
    approval="never",                          # CODEX_APPROVAL に相当
    dangerously_bypass=False,                  # CODEX_DANGEROUS_BYPASS に相当
    extra_args=["--skip-git-repo-check"],      # 追加フラグ（任意）
)
```

CLI 起動時は、無人実行で systemd の sandbox 制約に当たりやすいため `CODEX_DANGEROUS_BYPASS` のデフォルトは `true`。プログラム利用の `CodexRunner` は明示指定しない限り `False`。

`CODEX_PATH` に絶対パスを指定した場合、その bin ディレクトリを Codex 実行時の `PATH` 先頭に追加する。`/usr/bin/env node` shebang を使う Codex CLI が systemd の狭い `PATH` で node を見失う問題を避けるため。
