#!/bin/bash

# 定義路徑
BASE_DIR="/Users/simonhuang/.openclaw/workspace-kira/Dev/alice_scanner"
VENV_PYTHON="$BASE_DIR/venv/bin/python3"

# API Keys (從 ~/.openclaw/.env 讀取)
if [ -f "$HOME/.openclaw/.env" ]; then
    export $(grep -v '^#' "$HOME/.openclaw/.env" | xargs)
fi

echo "--------------------------------------------------"
echo "🚀 [$(date)] Alice Scanner 自動更新流程啟動..."
echo "--------------------------------------------------"

cd $BASE_DIR

# 0. 檢查今天是否為台灣交易日
echo "📅 檢查今日是否為交易日..."
IS_TRADING_DAY=$($VENV_PYTHON -c "
import requests, urllib3
from datetime import datetime, timedelta
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
today = datetime.now().strftime('%Y%m%d')
url = f'https://www.twse.com.tw/rwd/zh/fund/T86?date={today}&selectType=ALLBUT0999&response=json'
try:
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
    data = r.json()
    print('yes' if data.get('stat') == 'OK' else 'no')
except:
    print('no')
")

if [ "$IS_TRADING_DAY" != "yes" ]; then
    echo "🚫 今日非交易日，跳過執行。"
    exit 0
fi
echo "✅ 今日為交易日，繼續執行..."

# 1. 執行全市場籌碼+技術面掃描 (V3)
echo "🔍 執行 V3 全市場掃描..."
$VENV_PYTHON alice_scanner_v3.py
if [ $? -ne 0 ]; then echo "❌ 掃描失敗，中止流程"; exit 1; fi

# 2. 同步數據至 Google Sheets (需先建立分頁)
echo "📊 同步數據至 Google Sheets..."
$VENV_PYTHON upload_to_sheets.py

# 3. 生成 AI 專業評論 (需要分頁已存在)
echo "🤖 生成 AI 深度解析..."
$VENV_PYTHON alice_insights.py

# 4. 更新 Web UI (index.html)
echo "🌐 生成最新 Web 展示頁面..."
$VENV_PYTHON web_generator.py

# 5. 推送到 GitHub Pages
echo "📤 同步至 GitHub 伺服器..."
git add .
git commit -m "update: daily report $(date +%F)"
git push origin main

# 6. Telegram 推播
echo "📲 發送 Telegram 每日選股通知..."
$VENV_PYTHON telegram_notifier.py

echo "--------------------------------------------------"
echo "✅ [$(date)] Alice Scanner 今日任務圓滿達成！"
echo "--------------------------------------------------"
