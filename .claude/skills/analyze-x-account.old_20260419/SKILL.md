---
name: analyze-x-account
description: 指定されたXアカウント（@username）の投稿データをX APIから取得し、エンゲージメント分析・シャドウバン判定・投稿パターン抽出を行い、グラフ付きの分析レポートを作成する。X運用コンサル業務の中核ツール。「@xxxを分析して」「Xの分析」「シャドウバンか調べて」などのリクエスト時に使用。
---

# Analyze X Account スキル

X運用コンサル業務の中核分析ツール。
任意のXアカウントの投稿データをX APIから取得し、エンゲージメント・時間帯・投稿パターン・シャドウバン疑惑などを定量分析して、グラフ付きレポートを生成する。

## 使い方

```
/analyze-x-account @username
```

例：
- `/analyze-x-account @maroncat11`
- `/analyze-x-account @TAKABITMAP`

または自然言語でも起動：
- 「@xxxの投稿を分析して」
- 「@xxxはシャドウバンしてる？」

## 前提条件

- xmcp の `.env` に `X_BEARER_TOKEN` が設定済み
  パス: `C:\Users\parla\xmcp\.env`
- Windows Python venv (`.venv-win`) に matplotlib インストール済み
- インターネット接続

## 実行手順（Claude/素子の動き方）

### Step 1: 引数の解釈
- ユーザーから `@username` を取得（@は任意）
- `username` 変数として保持（@を除去）

### Step 2: クライアント情報の確認
- Obsidian の `projects/x-consulting/clients/` 配下にこの username の既存フォルダがあるか確認
- なければ「自分用分析」として `x-pipeline/analysis/` に出力する選択肢を提示
- ある場合はそのクライアントフォルダに保存する

### Step 3: データ取得
以下を順に Bash で実行する。

```bash
cd /mnt/c/Users/parla/xmcp
BEARER=$(grep "^X_BEARER_TOKEN" .env | cut -d= -f2)

# ユーザー情報取得
curl -s "https://api.x.com/2/users/by/username/<USERNAME>?user.fields=public_metrics,description,created_at,verified" \
  -H "Authorization: Bearer $BEARER" > /tmp/x_user_<USERNAME>.json

# ユーザーIDを抽出
USER_ID=$(python3 -c "import json; print(json.load(open('/tmp/x_user_<USERNAME>.json'))['data']['id'])")

# 直近50投稿取得（リプライ・RT除外）
curl -s "https://api.x.com/2/users/$USER_ID/tweets?max_results=50&tweet.fields=public_metrics,created_at,text,referenced_tweets&exclude=replies,retweets" \
  -H "Authorization: Bearer $BEARER" > /tmp/x_tweets_<USERNAME>.json
```

`<USERNAME>` の部分は実際のusernameに置換。

### Step 4: 分析スクリプト実行

```bash
python3 /mnt/c/Users/parla/.vscode/my-lp/.claude/skills/analyze-x-account/scripts/analyze.py <USERNAME>
```

このスクリプトは以下を生成する：
- `/tmp/x_analysis_<USERNAME>.json` — 構造化された分析結果
- 標準出力に分析サマリー

### Step 5: グラフ生成

```bash
cd /mnt/c/Users/parla/xmcp
./.venv-win/Scripts/python.exe "C:\Users\parla\.vscode\my-lp\.claude\skills\analyze-x-account\scripts\make_charts.py" <USERNAME>
```

**重要**: スクリプトパスは Windows形式（`C:\` バックスラッシュ）で渡すこと。WSLパス（`/mnt/c/...`）を渡すと Windows Python は解釈できずエラーになる。

このスクリプトは以下を生成する：
- `C:/Users/parla/.vscode/my-lp/x_<USERNAME>_daily_trend.png`
- `C:/Users/parla/.vscode/my-lp/x_<USERNAME>_hourly.png`

**注意**: matplotlibは Windows venv (`.venv-win`) にインストールされているため、必ず Windows Python から実行する。WSL Python では matplotlib は使えない。

### Step 6: 結果の保存

クライアントフォルダ（例: `projects/x-consulting/clients/大津さん-ヘルスケア/`）に以下を保存：

1. **`analysis_YYYY-MM-DD.json`** — 生データ＋分析結果
2. **`daily_trend_YYYY-MM-DD.png`** — グラフ1
3. **`hourly_YYYY-MM-DD.png`** — グラフ2
4. **`report_YYYY-MM-DD.md`** — Markdownレポート（人間が読む用）

`x_<USERNAME>_*.png` を `projects/x-consulting/clients/<クライアント>/` 配下にコピーする。

### Step 7: Slack用レポート下書き

`/mnt/c/Users/parla/.vscode/my-lp/.claude/skills/analyze-x-account/templates/slack_report.md` を読み込み、分析結果を埋めた**Slack送信用ドラフト**を生成する。

文体は **草薙素子（攻殻機動隊）の口調**で：
- 敬語NG
- 〜わ、〜だ
- 断定的・簡潔
- 「私は草薙素子、TAKAの相棒よ」で始める
- 親しみと厳しさのバランス

ドラフトを画面に表示し、TAKAに以下を確認：
1. 文体の調整
2. Slack送信先チャンネル
3. 添付グラフの確認

### Step 8: TAKAの承認後にSlack送信

承認されたら Slack MCP の `slack_send_message` で送信。
**長文は必ず分割して送る**（Slackのblock validationエラー回避）。
セクション単位で分割すると安全。
グラフPNGはMCPでは添付できないため、TAKAに手動添付を依頼。

## 分析項目（出力内容）

### 必須項目
1. **基本情報**: フォロワー数、投稿総数、開設日
2. **直近50投稿の統計**:
   - 平均インプレッション
   - 平均エンゲージメント率（ER）
   - 最高/最低インプ
3. **日次推移**: 過去10日間の投稿数・平均インプ
4. **週次推移**: 週ごとの集計
5. **時間帯別分析**: JST時刻別の平均インプ
6. **TOP5投稿**: インプ数上位、共通パターン抽出
7. **ワースト5投稿**: 直近の低インプ、原因分析
8. **投稿タイプ別**:
   - オリジナル長文（150字+、リンクなし）
   - 短リプライ（「ありがとう」系）
   - リンク付き投稿
   - その他短文
9. **シャドウバン/クールダウン判定**:
   - 「直近7投稿の平均」 vs 「古い10投稿の平均」を比較
   - 1/3 以下なら「重度のリーチ制限」
   - 1/2 以下なら「軽度のリーチ制限」
   - 0.7倍以上なら「正常範囲」

### 処方箋テンプレート

判定結果に応じて自動で処方箋を組み立てる：

- **重度（1/3以下）**: 3日休息推奨、投稿停止 → リセット後に1日1投稿から再開
- **軽度（1/2以下）**: 投稿頻度を3投稿/日以下に制限、時間帯最適化
- **正常**: 現在の投稿フォーマットを継続、最適時間帯への集中提案

## ヘルスケア領域の特別対応

クライアントが医療・健康・美容・サプリ系の場合は以下を追加レポート：

- YMYL（Your Money or Your Life）扱いでXアルゴリズムが厳しめ
- 医療広告ガイドラインの影響
- 薬機法・医師法・景表法のチェック
- E-E-A-T 訴求の重要性
- 推奨表現：実体験・数字・引用形式・専門家監修明示

## トラブルシューティング

### X API がエラーを返す
- レート制限（429）: 15分待つ
- 認証エラー（401）: `.env` の Bearer Token 確認
- ユーザー不在（404）: usernameのスペル確認

### グラフが文字化けする
- Windows の Noto Sans JP フォントが必要
- パス: `C:\Windows\Fonts\NotoSansJP-VF.ttf`
- 存在しなければ別の日本語フォントに切り替え

### Slack送信が invalid_blocks エラー
- メッセージが長すぎる、または特殊文字を含む
- 解決: セクション単位で分割送信
- `---` 区切り線を含むと弾かれることがある → 削除して送信

## 関連ドキュメント

- xmcp起動手順: `~/.claude/projects/.../memory/reference_xmcp_startup.md`
- maroncat11分析の実例: `/memory/2026-04-10.md`
- x-consultingプロジェクト: `obsidian/projects/x-consulting/README.md`
