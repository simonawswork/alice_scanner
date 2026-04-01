#!/bin/bash

# 定義路徑
BASE_DIR="/Users/simonhuang/.openclaw/workspace-kira/Dev/alice_scanner"
VENV_PYTHON="$BASE_DIR/venv/bin/python3"

# API Keys
export GEMINI_API_KEY="AIzaSyAPOKGQUft_OFKi2lnfSfbrYqRpGKQyiU0"

echo "--------------------------------------------------"
echo "🚀 [$(date)] Alice Scanner 自動更新流程啟動..."
echo "--------------------------------------------------"

cd $BASE_DIR

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

echo "--------------------------------------------------"
echo "✅ [$(date)] Alice Scanner 今日任務圓滿達成！"
echo "--------------------------------------------------"
