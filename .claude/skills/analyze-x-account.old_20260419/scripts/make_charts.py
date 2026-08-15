#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_charts.py - 分析結果からグラフ2枚を生成

使い方:
    python make_charts.py <username> [output_dir]

前提:
    /tmp/x_analysis_<username>.json が存在すること（analyze.py 実行後）
    Windows venv (.venv-win) の matplotlib 必須

出力:
    <output_dir>/x_<username>_daily_trend.png
    <output_dir>/x_<username>_hourly.png

    output_dir 省略時は C:/Users/parla/.vscode/my-lp/
"""

import json
import sys
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch


def setup_japanese_font():
    """日本語フォントをセットアップ"""
    font_candidates = [
        r"C:\Windows\Fonts\NotoSansJP-VF.ttf",
        r"C:\Windows\Fonts\YuGothB.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
    ]
    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                font_manager.fontManager.addfont(font_path)
                prop = font_manager.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = prop.get_name()
                break
            except Exception:
                continue
    plt.rcParams['axes.unicode_minus'] = False


def make_daily_chart(username, analysis, output_path):
    """日次推移グラフ"""
    daily = analysis['daily'][:10]  # 直近10日
    daily.reverse()  # 古い順に並び替え

    dates = [d['date'][5:] for d in daily]  # MM-DD
    posts = [d['post_count'] for d in daily]
    avg_imp = [d['avg_imp'] for d in daily]

    fig, ax1 = plt.subplots(figsize=(11, 6))

    color1 = '#e74c3c'
    ax1.set_xlabel('日付', fontsize=13)
    ax1.set_ylabel('平均インプレッション数', color=color1, fontsize=13)
    ax1.plot(dates, avg_imp, color=color1, marker='o', linewidth=3,
             markersize=10, label='平均インプ')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, max(avg_imp) * 1.15 if avg_imp else 100)
    ax1.grid(True, alpha=0.3)

    # ピークと底をアノテート
    peak_idx = avg_imp.index(max(avg_imp))
    bottom_idx = avg_imp.index(min(avg_imp))

    ax1.annotate(f'ピーク\n{max(avg_imp):,}imp',
                 xy=(dates[peak_idx], avg_imp[peak_idx]),
                 xytext=(dates[peak_idx], avg_imp[peak_idx] * 1.05 + 100),
                 ha='center', fontsize=11, fontweight='bold', color='#c0392b',
                 arrowprops=dict(arrowstyle='->', color='#c0392b'))
    if bottom_idx != peak_idx:
        ax1.annotate(f'底\n{min(avg_imp):,}imp',
                     xy=(dates[bottom_idx], avg_imp[bottom_idx]),
                     xytext=(dates[bottom_idx], max(avg_imp) * 0.4),
                     ha='center', fontsize=11, fontweight='bold', color='#8e44ad',
                     arrowprops=dict(arrowstyle='->', color='#8e44ad'))

    # 投稿数（副軸）
    ax2 = ax1.twinx()
    color2 = '#3498db'
    ax2.set_ylabel('投稿数', color=color2, fontsize=13)
    ax2.bar(dates, posts, alpha=0.25, color=color2, label='投稿数')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, max(posts) * 1.5 if posts else 5)

    sb = analysis['shadowban_check']
    title = f'@{username} 日次インプレッション推移（直近{len(dates)}日）\n判定: {sb["diagnosis"]}（直近7投稿は古い10投稿の{sb["ratio"]:.0%}）'
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def make_hourly_chart(username, analysis, output_path):
    """時間帯別グラフ"""
    hourly = sorted(analysis['hourly'], key=lambda x: x['hour_jst'])

    hours = [f"{h['hour_jst']}時" for h in hourly]
    hour_imps = [h['avg_imp'] for h in hourly]

    if not hour_imps:
        return

    max_imp = max(hour_imps)

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = []
    for v in hour_imps:
        if v >= max_imp * 0.7:
            colors.append('#e74c3c')
        elif v >= max_imp * 0.3:
            colors.append('#f39c12')
        else:
            colors.append('#bdc3c7')

    bars = ax.bar(hours, hour_imps, color=colors, edgecolor='#34495e', linewidth=1.5)

    for bar, val in zip(bars, hour_imps):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + max_imp * 0.02,
                f'{val:,}', ha='center', fontsize=10, fontweight='bold')

    ax.set_xlabel('投稿時間帯（JST）', fontsize=13)
    ax.set_ylabel('平均インプレッション数', fontsize=13)

    best_hour = max(hourly, key=lambda x: x['avg_imp'])
    title = f'@{username} 時間帯別平均インプレッション\nベストタイム: {best_hour["hour_jst"]}時台（{best_hour["avg_imp"]:,}imp）'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_ylim(0, max_imp * 1.15)
    ax.grid(True, axis='y', alpha=0.3)

    legend_elements = [
        Patch(facecolor='#e74c3c', label='優良時間帯（ピークの70%以上）'),
        Patch(facecolor='#f39c12', label='中程度（30〜70%）'),
        Patch(facecolor='#bdc3c7', label='弱い時間帯（30%未満）'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: make_charts.py <username> [output_dir]")
        sys.exit(1)

    username = sys.argv[1].lstrip('@')
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'C:/Users/parla/.vscode/my-lp'

    # WSL→Windowsパス変換
    if output_dir.startswith('/mnt/c/'):
        output_dir = 'C:' + output_dir[6:]

    # WSL/Windows 両方からアクセス可能なパスを優先
    candidates = [
        f'C:/Users/parla/.vscode/my-lp/.tmp_x_analysis/x_analysis_{username}.json',
        f'/mnt/c/Users/parla/.vscode/my-lp/.tmp_x_analysis/x_analysis_{username}.json',
        f'/tmp/x_analysis_{username}.json',
    ]
    analysis_path = None
    for c in candidates:
        if os.path.exists(c):
            analysis_path = c
            break
    if not analysis_path:
        print(f"分析ファイルが見つかりません。試したパス:")
        for c in candidates:
            print(f"  - {c}")
        print(f"先に analyze.py を実行してください")
        sys.exit(1)

    with open(analysis_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    setup_japanese_font()

    daily_path = f'{output_dir}/x_{username}_daily_trend.png'
    hourly_path = f'{output_dir}/x_{username}_hourly.png'

    make_daily_chart(username, data['analysis'], daily_path)
    print(f'保存: {daily_path}')

    make_hourly_chart(username, data['analysis'], hourly_path)
    print(f'保存: {hourly_path}')


if __name__ == '__main__':
    main()
