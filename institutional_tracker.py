import requests
import pandas as pd
from datetime import datetime
import time

def get_institutional_investors():
    """
    從證交所抓取今日三大法人買賣超排行 (上市)
    URL: https://www.twse.com.tw/rwd/zh/fund/T86FU1?date={date}&selectType=ALLBUT0999&response=json
    """
    today_str = datetime.now().strftime("%Y%m%d")
    # 測試用：如果是週末或還沒收盤，可能要抓前一天的數據，這裡先嘗試抓今日
    url = f"https://www.twse.com.tw/rwd/zh/fund/T86FU1?date={today_str}&selectType=ALLBUT0999&response=json"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('stat') != 'OK':
            print(f"⚠️ 無法取得今日 ({today_str}) 三大法人數據，可能尚未更新或休市。")
            return None
        
        # 欄位索引: 0:證券代號, 1:證券名稱, 2:外資買賣超, 3:投信買賣超, 4:自營商買賣超...
        # 具體索引依證交所格式，通常 2:外陸資買進, 3:外陸資賣出, 4:外陸資買賣超
        # 我們主要看 投信買賣超(10) 與 外資買賣超(4)
        
        rows = data.get('data', [])
        inst_data = []
        for row in rows:
            symbol = row[0].strip()
            name = row[1].strip()
            foreign_net = int(row[4].replace(',', ''))  # 外資買賣超
            trust_net = int(row[10].replace(',', ''))   # 投信買賣超
            
            inst_data.append({
                "symbol": f"{symbol}.TW",
                "外資買賣超": foreign_net,
                "投信買賣超": trust_net,
                "法人合計": foreign_net + trust_net
            })
            
        return pd.DataFrame(inst_data)
    except Exception as e:
        print(f"❌ 抓取法人數據出錯: {e}")
        return None

if __name__ == "__main__":
    df = get_institutional_investors()
    if df is not None:
        print(df.sort_values(by="投信買賣超", ascending=False).head(10))
