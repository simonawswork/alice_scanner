#!/bin/bash

# 定義路徑
BASE_DIR="/home/ubuntu/.openclaw/workspace/alice_scanner"
VENV_PYTHON="$BASE_DIR/venv/bin/python3"

echo "--------------------------------------------------"
echo "🚀 [$(date)] Alice Scanner 自動更新流程啟動..."
echo "--------------------------------------------------"

cd $BASE_DIR

# 1. 執行全市場籌碼+技術面掃描 (V3)
echo "🔍 執行 V3 全市場掃描..."
$VENV_PYTHON alice_scanner_v3.py

# 2. 生成 AI 專業評論
echo "🤖 生成 AI 深度解析..."
$VENV_PYTHON alice_insights.py

# 3. 同步數據至 Google Sheets
echo "📊 同步數據至 Google Sheets..."
$VENV_PYTHON upload_to_sheets.py

# 4. 更新 Web UI (index.html)
echo "🌐 生成最新 Web 展示頁面..."
$VENV_PYTHON web_generator.py

# 5. 推送到 GitHub Pages
echo "📤 同步至 GitHub 伺服器..."
git add .
git commit -m "update: daily report $(date +%F)"
git push origin main

echo "--------------------------------------------------"
echo "✅ [$(date)] Alice Scanner 今日任務圓滿達成！"
echo "--------------------------------------------------"
