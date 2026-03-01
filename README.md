# Alice Scanner 🚀 (V2.0)

台股全市場 AI 選股與自動化監控系統。

## 專案願景
Alice Scanner 旨在結合**量化篩選**與 **AI 深度解析**，為投資者提供每日最具潛力的標的。透過自動化的數據處理與網頁生成，建立一個專業、透明且具備洞察力的財經分析平台。

## 核心功能
1.  **全市場掃描 (All-Market Scan)**：
    - 每日自動抓取台股上市、上櫃（約 1,700 檔）所有股票數據。
    - 採用 10 執行緒平行處理，快速分析均線排列與量能變化。
2.  **飆股篩選模型 (Rocket Screener)**：
    - **多頭排列**：篩選價格站在 5MA、20MA 以上的標的。
    - **動能過濾**：鎖定成交量放大 1.5 倍以上、漲幅大於 2.5% 的強勢股。
    - **突破意圖**：自動偵測股價是否正處於 20 日新高附近的突破帶。
3.  **Alice AI 深度評論**：
    - 針對每日 Top 5 推薦標的，結合市場技術面與籌碼面，由 Alice 撰寫專業的投資觀點。
4.  **自動化發佈系統**：
    - **Google Sheets 同步**：每日自動建立日期分頁，備份完整掃描數據。
    - **Web Generator**：將數據與 AI 評論轉換為專業的 HTML 展示頁面。
    - **GitHub Pages 整合**：透過 Git 自動更新，實現免伺服器網站架設。

## 系統架構
- `alice_scanner_v2.py`: 全市場掃描核心引擎。
- `alice_insights.py`: AI 分析與評論生成器。
- `upload_to_sheets.py`: Google Sheets 數據同步工具。
- `web_generator.py`: 靜態網頁 (index.html) 生成腳本。
- `google_key.json`: Google API 憑證 (已排除於 Git)。

## 執行與部署
1.  **一鍵更新流程**：
    ```bash
    ./venv/bin/python3 alice_scanner_v2.py && \
    ./venv/bin/python3 alice_insights.py && \
    ./venv/bin/python3 upload_to_sheets.py && \
    ./venv/bin/python3 web_generator.py && \
    git add . && git commit -m "update: daily report" && git push
    ```
2.  **網站瀏覽**：
    透過 GitHub Pages 瀏覽：`https://simonawswork.github.io/alice_scanner/`

---
*本專案僅供研究與策略開發使用，不構成任何投資建議。投資有風險，入市需謹慎。*
