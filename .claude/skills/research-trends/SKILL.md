# Research Trends スキル

指定されたトピックについて最新トレンドをリサーチし、アプリ開発のインスピレーションを提供する。

## 使い方

```
/research-trends [トピック]
```

例：
- `/research-trends Product Hunt`
- `/research-trends AI tools`
- `/research-trends productivity apps`

## 実行内容

1. **WebSearchで最新情報を収集**
   - 指定トピックの最新トレンドを検索
   - 2026年の最新データを優先

2. **構造化されたレポートを出力**

3. **Obsidianに自動保存** (必須)
   - 保存先: `/mnt/c/Users/parla/.vscode/obsidian/clawd-workspace-for-obsidian/research/`
   - ファイル名: `YYYY-MM-DD_[トピック名(英語・小文字・ハイフン区切り)].md`
   - 例: `2026-03-01_product-hunt.md`, `2026-03-15_ai-tools.md`

### 出力フォーマット

YAMLフロントマター付きのMarkdownファイルとして保存:

```markdown
---
date: YYYY-MM-DD
topic: [トピック名]
tags:
  - research
  - trends
  - [トピック関連タグ]
  - app-development
---

# [トピック] トレンドレポート（YYYY年M月）

## トップ5アイテム
1. **名前** - 説明
2. ...

## カテゴリ・テーマ
| カテゴリ | 特徴 |
|---------|------|
| カテゴリA | 特徴 |

## キーテイクアウェイ
- ポイント1
- ポイント2
- ポイント3

## アプリ開発へのインサイト

> **「1つのことを美しくやる」の観点から**

- 実践的なアイデア1
- 実践的なアイデア2

## Sources
- [ソース名](URL)
```

## 注意事項

- シンプルで使いやすいアプリのアイデアを優先
- UI/UXの観点を含める
- 具体的で実装可能なインサイトを提供
- **リサーチ完了後、必ずObsidianに保存すること**
- 保存完了後、ファイルパスをユーザーに通知すること
