# .vscode/my-lp プロジェクト

このディレクトリは Claude Code の初期セットアップ時に作られたローカルワークスペース。
現在は **素子として動作するためのフォールバック起点** として維持している。

## 素子の設定はどこにあるか

- **素子の人格・話し方・共通ルール**: `~/.claude/CLAUDE.md`（グローバル、2026-04-18 移行）
- **プロジェクト情報・運用ルール**: Claudeメモリ `/home/parla/.claude/projects/-mnt-c-Users-parla--vscode-my-lp/memory/`
- **日次セッションメモ**: `/mnt/c/Users/parla/Documents/obsidian/clawd-workspace-for-obsidian/memory/YYYY-MM-DD.md`

## CLAUDE.md 階層化（2026-04-18確定）

| 場所 | 用途 | 読み込まれるタイミング |
|---|---|---|
| `~/.claude/CLAUDE.md` | 素子の人格・共通ルール（グローバル） | どのプロジェクトで起動しても |
| `~/Documents/obsidian/clawd-workspace-for-obsidian/CLAUDE.md` | **プリン用キャラ設定**（VPS側Claude Code用） | VPSで起動時／ローカルでObsidianフォルダから起動時（後者は注意） |
| このファイル `.vscode/my-lp/CLAUDE.md` | プレースホルダー（参照先明示） | ここから起動時 |

## 運用上の注意

- **ローカルで素子として作業したい** → このディレクトリ（`.vscode/my-lp`）または任意の他ディレクトリから起動（グローバルCLAUDE.mdが読まれる）
- **Obsidian作業フォルダから起動した場合** → プリン用CLAUDE.mdが読まれてしまうので、素子として動かしたい作業には向かない
- **VPS側での作業** → プリンが稼働するため、素子設定は読まれない（正しい動作）

素子の最新状態は `~/.claude/CLAUDE.md` が正。このファイルに素子の人格情報は書かない（重複防止）。
