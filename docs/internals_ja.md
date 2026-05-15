# 内部実装の詳細

[English version](internals.md)

## なぜ `--dangerously-skip-permissions` が必要か

Claude Code は通常、ファイル書き込みやコマンド実行の前にターミナルで確認を求める：

```
Do you want to run this command?
  python experiment.py
❯ Yes  No
```

subprocess から呼び出した場合、stdin が繋がっていないためこのプロンプトで処理が無限にブロックされる。  
`--dangerously-skip-permissions` はこの確認をスキップするフラグ。

このライブラリは個人用途・実験専用インスタンスでの利用を前提としており、Slack ワークスペースのメンバーを信頼できる環境での使用を想定している。共有環境では注意が必要。

---

## Runner の切り替え

Slack 側の処理は runner の `run(instruction, session_id)` だけを呼び出す。Claude Code では `ClaudeRunner`、Codex では `CodexRunner` を使い、`BOT_RUNNER` 環境変数で選択する。

`!compact` は Claude Code の `/compact` に依存しているため、Codex runner では未対応として返答する。

---

## セッション管理の仕組み

### スレッドとセッションの対応

Slack の `thread_ts`（スレッドのタイムスタンプ）と runner provider をキーに、CLI の `session_id` を SQLite で管理する。

```
Slack thread_ts + provider  ↔  session_id
"1234567890" + "claude"     →  "abc12345-..."
"1234567890" + "codex"      →  "019e..."
```

同じスレッドへの返信が来たとき、Claude Code は `--resume <session_id>`、Codex は `codex exec resume <session_id>` で会話を継続する。

Codex の `--ask-for-approval`、`--sandbox`、`--dangerously-bypass-approvals-and-sandbox` は `exec` サブコマンドの前に置く。`codex exec --ask-for-approval never ...` の順序では失敗するバージョンがある。

### セッション ID の取得方法

`--session-id` フラグには以下の制約がある（実際に試して判明）：

- `--session-id` 単体（新規セッション時）→ エラー
- `--session-id` と `--resume` の同時指定 → エラー（`--fork-session` が必要と言われる）

正しい方法: 新規セッションはフラグなしで実行し、完了後に `~/.claude/projects/{project_dir}/` 以下の最新 `.jsonl` ファイル名からセッション ID を取得する。

```python
def _latest_session_id(self):
    files = glob.glob(f"{self.project_dir}/*.jsonl")
    latest = max(files, key=os.path.getmtime)
    return os.path.basename(latest).replace(".jsonl", "")
```

Codex は `~/.codex/sessions/YYYY/MM/DD/*.jsonl` の `session_meta.payload.id` を session ID として取得する。

---

## ロックの仕組み

同一スレッドへの連続メッセージで Claude が並列起動しないよう、SQLite の `locks` テーブルで排他制御している。  
`INSERT` の一意制約（`thread_ts` が PRIMARY KEY）を利用しており、二重取得時は `IntegrityError` が発生してロック失敗と判断する。

TTL（runner の timeout + 30分バッファ）を超えた残留ロックは次回の `acquire_lock` 時に自動削除される。  
起動時にも `clear_all_locks()` を呼び出してクラッシュ時の残留ロックをクリアする。

---

## タイムアウト時の挙動

`subprocess.run()` はタイムアウト時に内部で `process.kill()` を呼ぶため、Claude のプロセスは強制終了される（バックグラウンドで継続することはない）。

タイムアウト後でもセッション ID を取得・保存しておくことで、次のメッセージで `--resume` による再開が可能：

```python
except subprocess.TimeoutExpired:
    if not session_id:
        session_id = self._latest_session_id()
    return "⏱ タイムアウトしました。続きから再開するには返信してください。", session_id
```
