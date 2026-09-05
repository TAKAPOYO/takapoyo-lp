#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze.py - Xアカウントの投稿データを分析する

使い方:
    python3 analyze.py <username>

前提:
    /tmp/x_user_<username>.json と /tmp/x_tweets_<username>.json が存在すること
    （SKILL.md の Step 3 で curl 取得済み）

出力:
    /tmp/x_analysis_<username>.json に分析結果を保存
    標準出力に分析サマリーを出力
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict


def load_data(username):
    """ユーザー情報と投稿データを読み込む"""
    with open(f'/tmp/x_user_{username}.json', 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    with open(f'/tmp/x_tweets_{username}.json', 'r', encoding='utf-8') as f:
        tweets_data = json.load(f)
    return user_data, tweets_data


def classify_tweet(text):
    """投稿のタイプを判定"""
    is_short_reply = (
        len(text) < 80 and
        ('ありがとう' in text or '嬉しい' in text or '感謝' in text or
         (text.count('！') >= 2 and len(text) < 50))
    )
    has_url = 'https://t.co' in text or 'http://' in text
    is_original_long = len(text) > 150 and not has_url
    return {
        'is_short_reply': is_short_reply,
        'has_url': has_url,
        'is_original_long': is_original_long,
        'length': len(text),
    }


def analyze_tweets(user_data, tweets_data):
    """投稿を分析し、構造化されたレポートを返す"""
    user = user_data.get('data', {})
    tweets = tweets_data.get('data', [])

    if not tweets:
        return {'error': 'No tweets found', 'user': user}

    # 各投稿のメトリクス整理
    rows = []
    for t in tweets:
        m = t.get('public_metrics', {})
        imp = m.get('impression_count', 0)
        likes = m.get('like_count', 0)
        rts = m.get('retweet_count', 0)
        replies = m.get('reply_count', 0)
        quotes = m.get('quote_count', 0)
        bookmarks = m.get('bookmark_count', 0)
        engagement = likes + rts + replies + quotes + bookmarks
        er = (engagement / imp * 100) if imp > 0 else 0
        created = datetime.fromisoformat(t['created_at'].replace('Z', '+00:00'))
        text = t['text']
        cls = classify_tweet(text)
        rows.append({
            'id': t['id'],
            'date': created,
            'date_iso': t['created_at'],
            'text': text,
            'imp': imp,
            'likes': likes,
            'rts': rts,
            'replies': replies,
            'quotes': quotes,
            'bookmarks': bookmarks,
            'engagement': engagement,
            'er': er,
            **cls,
        })

    # 日付順（新しい順）
    rows.sort(key=lambda x: x['date'], reverse=True)

    # 全体統計
    total_imp = sum(r['imp'] for r in rows)
    total_eng = sum(r['engagement'] for r in rows)
    avg_imp = total_imp / len(rows)
    avg_eng = total_eng / len(rows)
    avg_er = sum(r['er'] for r in rows) / len(rows)
    max_imp = max(r['imp'] for r in rows)
    min_imp = min(r['imp'] for r in rows)

    # 直近7投稿 vs 古い10投稿（シャドウバン判定）
    recent7 = rows[:7]
    older10 = rows[-10:]
    recent7_avg = sum(r['imp'] for r in recent7) / len(recent7)
    older10_avg = sum(r['imp'] for r in older10) / len(older10)
    ratio = recent7_avg / older10_avg if older10_avg > 0 else 1.0

    # 判定
    if ratio < 0.33:
        diagnosis = '重度のリーチ制限'
        severity = 'severe'
    elif ratio < 0.5:
        diagnosis = '軽度のリーチ制限'
        severity = 'mild'
    elif ratio < 0.7:
        diagnosis = '微減傾向'
        severity = 'mild_decline'
    else:
        diagnosis = '正常範囲'
        severity = 'normal'

    # 日次集計（JST）
    daily = defaultdict(list)
    for r in rows:
        jst = r['date'] + timedelta(hours=9)
        daily[jst.date()].append(r['imp'])
    daily_summary = []
    for d in sorted(daily.keys(), reverse=True):
        imps = daily[d]
        daily_summary.append({
            'date': d.isoformat(),
            'post_count': len(imps),
            'avg_imp': round(sum(imps) / len(imps)),
            'total_imp': sum(imps),
        })

    # 週次集計
    weekly = defaultdict(list)
    for r in rows:
        jst = r['date'] + timedelta(hours=9)
        wk = jst.strftime('%Y-W%U')
        weekly[wk].append(r['imp'])
    weekly_summary = []
    for wk in sorted(weekly.keys()):
        imps = weekly[wk]
        weekly_summary.append({
            'week': wk,
            'post_count': len(imps),
            'avg_imp': round(sum(imps) / len(imps)),
            'max_imp': max(imps),
            'min_imp': min(imps),
        })

    # 時間帯別（JST）
    hours = defaultdict(list)
    for r in rows:
        jst = r['date'] + timedelta(hours=9)
        hours[jst.hour].append(r['imp'])
    hourly_summary = []
    for h in sorted(hours.keys()):
        imps = hours[h]
        hourly_summary.append({
            'hour_jst': h,
            'post_count': len(imps),
            'avg_imp': round(sum(imps) / len(imps)),
        })

    # ベスト時間帯
    best_hour = max(hourly_summary, key=lambda x: x['avg_imp']) if hourly_summary else None

    # TOP5/ワースト5
    top5 = sorted(rows, key=lambda x: x['imp'], reverse=True)[:5]
    worst5 = sorted(rows, key=lambda x: x['imp'])[:5]

    # 投稿タイプ別
    short_replies = [r for r in rows if r['is_short_reply']]
    with_url = [r for r in rows if r['has_url']]
    original_long = [r for r in rows if r['is_original_long']]
    other = [r for r in rows if not r['is_short_reply'] and not r['has_url'] and not r['is_original_long']]

    def type_stats(label, lst):
        if not lst:
            return {'label': label, 'count': 0, 'avg_imp': 0, 'avg_er': 0}
        return {
            'label': label,
            'count': len(lst),
            'avg_imp': round(sum(r['imp'] for r in lst) / len(lst)),
            'avg_er': round(sum(r['er'] for r in lst) / len(lst), 2),
        }

    # シリアライズ可能な形に変換
    def clean(t):
        return {
            'id': t['id'],
            'date_iso': t['date_iso'],
            'text': t['text'],
            'imp': t['imp'],
            'likes': t['likes'],
            'rts': t['rts'],
            'replies': t['replies'],
            'bookmarks': t['bookmarks'],
            'engagement': t['engagement'],
            'er': round(t['er'], 2),
            'length': t['length'],
            'has_url': t['has_url'],
            'is_short_reply': t['is_short_reply'],
        }

    result = {
        'username': user.get('username'),
        'name': user.get('name'),
        'description': user.get('description'),
        'verified': user.get('verified'),
        'created_at': user.get('created_at'),
        'public_metrics': user.get('public_metrics', {}),
        'analysis': {
            'tweet_count_analyzed': len(rows),
            'overall': {
                'avg_imp': round(avg_imp),
                'avg_engagement': round(avg_eng, 1),
                'avg_er_pct': round(avg_er, 2),
                'max_imp': max_imp,
                'min_imp': min_imp,
                'total_imp': total_imp,
            },
            'shadowban_check': {
                'recent7_avg_imp': round(recent7_avg),
                'older10_avg_imp': round(older10_avg),
                'ratio': round(ratio, 3),
                'diagnosis': diagnosis,
                'severity': severity,
            },
            'daily': daily_summary,
            'weekly': weekly_summary,
            'hourly': hourly_summary,
            'best_hour_jst': best_hour,
            'top5': [clean(t) for t in top5],
            'worst5': [clean(t) for t in worst5],
            'type_stats': [
                type_stats('オリジナル長文（150字+リンクなし）', original_long),
                type_stats('短リプライ（挨拶系）', short_replies),
                type_stats('リンク付き投稿', with_url),
                type_stats('その他短文', other),
            ],
        },
    }

    return result


def print_summary(result):
    """標準出力に分析サマリーを出力"""
    if 'error' in result:
        print(f"エラー: {result['error']}")
        return

    user = result
    a = result['analysis']
    pm = user['public_metrics']

    print("=" * 80)
    print(f"X アカウント分析: @{user['username']}")
    print(f"名前: {user['name']}")
    print(f"認証: {user['verified']}")
    print(f"開設: {user['created_at']}")
    print("=" * 80)
    print(f"フォロワー: {pm.get('followers_count', 0):,}")
    print(f"フォロー中: {pm.get('following_count', 0):,}")
    print(f"投稿総数: {pm.get('tweet_count', 0):,}")
    print()
    print("【分析対象】 直近", a['tweet_count_analyzed'], "投稿")
    print()
    o = a['overall']
    print(f"平均インプ: {o['avg_imp']:,}")
    print(f"平均エンゲージメント: {o['avg_engagement']}")
    print(f"平均エンゲージメント率: {o['avg_er_pct']}%")
    print(f"最高インプ: {o['max_imp']:,}")
    print(f"最低インプ: {o['min_imp']:,}")
    print()
    sb = a['shadowban_check']
    print("=" * 80)
    print("【リーチ制限判定】")
    print(f"直近7投稿の平均インプ: {sb['recent7_avg_imp']:,}")
    print(f"古い10投稿の平均インプ: {sb['older10_avg_imp']:,}")
    print(f"比率: {sb['ratio']} ({int((1-sb['ratio'])*100)}%減少)")
    print(f">>> 判定: {sb['diagnosis']} <<<")
    print("=" * 80)
    print()

    print("【日次推移（最新10日）】")
    for d in a['daily'][:10]:
        print(f"  {d['date']}  投稿{d['post_count']:>2}本  平均{d['avg_imp']:>6,}imp")
    print()

    print("【時間帯別 平均インプ（JST）】")
    sorted_hours = sorted(a['hourly'], key=lambda x: x['avg_imp'], reverse=True)
    for h in sorted_hours:
        marker = ' 🏆' if h == sorted_hours[0] else ''
        print(f"  {h['hour_jst']:>2}時台  投稿{h['post_count']:>2}本  平均{h['avg_imp']:>6,}imp{marker}")
    print()

    print("【TOP5 投稿】")
    for i, t in enumerate(a['top5'], 1):
        print(f"  #{i} {t['imp']:,}imp ER{t['er']}%  {t['text'][:60]}")
    print()

    print("【ワースト5 投稿】")
    for i, t in enumerate(a['worst5'], 1):
        print(f"  #{i} {t['imp']}imp  {t['text'][:60]}")
    print()

    print("【投稿タイプ別】")
    for ts in a['type_stats']:
        print(f"  {ts['label']:<35} {ts['count']:>3}投稿 平均{ts['avg_imp']:>5,}imp ER{ts['avg_er']}%")


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze.py <username>")
        sys.exit(1)

    username = sys.argv[1].lstrip('@')

    try:
        user_data, tweets_data = load_data(username)
    except FileNotFoundError as e:
        print(f"データファイルが見つかりません: {e}")
        print(f"先に X API でデータ取得してください（SKILL.md Step 3 参照）")
        sys.exit(1)

    result = analyze_tweets(user_data, tweets_data)

    # 保存（WSL/Windows 両方からアクセス可能な場所）
    import os as _os
    shared_dir = '/mnt/c/Users/parla/.vscode/my-lp/.tmp_x_analysis'
    _os.makedirs(shared_dir, exist_ok=True)
    output_path = f'{shared_dir}/x_analysis_{username}.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    # 旧パスにも互換性のため保存
    with open(f'/tmp/x_analysis_{username}.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    # サマリー出力
    print_summary(result)
    print()
    print(f"分析結果を保存: {output_path}")


if __name__ == '__main__':
    main()
