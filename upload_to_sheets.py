import gspread
import csv
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

BASE_DIR = "/home/ubuntu/.openclaw/workspace/alice_scanner"
GOOGLE_KEY = os.path.join(BASE_DIR, "google_key.json")
CSV_FILE = os.path.join(BASE_DIR, "daily_scan_results.csv")
SHEET_NAME = "Alice_Daily_Report"

def upload():
    try:
        # 1. 驗證與連線
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_KEY, scope)
        client = gspread.authorize(creds)
        
        # 2. 開啟試算表
        sh = client.open(SHEET_NAME)
        
        # 3. 建立新分頁 (以日期命名)
        tab_name = datetime.now().strftime("%Y-%m-%d")
        try:
            ws = sh.add_worksheet(title=tab_name, rows="100", cols="20")
        except:
            ws = sh.worksheet(tab_name)
            ws.clear()
            
        # 4. 讀取 CSV 並寫入
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            data = list(csv.reader(f))
            if data:
                ws.update('A1', data)
                print(f"✅ 成功將結果上傳至 {SHEET_NAME} -> 分頁: {tab_name}")
            else:
                print("❌ CSV 檔案為空。")
                
    except Exception as e:
        print(f"❌ 上傳錯誤: {e}")

if __name__ == "__main__":
    upload()
