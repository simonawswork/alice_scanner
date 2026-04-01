import pandas as pd
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from google import genai

# 設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "daily_scan_results.csv")
GOOGLE_KEY = os.path.join(BASE_DIR, "google_key.json")
SHEET_NAME = "Alice_Daily_Report"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"


def get_alice_insight(row):
    """呼叫 Gemini API 為單一個股生成 AI 專業評論"""
    symbol = row['代號']
    name = row.get('名稱', symbol)
    change = row.get('漲幅%', 'N/A')
    vol_ratio = row.get('量能倍率', 'N/A')
    above_5ma = row.get('站上5MA', 'N/A')
    above_20ma = row.get('站上20MA', 'N/A')
    near_high = row.get('突破意圖', 'N/A')
    foreign = row.get('外資(張)', 'N/A')
    trust = row.get('投信(張)', 'N/A')
    support = row.get('支撐', 'N/A')
    resistance = row.get('壓力', 'N/A')

    prompt = f"""你是一位台股專業分析師 Alice，請根據以下技術面與籌碼面數據，為這檔股票撰寫一段 100~150 字的繁體中文投資分析評論。

股票代號: {symbol}
股票名稱: {name}
今日漲幅: {change}%
量能倍率 (vs 20日均量): {vol_ratio} 倍
站上 5MA: {above_5ma}
站上 20MA: {above_20ma}
突破意圖 (近 20 日新高帶): {near_high}
外資買賣超(張): {foreign}
投信買賣超(張): {trust}
支撐價位: {support}
壓力價位: {resistance}

請以【{name}】開頭，分析技術面訊號與籌碼動向，給出操作建議（守哪個位置、短線或波段），語氣專業但易懂。不要加入免責聲明。"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"  ⚠️ Gemini 評論失敗 ({symbol}): {e}")
        return f"【{name}】今日漲幅 {change}%，量能放大 {vol_ratio} 倍，技術面多頭排列，建議持續追蹤。"


def generate_and_upload_insights():
    if not GEMINI_API_KEY:
        print("❌ 未設定 GEMINI_API_KEY 環境變數")
        return

    try:
        # 1. 讀取掃描結果
        df = pd.read_csv(CSV_FILE).head(5)  # 只分析前 5 檔
        print(f"📂 讀取掃描結果：{len(df)} 檔")

        # 2. 逐筆呼叫 Gemini 生成評論
        print("\n🤖 【Alice AI 每日盤後深度評論】")
        print("-" * 60)
        insights = []
        for _, row in df.iterrows():
            print(f"  🔍 分析 {row.get('名稱', row['代號'])} ({row['代號']})...")
            comment = get_alice_insight(row)
            insights.append(comment)
            print(f"  ✅ {comment[:60]}...\n")

        df['Alice AI 專業評論'] = insights

        # 3. 顯示完整結果
        print("\n📋 完整評論：")
        for _, row in df.iterrows():
            print(f"📍 {row['代號']} {row.get('名稱', '')}：\n{row['Alice AI 專業評論']}\n")

        # 4. 上傳到 Google Sheets（需要 google_key.json）
        if os.path.exists(GOOGLE_KEY):
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_KEY, scope)
            client = gspread.authorize(creds)

            sh = client.open(SHEET_NAME)
            tab_name = datetime.now().strftime("%Y-%m-%d")
            ws = sh.worksheet(tab_name)

            ws.update('H1', [["Alice AI 專業評論"]])
            ws.update('H2', [[row['Alice AI 專業評論']] for _, row in df.iterrows()])

            print(f"✨ Alice AI 評論已成功同步到 Google Sheets ({tab_name})！")
        else:
            print("⚠️  未找到 google_key.json，跳過 Google Sheets 同步")

    except FileNotFoundError:
        print(f"❌ 找不到掃描結果檔案：{CSV_FILE}")
        print("   請先執行 alice_scanner_v3.py")
    except Exception as e:
        print(f"❌ 評論生成失敗: {e}")


if __name__ == "__main__":
    generate_and_upload_insights()
