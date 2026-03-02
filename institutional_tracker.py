import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json

def get_institutional_data():
    """
    精準抓取上市櫃法人數據 (V3.4 強化版)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.twse.com.tw/zh/page/trading/fund/T86FU1.html'
    }
    
    inst_map = {}
    today = datetime.now()
    
    # 嘗試找最近 7 天，確保避開連假
    for i in range(7):
        target_date = today - timedelta(days=i)
        if target_date.weekday() >= 5: continue # 跳過週末
        
        d_str = target_date.strftime("%Y%m%d")
        # 櫃買中心使用民國日期格式: 115/03/02
        roc_year = target_date.year - 1911
        d_tpex = f"{roc_year}/{target_date.strftime('%m/%d')}"
        
        print(f"🕵️ 嘗試抓取 {d_str} 的法人數據...")
        
        # A. 上市 (TWSE)
        url_twse = f"https://www.twse.com.tw/rwd/zh/fund/T86FU1?date={d_str}&selectType=ALLBUT0999&response=json"
        # B. 上櫃 (TPEx)
        url_tpex = f"https://www.tpex.org.tw/web/stock/aftertrading/fund/t86/t86_result.php?l=zh-tw&d={d_tpex}&stk_typ=EW"
        
        try:
            # 抓上市
            resp_twse = requests.get(url_twse, headers=headers, timeout=10)
            data_twse = resp_twse.json()
            
            if data_twse.get('stat') == 'OK':
                for row in data_twse.get('data', []):
                    sid = row[0].strip()
                    # 0:代號, 1:名稱, 2:外資買, 3:外資賣, 4:外資淨, 10:投信淨
                    foreign = int(row[4].replace(',', ''))
                    trust = int(row[10].replace(',', ''))
                    inst_map[f"{sid}.TW"] = {"外資": foreign, "投信": trust}
                
                # 抓上櫃 (只有在上市 OK 時才抓，確保日期同步)
                resp_tpex = requests.get(url_tpex, headers=headers, timeout=10)
                data_tpex = resp_tpex.json()
                if data_tpex.get('aaData'):
                    for row in data_tpex.get('aaData', []):
                        sid = row[0].strip()
                        # 上櫃格式: 0:代號, 5:外資淨, 11:投信淨
                        foreign = int(row[5].replace(',', ''))
                        trust = int(row[11].replace(',', ''))
                        inst_map[f"{sid}.TWO"] = {"外資": foreign, "投信": trust}
                
                print(f"✅ 成功! 取得 {d_str} 數據，共計 {len(inst_map)} 檔標的。")
                return inst_map
            else:
                print(f"❌ {d_str} 尚無數據 (證交所回傳: {data_twse.get('stat')})")
        except Exception as e:
            print(f"⚠️ 解析 {d_str} 出錯: {e}")
        
        time.sleep(2) # 禮貌延遲
        
    return {}

if __name__ == "__main__":
    data = get_institutional_data()
    print(f"測試結果: 抓到 {len(data)} 筆數據。")
